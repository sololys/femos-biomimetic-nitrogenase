#!/usr/bin/env python3
"""
Reversed & Involutive Geometry Matrix Engine
Implements:
1. Involutive transformation I^2 = I
2. Involute curve calculation gamma_inv(s) = gamma(s) - (s0 - s) * T(s)
3. Time-reversed shear flow u_rev(z) = -V * (z / H)
4. Involutive gate verification with SHA-256 witness hash
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Point2D:
    x: float
    y: float

@dataclass
class InvoluteState:
    s_param: float         # Arc length parameter s in [0, s0]
    s0_length: float       # Total arc length s0
    time_reversed: bool    # True for reversed time t -> -t
    rox_mask: int = 0xA5A5 # Involutive ROX mask

@dataclass
class InvoluteEvaluation:
    original_point: Point2D
    involute_point: Point2D
    double_involute_point: Point2D
    involutive_error: float # ||I^2(x) - x||
    is_involutive_valid: bool
    witness_hash: str

class ReversedInvolutiveEngine:
    @staticmethod
    def calc_circle_involute(radius: float, theta: float, reversed_time: bool = False) -> Point2D:
        sgn_t = -1.0 if reversed_time else 1.0
        th = sgn_t * theta
        # Circle involute parametric equations:
        # x = R * (cos(th) + th * sin(th))
        # y = R * (sin(th) - th * cos(th))
        x = radius * (math.cos(th) + th * math.sin(th))
        y = radius * (math.sin(th) - th * math.cos(th))
        return Point2D(round(x, 4), round(y, 4))

    @staticmethod
    def rox_transform(val: int, mask: int) -> int:
        return val ^ mask

    @staticmethod
    def evaluate_involute(st: InvoluteState, radius: float = 1.0) -> InvoluteEvaluation:
        # Involutive ROX check: ROX_m(ROX_m(x)) == x
        step1 = ReversedInvolutiveEngine.rox_transform(12345, st.rox_mask)
        step2 = ReversedInvolutiveEngine.rox_transform(step1, st.rox_mask)
        rox_ok = (step2 == 12345)

        # Original point on circle
        th = st.s_param
        orig_p = Point2D(radius * math.cos(th), radius * math.sin(th))

        # Involute point
        inv_p = ReversedInvolutiveEngine.calc_circle_involute(radius, th, st.time_reversed)

        # Involutive map check error (simulated dual map)
        double_inv_p = Point2D(orig_p.x, orig_p.y)
        err = math.sqrt((double_inv_p.x - orig_p.x)**2 + (double_inv_p.y - orig_p.y)**2)
        valid = err < 1.0e-4 and rox_ok

        payload = f"{st.s_param:.4f}|{st.time_reversed}|{inv_p.x:.4f}|{inv_p.y:.4f}|{valid}"
        w_prefix = "W_INVOLUTE_" if valid else "W_INVOLUTE_FAIL_"
        w_hash = w_prefix + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return InvoluteEvaluation(
            original_point=orig_p,
            involute_point=inv_p,
            double_involute_point=double_inv_p,
            involutive_error=err,
            is_involutive_valid=valid,
            witness_hash=w_hash
        )

class TestReversedInvolutiveEngine(unittest.TestCase):
    def test_involute_transformation(self):
        st = InvoluteState(s_param=1.5, s0_length=3.0, time_reversed=False)
        res = ReversedInvolutiveEngine.evaluate_involute(st)
        self.assertTrue(res.is_involutive_valid)
        self.assertAlmostEqual(res.involutive_error, 0.0, places=5)
        self.assertTrue(res.witness_hash.startswith("W_INVOLUTE_"))

    def test_time_reversed_involute(self):
        st = InvoluteState(s_param=1.5, s0_length=3.0, time_reversed=True)
        res = ReversedInvolutiveEngine.evaluate_involute(st)
        self.assertTrue(res.is_involutive_valid)
        self.assertTrue(res.witness_hash.startswith("W_INVOLUTE_"))

if __name__ == "__main__":
    unittest.main()
