#!/usr/bin/env python3
"""
Kreativ-Core System Manager: Quantum Control Core Engine
Implements Orfeus Protocol, OMNI-Rosetta translation, Kerr Admissibility,
Symmetry & Lattice Deformation Detection, and Fail-Closed Guard.
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import Dict, Any, Tuple

@dataclass
class QuantumControlState:
    kerr_admissibility: float    # e.g., 0.984 (98.4%)
    discipline_score: float      # e.g., 0.991 (99.1%)
    lattice_deformation: float   # > 0.05 indicates deformation failure
    t_uv_h_plus_valid: bool
    t_uv_h_minus_safe: bool

@dataclass
class ControlEvaluation:
    state: QuantumControlState
    lattice_healthy: bool
    pilot_admissible: bool
    fail_closed_active: bool
    termination_reason: str
    witness_hash: str

class KreativCoreQuantumEngine:
    @staticmethod
    def evaluate(s: QuantumControlState) -> ControlEvaluation:
        # Symmetry check: Lattice deformation threshold <= 0.05
        lattice_healthy = s.lattice_deformation <= 0.05
        
        # Pilot admissibility check
        pilot_admissible = (
            s.t_uv_h_plus_valid and 
            s.t_uv_h_minus_safe and 
            s.kerr_admissibility >= 0.95 and 
            s.discipline_score >= 0.95 and
            lattice_healthy
        )

        # Fail-closed guard activation
        if not lattice_healthy:
            fail_closed_active = True
            termination_reason = (
                "Deformation Failure Detected. Fail-Closed State Activated: "
                "Preventing Pilot Execution due to Deformation Failure (as per Discipline)."
            )
        elif not pilot_admissible:
            fail_closed_active = True
            termination_reason = "Pilot Admissibility Criteria Violation. Execution Halted."
        else:
            fail_closed_active = False
            termination_reason = "SYSTEM_HEALTHY_PILOT_EXECUTION_PERMITTED"

        # SHA-256 Witness Hash
        payload = f"{s.kerr_admissibility:.4f}|{s.discipline_score:.4f}|{s.lattice_deformation:.4f}|{fail_closed_active}"
        w_prefix = "W_SAFE_" if not fail_closed_active else "W_FAILCLOSED_"
        w_hash = w_prefix + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return ControlEvaluation(
            state=s,
            lattice_healthy=lattice_healthy,
            pilot_admissible=pilot_admissible,
            fail_closed_active=fail_closed_active,
            termination_reason=termination_reason,
            witness_hash=w_hash
        )

class TestKreativCoreQuantumEngine(unittest.TestCase):
    def test_healthy_state(self):
        s = QuantumControlState(
            kerr_admissibility=0.984,
            discipline_score=0.991,
            lattice_deformation=0.02,
            t_uv_h_plus_valid=True,
            t_uv_h_minus_safe=True
        )
        res = KreativCoreQuantumEngine.evaluate(s)
        self.assertTrue(res.lattice_healthy)
        self.assertTrue(res.pilot_admissible)
        self.assertFalse(res.fail_closed_active)
        self.assertTrue(res.witness_hash.startswith("W_SAFE_"))

    def test_deformation_fail_closed(self):
        s = QuantumControlState(
            kerr_admissibility=0.984,
            discipline_score=0.991,
            lattice_deformation=0.12, # Deformed > 0.05
            t_uv_h_plus_valid=True,
            t_uv_h_minus_safe=True
        )
        res = KreativCoreQuantumEngine.evaluate(s)
        self.assertFalse(res.lattice_healthy)
        self.assertFalse(res.pilot_admissible)
        self.assertTrue(res.fail_closed_active)
        self.assertIn("Deformation Failure Detected", res.termination_reason)
        self.assertTrue(res.witness_hash.startswith("W_FAILCLOSED_"))

if __name__ == "__main__":
    unittest.main()
