#!/usr/bin/env python3
"""
Morandi Vindu Hjertet Engine
Simulates:
1. Pulsing Quantum Heart rate f_heart
2. Energy barrier phase window Delta V_barrier(theta) -> 0
3. Morandi M001 Invariant & Glans detection
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class MorandiHeartState:
    heart_rate_hz: float = 1.16       # Heartbeat frequency (Hz)
    electron_phase_rad: float = 3.14159# theta_e = pi (opposite side)
    neutron_phase_rad: float = 0.0     # theta_n = 0
    glans_reflection: float = 0.0     # Matte surface (0.0), Glans (> 0.05)

class MorandiHeartEngine:
    @staticmethod
    def calc_barrier_potential(theta_e: float, theta_n: float) -> float:
        # Delta V_barrier = V0 * cos^2( (theta_e - theta_n)/2 )
        # When theta_e - theta_n = pi, cos(pi/2) = 0 -> V_barrier = 0
        diff = theta_e - theta_n
        return math.cos(diff / 2.0)**2

    @staticmethod
    def evaluate_heart(state: MorandiHeartState = MorandiHeartState()) -> Dict[str, Any]:
        v_barrier = MorandiHeartEngine.calc_barrier_potential(state.electron_phase_rad, state.neutron_phase_rad)
        glans_kill = state.glans_reflection > 0.05

        window_open = v_barrier < 0.05 and not glans_kill
        verdict = "MORANDI HEART PULSING OPEN" if window_open else ("GLANS KILL TRIGGERED" if glans_kill else "WINDOW CLOSED")

        payload = f"{state.heart_rate_hz:.2f}|{v_barrier:.4f}|{state.glans_reflection:.4f}|{verdict}"
        w_hash = "W_MORANDI_HEART_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return {
            "heart_rate_hz": state.heart_rate_hz,
            "barrier_potential_V": round(v_barrier, 6),
            "glans_reflection": state.glans_reflection,
            "window_open": window_open,
            "verdict": verdict,
            "witness_hash": w_hash
        }

class TestMorandiHeartEngine(unittest.TestCase):
    def test_window_opening_at_opposite_phase(self):
        state = MorandiHeartState(electron_phase_rad=math.pi, neutron_phase_rad=0.0)
        res = MorandiHeartEngine.evaluate_heart(state)
        self.assertTrue(res["window_open"])
        self.assertAlmostEqual(res["barrier_potential_V"], 0.0, places=4)
        self.assertEqual(res["verdict"], "MORANDI HEART PULSING OPEN")
        self.assertTrue(res["witness_hash"].startswith("W_MORANDI_HEART_"))

    def test_glans_kill_trigger(self):
        state = MorandiHeartState(glans_reflection=0.10) # Glans active -> Kill
        res = MorandiHeartEngine.evaluate_heart(state)
        self.assertFalse(res["window_open"])
        self.assertEqual(res["verdict"], "GLANS KILL TRIGGERED")

if __name__ == "__main__":
    unittest.main()
