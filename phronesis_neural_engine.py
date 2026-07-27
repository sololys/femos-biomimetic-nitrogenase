#!/usr/bin/env python3
"""
Phronesis Neural Projection Engine — Production Reference
Implements mEC continuous attractor grid cells, boundary cell non-expansive metric projection,
ROX involution symmetry check, and hippocampal WORM ledger.
"""

import numpy as np
import hashlib
import json
import unittest
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Tuple, List, Optional

class GateVerdict(Enum):
    KILL = 0
    HOLD = 1
    OPEN = 2

@dataclass
class SpatialState:
    """ Representerer det romlige koordinat-estimatet i hjernen """
    x: float
    y: float
    cognitive_stress: float = 0.0 # Induserer drift / desorientering

@dataclass
class NeuralGateResult:
    """ Resultatet etter en tur gjennom hjernens projeksjons- og port-arkitektur """
    y_raw: SpatialState         # Uforankret kandidat fra grid-celler
    x_projected: SpatialState   # Forankret tilstand fra grenseceller
    d_A: float                  # Metrisk avvik (residuum)
    rox_valid: bool             # Resultat av symmetrisjekk
    verdict: GateVerdict        # Systemets dom
    hippocampal_hash: str       # WORM-logg (om OPEN)

class PhronesisNeuralEngine:
    def __init__(self, env_bounds: Tuple[float, float, float, float]):
        # env_bounds: (x_min, x_max, y_min, y_max)
        self.bounds = env_bounds
        self.eps_rox = 1e-6 # Toleranse for involutiv symmetri
        self.hippocampus_worm: List[str] = ["GENESIS_CA3_000"]
        self.reference_safe_state = SpatialState(0.0, 0.0)

    def phi_continuous_attractor(self, state: SpatialState, velocity: Tuple[float, float]) -> SpatialState:
        """ 
        [Generativ Sektor - Fail-Open]
        Grid-cellene propagerer tilstanden basert på hastighet.
        Høyt kognitivt stress introduserer drift (epistemisk støy).
        """
        drift_x = float(np.random.normal(0, state.cognitive_stress * 0.1))
        drift_y = float(np.random.normal(0, state.cognitive_stress * 0.1))
        
        return SpatialState(
            x = state.x + velocity[0] + drift_x,
            y = state.y + velocity[1] + drift_y,
            cognitive_stress = state.cognitive_stress
        )

    def pi_a_metric_projection(self, y_cand: SpatialState) -> Tuple[SpatialState, float]:
        """
        [Realiseringssektor - Grenseceller]
        Tvinger den uforankrede banen ned på den konvekse, tillatte geometrien.
        Beregner restavstand d_A.
        """
        xmin, xmax, ymin, ymax = self.bounds
        
        # Ikke-ekspansiv projeksjon
        proj_x = float(np.clip(y_cand.x, xmin, xmax))
        proj_y = float(np.clip(y_cand.y, ymin, ymax))
        
        # Residuum / metrisk avvik
        d_A = float(np.sqrt((y_cand.x - proj_x)**2 + (y_cand.y - proj_y)**2))
        
        return SpatialState(proj_x, proj_y, y_cand.cognitive_stress), d_A

    def rox_involution_check(self, state: SpatialState) -> bool:
        """
        [Symmetrisjekk - R^2 ≈ I]
        Verifiserer det heksagonale koordinatnettets interne koherens.
        Hvis stresset er for høyt, kollapser den matematiske identiteten.
        """
        R_a = np.array([[1.0, 0.0], [0.0, -1.0]]) 
        
        if state.cognitive_stress > 0.8:
            error_matrix = np.array([[0.0, 0.1], [0.1, 0.0]])
            R_a_applied = R_a + error_matrix
        else:
            R_a_applied = R_a
            
        R_a_squared = np.dot(R_a_applied, R_a_applied)
        identity = np.eye(2)
        
        deviation = float(np.max(np.abs(R_a_squared - identity)))
        return deviation <= self.eps_rox

    def omega_gate(self, d_A: float, rox_valid: bool) -> GateVerdict:
        """
        [Domstolen]
        Beslutter om den kognitive persepsjonen kan realiseres som romlig bevissthet.
        """
        if not rox_valid:
            return GateVerdict.KILL
            
        if d_A > 0.05:
            return GateVerdict.HOLD
            
        return GateVerdict.OPEN

    def process_step(self, current_state: SpatialState, velocity: Tuple[float, float]) -> NeuralGateResult:
        y_cand = self.phi_continuous_attractor(current_state, velocity)
        x_proj, d_A = self.pi_a_metric_projection(y_cand)
        rox_valid = self.rox_involution_check(y_cand)
        verdict = self.omega_gate(d_A, rox_valid)
        
        w_hash = "REJECTED"
        if verdict == GateVerdict.OPEN:
            payload = f"{x_proj.x:.3f}|{x_proj.y:.3f}|{self.hippocampus_worm[-1]}"
            w_hash = hashlib.sha256(payload.encode()).hexdigest()[:16]
            self.hippocampus_worm.append(w_hash)
            
        return NeuralGateResult(y_cand, x_proj, d_A, rox_valid, verdict, w_hash)

class TestNeuralProjectionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PhronesisNeuralEngine(env_bounds=(0.0, 10.0, 0.0, 10.0))

    def test_open_smooth_path(self):
        state = SpatialState(5.0, 5.0)
        res = self.engine.process_step(state, velocity=(0.5, 0.5))
        
        self.assertEqual(res.verdict, GateVerdict.OPEN)
        self.assertAlmostEqual(res.d_A, 0.0)
        self.assertNotEqual(res.hippocampal_hash, "REJECTED")

    def test_hold_border_cell_clamp(self):
        state = SpatialState(9.8, 5.0)
        res = self.engine.process_step(state, velocity=(0.5, 0.0))
        
        self.assertEqual(res.verdict, GateVerdict.HOLD)
        self.assertTrue(res.d_A > 0.0)
        self.assertAlmostEqual(res.x_projected.x, 10.0)
        self.assertEqual(res.hippocampal_hash, "REJECTED")

    def test_kill_rox_symmetry_break(self):
        state = SpatialState(5.0, 5.0, cognitive_stress=1.0)
        res = self.engine.process_step(state, velocity=(0.1, 0.1))
        
        self.assertFalse(res.rox_valid)
        self.assertEqual(res.verdict, GateVerdict.KILL)

def run_audit():
    print("=== Phronesis Neural Projection Engine (Locus Zero Level 0) ===\n")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNeuralProjectionEngine)
    test_result = unittest.TextTestRunner(verbosity=0).run(suite)
    
    engine = PhronesisNeuralEngine(env_bounds=(0.0, 10.0, 0.0, 10.0))
    state_ok = SpatialState(2.0, 2.0, cognitive_stress=0.0)
    state_wall = SpatialState(9.8, 2.0, cognitive_stress=0.0)
    state_lost = SpatialState(5.0, 5.0, cognitive_stress=0.9)
    
    res_ok = engine.process_step(state_ok, velocity=(1.0, 0.0))
    res_wall = engine.process_step(state_wall, velocity=(1.0, 0.0))
    res_lost = engine.process_step(state_lost, velocity=(1.0, 0.0))
    
    audit_report = {
        "status": "OPEN_AS_NEURAL_PROJECTION_DEMONSTRATOR",
        "tests_passed": f"{test_result.testsRun - len(test_result.failures) - len(test_result.errors)}/{test_result.testsRun}",
        "execution_log": [
            {
                "scenario": "Clear Path (Nash Equilibrium)",
                "d_A": round(res_ok.d_A, 4),
                "rox_valid": res_ok.rox_valid,
                "gate_verdict": res_ok.verdict.name,
                "hippocampus_log": res_ok.hippocampal_hash
            },
            {
                "scenario": "Hit Boundary (Border Cell Projection)",
                "d_A": round(res_wall.d_A, 4),
                "rox_valid": res_wall.rox_valid,
                "gate_verdict": res_wall.verdict.name,
                "hippocampus_log": res_wall.hippocampal_hash
            },
            {
                "scenario": "Cognitive Stress (ROX Integrity Break)",
                "d_A": round(res_lost.d_A, 4),
                "rox_valid": res_lost.rox_valid,
                "gate_verdict": res_lost.verdict.name,
                "hippocampus_log": res_lost.hippocampal_hash
            }
        ]
    }
    
    print("[AUDIT REPORT JSON]")
    print(json.dumps(audit_report, indent=2))

if __name__ == "__main__":
    run_audit()
