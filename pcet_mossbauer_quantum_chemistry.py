#!/usr/bin/env python3
"""
pcet_mossbauer_quantum_chemistry.py
==================================
Spor 1: Kvantekjemisk PCET & Mössbauer Fastpunkt-Modell for Fe-Mo-S Nitrogenase

Inneholder:
1. IsotopeMechanics: Semiclassisk & kvantetunnelering for H/D/T isotopsubstitusjon (KIE).
2. FeClusterMossbauerModel: Elektron-tetthet ved Fe-kjernen rho(0), spinn-tilstander og isomerskift delta avvik (delta_delta).
3. HydrogenEvolutionCompetition: Konkurranse mellom N2-reduksjon og H2 ko-evolusjon i biomimetiske Fe-Mo-S klynger.
"""

import math
import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, List, Any

# Fysiske konstanter
HBAR = 1.054571817e-34       # J s
KB = 1.380649e-23            # J/K
EV_TO_J = 1.602176634e-19    # J per eV
MASS_H = 1.6735575e-27       # kg (Hydrogen)
MASS_D = 3.3435837e-27       # kg (Deuterium)
MASS_T = 5.0073567e-27       # kg (Tritium)

# =====================================================================
# 1. Kinetisk Isotopeffekt (KIE) & PCET Mekanikk
# =====================================================================

@dataclass
class PCETParams:
    temperature_k: float = 298.15     # Temperatur i Kelvin
    nu_stretch_cm1: float = 3000.0    # Fe-H/Fe-OH strekkfrekvens i cm^-1
    barrier_height_ev: float = 0.45   # Aktiveringsbarriere E_a (eV)
    barrier_width_angstrom: float = 0.5 # Barrierebredde for proton-tunnelering (Å)
    reorganization_energy_ev: float = 0.8 # Marcus omorganiseringsenergi lambda (eV)


class IsotopeMechanics:
    def __init__(self, params: PCETParams = PCETParams()):
        self.p = params
        # Konverter frekvens fra cm^-1 til Hz (omega = 2 pi c nu)
        self.c_cm_s = 2.99792458e10
        self.omega_H = 2 * math.pi * self.c_cm_s * self.p.nu_stretch_cm1

    def zpe_energy(self, mass_kg: float) -> float:
        """Beregner nullpunktsenergi ZPE = 1/2 hbar omega (i Joules)."""
        omega = self.omega_H * math.sqrt(MASS_H / mass_kg)
        return 0.5 * HBAR * omega

    def eckart_tunneling_factor(self, mass_kg: float) -> float:
        """Wigner / Bell barriere-tunneleringskorreksjon Gamma."""
        d_m = self.p.barrier_width_angstrom * 1e-10
        E_a_j = self.p.barrier_height_ev * EV_TO_J
        
        # Effektiv imasjinær frekvens ved barrieretoppen
        omega_i = math.sqrt((8 * E_a_j) / (mass_kg * d_m**2))
        u = (HBAR * omega_i) / (KB * self.p.temperature_k)
        
        if u >= 2 * math.pi:
            # Dyp tunnelering anomali
            return (u / 2) / math.sin(u / 2) if u < 6.0 else 15.0
        return 1.0 + (u**2) / 24.0

    def calculate_kie(self, target_isotope: str = "D") -> Dict[str, float]:
        """Beregner KIE = k_H / k_X med ZPE og tunneleringsbidrag."""
        mass_target = MASS_D if target_isotope == "D" else (MASS_T if target_isotope == "T" else MASS_H)
        
        zpe_H = self.zpe_energy(MASS_H)
        zpe_X = self.zpe_energy(mass_target)
        delta_zpe = zpe_H - zpe_X
        
        # Klassisk ZPE-forhold: exp(Delta ZPE / (k_B T))
        kie_zpe = math.exp(delta_zpe / (KB * self.p.temperature_k))
        
        # Tunneleringsforhold: Gamma_H / Gamma_X
        gamma_H = self.eckart_tunneling_factor(MASS_H)
        gamma_X = self.eckart_tunneling_factor(mass_target)
        kie_tunnel = gamma_H / gamma_X
        
        total_kie = kie_zpe * kie_tunnel
        
        return {
            "isotope": target_isotope,
            "total_kie": total_kie,
            "kie_zpe_component": kie_zpe,
            "kie_tunnel_component": kie_tunnel,
            "tunnel_factor_H": gamma_H,
            "tunnel_factor_X": gamma_X,
        }


