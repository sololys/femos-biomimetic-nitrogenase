#!/usr/bin/env python3
"""
Non-Newtonian & Viscoelastic Fluid Dynamics Engine
Implements:
1. Power-Law (Ostwald-de Waele) model: tau = K * gamma_dot^n
2. Carreau-Yasuda model: mu_eff = mu_inf + (mu_0 - mu_inf) * [1 + (lambda * gamma_dot)^a]^((n-1)/a)
3. Weissenberg Number Wi = lambda * gamma_dot
4. First Normal Stress Difference N1 = Psi1 * gamma_dot^2
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class RheologyParams:
    flow_consistency_K: float = 0.5    # Pa s^n
    flow_index_n: float = 0.6          # n < 1 shear-thinning, n = 1 newtonian, n > 1 shear-thickening
    mu_0_zero_shear: float = 1.0       # Pa s
    mu_inf_infinite_shear: float = 1.0e-3 # Pa s
    relaxation_time_lambda: float = 0.1 # seconds
    yasuda_a: float = 2.0
    psi1_first_normal: float = 0.05    # Pa s^2

class NonNewtonianEngine:
    @staticmethod
    def calc_power_law_viscosity(shear_rate: float, params: RheologyParams) -> float:
        rate = max(1.0e-4, abs(shear_rate))
        return params.flow_consistency_K * (rate**(params.flow_index_n - 1.0))

    @staticmethod
    def calc_carreau_yasuda_viscosity(shear_rate: float, params: RheologyParams) -> float:
        rate = abs(shear_rate)
        inner = 1.0 + (params.relaxation_time_lambda * rate)**params.yasuda_a
        exponent = (params.flow_index_n - 1.0) / params.yasuda_a
        return params.mu_inf_infinite_shear + (params.mu_0_zero_shear - params.mu_inf_infinite_shear) * (inner**exponent)

    @staticmethod
    def calc_weissenberg_number(shear_rate: float, params: RheologyParams) -> float:
        return params.relaxation_time_lambda * abs(shear_rate)

    @staticmethod
    def evaluate_rheology(shear_rate: float, params: RheologyParams = RheologyParams()) -> Dict[str, Any]:
        mu_power = NonNewtonianEngine.calc_power_law_viscosity(shear_rate, params)
        mu_carreau = NonNewtonianEngine.calc_carreau_yasuda_viscosity(shear_rate, params)
        Wi = NonNewtonianEngine.calc_weissenberg_number(shear_rate, params)
        N1 = params.psi1_first_normal * (shear_rate**2)

        valid = math.isfinite(mu_power) and math.isfinite(mu_carreau) and Wi < 10.0
        elastic_instability = Wi > 5.0

        if params.flow_index_n < 1.0:
            regime = "Shear-Thinning (Pseudoplastisk)"
        elif params.flow_index_n == 1.0:
            regime = "Newtonsk Væske Baseline"
        else:
            regime = "Shear-Thickening (Dilatant)"

        payload = f"{shear_rate:.2f}|{params.flow_index_n:.2f}|{mu_power:.4e}|{Wi:.4f}|{valid}"
        w_hash = "W_NON_NEWTONIAN_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return {
            "shear_rate": round(shear_rate, 2),
            "mu_power_law": round(mu_power, 6),
            "mu_carreau_yasuda": round(mu_carreau, 6),
            "weissenberg_Wi": round(Wi, 4),
            "normal_stress_N1": round(N1, 4),
            "fluid_regime": regime,
            "elastic_instability": elastic_instability,
            "valid": valid,
            "verdict": "NON-NEWTONIAN OPEN" if valid else "ELASTIC FAIL",
            "witness_hash": w_hash
        }

class TestNonNewtonianEngine(unittest.TestCase):
    def test_shear_thinning_behavior(self):
        params = RheologyParams(flow_index_n=0.5, flow_consistency_K=1.0)
        res_low = NonNewtonianEngine.evaluate_rheology(1.0, params)
        res_high = NonNewtonianEngine.evaluate_rheology(100.0, params)

        self.assertLess(res_high["mu_power_law"], res_low["mu_power_law"])
        self.assertEqual(res_low["fluid_regime"], "Shear-Thinning (Pseudoplastisk)")
        self.assertTrue(res_low["witness_hash"].startswith("W_NON_NEWTONIAN_"))

    def test_weissenberg_number(self):
        params = RheologyParams(relaxation_time_lambda=0.2)
        res = NonNewtonianEngine.evaluate_rheology(10.0, params)
        self.assertEqual(res["weissenberg_Wi"], 2.0)

if __name__ == "__main__":
    unittest.main()
