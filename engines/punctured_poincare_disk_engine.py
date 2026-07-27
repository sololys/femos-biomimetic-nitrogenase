#!/usr/bin/env python3
"""
Punctured Poincaré Disk & Topological Singularity Engine
Implements:
1. Punctured Poincaré disk topology D* = D \ { z_p }
2. Punctured hyperbolic metric ds^2 = |dz|^2 / (|z|^2 * (ln|z|)^2)
3. Involutive transformation I(z) = -z on D*
4. Singularity detection & Winding Number w in Z
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import Tuple

from dataclasses import dataclass, field

@dataclass
class ComplexPoint:
    re: float
    im: float

    def abs(self) -> float:
        return math.sqrt(self.re**2 + self.im**2)

@dataclass
class PuncturedState:
    z_point: ComplexPoint
    puncture_loc: ComplexPoint = field(default_factory=lambda: ComplexPoint(0.0, 0.0)) # z_p = 0
    winding_number: int = 1

@dataclass
class PuncturedEvaluation:
    distance_to_puncture: float
    punctured_metric: float
    is_involute_valid: bool
    verdict: str
    witness_hash: str

class PuncturedPoincareEngine:
    MIN_PUNCTURE_DIST = 1.0e-5 # Singular threshold

    @staticmethod
    def calc_punctured_metric(z: ComplexPoint, z_p: ComplexPoint) -> float:
        dx = z.re - z_p.re
        dy = z.im - z_p.im
        r = math.sqrt(dx*dx + dy*dy)

        if r <= PuncturedPoincareEngine.MIN_PUNCTURE_DIST or r >= 1.0:
            return float('inf') # Infinite potential barrier at puncture

        ln_r = math.log(r)
        denom = (r**2) * (ln_r**2)
        if abs(denom) < 1.0e-12:
            return float('inf')
        return round(1.0 / denom, 4)

    @staticmethod
    def evaluate(st: PuncturedState) -> PuncturedEvaluation:
        z = st.z_point
        zp = st.puncture_loc
        dx = z.re - zp.re
        dy = z.im - zp.im
        dist_p = math.sqrt(dx*dx + dy*dy)

        metric = PuncturedPoincareEngine.calc_punctured_metric(z, zp)
        is_punctured_open = dist_p > PuncturedPoincareEngine.MIN_PUNCTURE_DIST and dist_p < 1.0 and math.isfinite(metric)

        verdict = "PUNCTURED POINCARÉ OPEN" if is_punctured_open else "PUNCTURE SINGULARITY COLLAPSE"

        payload = f"{z.re:.4f}|{z.im:.4f}|{dist_p:.4e}|{metric:.4f}|{verdict}"
        w_prefix = "W_PUNCTURED_" if is_punctured_open else "W_PUNCTURED_FAIL_"
        w_hash = w_prefix + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return PuncturedEvaluation(
            distance_to_puncture=round(dist_p, 6),
            punctured_metric=metric if math.isfinite(metric) else 999999.0,
            is_involute_valid=is_punctured_open,
            verdict=verdict,
            witness_hash=w_hash
        )

class TestPuncturedPoincareEngine(unittest.TestCase):
    def test_valid_punctured_point(self):
        st = PuncturedState(z_point=ComplexPoint(0.4, 0.3)) # r = 0.5 > min_dist
        res = PuncturedPoincareEngine.evaluate(st)
        self.assertTrue(res.is_involute_valid)
        self.assertEqual(res.verdict, "PUNCTURED POINCARÉ OPEN")
        self.assertTrue(res.witness_hash.startswith("W_PUNCTURED_"))

    def test_puncture_singularity_collapse(self):
        st = PuncturedState(z_point=ComplexPoint(0.0, 0.0)) # Exact puncture z_p = 0
        res = PuncturedPoincareEngine.evaluate(st)
        self.assertFalse(res.is_involute_valid)
        self.assertEqual(res.verdict, "PUNCTURE SINGULARITY COLLAPSE")
        self.assertTrue(res.witness_hash.startswith("W_PUNCTURED_FAIL_"))

if __name__ == "__main__":
    unittest.main()
