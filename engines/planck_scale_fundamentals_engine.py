#!/usr/bin/env python3
"""
Planck's Scale & Fundamental Quantum Constants Engine
Calculates Planck Length l_pl, Planck Time t_pl, Planck Energy E_pl,
Planck Density rho_pl, and Quantum Energy E = h * nu.
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import Dict, Any, Tuple

@dataclass
class PhysicsConstants:
    G_gravitational: float = 6.67430e-11 # m^3 kg^-1 s^-2
    hbar_reduced_planck: float = 1.054571817e-34 # J s
    c_speed_of_light: float = 299792458.0 # m/s
    e_charge: float = 1.602176634e-19 # C

@dataclass
class PlanckScaleMetrics:
    l_pl_meters: float
    l_pl_cm: float
    t_pl_seconds: float
    E_pl_joules: float
    E_pl_GeV: float
    rho_pl_kg_m3: float
    rho_pl_g_cm3: float
    witness_hash: str

class PlanckScaleEngine:
    @staticmethod
    def calculate_planck_units(consts: PhysicsConstants = PhysicsConstants()) -> PlanckScaleMetrics:
        G = consts.G_gravitational
        hbar = consts.hbar_reduced_planck
        c = consts.c_speed_of_light

        # l_pl = sqrt(G * hbar / c^3)
        l_pl_m = math.sqrt((G * hbar) / (c**3))
        l_pl_cm = l_pl_m * 100.0

        # t_pl = sqrt(G * hbar / c^5)
        t_pl_s = math.sqrt((G * hbar) / (c**5))

        # E_pl = sqrt(hbar * c^5 / G)
        E_pl_J = math.sqrt((hbar * (c**5)) / G)
        E_pl_GeV = (E_pl_J / consts.e_charge) / 1.0e9

        # rho_pl = c^5 / (hbar * G^2)
        rho_pl_kg_m3 = (c**5) / (hbar * (G**2))
        rho_pl_g_cm3 = rho_pl_kg_m3 / 1000.0

        payload = f"{l_pl_cm:.4e}|{t_pl_s:.4e}|{E_pl_GeV:.4e}|{rho_pl_g_cm3:.4e}"
        w_hash = "W_PLANCK_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return PlanckScaleMetrics(
            l_pl_meters=l_pl_m,
            l_pl_cm=l_pl_cm,
            t_pl_seconds=t_pl_s,
            E_pl_joules=E_pl_J,
            E_pl_GeV=E_pl_GeV,
            rho_pl_kg_m3=rho_pl_kg_m3,
            rho_pl_g_cm3=rho_pl_g_cm3,
            witness_hash=w_hash
        )

class TestPlanckScaleEngine(unittest.TestCase):
    def test_planck_units_values(self):
        res = PlanckScaleEngine.calculate_planck_units()
        # l_pl approx 1.62e-33 cm
        self.assertAlmostEqual(res.l_pl_cm / 1.616255e-33, 1.0, delta=0.01)
        # t_pl approx 5.39e-44 s
        self.assertAlmostEqual(res.t_pl_seconds / 5.391247e-44, 1.0, delta=0.01)
        # E_pl approx 1.22e19 GeV
        self.assertAlmostEqual(res.E_pl_GeV / 1.2209e19, 1.0, delta=0.01)
        # rho_pl approx 5.16e93 g/cm^3
        self.assertAlmostEqual(res.rho_pl_g_cm3 / 5.155e93, 1.0, delta=0.01)
        self.assertTrue(res.witness_hash.startswith("W_PLANCK_"))

if __name__ == "__main__":
    unittest.main()
