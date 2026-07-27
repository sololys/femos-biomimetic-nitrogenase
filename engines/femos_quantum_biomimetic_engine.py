#!/usr/bin/env python3
"""
femos_quantum_biomimetic_engine.py
==================================
Integrated Biomimetic Fe-Mo-S Quantum Control & Realization Engine (v1.0)

Combines:
1. QSA Quantum State-Space Control (15 states, 6 control inputs, Riccati H_inf gain tuning across Nominal/Thermal/Shock regimes).
2. PCET & Mössbauer Gate Evaluator (KIE gate, Isomer shift Δδ zone classification, Faradaic Efficiency, Perturbation recovery).
3. CIVIL Anaerobic Spectrometer (O2 threshold < 0.5 ppm, NH3 noise prohibition).
4. Atlas 4-Layer Realization Pipeline & WORM Witness Hashing.
"""

import sys
import math
import json
import time
import hashlib
import numpy as np
import scipy.linalg as la
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Any, Optional

# =====================================================================
# 1. PCET & Mössbauer Data Structures
# =====================================================================

@dataclass
class Candidate:
    name: str
    kie: float          # Kinetic Isotope Effect (PCET threshold: 2.0 <= KIE <= 7.0)
    delta_delta: float  # Mössbauer isomer shift deviation from canonical 0.8 mm/s
    stability: float    # Structural stability (0.0 to 1.0, required >= 0.80)
    fe: float           # Faradaic Efficiency (0.0 to 1.0, required >= 0.85)
    delta_E_mV: float   # Improvement in overpotential (mV, required >= 100)
    recovery_30s: float # 30s perturbation recovery drift (required <= 0.05)
    o2_ppm: float       # Anaerobic atmosphere O2 level (required < 0.5 ppm)
    nh3_ppm: float      # Anthropocene NH3 noise (required == 0.0 ppm)


# =====================================================================
# 2. Gate Definitions (Fail-Closed Architecture)
# =====================================================================

def kie_gate(kie: float) -> Tuple[str, str]:
    if kie < 2.0:
        return "KILL", "KIE under PCET-terskel (< 2.0)"
    if kie > 7.0:
        return "HOLD", "KIE indikerer uforutsigbar kvantetunnelering (> 7.0)"
    return "PASS", "Godkjent PCET-mekanisme (2.0 <= KIE <= 7.0)"


def mossbauer_zone(delta: float) -> Tuple[str, str]:
    if not math.isfinite(delta):
        return "HOLD", "Ugyldig Δδ verdikonstruksjon"
    if -0.04 <= delta <= 0.04:
        return "NO_MUTATION", "Isometric null zone (Kanonisk fastpunkt ±0.04 mm/s)"
    if 0.04 < delta <= 0.10:
        return "PERIPHERAL_INDUCTION", "Moderat elektronunderskudd"
    if delta > 0.10:
        return "ASYMMETRIC_DONATION", "Sterkt elektronunderskudd i Fe-klyngen"
    if -0.10 <= delta < -0.04:
        return "APICAL_ELECTRON_DRAIN", "Moderat elektronoverføring"
    if delta < -0.10:
        return "GLOBAL_ELECTRON_DRAIN", "Ekstrem elektronoverføring / destabilisering"
    return "HOLD", "Uklassifisert Mössbauer-sone"


def performance_gate(c: Candidate) -> Tuple[str, str]:
    if c.delta_E_mV < 100:
        return "KILL", f"Utilstrekkelig overpotensialforbedring ({c.delta_E_mV:.1f} mV < 100 mV)"
    if c.fe < 0.85:
        return "KILL", f"Utilstrekkelig Faradaic Efficiency ({c.fe*100:.1f}% < 85%)"
    return "PASS", "Ytelse innenfor tillatte grenser"


def perturbation_gate(c: Candidate) -> Tuple[str, str]:
    if c.recovery_30s > 0.05:
        return "KILL", f"Gjenoppretting feilet etter perturbasjon ({c.recovery_30s:.3f} > 0.05)"
    if c.stability < 0.80:
        return "KILL", f"Latent strukturell instabilitet ({c.stability:.2f} < 0.80)"
    return "PASS", "Strukturell perturbasjonsgjenoppretting godkjent"


def civil_anaerobic_gate(c: Candidate) -> Tuple[str, str]:
    if c.o2_ppm >= 0.5:
        return "KILL", f"Anaerob svikt: O2-nivå for høyt ({c.o2_ppm:.2f} ppm >= 0.5 ppm)"
    if c.nh3_ppm > 0.0:
        return "KILL", f"Antropocen kontaminering detektert: NH3 = {c.nh3_ppm:.2f} ppm"
    return "PASS", "Anaerob miljørenhet bekreftet"


