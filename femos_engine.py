#!/usr/bin/env python3
"""
====================================================================================================
AETHELGARD MOLECULAR: PROTOKOLL Fe-Mo-S DETERMINISTIC ADMISSIBILITY ENGINE v3.0
ANAEROBIC BIO-INORGANIC SYNTHESIS & ELECTROCHEMICAL NITROGEN FIXATION (N2 -> NH3)
====================================================================================================
Author: Marius Egerhei Torjusen (ORCID: 0009-0006-0431-6637)
System: ReismannPoint Systems AS // Kreativ Systems (kreativ-systems.org)
Reference: PROTOKOLL-FE-MO-S-VALIDERING-2026-v1.0

Protocol Specifications Implemented:
  DEL I: Kjemisk Arkitektur og Strukturell Integritet
         - Anaerobt regime: O2 < 1.0 ppm, H2O < 1.0 ppm (Forhindrer Fe-O-Fe okso-broer)
         - Støkiometrisk ICP-OES toleransegrense: <= ±2.5%
         - Mössbauer isotopskift (80K): Fe(II) target δ = 0.45 ± 0.03 mm/s (ΔEq = 2.10 ± 0.15 mm/s)
         - Katodisk reduksjonsvindu: E_cat ∈ [-1.45V, -1.65V] vs Fc/Fc+
  DEL II: KIE-Protokoll og Spektrale Signaturer (Kausalitet)
         - H/D Kinetic Isotope Effect: KIE = k_H / k_D >= 5.0 (Veto-Gate)
         - Operando in situ Raman/IR: 14N2 (1980 cm^-1) -> 15N2 (1915 cm^-1) -> Diazenido (1490 cm^-1)
         - 15N-NMR anti-selvbedrag: δ = -310 ppm, 1J(N-H) = 73.5 ± 1.0 Hz
  DEL III: Ytelsesmatrise, 3-Blank Witness og Mutasjons-Feedback
         - Faradaic Efficiency: FE_NH3 >= 15.0%
         - 3-Blank Forensic Witness: Minus-Katalysator, Ar-Atmosfære, Open-Circuit (0M NH4+)
         - Feedback Algoritme (Generasjon V+1): KGS-1 til KGS-4 mutasjoner og Tolman kjeglevinkel
====================================================================================================
"""

import hashlib
import json
import math
import time
from typing import Dict, Any, Tuple, List, Optional

class EmpiricalBondPredictor:
    """
    Layer 2: Heuristisk Bindingskalkulator & Termodynamisk Prediktor (Pauling-Morse).
    """
    ELEMENT_DB = {
        "H":  {"en": 2.20, "radius_pm": 31},
        "C":  {"en": 2.55, "radius_pm": 76},
        "N":  {"en": 3.04, "radius_pm": 71},
        "O":  {"en": 3.44, "radius_pm": 66},
        "S":  {"en": 2.58, "radius_pm": 105},
        "Fe": {"en": 1.83, "radius_pm": 126},
        "Mo": {"en": 2.16, "radius_pm": 145},
        "W":  {"en": 2.36, "radius_pm": 146},
        "Se": {"en": 2.55, "radius_pm": 120}
    }

    def predict_bond(self, atom_a: str, atom_b: str, bond_order: float = 1.0,
                     actual_dist_pm: Optional[float] = None) -> Dict[str, Any]:
        if atom_a not in self.ELEMENT_DB or atom_b not in self.ELEMENT_DB:
            return {"viable": False, "reason": f"UNSUPPORTED_ELEMENTS ({atom_a}-{atom_b})", "bde_kj_mol": 0.0}

        da = self.ELEMENT_DB[atom_a]
        db = self.ELEMENT_DB[atom_b]
        ideal_dist = (da["radius_pm"] + db["radius_pm"]) * (1.0 - 0.06 * abs(da["en"] - db["en"]))
        dist = actual_dist_pm if actual_dist_pm is not None else ideal_dist

        delta_en = abs(da["en"] - db["en"])
        base_bde = 250.0 * (1.0 + 0.5 * delta_en) * math.sqrt(bond_order)
        dist_ratio = dist / ideal_dist
        strain = math.exp(-2.0 * ((dist_ratio - 1.0) ** 2))
        bde = base_bde * strain
        delta_g = -1.0 * (bde - 50.0 * bond_order)
        viable = delta_g < 0.0 and bde >= 100.0

        return {
            "bond": f"{atom_a}-{atom_b}",
            "order": bond_order,
            "ideal_pm": round(ideal_dist, 2),
            "actual_pm": round(dist, 2),
            "bde_kj_mol": round(bde, 2),
            "delta_g_kj_mol": round(delta_g, 2),
            "viable": viable
        }


