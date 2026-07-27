#!/usr/bin/env python3
"""
P vs NP: Fibered Computational Landscape Engine
Implements Instance Base Space X, Witness Fiber W_x, Path Fiber Gamma_x,
Transition Geometry G_x (forced_ratio), Resource Space R_x, and Complexity Projections.
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

@dataclass
class LandscapeInstance:
    instance_id: str
    n_vars: int
    n_clauses: int
    forced_ratio: float
    conflict_density: float

@dataclass
class PathCost:
    time_T: float
    space_S: float
    branching_B: float
    conflicts_C: float

@dataclass
class LandscapeEvaluation:
    instance: LandscapeInstance
    witness_count: int
    has_witness: bool
    phase: str
    projections: Dict[str, Any]
    path_cost: PathCost
    witness_hash: str

class FiberedLandscapeEngine:
    @staticmethod
    def classify_phase(forced_ratio: float) -> str:
        if forced_ratio >= 0.75:
            return "FORCED_DOMINANT"
        elif forced_ratio >= 0.50:
            return "GUIDED_NO_CONFLICT"
        elif forced_ratio >= 0.25:
            return "SEARCH_WITH_CONFLICT"
        else:
            return "HOLD_TIMEOUT"

    @staticmethod
    def evaluate_instance(inst: LandscapeInstance) -> LandscapeEvaluation:
        phase = FiberedLandscapeEngine.classify_phase(inst.forced_ratio)
        
        # Estimate witness count |W_x| based on forced ratio & density
        raw_witnesses = max(0, int(2**(inst.n_vars * (1.0 - inst.forced_ratio) * 0.3) - inst.conflict_density * 10))
        witness_count = raw_witnesses if phase != "HOLD_TIMEOUT" else 0
        has_witness = witness_count > 0 or inst.forced_ratio > 0.8

        # Compute Path Cost
        if phase == "FORCED_DOMINANT":
            time_T = float(inst.n_vars * 1.5)
            space_S = float(inst.n_vars * 0.5)
            branching_B = 1.05
            conflicts_C = float(inst.conflict_density * 2)
        elif phase == "GUIDED_NO_CONFLICT":
            time_T = float(inst.n_vars**2 * 0.8)
            space_S = float(inst.n_vars * 1.2)
            branching_B = 1.35
            conflicts_C = float(inst.conflict_density * 8)
        elif phase == "SEARCH_WITH_CONFLICT":
            time_T = float(2**(inst.n_vars * 0.4))
            space_S = float(inst.n_vars * 2.5)
            branching_B = 1.85
            conflicts_C = float(inst.conflict_density * 25)
        else: # HOLD_TIMEOUT
            time_T = 10000.0
            space_S = float(inst.n_vars * 5.0)
            branching_B = 2.0
            conflicts_C = 999.0

        path_cost = PathCost(
            time_T=round(time_T, 2),
            space_S=round(space_S, 2),
            branching_B=round(branching_B, 2),
            conflicts_C=round(conflicts_C, 2)
        )

        # Projections
        projections = {
            "P": phase in ["FORCED_DOMINANT", "GUIDED_NO_CONFLICT"],
            "NP": has_witness,
            "coNP": not has_witness,
            "sharpP_count": witness_count,
            "FNP_constructible": has_witness,
            "PSPACE_bounded": space_S <= inst.n_vars * 10
        }

        # SHA-256 Witness Hash
        payload = f"{inst.instance_id}|{inst.n_vars}|{inst.forced_ratio:.4f}|{phase}|{has_witness}"
        w_hash = "W_LANDSCAPE_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return LandscapeEvaluation(
            instance=inst,
            witness_count=witness_count,
            has_witness=has_witness,
            phase=phase,
            projections=projections,
            path_cost=path_cost,
            witness_hash=w_hash
        )

class TestFiberedLandscapeEngine(unittest.TestCase):
    def test_forced_dominant_phase(self):
        inst = LandscapeInstance("INST_001", n_vars=20, n_clauses=80, forced_ratio=0.85, conflict_density=0.1)
        res = FiberedLandscapeEngine.evaluate_instance(inst)
        self.assertEqual(res.phase, "FORCED_DOMINANT")
        self.assertTrue(res.projections["P"])
        self.assertTrue(res.projections["NP"])

    def test_search_conflict_phase(self):
        inst = LandscapeInstance("INST_002", n_vars=30, n_clauses=120, forced_ratio=0.35, conflict_density=0.6)
        res = FiberedLandscapeEngine.evaluate_instance(inst)
        self.assertEqual(res.phase, "SEARCH_WITH_CONFLICT")
        self.assertFalse(res.projections["P"])

    def test_hold_timeout_phase(self):
        inst = LandscapeInstance("INST_003", n_vars=50, n_clauses=200, forced_ratio=0.10, conflict_density=0.9)
        res = FiberedLandscapeEngine.evaluate_instance(inst)
        self.assertEqual(res.phase, "HOLD_TIMEOUT")
        self.assertEqual(res.path_cost.time_T, 10000.0)

if __name__ == "__main__":
    unittest.main()