def realization_energy(c: Candidate) -> float:
    e_kie = max(0.0, 2.0 - c.kie) + max(0.0, c.kie - 7.0)
    e_delta = abs(c.delta_delta)
    e_stability = max(0.0, 0.80 - c.stability)
    e_fe = max(0.0, 0.85 - c.fe)
    e_E = max(0.0, 100.0 - c.delta_E_mV) / 100.0
    e_recovery = max(0.0, c.recovery_30s - 0.05)
    e_o2 = max(0.0, c.o2_ppm - 0.5)
    e_nh3 = max(0.0, c.nh3_ppm)
    
    return (
        2.0 * e_kie**2 +
        5.0 * e_delta**2 +
        3.0 * e_stability**2 +
        3.0 * e_fe**2 +
        2.0 * e_E**2 +
        4.0 * e_recovery**2 +
        10.0 * e_o2**2 +
        10.0 * e_nh3**2
    )


# =====================================================================
# 3. Quantum State-Space Control (QSA Fe-Mo Engine)
# =====================================================================

class QSAFeMoControlEngine:
    def __init__(self, dt: float = 4e-9, n_state: int = 15, n_ctrl: int = 6):
        self.dt = dt
        self.n_state = n_state
        self.n_ctrl = n_ctrl
        self.q24_scale = 2**24

        # Physical relaxation dynamics: T1 = 50us, T2 = 30us
        self.gamma_1 = 1.0 / 50e-6
        self.gamma_2 = 1.0 / 30e-6

        # Build continuous state matrix A_c
        diag_A = [-self.gamma_2, -self.gamma_2, -self.gamma_1, -self.gamma_2, -self.gamma_2, -self.gamma_1] + \
                 [-2*self.gamma_2]*4 + [-self.gamma_1 - self.gamma_2]*4 + [-2*self.gamma_1]
        self.A_c = np.diag(diag_A)

        # Parasitic ZZ-coupling between active Fe-Mo cluster states
        self.zeta_zz = 2 * np.pi * 50e3  # 50 kHz
        self.A_c[6, 7] = self.zeta_zz
        self.A_c[7, 6] = -self.zeta_zz

        # Discrete-time plant matrix A_d
        self.A_d = np.eye(self.n_state) + self.A_c * self.dt

        # Control input matrix B_c (Rabi drive @ 20 MHz)
        self.rabi_rate = 2 * np.pi * 20e6
        self.B_c = np.zeros((self.n_state, self.n_ctrl))
        np.fill_diagonal(self.B_c, self.rabi_rate)
        np.random.seed(42)
        self.B_c += np.random.normal(0, self.rabi_rate * 0.05, (self.n_state, self.n_ctrl))
        self.B_d = self.B_c * self.dt

    def compute_regime_gains(self) -> Dict[str, List[np.ndarray]]:
        regimes = ["nominal", "thermal", "shock"]
        Q_pen = np.eye(self.n_state) * 1e8
        R_pen = np.eye(self.n_ctrl) * 1.0

        # Continuous Algebraic Riccati Equation (CARE)
        P = la.solve_continuous_are(self.A_c, self.B_c, Q_pen, R_pen)
        K_ideal = la.inv(R_pen) @ self.B_c.T @ P

        gains = {}
        for regime in regimes:
            gains[regime] = []
            scale_mult = 1.0 if regime == "nominal" else (0.85 if regime == "thermal" else 0.50)
            for k_idx in range(16):
                K_scaled = K_ideal * (scale_mult - k_idx * 0.01)
                K_q24 = (K_scaled * self.q24_scale).astype(int) / self.q24_scale
                gains[regime].append(K_q24)
        return gains

    def analyze_regime_stability(self) -> Dict[str, Any]:
        gains = self.compute_regime_gains()
        report = {}

        for regime, K_list in gains.items():
            regime_res = []
            for k_idx, K in enumerate(K_list):
                A_cl = self.A_d - self.B_d @ K
                eigvals, eigvecs = la.eig(A_cl)
                rho = float(np.max(np.abs(eigvals)))
                margin = float(1.0 - rho)
                cond_v = float(np.linalg.cond(eigvecs))
                regime_res.append({
                    "idx": k_idx,
                    "spectral_radius": rho,
                    "margin": margin,
                    "cond_v": cond_v,
                    "eigvecs": eigvecs
                })
            report[regime] = regime_res

        # Calculate transient amplification factors across regime shifts
        V_nom = report["nominal"][7]["eigvecs"]
        V_therm = report["thermal"][10]["eigvecs"]
        V_shock = report["shock"][2]["eigvecs"]

        growth_nom_to_therm = float(np.linalg.norm(la.inv(V_therm) @ V_nom, ord=2))
        growth_therm_to_shock = float(np.linalg.norm(la.inv(V_shock) @ V_therm, ord=2))

        return {
            "regimes": report,
            "transient_growth": {
                "nominal_to_thermal": growth_nom_to_therm,
                "thermal_to_shock": growth_therm_to_shock
            }
        }


# =====================================================================
# 4. Atlas Realization Pipeline & WORM Hashing
# =====================================================================

