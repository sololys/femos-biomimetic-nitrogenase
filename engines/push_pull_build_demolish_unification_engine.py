#!/usr/bin/env python3
"""
Push-Pull & Build-Demolish Unification Engine
Simulates:
1. The 4 dynamic forces: Push, Pull, Build, Demolish
2. Unification tensor U = [[Push, Pull], [Build, Demolish]] with det(U) = 1.0000
3. Inverse Reversal Tensor U^(-1)
4. Involutive Matrix Operator J_involute = [[0, 1], [1, 0]] with J^2 = Identity
5. Circle Involute Parametric Trajectory gamma(t) = R0*(cos(t)+t*sin(t), sin(t)-t*cos(t))
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import Dict, Any, Tuple

@dataclass
class UnificationState:
    f_push: float = 2.0      # Push force
    f_pull: float = 1.0      # Pull force
    b_build: float = 1.0     # Build force
    d_demolish: float = 1.0  # Demolish force (det = 2*1 - 1*1 = 1)
    reversal_applied: bool = False # Reversal operator active
    involute_applied: bool = False # Involutive operator active

class PushPullUnificationEngine:
    @staticmethod
    def calc_tensor_determinant(push: float, pull: float, build: float, demolish: float) -> float:
        return (push * demolish) - (pull * build)

    @staticmethod
    def calc_circle_involute(t: float, r0: float = 1.0) -> Tuple[float, float]:
        x = r0 * (math.cos(t) + t * math.sin(t))
        y = r0 * (math.sin(t) - t * math.cos(t))
        return x, y

    @staticmethod
    def evaluate_unification(state: UnificationState = UnificationState()) -> Dict[str, Any]:
        if state.involute_applied:
            # Involutive matrix J = [[0, 1], [1, 0]] swaps diagonal/antidiagonal: J^2 = Identity
            r_push = state.b_build
            r_pull = state.d_demolish
            r_build = state.f_push
            r_demolish = state.f_pull
            det_u = PushPullUnificationEngine.calc_tensor_determinant(r_push, r_pull, r_build, r_demolish)
            status = "INVOLUTIVE MATRIX OPERATOR ACTIVE (J^2 = IDENTITY)"
        elif state.reversal_applied:
            # Reversal matrix U^(-1)
            r_push = state.d_demolish
            r_pull = -state.f_pull
            r_build = -state.b_build
            r_demolish = state.f_push
            det_u = (r_push * r_demolish) - (r_pull * r_build)
            status = "REVERSAL OPERATOR ACTIVE (U^-1 INVERSE MATRIX)"
        else:
            r_push, r_pull, r_build, r_demolish = state.f_push, state.f_pull, state.b_build, state.d_demolish
            det_u = PushPullUnificationEngine.calc_tensor_determinant(r_push, r_pull, r_build, r_demolish)
            status = "FORWARD UNIFICATION ACTIVE"
        
        balanced = abs(det_u - 1.0000) < 1.0e-3
        verdict = "PUSH-PULL BUILD-DEMOLISH UNIFIED" if balanced else "UNBALANCED FORCE KILL"

        payload = f"{r_push:.2f}|{r_pull:.2f}|{r_build:.2f}|{r_demolish:.2f}|{det_u:.4f}|{verdict}"
        w_hash = "W_UNIFICATION_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return {
            "f_push": r_push,
            "f_pull": r_pull,
            "b_build": r_build,
            "d_demolish": r_demolish,
            "tensor_determinant": round(det_u, 4),
            "reversal_applied": state.reversal_applied,
            "involute_applied": state.involute_applied,
            "status": status,
            "balanced": balanced,
            "verdict": verdict,
            "witness_hash": w_hash
        }

class TestPushPullUnificationEngine(unittest.TestCase):
    def test_harmonic_unification_balance(self):
        state = UnificationState(f_push=2.0, f_pull=1.0, b_build=1.0, d_demolish=1.0)
        res = PushPullUnificationEngine.evaluate_unification(state)
        self.assertTrue(res["balanced"])
        self.assertEqual(res["tensor_determinant"], 1.0000)
        self.assertEqual(res["verdict"], "PUSH-PULL BUILD-DEMOLISH UNIFIED")
        self.assertTrue(res["witness_hash"].startswith("W_UNIFICATION_"))

    def test_involutive_matrix_operator(self):
        state = UnificationState(f_push=2.0, f_pull=1.0, b_build=1.0, d_demolish=1.0, involute_applied=True)
        res = PushPullUnificationEngine.evaluate_unification(state)
        self.assertTrue(res["involute_applied"])
        self.assertEqual(res["status"], "INVOLUTIVE MATRIX OPERATOR ACTIVE (J^2 = IDENTITY)")

    def test_circle_involute_curve(self):
        x, y = PushPullUnificationEngine.calc_circle_involute(t=0.0, r0=1.0)
        self.assertAlmostEqual(x, 1.0, places=4)
        self.assertAlmostEqual(y, 0.0, places=4)

    def test_reversal_operator_inversion(self):
        state = UnificationState(f_push=2.0, f_pull=1.0, b_build=1.0, d_demolish=1.0, reversal_applied=True)
        res = PushPullUnificationEngine.evaluate_unification(state)
        self.assertTrue(res["reversal_applied"])
        self.assertEqual(res["tensor_determinant"], 1.0000)

if __name__ == "__main__":
    unittest.main()
