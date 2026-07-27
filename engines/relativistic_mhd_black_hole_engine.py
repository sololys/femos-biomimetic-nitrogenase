#!/usr/bin/env python3
"""
Relativistic Magnetohydrodynamics (RMHD) & Black Hole Astrophysics Engine
Implements:
1. Relativistic Lorentz factor gamma = 1 / sqrt(1 - v^2/c^2)
2. Magnetization parameter sigma_MHD = b^2 / (rho * c^2)
3. Relativistic Alfven velocity v_A = c * sqrt(b^2 / (w + b^2))
4. Kerr black hole horizon r_plus = M + sqrt(M^2 - a^2)
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import Dict, Any

C_LIGHT = 299792458.0 # m/s

@dataclass
class RMHDParams:
    plasma_velocity_v: float = 0.8 * C_LIGHT # 0.8c
    rest_density_rho: float = 1.0e-10        # kg/m^3
    magnetic_field_b: float = 10.0            # Tesla
    kerr_spin_a: float = 0.9                  # a/M <= 1.0
    radius_r: float = 3.0                     # r in units of GM/c^2

class RHMDEngine:
    @staticmethod
    def calc_lorentz_factor(v: float) -> float:
        if abs(v) >= C_LIGHT:
            return float('inf')
        return 1.0 / math.sqrt(1.0 - (v / C_LIGHT)**2)

    @staticmethod
    def calc_magnetization(b: float, rho: float) -> float:
        if rho <= 0:
            return float('inf')
        b_sq = b**2
        return b_sq / (rho * (C_LIGHT**2))

    @staticmethod
    def calc_rel_alfven_velocity(b: float, rho: float) -> float:
        w = rho * (C_LIGHT**2) # Enthalpy approximation
        b_sq = b**2
        return C_LIGHT * math.sqrt(b_sq / (w + b_sq))

    @staticmethod
    def evaluate_rmhd(params: RMHDParams = RMHDParams()) -> Dict[str, Any]:
        v = params.plasma_velocity_v
        r = params.radius_r
        a = params.kerr_spin_a

        # Kerr Outer Horizon r_plus = 1 + sqrt(1 - a^2) in GM/c^2 units
        r_plus = 1.0 + math.sqrt(max(0.0, 1.0 - a**2))
        
        gamma = RHMDEngine.calc_lorentz_factor(v)
        sigma = RHMDEngine.calc_magnetization(params.magnetic_field_b, params.rest_density_rho)
        v_A = RHMDEngine.calc_rel_alfven_velocity(params.magnetic_field_b, params.rest_density_rho)

        admissible = r > r_plus and v < C_LIGHT and math.isfinite(gamma)
        verdict = "RMHD ASTROPHYSICS OPEN" if admissible else "HORIZON EVENT COLLAPSE"

        payload = f"{v:.4e}|{r:.4f}|{a:.4f}|{gamma:.4f}|{sigma:.4e}|{verdict}"
        w_prefix = "W_RMHD_" if admissible else "W_RMHD_FAIL_"
        w_hash = w_prefix + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return {
            "lorentz_gamma": round(gamma, 4) if math.isfinite(gamma) else 999999.0,
            "magnetization_sigma": round(sigma, 6) if math.isfinite(sigma) else 999999.0,
            "rel_alfven_velocity_vA": round(v_A, 2),
            "kerr_horizon_r_plus": round(r_plus, 4),
            "admissible": admissible,
            "verdict": verdict,
            "witness_hash": w_hash
        }

class TestRHMDEngine(unittest.TestCase):
    def test_rel_lorentz_factor(self):
        v = 0.8 * C_LIGHT
        gamma = RHMDEngine.calc_lorentz_factor(v)
        self.assertAlmostEqual(gamma, 1.6667, places=3)

    def test_rmhd_evaluation(self):
        params = RMHDParams(plasma_velocity_v=0.6 * C_LIGHT, radius_r=3.0, kerr_spin_a=0.9)
        res = RHMDEngine.evaluate_rmhd(params)
        self.assertTrue(res["admissible"])
        self.assertEqual(res["verdict"], "RMHD ASTROPHYSICS OPEN")
        self.assertTrue(res["witness_hash"].startswith("W_RMHD_"))

if __name__ == "__main__":
    unittest.main()
