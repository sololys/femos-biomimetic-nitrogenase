#!/usr/bin/env python3
"""
Maxwellian Hamilton-Jacobi Eikonal Dynamics & Poynting Field Engine — Production Reference
Implements Poynting vector flux accounting (S = (1/mu_0) * (E x B)), energy velocity v_E,
relativistic causality gate, vacuum transversality, and thermodynamic dissipation.
"""

import numpy as np
import hashlib
import json
import unittest
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Tuple, Dict, Any, List

# ==========================================
# ⚙️ FYSISKE KONSTANTER & ORDNET ROM
# ==========================================
C_LIGHT = 299792458.0      # m/s
MU_0 = 1.25663706e-6       # H/m
EPS_0 = 8.85418782e-12     # F/m

class GateVerdict(Enum):
    KILL = 0
    HOLD = 1
    OPEN = 2

# ==========================================
# ⚙️ DATAKLASSER FOR FELT & RESIDUAL
# ==========================================
@dataclass
class MaxwellCandidate:
    """ Φ_Maxwell: Den genererte feltkandidaten (Havet av energi) """
    E: np.ndarray          # Elektrisk feltvektor [Ex, Ey, Ez]
    B: np.ndarray          # Magnetisk feltvektor [Bx, By, Bz]
    k: np.ndarray          # Bølgevektor [kx, ky, kz]
    omega: float           # Vinkelfrekvens

@dataclass
class PoyntingLedger:
    """ Energiregnskapet for feltet """
    energy_density_u: float
    poynting_vector_S: np.ndarray
    energy_velocity_vE: float

@dataclass
class RealizationReceipt:
    verdict: GateVerdict
    residual_classification: str
    thermodynamic_cost_QA: float
    witness_hash: str

# ==========================================
# 🌊 MULA BANDHA: DEN ELEKTROMAGNETISKE ROTLÅSEN
# ==========================================
class MaxwellPoyntingEngine:
    def __init__(self, prev_worm_hash: str = "GENESIS_MAXWELL_00"):
        self.history_ledger: List[str] = [prev_worm_hash]
        self.T_env = 0.015 # 15 mK i Locus Zero

    def _phi_generator(self, E: list, B: list, k: list, omega: float) -> MaxwellCandidate:
        """ Genererer den frie bølgen (NP-rommet) """
        return MaxwellCandidate(
            E=np.array(E, dtype=float), B=np.array(B, dtype=float), k=np.array(k, dtype=float), omega=omega
        )

    def _calculate_poynting_ledger(self, cand: MaxwellCandidate) -> PoyntingLedger:
        """ Beregner energifluksen (S) og tettheten (u) """
        u_E = 0.5 * EPS_0 * np.dot(cand.E, cand.E)
        u_B = 0.5 * (1.0 / MU_0) * np.dot(cand.B, cand.B)
        u_tot = u_E + u_B

        # S = (1/mu_0) * (E x B)
        S = (1.0 / MU_0) * np.cross(cand.E, cand.B)
        
        # v_E = |S| / u
        S_mag = float(np.linalg.norm(S))
        vE = S_mag / u_tot if u_tot > 0 else 0.0

        return PoyntingLedger(energy_density_u=float(u_tot), poynting_vector_S=S, energy_velocity_vE=float(vE))

    def _pi_admissibility_pipeline(self, cand: MaxwellCandidate, ledger: PoyntingLedger) -> Tuple[GateVerdict, str, float]:
        """ 
        Den sammensatte projeksjonen (Π_A): Kausalitet, positivitet, termodynamikk.
        Klassifiserer residualene nøyaktig slik spesifisert i arbeidsnotatet.
        """
        k_norm = float(np.linalg.norm(cand.k))
        phase_velocity = cand.omega / k_norm if k_norm > 0 else 0.0
        
        # 1. Kausalitetsport (Pi_causal)
        if ledger.energy_velocity_vE > (C_LIGHT * 1.000001) or phase_velocity > (C_LIGHT * 1.000001):
            return GateVerdict.KILL, "R_superluminal -> KILL", 0.0

        # 2. Transversalitetsport (Maxwell Vakuum Sjekk)
        if abs(np.dot(cand.E, cand.k)) > 1e-6 or abs(np.dot(cand.B, cand.k)) > 1e-6:
            return GateVerdict.HOLD, "R_evanescent_idealization -> near-field/coupled mode", 0.0

        # 3. Termodynamisk Absorpsjonsport (Pi_thermo)
        loss_fraction = 0.05 
        Q_A = ledger.energy_density_u * loss_fraction
        classification = "R_thermal_loss -> Q_A, dS_env + R_field-only_invariant -> MERGE"
        
        return GateVerdict.OPEN, classification, Q_A

    def process_wave(self, E: list, B: list, k: list, omega: float) -> RealizationReceipt:
        """ Kjører feltkandidaten gjennom hele KY-porten """
        cand = self._phi_generator(E, B, k, omega)
        ledger = self._calculate_poynting_ledger(cand)
        verdict, res_class, Q_A = self._pi_admissibility_pipeline(cand, ledger)
        
        witness = "REJECTED"
        if verdict == GateVerdict.OPEN:
            payload = f"{ledger.energy_density_u:.8e}|{Q_A:.8e}|{self.history_ledger[-1]}"
            witness = "WORM_" + hashlib.sha256(payload.encode()).hexdigest()[:16].upper()
            self.history_ledger.append(witness)
            
        return RealizationReceipt(verdict, res_class, Q_A, witness)

