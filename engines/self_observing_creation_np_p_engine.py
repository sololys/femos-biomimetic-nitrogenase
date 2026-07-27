#!/usr/bin/env python3
"""
Self-Observing Creation Engine
Simulates:
1. Paper self-observation operator O_paper(P_doc)
2. Strict Asymmetry: NP = FAIL-CLOSED vs P = FAIL-OPEN
3. Enforcement against forbidden inverse dynamics
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AsymmetryState:
    np_verified: bool = False       # Unverified NP candidate -> triggers FAIL-CLOSED
    p_trajectory_active: bool = True# P phase space -> FAIL-OPEN
    reverse_mode_requested: bool = False # Reverse mode strictly FORBIDDEN

class SelfObservingCreationEngine:
    @staticmethod
    def evaluate_asymmetry(state: AsymmetryState = AsymmetryState()) -> Dict[str, Any]:
        # Rule 1: Forbidden reverse mode kill
        if state.reverse_mode_requested:
            verdict = "FORBIDDEN REVERSAL KILL"
            valid = False
            np_state = "INVALID_REVERSE"
            p_state = "INVALID_REVERSE"
        else:
            # Rule 2: NP is FAIL-CLOSED (if not verified -> collapse to 0)
            np_state = "OPEN_VALID" if state.np_verified else "FAIL-CLOSED (COLLAPSED TO ZERO)"
            
            # Rule 3: P is FAIL-OPEN (always evolving)
            p_state = "FAIL-OPEN (CONTINUOUS EVOLUTION)" if state.p_trajectory_active else "FAIL-OPEN (STANDBY)"
            
            valid = True
            verdict = "SELF-OBSERVING CREATION VALIDATED"

        payload = f"{state.np_verified}|{state.p_trajectory_active}|{state.reverse_mode_requested}|{verdict}"
        w_hash = "W_SELF_OBSERVING_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return {
            "np_phase_space_state": np_state,
            "p_phase_space_state": p_state,
            "reverse_mode": state.reverse_mode_requested,
            "valid": valid,
            "verdict": verdict,
            "witness_hash": w_hash
        }

class TestSelfObservingCreationEngine(unittest.TestCase):
    def test_np_fail_closed_and_p_fail_open(self):
        state = AsymmetryState(np_verified=False, p_trajectory_active=True)
        res = SelfObservingCreationEngine.evaluate_asymmetry(state)
        self.assertTrue(res["valid"])
        self.assertEqual(res["np_phase_space_state"], "FAIL-CLOSED (COLLAPSED TO ZERO)")
        self.assertEqual(res["p_phase_space_state"], "FAIL-OPEN (CONTINUOUS EVOLUTION)")
        self.assertEqual(res["verdict"], "SELF-OBSERVING CREATION VALIDATED")
        self.assertTrue(res["witness_hash"].startswith("W_SELF_OBSERVING_"))

    def test_forbidden_reversal_trigger(self):
        state = AsymmetryState(reverse_mode_requested=True)
        res = SelfObservingCreationEngine.evaluate_asymmetry(state)
        self.assertFalse(res["valid"])
        self.assertEqual(res["verdict"], "FORBIDDEN REVERSAL KILL")

if __name__ == "__main__":
    unittest.main()
