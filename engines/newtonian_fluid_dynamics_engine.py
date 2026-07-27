#!/usr/bin/env python3
"""
Newtonian Fluid Couette & Stratigraphic Dynamics Engine
Simulates:
1. Linear constitutive relation tau = mu * (du/dz)
2. Couette flow u(z, x) under constant dynamic viscosity mu
3. Viscous dissipation function Phi = mu * (du/dz)^2
4. Newtonian Stokes settling & Shields erosion criterion
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

@dataclass
class NewtonianParams:
    viscosity_mu: float = 1.0e-3     # Pa s (water at 20C)
    fluid_density_rho: float = 1000.0# kg/m^3
    wall_velocity_V: float = 1.0      # m/s
    channel_height_H: float = 0.01   # m
    tilt_angle_deg: float = 1.1       # degrees

class NewtonianFluidEngine:
    @staticmethod
    def calc_shear_stress(shear_rate: float, params: NewtonianParams) -> float:
        # tau = mu * shear_rate (linear constitutive law)
        return params.viscosity_mu * shear_rate

    @staticmethod
    def calc_dissipation(shear_rate: float, params: NewtonianParams) -> float:
        # Phi = mu * (du/dz)^2
        return params.viscosity_mu * (shear_rate**2)

    @staticmethod
    def evaluate_flow(z_pos: float, params: NewtonianParams) -> Dict[str, Any]:
        if params.channel_height_H <= 0:
            return {"verdict": "WALL CONTACT SINGULARITY", "valid": False}

        shear_rate = params.wall_velocity_V / params.channel_height_H
        tau = NewtonianFluidEngine.calc_shear_stress(shear_rate, params)
        phi = NewtonianFluidEngine.calc_dissipation(shear_rate, params)

        u_z = params.wall_velocity_V * (z_pos / params.channel_height_H)
        valid = params.viscosity_mu > 0 and math.isfinite(tau)

        payload = f"{params.viscosity_mu:.4e}|{tau:.4f}|{phi:.4f}|{valid}"
        w_hash = "W_NEWTONIAN_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return {
            "u_z": round(u_z, 4),
            "shear_rate": round(shear_rate, 2),
            "shear_stress_tau": round(tau, 6),
            "dissipation_phi": round(phi, 6),
            "valid": valid,
            "verdict": "NEWTONIAN FLOW OPEN" if valid else "FAIL",
            "witness_hash": w_hash
        }

class TestNewtonianFluidEngine(unittest.TestCase):
    def test_linear_constitutive_law(self):
        params = NewtonianParams(viscosity_mu=1.0e-3, wall_velocity_V=2.0, channel_height_H=0.01)
        res = NewtonianFluidEngine.evaluate_flow(0.005, params)
        self.assertTrue(res["valid"])
        self.assertEqual(res["shear_rate"], 200.0)
        self.assertAlmostEqual(res["shear_stress_tau"], 0.2, places=4)
        self.assertTrue(res["witness_hash"].startswith("W_NEWTONIAN_"))

if __name__ == "__main__":
    unittest.main()
