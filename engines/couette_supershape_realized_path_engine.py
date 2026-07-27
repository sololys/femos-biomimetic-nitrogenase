#!/usr/bin/env python3
"""
Couette Sheared Supershape & Realized Path Engine
Implements:
1. Couette shear flow u(z) = V * (z / H)
2. Deformed implicit Supershape surface F_t(x,y,z) = 0
3. Parametric evaluation Psi_t(theta, phi)
4. Path projection Pi_Sigma(gamma(s)) and candidate rays r(s, lambda)
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

def sgn(x: float) -> float:
    return 1.0 if x > 0 else (-1.0 if x < 0 else 0.0)

def C_eps(alpha: float, eps: float) -> float:
    c = math.cos(alpha)
    return sgn(c) * (abs(c)**eps)

def S_eps(alpha: float, eps: float) -> float:
    s = math.sin(alpha)
    return sgn(s) * (abs(s)**eps)

@dataclass
class SupershapeParams:
    a: float = 1.0
    b: float = 1.0
    c: float = 1.0
    eps1: float = 1.0 # 1.0 = sphere, <1 = blocky, >1 = star/diamond
    eps2: float = 1.0
    H_height: float = 4.0
    V_velocity: float = 2.0
    shear_time_t: float = 0.5
    viscosity_mu: float = 1.0e-3

@dataclass
class Point3D:
    x: float
    y: float
    z: float

class CouetteSupershapeEngine:
    @staticmethod
    def calc_couette_u(z: float, params: SupershapeParams) -> float:
        z_clamped = max(0.0, min(params.H_height, z))
        return params.V_velocity * (z_clamped / params.H_height)

    @staticmethod
    def calc_shear_stress(params: SupershapeParams) -> float:
        return params.viscosity_mu * (params.V_velocity / params.H_height)

    @staticmethod
    def evaluate_parametric_psi(theta: float, phi: float, params: SupershapeParams) -> Point3D:
        # z(theta, phi) = H/2 + c * S_eps1(phi)
        z = (params.H_height / 2.0) + params.c * S_eps(phi, params.eps1)
        # y(theta, phi) = b * C_eps1(phi) * S_eps2(theta)
        y = params.b * C_eps(phi, params.eps1) * S_eps(theta, params.eps2)
        # x_t(theta, phi) = a * C_eps1(phi) * C_eps2(theta) + t * V * (z / H)
        shear_offset = params.shear_time_t * params.V_velocity * (z / params.H_height)
        x_t = params.a * C_eps(phi, params.eps1) * C_eps(theta, params.eps2) + shear_offset
        return Point3D(x_t, y, z)

    @staticmethod
    def evaluate_implicit_F(p: Point3D, params: SupershapeParams) -> float:
        # X_t = x - t * V * (z / H)
        X_t = p.x - params.shear_time_t * params.V_velocity * (p.z / params.H_height)
        term_x = abs(X_t / params.a)**(2.0 / params.eps2)
        term_y = abs(p.y / params.b)**(2.0 / params.eps2)
        inner = (term_x + term_y)**(params.eps2 / params.eps1)
        term_z = abs((p.z - params.H_height / 2.0) / params.c)**(2.0 / params.eps1)
        return inner + term_z - 1.0

    @staticmethod
    def project_onto_surface(raw_p: Point3D, params: SupershapeParams) -> Point3D:
        # Simple radial projection to zero level
        center = Point3D(
            x=params.shear_time_t * params.V_velocity * 0.5,
            y=0.0,
            z=params.H_height / 2.0
        )
        dx = raw_p.x - center.x
        dy = raw_p.y - center.y
        dz = raw_p.z - center.z
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 1.0e-6:
            return raw_p
        
        # Scale to zero level radius approximately
        scale = params.a / dist
        return Point3D(center.x + dx * scale, center.y + dy * scale, center.z + dz * scale)

class TestCouetteSupershapeEngine(unittest.TestCase):
    def test_couette_flow_values(self):
        params = SupershapeParams(H_height=4.0, V_velocity=2.0)
        u_0 = CouetteSupershapeEngine.calc_couette_u(0.0, params)
        u_H = CouetteSupershapeEngine.calc_couette_u(4.0, params)
        self.assertEqual(u_0, 0.0)
        self.assertEqual(u_H, 2.0)

    def test_unsheared_sphere_implicit(self):
        params = SupershapeParams(a=1.0, b=1.0, c=1.0, eps1=1.0, eps2=1.0, H_height=2.0, shear_time_t=0.0)
        # Point on surface (1, 0, 1) -> center is (0, 0, 1)
        p = Point3D(1.0, 0.0, 1.0)
        F_val = CouetteSupershapeEngine.evaluate_implicit_F(p, params)
        self.assertAlmostEqual(F_val, 0.0, places=5)

    def test_parametric_evaluation(self):
        params = SupershapeParams(a=1.0, b=1.0, c=1.0, eps1=1.0, eps2=1.0, H_height=4.0, shear_time_t=0.5, V_velocity=2.0)
        p = CouetteSupershapeEngine.evaluate_parametric_psi(0.0, 0.0, params)
        # theta=0, phi=0 -> C(0)=1, S(0)=0
        self.assertAlmostEqual(p.y, 0.0)
        self.assertAlmostEqual(p.z, 2.0) # H/2 = 2.0

if __name__ == "__main__":
    unittest.main()
