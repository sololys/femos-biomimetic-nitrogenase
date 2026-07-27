#!/usr/bin/env python3
"""
Proton-Neutron Capture & Isotope Formation Engine
Simulates Vector Sums (F_attr vs F_rep), 110:1 Frequency Ratio, Time Window Barrier,
and Deuterium (2H) / Tritium (3H) Nucleosynthesis.
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

@dataclass
class CaptureState:
    distance_d_fm: float       # Distance d in femtometers (fm)
    electron_phase_rad: float # Hydrogen electron phase (0 to 2*pi)
    n_captured_neutrons: int  # 0 -> 1H, 1 -> 2H (Deuterium), 2 -> 3H (Tritium)
    quark_attraction: float   # Green vector magnitude F_attr
    quark_repulsion: float    # Red vector magnitude F_rep

@dataclass
class CaptureEvaluation:
    net_force: float          # F_attr - F_rep > 0
    barrier_open: bool        # True when electron phase is on opposite side (pi +- pi/3)
    capture_successful: bool
    resulting_isotope: str    # "Hydrogen-1", "Deuterium-2", "Tritium-3"
    witness_hash: str

class ProtonNeutronCaptureEngine:
    RATIO_110 = 110.0 # 110 rotations per single Hydrogen electron rotation

    @staticmethod
    def evaluate_capture(st: CaptureState) -> CaptureEvaluation:
        # Net Force calculation: F_attr >> F_rep
        net_force = max(0.0, st.quark_attraction - st.quark_repulsion)
        
        # Barrier is open when electron is on opposite side of neutron (phase near pi)
        phase_normalized = st.electron_phase_rad % (2 * math.pi)
        barrier_open = (math.pi - 1.0) <= phase_normalized <= (math.pi + 1.0)

        # Successful capture if barrier is open and net force > threshold at distance d
        capture_successful = barrier_open and net_force > 5.0 and st.distance_d_fm < 10.0

        if capture_successful:
            total_neutrons = st.n_captured_neutrons + 1
        else:
            total_neutrons = st.n_captured_neutrons

        if total_neutrons == 0:
            isotope = "Hydrogen-1 (^1H)"
        elif total_neutrons == 1:
            isotope = "Deuterium-2 (^2H)"
        else:
            isotope = "Tritium-3 (^3H)"

        payload = f"{st.distance_d_fm:.2f}|{st.electron_phase_rad:.2f}|{total_neutrons}|{net_force:.2f}|{capture_successful}"
        w_hash = "W_NUCLEO_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return CaptureEvaluation(
            net_force=round(net_force, 2),
            barrier_open=barrier_open,
            capture_successful=capture_successful,
            resulting_isotope=isotope,
            witness_hash=w_hash
        )

class TestProtonNeutronCaptureEngine(unittest.TestCase):
    def test_deuterium_formation_open_window(self):
        st = CaptureState(
            distance_d_fm=4.0,
            electron_phase_rad=math.pi, # Opposite side -> window open
            n_captured_neutrons=0,
            quark_attraction=45.0, # Green vector
            quark_repulsion=12.0   # Red vector
        )
        res = ProtonNeutronCaptureEngine.evaluate_capture(st)
        self.assertTrue(res.barrier_open)
        self.assertTrue(res.capture_successful)
        self.assertEqual(res.resulting_isotope, "Deuterium-2 (^2H)")
        self.assertTrue(res.witness_hash.startswith("W_NUCLEO_"))

    def test_barrier_closed_side(self):
        st = CaptureState(
            distance_d_fm=4.0,
            electron_phase_rad=0.0, # Same side -> barrier closed
            n_captured_neutrons=0,
            quark_attraction=45.0,
            quark_repulsion=12.0
        )
        res = ProtonNeutronCaptureEngine.evaluate_capture(st)
        self.assertFalse(res.barrier_open)
        self.assertFalse(res.capture_successful)

if __name__ == "__main__":
    unittest.main()