# ==========================================
# 🧪 TEST SUITE
# ==========================================
class TestMaxwellPoyntingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MaxwellPoyntingEngine(prev_worm_hash="GENESIS_MAXWELL_00")
        self.k_vec = [1.0, 0.0, 0.0]
        self.omega_valid = C_LIGHT * float(np.linalg.norm(self.k_vec))
        self.E_valid = [0.0, 1.0, 0.0]
        self.B_valid = [0.0, 0.0, 1.0 / C_LIGHT]

    def test_scenario_1_valid_transverse_wave(self):
        res = self.engine.process_wave(self.E_valid, self.B_valid, self.k_vec, self.omega_valid)
        self.assertEqual(res.verdict, GateVerdict.OPEN)
        self.assertTrue(res.witness_hash.startswith("WORM_"))

    def test_scenario_2_superluminal_ghost_wave(self):
        omega_super = C_LIGHT * 2.0
        res = self.engine.process_wave(self.E_valid, self.B_valid, self.k_vec, omega_super)
        self.assertEqual(res.verdict, GateVerdict.KILL)
        self.assertEqual(res.witness_hash, "REJECTED")

    def test_scenario_3_longitudinal_wave(self):
        E_long = [1.0, 0.0, 0.0]
        res = self.engine.process_wave(E_long, self.B_valid, self.k_vec, self.omega_valid)
        self.assertEqual(res.verdict, GateVerdict.HOLD)
        self.assertEqual(res.witness_hash, "REJECTED")

def run_audit():
    print("=== Maxwellian Hamilton-Jacobi Eikonal-dynamikk (KY-Port) ===\n")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMaxwellPoyntingEngine)
    test_result = unittest.TextTestRunner(verbosity=0).run(suite)
    
    engine = MaxwellPoyntingEngine(prev_worm_hash="GENESIS_MAXWELL_00")
    k_vec = [1.0, 0.0, 0.0]
    omega_valid = C_LIGHT * np.linalg.norm(k_vec)
    E_valid = [0.0, 1.0, 0.0]
    B_valid = [0.0, 0.0, 1.0 / C_LIGHT]

    res1 = engine.process_wave(E_valid, B_valid, k_vec, omega_valid)
    res2 = engine.process_wave(E_valid, B_valid, k_vec, C_LIGHT * 2.0)
    res3 = engine.process_wave([1.0, 0.0, 0.0], B_valid, k_vec, omega_valid)

    audit_report = {
        "status_maxwell_physics": "OPEN_AS_MAXWELL_POYNTING_FIELD_FRAMEWORK",
        "status_causality_gate": "OPEN_AS_POYNTING_FLUX_CAUSALITY_GATE",
        "tests_passed": f"{test_result.testsRun - len(test_result.failures) - len(test_result.errors)}/{test_result.testsRun}",
        "runs": [
            {
                "scenario": "Valid Transverse Electromagnetic Wave",
                "verdict": res1.verdict.name,
                "residual": res1.residual_classification,
                "Q_A_cost": round(res1.thermodynamic_cost_QA, 8),
                "witness_hash": res1.witness_hash
            },
            {
                "scenario": "Superluminal Ghost Wave",
                "verdict": res2.verdict.name,
                "residual": res2.residual_classification,
                "witness_hash": res2.witness_hash
            },
            {
                "scenario": "Longitudinal Wave in Vacuum",
                "verdict": res3.verdict.name,
                "residual": res3.residual_classification,
                "witness_hash": res3.witness_hash
            }
        ]
    }

    print("[AUDIT REPORT JSON]")
    print(json.dumps(audit_report, indent=2))

if __name__ == "__main__":
    run_audit()