# =====================================================================
# 2. Mössbauer Isomerskift (delta_delta) & Spinn-tilstander
# =====================================================================

@dataclass
class FeStateConfig:
    oxidation_state: int  # 2 for Fe(II), 3 for Fe(III), 4 for Fe(IV)
    spin_s: float         # 0, 0.5, 1.0, 1.5, 2.0, 2.5
    coordination_num: int # 4, 5, 6 (tetraedrisk, trigonal bipyramidal, oktaedrisk)
    ligand_donating_index: float # 0.0 (ren S), 1.0 (sterk N/O donor)


class FeClusterMossbauerModel:
    def __init__(self, canonical_shift_ref: float = 0.80):
        self.delta_ref = canonical_shift_ref
        
        # Kalibreringskoeffisienter for s-elektrontetthet rho(0)
        # delta = alpha * (rho(0) - rho_ref) + beta
        self.alpha_scale = -0.32  # mm/s per (a.u.)^-3
        self.rho_ref = 15.20     # Referansetetthet i a.u.

    def estimate_electron_density(self, config: FeStateConfig) -> float:
        """Estimere s-elektrontetthet rho(0) basert på oksidasjonstrinn og avskjerming fra d-elektroner."""
        # Antall d-elektroner
        n_d = 6 - (config.oxidation_state - 2)
        
        # d-elektroner skjermer 3s-elektroner fra Fe-kjernen -> reduserer rho(0)
        shielding_effect = 0.45 * n_d
        
        # High-spin tilstander har større d-skjerming enn low-spin
        spin_shielding = 0.12 * config.spin_s
        
        # Ligandklor- / svovel-donering øker kovalent deling -> reduserer d-skjerming
        covalency_boost = 0.35 * config.ligand_donating_index
        
        rho_0 = 17.50 - shielding_effect - spin_shielding + covalency_boost
        return rho_0

    def calculate_isomer_shift(self, config: FeStateConfig) -> Dict[str, Any]:
        """Beregner Mössbauer isomerskift delta og avvik delta_delta fra 0.80 mm/s."""
        rho_0 = self.estimate_electron_density(config)
        delta_calc = self.alpha_scale * (rho_0 - self.rho_ref) + 0.65
        delta_delta = delta_calc - self.delta_ref
        
        # Kategori-bestemmelse
        if -0.04 <= delta_delta <= 0.04:
            zone = "ISOMETRIC_NULL_ZONE"
            verdict = "PASS"
        elif 0.04 < delta_delta <= 0.10:
            zone = "PERIPHERAL_INDUCTION"
            verdict = "HOLD"
        elif delta_delta > 0.10:
            zone = "ASYMMETRIC_DONATION"
            verdict = "HOLD"
        elif -0.10 <= delta_delta < -0.04:
            zone = "APICAL_ELECTRON_DRAIN"
            verdict = "HOLD"
        else:
            zone = "GLOBAL_ELECTRON_DRAIN"
            verdict = "KILL"
            
        return {
            "oxidation_state": config.oxidation_state,
            "spin_s": config.spin_s,
            "rho_zero": rho_0,
            "delta_calculated_mms": delta_calc,
            "delta_delta_mms": delta_delta,
            "mossbauer_zone": zone,
            "verdict": verdict
        }


# =====================================================================
# 3. H2 Ko-evolusjon vs N2 Reduksjonskonkurranse
# =====================================================================

