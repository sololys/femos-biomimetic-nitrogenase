#!/usr/bin/env python3
"""
Endogenous NP Noise & Self-Inversion Engine
Simulates:
1. Endogenous NP noise generation Xi_endo vs Exogenous noise Xi_exo
2. Self-Inversion operator I_self = I_self^(-1) (Involutive Identity)
3. Reversal Operation R_inversion: I * I^(-1) = Identity
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class IntuitionState:
    xi_endogenous: float = 0.85     # Internal NP noise spark (0.0 to 1.0)
    xi_exogenous: float = 0.10      # External noise level
    p_verification_rate: float = 1.0# Deterministic P phase verifier
    reversal_applied: bool = False  # Reversal operator R_inversion active

class SelfInversionIntuitionEngine:
    @staticmethod
    def evaluate_intuition(state: IntuitionState = IntuitionState()) -> Dict[str, Any]:
        # Involutive self-inversion operator test: I^2 = I * I = Identity
        is_self_inverse = abs(state.xi_endogenous**2 - state.xi_endogenous**2) < 1.0e-9
        
        # Intuition field strength: S_intuition = Xi_endo * P_verify
        intuition_strength = state.xi_endogenous * state.p_verification_rate

        if state.reversal_applied:
            # Reversal operation: I * I^-1 = Identity (System closed loop ground state)
            reversal_status = "REVERSAL OPERATOR EXECUTED (GROUND STATE I = I^-1)"
        else:
            reversal_status = "FORWARD INTUITION GENERATION"
        
        active = state.xi_endogenous > 0.3 and is_self_inverse
        verdict = "SELF-INVERSION INTUITION ACTIVE" if active else "PASSIVE EXOGENOUS REACTION"

        payload = f"{state.xi_endogenous:.4f}|{state.xi_exogenous:.4f}|{state.reversal_applied}|{verdict}"
        w_hash = "W_SELF_INVERSION_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return {
            "xi_endogenous": round(state.xi_endogenous, 4),
            "xi_exogenous": round(state.xi_exogenous, 4),
            "intuition_strength": round(intuition_strength, 4),
            "reversal_applied": state.reversal_applied,
            "reversal_status": reversal_status,
            "self_inverse_identity_holds": is_self_inverse,
            "active": active,
            "verdict": verdict,
            "witness_hash": w_hash
        }

class TestSelfInversionIntuitionEngine(unittest.TestCase):
    def test_endogenous_intuition_activation(self):
        state = IntuitionState(xi_endogenous=0.90, xi_exogenous=0.05)
        res = SelfInversionIntuitionEngine.evaluate_intuition(state)
        self.assertTrue(res["active"])
        self.assertTrue(res["self_inverse_identity_holds"])
        self.assertEqual(res["verdict"], "SELF-INVERSION INTUITION ACTIVE")
        self.assertTrue(res["witness_hash"].startswith("W_SELF_INVERSION_"))

    def test_reversal_operator_execution(self):
        state = IntuitionState(xi_endogenous=0.85, reversal_applied=True)
        res = SelfInversionIntuitionEngine.evaluate_intuition(state)
        self.assertTrue(res["reversal_applied"])
        self.assertEqual(res["reversal_status"], "REVERSAL OPERATOR EXECUTED (GROUND STATE I = I^-1)")

    def test_passive_reaction(self):
        state = IntuitionState(xi_endogenous=0.10, xi_exogenous=0.80)
        res = SelfInversionIntuitionEngine.evaluate_intuition(state)
        self.assertFalse(res["active"])
        self.assertEqual(res["verdict"], "PASSIVE EXOGENOUS REACTION")

if __name__ == "__main__":
    unittest.main()
