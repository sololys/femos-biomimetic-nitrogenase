#!/usr/bin/env python3
"""
Interdependent Gate Dynamics Engine
Simulates cross-gate coupling and resonance between:
1. Poincaré Disk Gates (Hyperbolic, Punctured, Observatory)
2. Local Realized System Gates (L0 FPGA, D1 Lorenz, M0 Morandi)
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class DiskGatesState:
    poincare_gate_open: bool = True
    punctured_gate_open: bool = True
    observatory_gate_open: bool = True
    disk_resonance_frequency: float = 4.26 # Hz

@dataclass
class LocalGatesState:
    l0_fpga_open: bool = True
    d1_lorenz_open: bool = True
    m0_morandi_open: bool = True
    local_clock_frequency: float = 4.26 # Hz

class InterdependentGateEngine:
    @staticmethod
    def calc_cross_coupling_resonance(disk: DiskGatesState, local: LocalGatesState) -> float:
        freq_diff = abs(disk.disk_resonance_frequency - local.local_clock_frequency)
        # Resonance coupling coefficient C in [0.0, 1.0]
        return math.exp(-freq_diff)

    @staticmethod
    def evaluate_interdependency(disk: DiskGatesState = DiskGatesState(), local: LocalGatesState = LocalGatesState()) -> Dict[str, Any]:
        disk_all_open = disk.poincare_gate_open and disk.punctured_gate_open and disk.observatory_gate_open
        local_all_open = local.l0_fpga_open and local.d1_lorenz_open and local.m0_morandi_open

        coupling_c = InterdependentGateEngine.calc_cross_coupling_resonance(disk, local)

        # Cross-gate fail-closed rule: If any disk gate closes, local gates trigger fail-closed safety
        harmony_open = disk_all_open and local_all_open and coupling_c >= 0.90
        verdict = "INTERDEPENDENT HARMONY OPEN" if harmony_open else "CROSS-GATE FAIL-CLOSED"

        payload = f"{disk_all_open}|{local_all_open}|{coupling_c:.4f}|{verdict}"
        w_hash = "W_INTERDEPENDENT_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return {
            "disk_gates_open": disk_all_open,
            "local_gates_open": local_all_open,
            "coupling_coefficient": round(coupling_c, 4),
            "harmony_open": harmony_open,
            "verdict": verdict,
            "witness_hash": w_hash
        }

class TestInterdependentGateEngine(unittest.TestCase):
    def test_harmony_open(self):
        disk = DiskGatesState()
        local = LocalGatesState()
        res = InterdependentGateEngine.evaluate_interdependency(disk, local)
        self.assertTrue(res["harmony_open"])
        self.assertEqual(res["verdict"], "INTERDEPENDENT HARMONY OPEN")
        self.assertTrue(res["witness_hash"].startswith("W_INTERDEPENDENT_"))

    def test_fail_closed_coupling(self):
        disk = DiskGatesState(punctured_gate_open=False) # Disk gate collapses
        local = LocalGatesState()
        res = InterdependentGateEngine.evaluate_interdependency(disk, local)
        self.assertFalse(res["harmony_open"])
        self.assertEqual(res["verdict"], "CROSS-GATE FAIL-CLOSED")

if __name__ == "__main__":
    unittest.main()
