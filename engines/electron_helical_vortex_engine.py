#!/usr/bin/env python3
"""
Helical Vortical Electron Orbit & Quantum Force Engine — Production Reference
Implements electron 3D helical orbit under F_quantum = (h/c^3) (v x a):
- Nucleus (Proton) at origin r = 0 (Red sphere)
- Electron Trajectory (Blue line) with Bohr radius a0 = 0.529177 Angstroms
- Zitterbewegung Path (Green dots) with Compton amplitude R_z = 0.50 * hbar / (2 m_e c)
- Microscopic Vorticity v x a & Quantized Axial Advance (Jerk direction a)
- Dynamic Regimes: HELICAL_PHASE_LOCK (OPEN), ZITTER_BUFFER (HOLD), COLLAPSE_KILL (KILL)
"""

import numpy as np
import hashlib
import json
import unittest
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Dict, Any

# PHYSICAL CONSTANTS
H_PLANCK = 6.62607015e-34       # J s
H_BAR = H_PLANCK / (2.0 * np.pi) # J s
C_SPEED = 2.99792458e8          # m/s
M_ELECTRON = 9.1093837015e-31   # kg
A0_BOHR = 0.529177210903e-10    # m

# Compton Zitterbewegung Amplitude: R_z = 0.50 * hbar / (2 m_e c)
R_ZITTER_COMPTON = 0.50 * (H_BAR / (2.0 * M_ELECTRON * C_SPEED))

class GateVerdict(Enum):
    KILL = 0
    HOLD = 1
    OPEN = 2

class HelicalRegime(Enum):
    HELICAL_PHASE_LOCK = "HELICAL_PHASE_LOCK"
    ZITTER_BUFFER = "ZITTER_BUFFER"
    COLLAPSE_KILL = "COLLAPSE_KILL"

@dataclass
class HelicalElectronReceipt:
    verdict: GateVerdict
    regime: HelicalRegime
    position_bohr: Tuple[float, float, float]
    velocity_mps: Tuple[float, float, float]
    acceleration_mps2: Tuple[float, float, float]
    quantum_force_N: float
    zitterbewegung_freq_rad_s: float
    vorticity_magnitude: float
    witness_hash: str