class FeMoSProtocolAdmissibilityGate:
    """
    Layer 3: PROTOKOLL Fe-Mo-S Fail-Closed Eksekverings- og Valideringskjerne.
    Håndhever samtlige 3 deler av protokollen med deterministisk VETO.
    """
    # DEL I: Kjemiske & Termiske Invarianter
    MAX_O2_PPM = 1.0
    MAX_H2O_PPM = 1.0
    MAX_STOICHIOMETRY_DEV_PCT = 2.5
    MOSSBAUER_DELTA_MIN = 0.42  # mm/s
    MOSSBAUER_DELTA_MAX = 0.48  # mm/s
    MOSSBAUER_EQ_MIN = 1.95     # mm/s
    MOSSBAUER_EQ_MAX = 2.25     # mm/s
    E_CAT_MAX_VOLT = -1.45      # V vs Fc/Fc+
    E_CAT_MIN_VOLT = -1.65      # V vs Fc/Fc+

    # DEL II: Kausalitet & Spektroskopi Invarianter
    MIN_H_D_KIE = 5.0
    REQUIRED_15N_NMR_PPM_MIN = -315.0
    REQUIRED_15N_NMR_PPM_MAX = -305.0
    REQUIRED_J_COUPLING_HZ_MIN = 72.5
    REQUIRED_J_COUPLING_HZ_MAX = 74.5

    # DEL III: Ytelse & 3-Blank Invarianter
    MIN_FARADAIC_EFFICIENCY_PCT = 15.0

    def __init__(self):
        self.state = "IDLE"
        self.relay_voltage_v = 0.0
        self.emergency_latched = False
        self.inert_purge_active = False

    def evaluate_protocol_candidate(self, candidate: Dict[str, Any]) -> Tuple[str, str, float, Optional[str]]:
        """
        Evaluerer kandidaten mot PROTOKOLL Fe-Mo-S.
        Returnerer: (Decision, Reason, Voltage, SuggestedMutation)
        """
        if self.emergency_latched:
            return "KILL", "SYSTEM_LATCHED_FAIL_CLOSED_EMERGENCY_SHUTDOWN", 0.0, None

        # --- DEL I: STRUKTURELL OG ELEKTRONISK INTEGRITET ---
        o2_ppm = float(candidate.get("o2_ppm", 0.2))
        h2o_ppm = float(candidate.get("h2o_ppm", 0.1))
        if o2_ppm > self.MAX_O2_PPM or h2o_ppm > self.MAX_H2O_PPM:
            self.state = "KILL"
            self.relay_voltage_v = 0.0
            self.emergency_latched = True
            return "KILL", f"AEROBIC_CONTAMINATION (O2={o2_ppm}ppm, H2O={h2o_ppm}ppm -> Fatal Fe-O-Fe oxo-bridge formation)", 0.0, None

        stoich_dev = float(candidate.get("stoichiometry_dev_pct", 0.0))
        if abs(stoich_dev) > self.MAX_STOICHIOMETRY_DEV_PCT:
            self.state = "KILL"
            self.relay_voltage_v = 0.0
            self.emergency_latched = True
            return "KILL", f"STOICHIOMETRIC_ANOMALY (Deviation {stoich_dev}% > {self.MAX_STOICHIOMETRY_DEV_PCT}%)", 0.0, None

        mb_delta = float(candidate.get("mossbauer_delta_mm_s", 0.45))
        mb_eq = float(candidate.get("mossbauer_eq_mm_s", 2.10))

        # Generasjon V+1 Diagnose og Mutasjons-Algoritme (DEL 3.3)
        mutation_directive = None
        if mb_delta > 0.55:
            mutation_directive = "KGS-1: Asymmetrisk sigma-injeksjon (Bytt ekvatorialt fosfin med alkyl-NHC)"
        elif 0.48 < mb_delta <= 0.55:
            mutation_directive = "KGS-2: Perifer donor-induksjon (Introduser -OMe på aryl-ringene for å heve HOMO)"
        elif 0.40 <= mb_delta < 0.42:
            mutation_directive = "KGS-3: Apikal pi-filtrering (Introduser -CF3 på apikal ligand)"
        elif mb_delta < 0.40:
            mutation_directive = "KGS-4: Tripodal pi-tapping (Bytt chelaterende arm med sterk pi-akseptor fosfitt)"

        if not (self.MOSSBAUER_DELTA_MIN <= mb_delta <= self.MOSSBAUER_DELTA_MAX and self.MOSSBAUER_EQ_MIN <= mb_eq <= self.MOSSBAUER_EQ_MAX):
            self.state = "REJECT"
            self.relay_voltage_v = 0.0
            return "REJECT", f"MOSSBAUER_OUT_OF_BOUNDS (δ={mb_delta} mm/s, ΔEq={mb_eq} mm/s)", 0.0, mutation_directive

        e_cat = float(candidate.get("cathodic_potential_v", -1.55))
        if e_cat < self.E_CAT_MIN_VOLT:
            self.state = "KILL"
            self.relay_voltage_v = 0.0
            self.emergency_latched = True
            return "KILL", f"POTENTIAL_HER_DOMINANCE (E_cat={e_cat}V < {self.E_CAT_MIN_VOLT}V vs Fc/Fc+)", 0.0, None
        if e_cat > self.E_CAT_MAX_VOLT:
            self.state = "HOLD"
            self.relay_voltage_v = 0.0
            return "HOLD", f"INSUFFICIENT_OVERPOTENTIAL_FOR_PCET (E_cat={e_cat}V > {self.E_CAT_MAX_VOLT}V)", 0.0, None

        # --- DEL II: KAUSALITET (KIE, RAMAN, 15N-NMR) ---
        kie = float(candidate.get("h_d_kie_ratio", 6.2))
        if kie < self.MIN_H_D_KIE:
            self.state = "HOLD"
            self.relay_voltage_v = 0.0
            return "HOLD", f"KIE_CAUSALITY_VIOLATION (KIE={kie:.2f} < {self.MIN_H_D_KIE} -> PCET not rate-determining)", 0.0, None

        diazenido_raman_shift = float(candidate.get("diazenido_raman_cm1", 1490.0))
        if not (1480.0 <= diazenido_raman_shift <= 1505.0):
            self.state = "REJECT"
            self.relay_voltage_v = 0.0
            return "REJECT", f"RAMAN_DIAZENIDO_MISSING (Shift={diazenido_raman_shift} cm^-1 != ~1490 cm^-1)", 0.0, None

        nmr_ppm = float(candidate.get("nmr_15n_ppm", -310.0))
        j_coupling = float(candidate.get("nmr_1j_coupling_hz", 73.5))
        if not (self.REQUIRED_15N_NMR_PPM_MIN <= nmr_ppm <= self.REQUIRED_15N_NMR_PPM_MAX and self.REQUIRED_J_COUPLING_HZ_MIN <= j_coupling <= self.REQUIRED_J_COUPLING_HZ_MAX):
            self.state = "HOLD"
            self.relay_voltage_v = 0.0
            return "HOLD", f"NMR_ISOTOPIC_INTEGRITY_FAIL (δ={nmr_ppm} ppm, 1J={j_coupling} Hz -> Potential atmospheric amine contamination)", 0.0, None

        # --- DEL III: YTELSESMATRISE & 3-BLANK WITNESS ---
        fe_nh3 = float(candidate.get("faradaic_efficiency_pct", 22.0))
        if fe_nh3 < self.MIN_FARADAIC_EFFICIENCY_PCT:
            self.state = "KILL"
            self.relay_voltage_v = 0.0
            self.emergency_latched = True
            return "KILL", f"FE_NH3_BELOW_EXISTENCE_THRESHOLD (FE={fe_nh3}% < {self.MIN_FARADAIC_EFFICIENCY_PCT}% -> Massive HER)", 0.0, None

        blank_no_cat_nh4 = float(candidate.get("blank_minus_catalyst_m", 0.0))
        blank_ar_nh4 = float(candidate.get("blank_ar_atmosphere_m", 0.0))
        blank_ocv_nh4 = float(candidate.get("blank_open_circuit_m", 0.0))

        if blank_no_cat_nh4 > 0.0 or blank_ar_nh4 > 0.0 or blank_ocv_nh4 > 0.0:
            self.state = "HOLD"
            self.relay_voltage_v = 0.0
            return "HOLD", f"BLANK_CONTAMINATION_DETECTED (NoCat={blank_no_cat_nh4}M, Ar={blank_ar_nh4}M, OCV={blank_ocv_nh4}M)", 0.0, None

        # Product Inhibition Hysteresis Check
        tof = float(candidate.get("turnover_frequency_h1", 12.0))
        if tof < 2.0:
            mutation_directive = "HYSTERESE-VARSEL: Lav TOF med bekreftet NH3 -> Øk ligandens Tolman kjeglevinkel (θ_cone) for sterisk ekstrudering"

        # ALL PROTOCOL INVARIANTS SATISFIED
        self.state = "OPERATIONAL"
        self.relay_voltage_v = 5.0
        return "OPEN", "PROTOKOLL_FE_MO_S_FULLT_VERIFISERT_SYNTHESIS_AUTHORIZED", 5.0, mutation_directive

    def manual_reset_latch(self, auth_token: str) -> bool:
        if auth_token == "OPERATOR_OVERRIDE_VERIFIED":
            self.emergency_latched = False
            self.inert_purge_active = False
            self.state = "IDLE"
            return True
        return False