class AtlasBiomimeticPipeline:
    def __init__(self):
        self.qsa_engine = QSAFeMoControlEngine()

    def run_full_evaluation(self, candidate: Candidate) -> Dict[str, Any]:
        trace = []

        # Layer 0: Anaerobic & Anthropocene Noise Filter
        verdict, reason = civil_anaerobic_gate(candidate)
        trace.append({"stage": "ANAEROBIC_CIVIL", "verdict": verdict, "reason": reason})
        if verdict != "PASS":
            return self._build_result(candidate, verdict, trace)

        # Layer 1: Kinetic Isotope Effect (PCET)
        verdict, reason = kie_gate(candidate.kie)
        trace.append({"stage": "KINETIC_ISOTOPE", "verdict": verdict, "reason": reason})
        if verdict != "PASS":
            return self._build_result(candidate, verdict, trace)

        # Layer 2: Mössbauer Isomer Shift Zone
        zone, reason = mossbauer_zone(candidate.delta_delta)
        trace.append({"stage": "MOSSBAUER_ZONE", "verdict": zone, "reason": reason})

        # Layer 3: Faradaic Efficiency & Overpotential
        verdict, reason = performance_gate(candidate)
        trace.append({"stage": "PERFORMANCE", "verdict": verdict, "reason": reason})
        if verdict != "PASS":
            return self._build_result(candidate, verdict, trace)

        # Layer 4: Perturbation Recovery & Structural Stability
        verdict, reason = perturbation_gate(candidate)
        trace.append({"stage": "PERTURBATION", "verdict": verdict, "reason": reason})
        if verdict != "PASS":
            return self._build_result(candidate, verdict, trace)

        final_verdict = "OPEN" if zone == "NO_MUTATION" else "HOLD"
        return self._build_result(candidate, final_verdict, trace)

    def _build_result(self, candidate: Candidate, verdict: str, trace: List[Dict[str, str]]) -> Dict[str, Any]:
        energy = realization_energy(candidate)
        
        # Build SHA-256 WORM witness seal
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        raw_data = f"{candidate.name}:{verdict}:{energy:.6f}:{timestamp}"
        cd_seal = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

        return {
            "candidate_name": candidate.name,
            "verdict": verdict,
            "realization_energy_V": float(energy),
            "trace": trace,
            "cd_seal_sha256": cd_seal,
            "timestamp_utc": timestamp
        }


# =====================================================================
# 5. CLI Execution & Test Suite
# =====================================================================

def main():
    print("=====================================================================")
    print("=== BIOMIMETIC Fe-Mo-S NITROGENASE & QUANTUM REALIZATION ENGINE ===")
    print("=====================================================================\n")

    # 1. Run QSA Quantum Control Stability Analysis
    qsa_engine = QSAFeMoControlEngine()
    qsa_results = qsa_engine.analyze_regime_stability()

    print("[QSA KVANTEMENT-ANALYSIS]")
    print(f"{'Regime':<10} | {'Idx':<3} | {'Spektralradius (ρ)':<20} | {'Margin':<10} | {'Kondisjonstall V'}")
    print("-" * 75)
    for regime, data in qsa_results["regimes"].items():
        for item in data:
            if item["idx"] in [0, 7, 15]:
                print(f"{regime:<10} | {item['idx']:<3} | {item['spectral_radius']:<20.6f} | {item['margin']:<10.6f} | {item['cond_v']:<15.2f}")
    print("-" * 75)
    print(f"Transient growth (Nominal -> Thermal): {qsa_results['transient_growth']['nominal_to_thermal']:.4f}")
    print(f"Transient growth (Thermal -> Shock):   {qsa_results['transient_growth']['thermal_to_shock']:.4f}\n")

    # 2. Evaluate Biomimetic Candidate Test Battery
    candidates = [
        Candidate("FeMo_01_Kanonisk_Ren", 3.8, 0.01, 0.95, 0.92, 140.0, 0.02, 0.1, 0.0),
        Candidate("FeMo_02_Low_KIE", 1.4, 0.02, 0.95, 0.90, 140.0, 0.02, 0.1, 0.0),
        Candidate("FeMo_03_O2_Contaminated", 4.0, 0.01, 0.96, 0.91, 150.0, 0.02, 1.2, 0.0),
        Candidate("FeMo_04_NH3_Anthropocene", 4.2, 0.01, 0.95, 0.90, 150.0, 0.02, 0.1, 0.4),
        Candidate("FeMo_05_Low_FE", 4.0, -0.06, 0.90, 0.60, 160.0, 0.03, 0.1, 0.0),
        Candidate("FeMo_06_Fragile_Recovery", 4.0, 0.01, 0.90, 0.90, 160.0, 0.12, 0.1, 0.0),
    ]

    pipeline = AtlasBiomimeticPipeline()
    print("[PORTVOKTER & PIPELINE-EVALUERING]")
    for c in candidates:
        res = pipeline.run_full_evaluation(c)
        print(f"\nKandidat: {res['candidate_name']:<25} | DOM: {res['verdict']:<6} | Tapsenergi V = {res['realization_energy_V']:.4f}")
        print(f"  SHA-256 Vitneforsegling: {res['cd_seal_sha256']}")
        for t in res["trace"]:
            print(f"  - {t['stage']:<18} -> {t['verdict']:<20} | {t['reason']}")

if __name__ == "__main__":
    main()
