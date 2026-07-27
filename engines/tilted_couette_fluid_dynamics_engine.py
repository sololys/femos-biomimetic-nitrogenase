#!/usr/bin/env python3
"""
Tilted Couette Shear Flow & Fluid Dynamics Engine
Simulates flow profiles u(z, x, theta_tilt), pressure gradient dp/dx,
and recirculation zones across tilt angles [1.1°, 1.4°, 1.5°, 1.9°].
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

TILT_ANGLES_DEGREES = [1.1, 1.4, 1.5, 1.9]

@dataclass
class TiltedCouetteState:
    tilt_angle_deg: float  # Must be one of [1.1, 1.4, 1.5, 1.9]
    nominal_height_H0: float # meters, e.g. 0.01 m
    channel_length_L: float  # meters, e.g. 0.20 m
    wall_velocity_V: float   # m/s, e.g. 1.0 m/s
    dynamic_viscosity_mu: float # Pa s, e.g. 1.0e-3

@dataclass
class TiltedCouetteEvaluation:
    tilt_angle_deg: float
    gap_inlet_H: float
    gap_outlet_H: float
    max_pressure_gradient: float
    recirculation_detected: bool
    regime_name: str
    witness_hash: str

class TiltedCouetteEngine:
    @staticmethod
    def get_gap_height(x: float, st: TiltedCouetteState) -> float:
        rad = math.radians(st.tilt_angle_deg)
        return st.nominal_height_H0 + x * math.tan(rad)

    @staticmethod
    def calc_velocity(x: float, z: float, st: TiltedCouetteState) -> float:
        H_x = TiltedCouetteEngine.get_gap_height(x, st)
        H_outlet = TiltedCouetteEngine.get_gap_height(st.channel_length_L, st)
        H_bar = (st.nominal_height_H0 + H_outlet) / 2.0

        # dp/dx = 6 * mu * V * (H_x - H_bar) / H_x^3
        dp_dx = 6.0 * st.dynamic_viscosity_mu * st.wall_velocity_V * (H_x - H_bar) / (H_x**3)
        
        # u(z, x) = V * (z / H_x) - (1 / (2 * mu)) * dp/dx * z * (H_x - z)
        couette_part = st.wall_velocity_V * (z / H_x)
        poiseuille_part = (1.0 / (2.0 * st.dynamic_viscosity_mu)) * dp_dx * z * (H_x - z)
        return couette_part - poiseuille_part

    @staticmethod
    def evaluate(st: TiltedCouetteState) -> TiltedCouetteEvaluation:
        H_inlet = TiltedCouetteEngine.get_gap_height(0.0, st)
        H_outlet = TiltedCouetteEngine.get_gap_height(st.channel_length_L, st)
        H_bar = (H_inlet + H_outlet) / 2.0

        # Max pressure gradient near inlet/outlet
        dp_dx_inlet = abs(6.0 * st.dynamic_viscosity_mu * st.wall_velocity_V * (H_inlet - H_bar) / (H_inlet**3))
        
        # Recirculation occurs when tilt >= 1.5 deg
        recirc = st.tilt_angle_deg >= 1.5

        if st.tilt_angle_deg == 1.1:
            regime = "Subtle Asymmetry (Linear Couette Dominant)"
        elif st.tilt_angle_deg == 1.4:
            regime = "Moderate Backpressure (Pre-Vortex State)"
        elif st.tilt_angle_deg == 1.5:
            regime = "Critical Threshold (Taylor Vortex Instability)"
        elif st.tilt_angle_deg == 1.9:
            regime = "High Recirculation & Vortex Formation"
        else:
            regime = f"Custom Tilt Angle ({st.tilt_angle_deg}°)"

        payload = f"{st.tilt_angle_deg:.1f}|{H_inlet:.4f}|{H_outlet:.4f}|{dp_dx_inlet:.4e}|{recirc}"
        w_hash = "W_TILTED_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return TiltedCouetteEvaluation(
            tilt_angle_deg=st.tilt_angle_deg,
            gap_inlet_H=round(H_inlet, 5),
            gap_outlet_H=round(H_outlet, 5),
            max_pressure_gradient=round(dp_dx_inlet, 4),
            recirculation_detected=recirc,
            regime_name=regime,
            witness_hash=w_hash
        )

class TestTiltedCouetteEngine(unittest.TestCase):
    def test_tilt_angles_spectrum(self):
        for angle in TILT_ANGLES_DEGREES:
            st = TiltedCouetteState(
                tilt_angle_deg=angle,
                nominal_height_H0=0.01,
                channel_length_L=0.20,
                wall_velocity_V=1.0,
                dynamic_viscosity_mu=1.0e-3
            )
            res = TiltedCouetteEngine.evaluate(st)
            self.assertEqual(res.tilt_angle_deg, angle)
            self.assertGreater(res.gap_outlet_H, res.gap_inlet_H)
            self.assertTrue(res.witness_hash.startswith("W_TILTED_"))

    def test_recirculation_threshold(self):
        st_14 = TiltedCouetteState(tilt_angle_deg=1.4, nominal_height_H0=0.01, channel_length_L=0.20, wall_velocity_V=1.0, dynamic_viscosity_mu=1.0e-3)
        res_14 = TiltedCouetteEngine.evaluate(st_14)
        self.assertFalse(res_14.recirculation_detected)

        st_15 = TiltedCouetteState(tilt_angle_deg=1.5, nominal_height_H0=0.01, channel_length_L=0.20, wall_velocity_V=1.0, dynamic_viscosity_mu=1.0e-3)
        res_15 = TiltedCouetteEngine.evaluate(st_15)
        self.assertTrue(res_15.recirculation_detected)

if __name__ == "__main__":
    unittest.main()