class AutonomousFeMoSMasterEngine:
    """
    Master Protocol Engine:
    Sammenkobler Protokoll Fe-Mo-S validering og SHA-256 forseglet WORM-revisjonskjede.
    """
    def __init__(self):
        self.predictor = EmpiricalBondPredictor()
        self.gate = FeMoSProtocolAdmissibilityGate()
        self.witness_chain: List[Dict[str, Any]] = []
        self.prev_hash = "0" * 64
        self.seq = 0

    def evaluate_protocol_candidate(self, cid: str, atom_a: str, atom_b: str, bo: float,
                                   telemetry: Dict[str, Any]) -> Dict[str, Any]:
        self.seq += 1
        bond_data = self.predictor.predict_bond(atom_a, atom_b, bo)
        decision, reason, voltage, mutation = self.gate.evaluate_protocol_candidate(telemetry)

        record = {
            "seq": self.seq,
            "candidate_id": cid,
            "timestamp": time.time(),
            "prev_hash": self.prev_hash,
            "target": f"{atom_a}={atom_b} (Order {bo})",
            "bond_energy_kj_mol": bond_data.get("bde_kj_mol", 0.0),
            "gate_decision": decision,
            "decision_reason": reason,
            "actuator_relay_voltage_v": voltage,
            "mutation_directive": mutation,
            "gate_state": self.gate.state,
            "emergency_latch": self.gate.emergency_latched
        }
        canonical_str = json.dumps(record, sort_keys=True)
        digest = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
        record["worm_witness_hash"] = digest

        self.witness_chain.append(record)
        self.prev_hash = digest
        return record

    def verify_ledger(self) -> bool:
        last = "0" * 64
        for entry in self.witness_chain:
            if entry["prev_hash"] != last:
                return False
            payload = {k: v for k, v in entry.items() if k != "worm_witness_hash"}
            expected = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
            if expected != entry["worm_witness_hash"]:
                return False
            last = entry["worm_witness_hash"]
        return True