class HydrogenEvolutionCompetition:
    def __init__(self):
        pass

    def evaluate_faradaic_split(self, overpotential_mv: float, pcet_kie: float) -> Tuple[float, float]:
        """
        Beregner fordeling mellom Faradaic Efficiency for N2 reduksjon (FE_N2)
        og bivannstoff-utvikling (FE_H2).
        """
        # H2-utvikling overtar hvis KIE er for lav (mangler PCET-kontroll)
        # eller hvis overpotensialet er for lite (< 100 mV).
        eta_factor = 1.0 / (1.0 + math.exp(-(overpotential_mv - 120.0) / 20.0))
        kie_factor = 1.0 if (2.0 <= pcet_kie <= 7.0) else 0.4
        
        fe_n2 = 0.95 * eta_factor * kie_factor
        fe_h2 = 1.0 - fe_n2
        return fe_n2, fe_h2


# =====================================================================
# 4. Hovedkjøring & Verifikasjon av Spor 1
# =====================================================================

def main():
    print("=====================================================================")
    print("=== SPOR 1: KVANTEKJEMISK PCET & MÖSSBAUER FASTPUNKT-MODELL (Fe-Mo-S) ===")
    print("=====================================================================\n")

    # 1. KIE Isotopeffekter
    pcet_mech = IsotopeMechanics()
    kie_d = pcet_mech.calculate_kie("D")
    kie_t = pcet_mech.calculate_kie("T")

    print("[1. KINETISK ISOTOPEFFEKT (PCET)]")
    print(f"  Deuterium KIE (k_H/k_D): {kie_d['total_kie']:.3f} (ZPE: {kie_d['kie_zpe_component']:.3f}, Tunnelering: {kie_d['kie_tunnel_component']:.3f})")
    print(f"  Tritium KIE   (k_H/k_T): {kie_t['total_kie']:.3f} (ZPE: {kie_t['kie_zpe_component']:.3f}, Tunnelering: {kie_t['kie_tunnel_component']:.3f})")
    
    val_status = "GODKJENT (2.0 <= KIE <= 7.0)" if 2.0 <= kie_d['total_kie'] <= 7.0 else "AVVIK"
    print(f"  -> PCET-Terskel Vurdering: {val_status}\n")

    # 2. Mössbauer Isomerskift for Spinn-tilstander
    moss_model = FeClusterMossbauerModel(canonical_shift_ref=0.80)
    
    test_configs = [
        FeStateConfig(oxidation_state=3, spin_s=2.5, coordination_num=6, ligand_donating_index=0.85), # Fe(III) High-spin FeMoCo active
        FeStateConfig(oxidation_state=2, spin_s=2.0, coordination_num=4, ligand_donating_index=0.60), # Fe(II) High-spin
        FeStateConfig(oxidation_state=4, spin_s=1.0, coordination_num=6, ligand_donating_index=0.90), # Fe(IV) Intermediær
    ]

    print("[2. MÖSSBAUER ISOMERSKIFT (delta_delta) OG SPINN-MAPPING]")
    print(f"{'Fe Oks.':<8} | {'Spinn S':<8} | {'rho(0) (a.u.)':<14} | {'delta (mm/s)':<14} | {'delta_delta (mm/s)':<18} | {'Sone & DOM'}")
    print("-" * 90)
    for cfg in test_configs:
        res = moss_model.calculate_isomer_shift(cfg)
        print(f"Fe({res['oxidation_state']})   | {res['spin_s']:<8.1f} | {res['rho_zero']:<14.3f} | {res['delta_calculated_mms']:<14.4f} | {res['delta_delta_mms']:<18.4f} | {res['mossbauer_zone']} ({res['verdict']})")
    print("-" * 90 + "\n")

    # 3. N2 / H2 Konkurranse
    h2_comp = HydrogenEvolutionCompetition()
    fe_n2, fe_h2 = h2_comp.evaluate_faradaic_split(overpotential_mv=140.0, pcet_kie=kie_d['total_kie'])

    print("[3. FARADAIC SPLIT (N2 Reduksjon vs H2 Ko-evolusjon)]")
    print(f"  Overpotensial: 140 mV | KIE: {kie_d['total_kie']:.2f}")
    print(f"  -> Faradaic Efficiency (N2 -> 2 NH3): {fe_n2*100:.1f}%")
    print(f"  -> Faradaic Efficiency (2 H+ -> H2):   {fe_h2*100:.1f}%\n")

if __name__ == "__main__":
    main()