# ==========================================
# ⚛️ HELICAL ELECTRON VORTEX ENGINE
# ==========================================
class ElectronHelicalVortexEngine:
    def __init__(self, prev_worm_hash: str = "GENESIS_ELECTRON_00"):
        self.history_ledger: List[str] = [prev_worm_hash]

    def compute_quantum_force(self, velocity: np.ndarray, acceleration: np.ndarray) -> np.ndarray:
        """ Beregner kvantekraft F_q = (h / c^3) * (v x a) """
        coeff = H_PLANCK / (C_SPEED ** 3)
        vorticity = np.cross(velocity, acceleration)
        return coeff * vorticity

    def compute_zitterbewegung_frequency(self) -> float:
        """ Beregner Zitterbewegung frekvens Omega = 2 m_e c^2 / hbar """
        return float((2.0 * M_ELECTRON * (C_SPEED ** 2)) / H_BAR)

    def simulate_helical_trajectory(self, t: float, zitter_amplitude: float = R_ZITTER_COMPTON) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Simulerer 3D helisk bane r(t), hastighet v(t), og akselerasjon a(t):
        - r_bohr = (a0 * cos(w0*t), a0 * sin(w0*t), v_z * t)
        - r_zitter = R_z * (cos(Omega*t), sin(Omega*t), 0.5 * sin(2*Omega*t))
        """
        w0 = 4.13413733e16 # Bohr vinkelfrekvens (rad/s)
        v_z = 1.0e5       # Helisk aksial hastighet (m/s)
        Omega = self.compute_zitterbewegung_frequency()

        # Bohr makro-bane
        r_bohr = np.array([
            A0_BOHR * np.cos(w0 * t),
            A0_BOHR * np.sin(w0 * t),
            v_z * t
        ])

        # Zitterbewegung mikro-svingninger
        r_zitter = zitter_amplitude * np.array([
            np.cos(Omega * t),
            np.sin(Omega * t),
            0.5 * np.sin(2.0 * Omega * t)
        ])

        r_total = r_bohr + r_zitter

        # Deriverte (hastighet & akselerasjon)
        v_bohr = np.array([
            -A0_BOHR * w0 * np.sin(w0 * t),
            A0_BOHR * w0 * np.cos(w0 * t),
            v_z
        ])
        v_zitter = zitter_amplitude * Omega * np.array([
            -np.sin(Omega * t),
            np.cos(Omega * t),
            np.cos(2.0 * Omega * t)
        ])
        v_total = v_bohr + v_zitter

        a_bohr = np.array([
            -A0_BOHR * (w0**2) * np.cos(w0 * t),
            -A0_BOHR * (w0**2) * np.sin(w0 * t),
            0.0
        ])
        a_zitter = zitter_amplitude * (Omega**2) * np.array([
            -np.cos(Omega * t),
            -np.sin(Omega * t),
            -2.0 * np.sin(2.0 * Omega * t)
        ])
        a_total = a_bohr + a_zitter

        return r_total, v_total, a_total

    def evaluate_engine(self, t: float = 0.0) -> HelicalElectronReceipt:
        """ Evaluerer helisk elektronbane, kvantekraft F_q og WORM-forsegler """
        r, v, a = self.simulate_helical_trajectory(t)
        F_q = self.compute_quantum_force(v, a)
        Omega = self.compute_zitterbewegung_frequency()
        vorticity = np.cross(v, a)
        vort_mag = float(np.linalg.norm(vorticity))
        fq_mag = float(np.linalg.norm(F_q))

        r_xy_mag = np.linalg.norm(r[:2])
        rel_diff = abs(r_xy_mag - A0_BOHR) / A0_BOHR

        if rel_diff < 0.15 and np.linalg.norm(v) < C_SPEED:
            regime = HelicalRegime.HELICAL_PHASE_LOCK
            verdict = GateVerdict.OPEN
        elif rel_diff < 0.35:
            regime = HelicalRegime.ZITTER_BUFFER
            verdict = GateVerdict.HOLD
        else:
            regime = HelicalRegime.COLLAPSE_KILL
            verdict = GateVerdict.KILL

        witness = "REJECTED"
        if verdict == GateVerdict.OPEN:
            payload = f"{r[0]:.6e}|{r[1]:.6e}|{fq_mag:.6e}|{vort_mag:.6e}|{self.history_ledger[-1]}"
            witness = "WORM_ELECTRON_" + hashlib.sha256(payload.encode()).hexdigest()[:16].upper()
            self.history_ledger.append(witness)

        return HelicalElectronReceipt(
            verdict,
            regime,
            (float(r[0]/A0_BOHR), float(r[1]/A0_BOHR), float(r[2]/A0_BOHR)),
            (float(v[0]), float(v[1]), float(v[2])),
            (float(a[0]), float(a[1]), float(a[2])),
            fq_mag,
            Omega,
            vort_mag,
            witness
        )

# ==========================================
# 🧪 TEST SUITE
# ==========================================
class TestElectronHelicalVortexEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ElectronHelicalVortexEngine()

    def test_zitterbewegung_frequency(self):
        Omega = self.engine.compute_zitterbewegung_frequency()
        self.assertGreater(Omega, 1.5e21)

    def test_quantum_force_calculation(self):
        v = np.array([1e6, 0.0, 0.0])
        a = np.array([0.0, 1e18, 0.0])
        F_q = self.engine.compute_quantum_force(v, a)
        self.assertAlmostEqual(F_q[0], 0.0)
        self.assertAlmostEqual(F_q[1], 0.0)
        self.assertGreater(F_q[2], 0.0)

    def test_engine_admissibility_open(self):
        res = self.engine.evaluate_engine(t=0.0)
        self.assertEqual(res.verdict, GateVerdict.OPEN)
        self.assertEqual(res.regime, HelicalRegime.HELICAL_PHASE_LOCK)
        self.assertTrue(res.witness_hash.startswith("WORM_ELECTRON_"))

def run_audit():
    print("=== Helical Vortical Electron Orbit & Quantum Force Audit ===\n")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestElectronHelicalVortexEngine)
    test_result = unittest.TextTestRunner(verbosity=0).run(suite)
    
    engine = ElectronHelicalVortexEngine()
    r1 = engine.evaluate_engine()

    audit_report = {
        "status_helical_electron": "OPEN_AS_HELICAL_VORTEX_DEMONSTRATOR",
        "status_quantum_force": "OPEN_AS_QUANTUM_FORCE_ZITTERBEWEGUNG_SIMULATOR",
        "tests_passed": f"{test_result.testsRun - len(test_result.failures) - len(test_result.errors)}/{test_result.testsRun}",
        "electron_execution": {
            "regime": r1.regime.value,
            "verdict": r1.verdict.name,
            "position_bohr": r1.position_bohr,
            "quantum_force_N": f"{r1.quantum_force_N:.4e}",
            "zitterbewegung_freq": f"{r1.zitterbewegung_freq_rad_s:.4e} rad/s",
            "vorticity_magnitude": f"{r1.vorticity_magnitude:.4e}",
            "witness": r1.witness_hash
        }
    }

    print("[AUDIT REPORT JSON]")
    print(json.dumps(audit_report, indent=2))

if __name__ == "__main__":
    run_audit()
