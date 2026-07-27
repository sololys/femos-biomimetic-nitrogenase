#!/usr/bin/env python3
"""
Magnetohydrodynamics (MHD) & Plasma Couette Flow Engine
Implements:
1. Hartmann Number Ha = B0 * H * sqrt(sigma / mu)
2. Hartmann velocity profile u(z) = V * sinh(Ha * z / H) / sinh(Ha)
3. Induced current density J_y = sigma * (E_y + u * B0)
4. Joule dissipation rate Phi_J = J_y^2 / sigma
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class MHDPlasmaParams:
    magnetic_field_B0: float = 0.5   # Tesla
    conductivity_sigma: float = 1.0e6# S/m (plasma / liquid metal)
    viscosity_mu: float = 1.0e-3     # Pa s
    wall_velocity_V: float = 1.0      # m/s
    channel_height_H: float = 0.01   # m
    electric_field_Ey: float = 0.0   # V/m

class MHDEngine:
    @staticmethod
    def calc_hartmann_number(params: MHDPlasmaParams) -> float:
        # Ha = B0 * H * sqrt(sigma / mu)
        ratio = params.conductivity_sigma / params.viscosity_mu
        return params.magnetic_field_B0 * params.channel_height_H * math.sqrt(ratio)

    @staticmethod
    def calc_hartmann_velocity(z: float, params: MHDPlasmaParams) -> float:
        Ha = MHDEngine.calc_hartmann_number(params)
        if Ha < 1.0e-4:
            # Linear Couette limit
            return params.wall_velocity_V * (z / params.channel_height_H)
        
        z_norm = z / params.channel_height_H
        num = math.sinh(Ha * z_norm)
        den = math.sinh(Ha)
        if den == 0:
            return 0.0
        return params.wall_velocity_V * (num / den)

    @staticmethod
    def evaluate_mhd(z: float, params: MHDPlasmaParams = MHDPlasmaParams()) -> Dict[str, Any]:
        Ha = MHDEngine.calc_hartmann_number(params)
        u_z = MHDEngine.calc_hartmann_velocity(z, params)

        # J_y = sigma * (E_y + u * B0)
        J_y = params.conductivity_sigma * (params.electric_field_Ey + u_z * params.magnetic_field_B0)
        # Phi_J = J_y^2 / sigma
        Phi_J = (J_y**2) / params.conductivity_sigma

        delta_Ha = params.channel_height_H / max(1.0, Ha)
        valid = math.isfinite(u_z) and math.isfinite(Phi_J) and Ha <= 50.0

        payload = f"{params.magnetic_field_B0:.2f}|{Ha:.4f}|{u_z:.4f}|{Phi_J:.4e}|{valid}"
        w_hash = "W_MHD_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return {
            "hartmann_number_Ha": round(Ha, 4),
            "hartmann_layer_delta": round(delta_Ha, 6),
            "velocity_u_z": round(u_z, 4),
            "current_density_Jy": round(J_y, 2),
            "joule_dissipation_Phi_J": round(Phi_J, 4),
            "valid": valid,
            "verdict": "MHD PLASMA OPEN" if valid else "MAGNETIC DISRUPTION",
            "witness_hash": w_hash
        }

class TestMHDEngine(unittest.TestCase):
    def test_hartmann_number_and_profile(self):
        params = MHDPlasmaParams(magnetic_field_B0=0.2, conductivity_sigma=1.0e4, viscosity_mu=1.0e-3)
        res = MHDEngine.evaluate_mhd(0.005, params)
        self.assertTrue(res["valid"])
        self.assertGreater(res["hartmann_number_Ha"], 0.0)
        self.assertTrue(res["witness_hash"].startswith("W_MHD_"))

    def test_zero_field_linear_couette_limit(self):
        params = MHDPlasmaParams(magnetic_field_B0=0.0) # B0 = 0 -> Ha = 0
        u_mid = MHDEngine.calc_hartmann_velocity(0.005, params) # z = H/2 = 0.005
        self.assertAlmostEqual(u_mid, 0.5, places=4) # V * 0.5 = 0.5 m/s

if __name__ == "__main__":
    unittest.main()
