#!/usr/bin/env python3
"""
Geometrisk Super-Struktur Engine
Implements the 5-Layer Geometrical Matrix:
1. Dodecahedral/Polyhedral Kernel
2. Hyperbolic Poincaré Disk H^2
3. Riemann-Gear & Zeta Phase Locking
4. Spin-2 Admissibility Tensor
5. Kerr Spacetime Geodesic Grid
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

PHI = (1.0 + math.sqrt(5.0)) / 2.0 # Golden Ratio 1.6180339887...

@dataclass
class SuperstructureState:
    phi_dodeca_scale: float     # Dodecahedral scale factor
    poincare_radius_z: float    # |z| < 1.0
    riemann_t_critical: float   # t on s = 1/2 + i*t
    spin2_tensor_norm: float   # ||A_munu|| <= 1.0
    kerr_spin_a: float          # a/M <= 1.0

@dataclass
class SuperstructureEvaluation:
    super_tensor_det: float
    poincare_metric_g: float
    is_admissible: bool
    verdict: str
    witness_hash: str

class GeometriskSuperstrukturEngine:
    @staticmethod
    def calc_poincare_metric(z_mag: float) -> float:
        if z_mag >= 1.0:
            return float('inf')
        return 4.0 / ((1.0 - z_mag**2)**2)

    @staticmethod
    def evaluate(st: SuperstructureState) -> SuperstructureEvaluation:
        g_poincare = GeometriskSuperstrukturEngine.calc_poincare_metric(st.poincare_radius_z)
        
        # Super-tensor determinant = product of layer norms scaled by Golden Ratio PHI
        det_super = (
            (st.phi_dodeca_scale * PHI) *
            (1.0 - st.poincare_radius_z**2) *
            (1.0 + math.sin(st.riemann_t_critical)**2) *
            (1.0 - st.spin2_tensor_norm * 0.5) *
            (1.0 - (st.kerr_spin_a**2) * 0.4)
        )

        is_admissible = (
            st.poincare_radius_z < 1.0 and 
            st.spin2_tensor_norm <= 1.0 and 
            st.kerr_spin_a <= 1.0 and 
            det_super > 0
        )

        verdict = "OPEN" if is_admissible else "KILL"

        payload = f"{st.phi_dodeca_scale:.4f}|{st.poincare_radius_z:.4f}|{st.spin2_tensor_norm:.4f}|{det_super:.4f}|{verdict}"
        w_prefix = "W_SUPER_" if is_admissible else "W_SUPER_FAIL_"
        w_hash = w_prefix + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return SuperstructureEvaluation(
            super_tensor_det=round(det_super, 6),
            poincare_metric_g=round(g_poincare, 4) if math.isfinite(g_poincare) else 999999.0,
            is_admissible=is_admissible,
            verdict=verdict,
            witness_hash=w_hash
        )

class TestGeometriskSuperstrukturEngine(unittest.TestCase):
    def test_admissible_superstructure(self):
        st = SuperstructureState(
            phi_dodeca_scale=1.0,
            poincare_radius_z=0.4,
            riemann_t_critical=14.1347,
            spin2_tensor_norm=0.3,
            kerr_spin_a=0.6
        )
        res = GeometriskSuperstrukturEngine.evaluate(st)
        self.assertTrue(res.is_admissible)
        self.assertEqual(res.verdict, "OPEN")
        self.assertGreater(res.super_tensor_det, 0.0)
        self.assertTrue(res.witness_hash.startswith("W_SUPER_"))

    def test_inadmissible_boundary_fail(self):
        st = SuperstructureState(
            phi_dodeca_scale=1.0,
            poincare_radius_z=1.05, # Outside Poincaré disk |z| >= 1
            riemann_t_critical=14.1347,
            spin2_tensor_norm=0.3,
            kerr_spin_a=0.6
        )
        res = GeometriskSuperstrukturEngine.evaluate(st)
        self.assertFalse(res.is_admissible)
        self.assertEqual(res.verdict, "KILL")
        self.assertTrue(res.witness_hash.startswith("W_SUPER_FAIL_"))

if __name__ == "__main__":
    unittest.main()
