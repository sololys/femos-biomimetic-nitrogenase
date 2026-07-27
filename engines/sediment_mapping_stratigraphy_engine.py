#!/usr/bin/env python3
"""
Sediment Mapping & Stratigraphic Dynamics Engine
Simulates Stokes settling velocity v_s, Shields erosion parameter tau_star,
and stratigraphic layer mapping [Leire/Støv, Silt/Kalk, Sand/Grus, Berggrunn].
"""

import math
import hashlib
import unittest
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

@dataclass
class SedimentParticle:
    name: str
    diameter_m: float  # d_p in meters
    density_kg_m3: float # rho_p e.g. 2650 kg/m^3 (quartz)

@dataclass
class FluidFlowState:
    fluid_density: float = 1000.0  # rho_f kg/m^3 (water)
    viscosity_mu: float = 1.0e-3    # Pa s
    wall_velocity_V: float = 1.0     # m/s
    channel_height_H: float = 0.01  # m
    gravity_g: float = 9.81         # m/s^2

@dataclass
class SedimentEvaluation:
    particle_name: str
    settling_velocity_vs: float # m/s
    shear_stress_tau: float     # Pa
    shields_parameter_tau_star: float
    stratigraphic_layer: str
    erosion_active: bool
    witness_hash: str

class SedimentMappingEngine:
    SHIELDS_CRITICAL = 0.045 # Critical Shields parameter for motion onset

    @staticmethod
    def calc_stokes_velocity(p: SedimentParticle, f: FluidFlowState) -> float:
        # v_s = g * (rho_p - rho_f) * d_p^2 / (18 * mu)
        delta_rho = p.density_kg_m3 - f.fluid_density
        return (f.gravity_g * delta_rho * (p.diameter_m**2)) / (18.0 * f.viscosity_mu)

    @staticmethod
    def calc_shields_parameter(p: SedimentParticle, f: FluidFlowState) -> Tuple[float, float]:
        # tau_w = mu * (V / H)
        tau_w = f.viscosity_mu * (f.wall_velocity_V / f.channel_height_H)
        delta_rho = p.density_kg_m3 - f.fluid_density
        tau_star = tau_w / (delta_rho * f.gravity_g * p.diameter_m)
        return tau_w, tau_star

    @staticmethod
    def evaluate_sediment(p: SedimentParticle, f: FluidFlowState = FluidFlowState()) -> SedimentEvaluation:
        v_s = SedimentMappingEngine.calc_stokes_velocity(p, f)
        tau_w = f.viscosity_mu * (f.wall_velocity_V / f.channel_height_H)
        delta_rho = p.density_kg_m3 - f.fluid_density
        tau_star = tau_w / (delta_rho * f.gravity_g * p.diameter_m)

        erosion = tau_star > SedimentMappingEngine.SHIELDS_CRITICAL

        # Stratigraphic classification based on particle diameter
        if p.diameter_m < 2.0e-6:
            layer = "Lag 1: LEIRE / STØV (< 2 µm)"
        elif p.diameter_m <= 63.0e-6:
            layer = "Lag 2: SILT / KALK (2 - 63 µm)"
        elif p.diameter_m <= 2.0e-3:
            layer = "Lag 3: SAND / GRUS (63 µm - 2 mm)"
        else:
            layer = "Lag 4: BERGGRUNN / STABIL MATRIX (> 2 mm)"

        payload = f"{p.name}|{p.diameter_m:.4e}|{v_s:.4e}|{tau_star:.4f}|{erosion}"
        w_hash = "W_SEDIMENT_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return SedimentEvaluation(
            particle_name=p.name,
            settling_velocity_vs=round(v_s, 6),
            shear_stress_tau=round(tau_w, 6),
            shields_parameter_tau_star=round(tau_star, 4),
            stratigraphic_layer=layer,
            erosion_active=erosion,
            witness_hash=w_hash
        )

class TestSedimentMappingEngine(unittest.TestCase):
    def test_sand_sediment_evaluation(self):
        p = SedimentParticle("Kvarts-Sand", diameter_m=200.0e-6, density_kg_m3=2650.0) # 200 µm sand
        res = SedimentMappingEngine.evaluate_sediment(p)
        self.assertGreater(res.settling_velocity_vs, 0.0)
        self.assertIn("Lag 3: SAND / GRUS", res.stratigraphic_layer)
        self.assertTrue(res.witness_hash.startswith("W_SEDIMENT_"))

    def test_clay_suspension(self):
        p = SedimentParticle("Leire-Partikkel", diameter_m=1.0e-6, density_kg_m3=2600.0) # 1 µm clay
        res = SedimentMappingEngine.evaluate_sediment(p)
        self.assertLess(res.settling_velocity_vs, 0.001)
        self.assertIn("Lag 1: LEIRE / STØV", res.stratigraphic_layer)

if __name__ == "__main__":
    unittest.main()