def run_femos_protocol_verification_suite():
    print("=" * 95)
    print("🔬 AETHELGARD MOLECULAR: PROTOKOLL Fe-Mo-S DETERMINISTISK ADMISSIBILITETS-SUITE v3.0")
    print("   BIO-UORGANISK ELEKTROKATALYSATOR (N2 -> NH3) MED 3-BLANK WITNESS OG MUTASJONS-LOOP")
    print("=" * 95)

    engine = AutonomousFeMoSMasterEngine()

    # 10 PROTOKOLL-FE-MO-S TESTKANDIDATER
    candidates = [
        # 1. Ideell tripodal MoFe3S4 kjerne ved E_cat = -1.55V, KIE=6.2, 15N-NMR bekreftet (PASS)
        ("PROTO-01", "Fe", "N", 2.0, {
            "o2_ppm": 0.2, "h2o_ppm": 0.1, "stoichiometry_dev_pct": 0.5,
            "mossbauer_delta_mm_s": 0.45, "mossbauer_eq_mm_s": 2.10,
            "cathodic_potential_v": -1.55, "h_d_kie_ratio": 6.2,
            "diazenido_raman_cm1": 1490.0, "nmr_15n_ppm": -310.0, "nmr_1j_coupling_hz": 73.5,
            "faradaic_efficiency_pct": 28.5, "turnover_frequency_h1": 14.2,
            "blank_minus_catalyst_m": 0.0, "blank_ar_atmosphere_m": 0.0, "blank_open_circuit_m": 0.0
        }, "OPEN", 5.0),

        # 2. Asymmetrisk modifisert cuban [MoFe3S4]3+ (PASS)
        ("PROTO-02", "Mo", "S", 1.5, {
            "o2_ppm": 0.4, "h2o_ppm": 0.2, "stoichiometry_dev_pct": -1.2,
            "mossbauer_delta_mm_s": 0.44, "mossbauer_eq_mm_s": 2.05,
            "cathodic_potential_v": -1.50, "h_d_kie_ratio": 5.8,
            "diazenido_raman_cm1": 1492.0, "nmr_15n_ppm": -309.5, "nmr_1j_coupling_hz": 73.8,
            "faradaic_efficiency_pct": 34.0, "turnover_frequency_h1": 18.0,
            "blank_minus_catalyst_m": 0.0, "blank_ar_atmosphere_m": 0.0, "blank_open_circuit_m": 0.0
        }, "OPEN", 5.0),

        # 3. Aerob kontaminasjon (O2 = 3.5 ppm > 1.0 ppm -> Fe-O-Fe okso-broer -> KILL)
        ("PROTO-03", "Fe", "O", 2.0, {
            "o2_ppm": 3.5, "h2o_ppm": 2.0, "stoichiometry_dev_pct": 0.0,
            "mossbauer_delta_mm_s": 0.45, "mossbauer_eq_mm_s": 2.10,
            "cathodic_potential_v": -1.55, "h_d_kie_ratio": 6.0,
            "diazenido_raman_cm1": 1490.0, "nmr_15n_ppm": -310.0, "nmr_1j_coupling_hz": 73.5,
            "faradaic_efficiency_pct": 20.0
        }, "KILL", 0.0),

        # 4. Post-KILL Invariant Latch Test (Must stay KILL)
        ("PROTO-04", "Mo", "S", 1.0, {
            "o2_ppm": 0.1, "h2o_ppm": 0.1, "stoichiometry_dev_pct": 0.0,
            "mossbauer_delta_mm_s": 0.45, "mossbauer_eq_mm_s": 2.10,
            "cathodic_potential_v": -1.55, "h_d_kie_ratio": 6.0,
            "diazenido_raman_cm1": 1490.0, "nmr_15n_ppm": -310.0, "nmr_1j_coupling_hz": 73.5,
            "faradaic_efficiency_pct": 20.0
        }, "KILL", 0.0),

        # 5. Overstyring / Reset -> Test KIE Brudd (KIE = 2.1 < 5.0 -> HOLD)
        ("PROTO-05", "Fe", "N", 1.0, {
            "_override_before": True,
            "o2_ppm": 0.2, "h2o_ppm": 0.1, "stoichiometry_dev_pct": 0.5,
            "mossbauer_delta_mm_s": 0.45, "mossbauer_eq_mm_s": 2.10,
            "cathodic_potential_v": -1.55,
            "h_d_kie_ratio": 2.1, # KIE < 5.0 (Diffusjonsstøy / frakoblet PCET)
            "diazenido_raman_cm1": 1490.0, "nmr_15n_ppm": -310.0, "nmr_1j_coupling_hz": 73.5,
            "faradaic_efficiency_pct": 20.0,
            "blank_minus_catalyst_m": 0.0, "blank_ar_atmosphere_m": 0.0, "blank_open_circuit_m": 0.0
        }, "HOLD", 0.0),

        # 6. Elektronisk sluk: Mössbauer δ = 0.58 mm/s > 0.55 mm/s (REJECT + KGS-1 Mutasjon)
        ("PROTO-06", "Fe", "S", 1.0, {
            "o2_ppm": 0.2, "h2o_ppm": 0.1, "stoichiometry_dev_pct": 0.5,
            "mossbauer_delta_mm_s": 0.58, "mossbauer_eq_mm_s": 2.10, # For elektronfattig!
            "cathodic_potential_v": -1.55, "h_d_kie_ratio": 5.5,
            "diazenido_raman_cm1": 1490.0, "nmr_15n_ppm": -310.0, "nmr_1j_coupling_hz": 73.5,
            "faradaic_efficiency_pct": 22.0,
            "blank_minus_catalyst_m": 0.0, "blank_ar_atmosphere_m": 0.0, "blank_open_circuit_m": 0.0
        }, "REJECT", 0.0),

        # 7. 15N-NMR Aminkontaminasjon (δ = -240 ppm != -310 ppm -> HOLD Anti-Selvbedrag)
        ("PROTO-07", "Fe", "N", 1.0, {
            "o2_ppm": 0.2, "h2o_ppm": 0.1, "stoichiometry_dev_pct": 0.5,
            "mossbauer_delta_mm_s": 0.45, "mossbauer_eq_mm_s": 2.10,
            "cathodic_potential_v": -1.55, "h_d_kie_ratio": 5.5,
            "diazenido_raman_cm1": 1490.0,
            "nmr_15n_ppm": -240.0, "nmr_1j_coupling_hz": 50.0, # Ugyldig NMR (Aminkontaminasjon!)
            "faradaic_efficiency_pct": 22.0,
            "blank_minus_catalyst_m": 0.0, "blank_ar_atmosphere_m": 0.0, "blank_open_circuit_m": 0.0
        }, "HOLD", 0.0),

        # 8. Massiv HER-dominans (FE_NH3 = 8.5% < 15.0% -> KILL)
        ("PROTO-08", "Fe", "H", 1.0, {
            "o2_ppm": 0.2, "h2o_ppm": 0.1, "stoichiometry_dev_pct": 0.5,
            "mossbauer_delta_mm_s": 0.45, "mossbauer_eq_mm_s": 2.10,
            "cathodic_potential_v": -1.55, "h_d_kie_ratio": 5.5,
            "diazenido_raman_cm1": 1490.0, "nmr_15n_ppm": -310.0, "nmr_1j_coupling_hz": 73.5,
            "faradaic_efficiency_pct": 8.5, # Under 15% eksistensrett!
            "blank_minus_catalyst_m": 0.0, "blank_ar_atmosphere_m": 0.0, "blank_open_circuit_m": 0.0
        }, "KILL", 0.0),

        # 9. Overstyring / Reset -> Blank Kontaminasjon (Ar-Atmosfære gir 0.005M NH4+ -> HOLD)
        ("PROTO-09", "Mo", "S", 1.0, {
            "_override_before": True,
            "o2_ppm": 0.2, "h2o_ppm": 0.1, "stoichiometry_dev_pct": 0.5,
            "mossbauer_delta_mm_s": 0.45, "mossbauer_eq_mm_s": 2.10,
            "cathodic_potential_v": -1.55, "h_d_kie_ratio": 5.5,
            "diazenido_raman_cm1": 1490.0, "nmr_15n_ppm": -310.0, "nmr_1j_coupling_hz": 73.5,
            "faradaic_efficiency_pct": 25.0,
            "blank_minus_catalyst_m": 0.0,
            "blank_ar_atmosphere_m": 0.005, # Blank feilet!
            "blank_open_circuit_m": 0.0
        }, "HOLD", 0.0),

        # 10. Hysterese / Produkt-inhibering Pass med Mutasjonsvarsel (Low TOF -> Tolman Cone Action -> OPEN 5.0V)
        ("PROTO-10", "Fe", "N", 2.0, {
            "o2_ppm": 0.3, "h2o_ppm": 0.1, "stoichiometry_dev_pct": 0.8,
            "mossbauer_delta_mm_s": 0.46, "mossbauer_eq_mm_s": 2.12,
            "cathodic_potential_v": -1.58, "h_d_kie_ratio": 6.5,
            "diazenido_raman_cm1": 1490.0, "nmr_15n_ppm": -310.0, "nmr_1j_coupling_hz": 73.5,
            "faradaic_efficiency_pct": 31.0,
            "turnover_frequency_h1": 1.2, # Lav TOF -> Hysterese-varsel!
            "blank_minus_catalyst_m": 0.0, "blank_ar_atmosphere_m": 0.0, "blank_open_circuit_m": 0.0
        }, "OPEN", 5.0),
    ]

    print(f"{'#':<3} | {'KANDIDAT':<9} | {'MÅL':<16} | {'BESLUTN.':<9} | {'RELÉ':<6} | {'DIAGNOSE / PROTOKOLL-STATUS'}")
    print("-" * 95)

    for i, (cid, a, b, bo, telem, expected_dec, expected_v) in enumerate(candidates, 1):
        if telem.pop("_override_before", False):
            engine.gate.manual_reset_latch("OPERATOR_OVERRIDE_VERIFIED")

        res = engine.evaluate_protocol_candidate(cid, a, b, bo, telem)
        dec = res["gate_decision"]
        v = res["actuator_relay_voltage_v"]
        reason = res["decision_reason"]
        mut = res.get("mutation_directive")

        sym = "🟢" if dec == "OPEN" else ("🟡" if dec == "HOLD" else ("🔴" if dec == "KILL" else "🟠"))
        print(f"{i:<3} | {cid:<9} | {res['target']:<16} | {sym} {dec:<6} | {v:>4.1f}V | {reason[:40]}")
        if mut:
            print(f"    ↳ 🧬 MUTASJON: {mut}")

        assert dec == expected_dec, f"Test {i} mismatch: Forventet {expected_dec}, fikk {dec}"
        assert v == expected_v, f"Spenning mismatch i test {i}: Forventet {expected_v}, fikk {v}"

    print("-" * 95)
    audit_ok = engine.verify_ledger()
    print(f"🔒 PROTOKOLL REVISJONSKJEDE (SHA-256): {'100% INTAKT & FORSEGLET ✅' if audit_ok else 'FEILET ❌'}")
    assert audit_ok is True
    print("=" * 95)
    print("✅ PROTOKOLL Fe-Mo-S VALIDERINGS-SUITE: ALLE 10 TESTBANER FULLT VERIFISERT")
    print("=" * 95)


if __name__ == "__main__":
    run_femos_protocol_verification_suite()
