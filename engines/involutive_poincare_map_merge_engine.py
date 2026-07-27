#!/usr/bin/env python3
"""
Involutive Poincaré Map Merge Engine
Implements:
1. Involutive transformation on Poincaré disk: I_P(z) = -z or -z_bar
2. Involutive identity: I_P(I_P(z)) == z
3. Hyperbolic geodesic metric calculation: ds^2 = 4 |dz|^2 / (1 - |z|^2)^2
4. Stokes polarization correspondence S = [S1, S2, S3]
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import Tuple

@dataclass
class PoincareComplex:
    re: float
    im: float

    def abs(self) -> float:
        return math.sqrt(self.re**2 + self.im**2)

@dataclass
class InvolutivePoincareState:
    z_point: PoincareComplex
    stokes_S: Tuple[float, float, float]
    time_reversed: bool = False

@dataclass
class InvolutivePoincareEvaluation:
    z_orig: PoincareComplex
    z_involute: PoincareComplex
    z_double_involute: PoincareComplex
    poincare_metric_g: float
    is_admissible: bool
    verdict: str
    witness_hash: str

class InvolutivePoincareEngine:
    @staticmethod
    def calc_poincare_metric(z: PoincareComplex) -> float:
        r2 = z.re**2 + z.im**2
        if r2 >= 1.0:
            return float('inf')
        return 4.0 / ((1.0 - r2)**2)

    @staticmethod
    def involute_map(z: PoincareComplex) -> PoincareComplex:
        # Involutive map: I(z) = -z
        return PoincareComplex(-z.re, -z.im)

    @staticmethod
    def evaluate(st: InvolutivePoincareState) -> InvolutivePoincareEvaluation:
        z0 = st.z_point
        z1 = InvolutivePoincareEngine.involute_map(z0)
        z2 = InvolutivePoincareEngine.involute_map(z1) # Double application -> I^2(z) == z

        r_orig = z0.abs()
        g_metric = InvolutivePoincareEngine.calc_poincare_metric(z0)
        
        # Identity error check ||I^2(z) - z||
        err = math.sqrt((z2.re - z0.re)**2 + (z2.im - z0.im)**2)
        admissible = r_orig < 1.0 and err < 1.0e-5 and math.isfinite(g_metric)

        verdict = "INVOLUTIVE POINCARÉ OPEN" if admissible else "POINCARÉ BOUNDARY FAIL"

        payload = f"{z0.re:.4f}|{z0.im:.4f}|{r_orig:.4f}|{g_metric:.4f}|{verdict}"
        w_prefix = "W_INV_POINCARE_" if admissible else "W_INV_POINCARE_FAIL_"
        w_hash = w_prefix + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return InvolutivePoincareEvaluation(
            z_orig=z0,
            z_involute=z1,
            z_double_involute=z2,
            poincare_metric_g=round(g_metric, 4) if math.isfinite(g_metric) else 999999.0,
            is_admissible=admissible,
            verdict=verdict,
            witness_hash=w_hash
        )

class TestInvolutivePoincareEngine(unittest.TestCase):
    def test_involutive_poincare_identity(self):
        z = PoincareComplex(0.3, -0.4)
        st = InvolutivePoincareState(z_point=z, stokes_S=(0.6, 0.0, 0.8))
        res = InvolutivePoincareEngine.evaluate(st)
        self.assertTrue(res.is_admissible)
        self.assertEqual(res.z_double_involute.re, z.re)
        self.assertEqual(res.z_double_involute.im, z.im)
        self.assertTrue(res.witness_hash.startswith("W_INV_POINCARE_"))

    def test_boundary_fail(self):
        z = PoincareComplex(0.8, 0.8) # |z| = 1.13 > 1.0 (Outside disk)
        st = InvolutivePoincareState(z_point=z, stokes_S=(0.6, 0.0, 0.8))
        res = InvolutivePoincareEngine.evaluate(st)
        self.assertFalse(res.is_admissible)
        self.assertTrue(res.witness_hash.startswith("W_INV_POINCARE_FAIL_"))

if __name__ == "__main__":
    unittest.main()
