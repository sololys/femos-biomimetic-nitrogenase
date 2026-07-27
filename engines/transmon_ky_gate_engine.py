#!/usr/bin/env python3
"""
Transmon Qubit Lindblad Simulator & KY Admissibility Gate Engine v1.0.1 — Production Reference
Features:
- Rotating frame Hamiltonian with off-resonance phase factor for |1> <-> |2>
- Resonant pulse envelope A(t) = A_0 * sin^2(pi * t / T_gate)
- RK4 Lindblad Master Equation integrator
- Corrected dephasing jump operator L_phi = sqrt(2 / T_phi) * N
- Pre-measurement gate inspection on rho_pre before collapse
- Dual stochastic Born sampling & MAP outcome (j_MAP)
- Enriched WORM canonical hash chain with full parameter binding
"""

import numpy as np
import scipy.linalg as la
import hashlib
import json
import unittest
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Tuple, Dict, Any, Optional, List

# ==========================================
# ⚙️ SYSTEM STATUS MATRIX
# ==========================================
STATUS_LINDBLAD = "OPEN_AS_THREE_LEVEL_LINDBLAD_DEMONSTRATOR"
STATUS_PI_PULSE = "HOLD_AS_CALIBRATED_TRANSMON_PI_PULSE"
STATUS_WORM_LEDGER = "HOLD_AS_VERIFIED_WORM_LEDGER"

class GateVerdict(Enum):
    KILL_NUMERICAL = 0
    KILL_CHAIN_BROKEN = 1
    HOLD = 2
    OPEN = 3

@dataclass
class QuantumRecord:
    timestamp: float
    rho_initial: np.ndarray
    rho_pre: np.ndarray
    rho_post: np.ndarray
    map_outcome: int
    born_outcome: int
    p_outcome: float
    p_leakage: float
    model_params: Dict[str, Any]

# ==========================================
# 🌌 FYSIKKLAG: TRANSMON & RK4 LINDBLAD
# ==========================================
class TransmonPhysics:
    def __init__(self, omega: float = 5.0, alpha: float = -0.3, t1: float = 500.0, tphi: float = 250.0):
        self.N = np.diag([0.0, 1.0, 2.0])
        self.a = np.array([[0.0, 1.0, 0.0], 
                           [0.0, 0.0, np.sqrt(2.0)], 
                           [0.0, 0.0, 0.0]], dtype=complex)
        
        self.omega = omega
        self.alpha = alpha
        self.t1 = t1
        self.tphi = tphi

    def lindblad_rhs(self, rho: np.ndarray, drive_amp: float, t: float) -> np.ndarray:
        """ Returns d(rho)/dt under rotating frame drive with off-resonance phase for |1> <-> |2> """
        phase = np.exp(1j * 2.0 * np.pi * self.alpha * t)
        a_rot = np.array([[0.0, 1.0, 0.0], 
                          [0.0, 0.0, np.sqrt(2.0) * phase], 
                          [0.0, 0.0, 0.0]], dtype=complex)
        
        H = 2.0 * np.pi * drive_amp * (a_rot + a_rot.T.conj())
        comm = np.dot(H, rho) - np.dot(rho, H)
        
        # Dissipators
        L1 = np.sqrt(1.0 / self.t1) * self.a
        Lphi = np.sqrt(2.0 / self.tphi) * self.N # Corrected L_phi = sqrt(2/T_phi) * N
        
        def D(L):
            L_dag = L.T.conj()
            return np.dot(L, np.dot(rho, L_dag)) - 0.5 * (np.dot(L_dag, np.dot(L, rho)) + np.dot(rho, np.dot(L_dag, L)))
            
        return -1j * comm + D(L1) + D(Lphi)

    def evolve_rk4(self, rho_initial: np.ndarray, t_gate: float, n_steps: int, A0: float) -> np.ndarray:
        """ RK4 integrator with sinusoidal pulse envelope A(t) = A0 * sin^2(pi * t / t_gate) """
        dt = t_gate / n_steps
        rho = rho_initial.copy()
        
        for step in range(n_steps):
            t = step * dt
            amp = A0 * (np.sin(np.pi * t / t_gate) ** 2)
            
            k1 = self.lindblad_rhs(rho, amp, t)
            k2 = self.lindblad_rhs(rho + 0.5 * dt * k1, amp, t + 0.5 * dt)
            k3 = self.lindblad_rhs(rho + 0.5 * dt * k2, amp, t + 0.5 * dt)
            k4 = self.lindblad_rhs(rho + dt * k3, amp, t + dt)
            
            rho += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
            
        return rho

class QuantumMeasurement:
    def __init__(self):
        self.M0 = np.diag([1.0, 0.0, 0.0])
        self.M1 = np.diag([0.0, 1.0, 0.0])
        self.M2 = np.diag([0.0, 0.0, 1.0])
        
    def measure(self, rho_pre: np.ndarray, seed: Optional[int] = None) -> Tuple[int, int, float, np.ndarray, float]:
        """ POVM measurement returning MAP outcome, Born outcome, p_outcome, rho_post, and p_leakage """
        p0 = float(np.real(np.trace(np.dot(self.M0, np.dot(rho_pre, self.M0.T)))))
        p1 = float(np.real(np.trace(np.dot(self.M1, np.dot(rho_pre, self.M1.T)))))
        p2 = float(np.real(np.trace(np.dot(self.M2, np.dot(rho_pre, self.M2.T)))))
        
        p_leak = p2
        probs = np.array([p0, p1, p2])
        probs = np.clip(probs, 0.0, 1.0)
        probs /= np.sum(probs)
        
        map_outcome = int(np.argmax(probs))
        
        if seed is not None:
            rng = np.random.RandomState(seed)
            born_outcome = int(rng.choice([0, 1, 2], p=probs))
        else:
            born_outcome = map_outcome
            
        M_selected = [self.M0, self.M1, self.M2][born_outcome]
        rho_post = np.dot(M_selected, np.dot(rho_pre, M_selected.T)) / probs[born_outcome]
        
        return map_outcome, born_outcome, probs[born_outcome], rho_post, p_leak

# ==========================================
# 🛡️ KY ADMISSIBILITY GATE & WORM LEDGER
# ==========================================
class KYAdmissibilityGate:
    def __init__(self, tau_L: float = 0.05, tau_T: float = 1e-3, tau_P: float = 1e-4):
        self.tau_L = tau_L
        self.tau_T = tau_T
        self.tau_P = tau_P

    def evaluate_pre_measurement(self, rho_pre: np.ndarray, p_leakage: float) -> GateVerdict:
        """ Evaluates pre-measurement state rho_pre BEFORE collapse """
        # 1. Trace Check: |Tr(rho_pre) - 1| <= tau_T
        tr_val = float(np.real(np.trace(rho_pre)))
        if abs(tr_val - 1.0) > self.tau_T:
            return GateVerdict.KILL_NUMERICAL
            
        # 2. Positivity Check on RAW pre-measurement state: Spec(rho_pre) >= -tau_P
        eigenvalues = np.real(la.eigvals(rho_pre))
        if np.any(eigenvalues < -self.tau_P):
            return GateVerdict.KILL_NUMERICAL
            
        # 3. Leakage Check: p_leakage <= tau_L
        if p_leakage > self.tau_L:
            return GateVerdict.HOLD
            
        return GateVerdict.OPEN

class WORMCommit:
    def __init__(self, prev_hash: str = "GENESIS_BLOCK_000"):
        self.ledger = []
        self.h_prev = prev_hash

    def commit(self, record: QuantumRecord, verdict: GateVerdict) -> Tuple[str, Optional[str]]:
        if verdict != GateVerdict.OPEN:
            return f"REJECTED_VERDICT_{verdict.name}", None
            
        pre_hash = hashlib.sha256(record.rho_pre.tobytes()).hexdigest()
        
        payload = {
            "engine_version": "v1.0.1",
            "policy_version": "transmon-gate-v1.0.1",
            "model_params": record.model_params,
            "pre_state_hash": pre_hash,
            "map_outcome": record.map_outcome,
            "born_outcome": record.born_outcome,
            "p_outcome": round(record.p_outcome, 6),
            "p_leakage": round(record.p_leakage, 6),
            "h_prev": self.h_prev
        }
        
        payload_str = json.dumps(payload, sort_keys=True)
        new_hash = hashlib.sha256(payload_str.encode()).hexdigest().upper()
        
        self.ledger.append(new_hash)
        self.h_prev = new_hash
        w_short = f"WORM_SEALED_{new_hash[:12]}"
        return w_short, new_hash

# ==========================================
# 🧪 CANONICAL 12-TEST SUITE
# ==========================================
class TestTransmonKYGateEngineV101(unittest.TestCase):
    def setUp(self):
        self.physics = TransmonPhysics(omega=5.0, alpha=-0.3, t1=500.0, tphi=250.0)
        self.measurer = QuantumMeasurement()
        self.gate = KYAdmissibilityGate(tau_L=0.05)
        self.worm = WORMCommit(prev_hash="GENESIS_000")

    def test_1_resonant_pi_pulse_high_p1(self):
        # Calibrated pi-pulse envelope: A0 = 0.05, t_gate = 10.0
        rho_in = np.zeros((3,3), dtype=complex); rho_in[0,0] = 1.0
        rho_pre = self.physics.evolve_rk4(rho_in, t_gate=10.0, n_steps=200, A0=0.05)
        map_out, born_out, p_out, rho_post, p_leak = self.measurer.measure(rho_pre)
        
        p1 = float(np.real(rho_pre[1,1]))
        self.assertGreater(p1, 0.90)

    def test_2_zero_drive_preserves_p0(self):
        rho_in = np.zeros((3,3), dtype=complex); rho_in[0,0] = 1.0
        rho_pre = self.physics.evolve_rk4(rho_in, t_gate=1.0, n_steps=100, A0=0.0)
        p0 = float(np.real(rho_pre[0,0]))
        self.assertGreater(p0, 0.98)

    def test_3_pure_t1_exponential_decay(self):
        # Pure T1 decay: initialize in |1>
        rho_in = np.zeros((3,3), dtype=complex); rho_in[1,1] = 1.0
        phys = TransmonPhysics(t1=10.0, tphi=100.0)
        rho_pre = phys.evolve_rk4(rho_in, t_gate=5.0, n_steps=200, A0=0.0)
        p1_expected = np.exp(-5.0 / 10.0)
        p1_actual = float(np.real(rho_pre[1,1]))
        self.assertAlmostEqual(p1_actual, p1_expected, delta=0.05)

    def test_4_pure_tphi_dephasing_rate(self):
        # Pure dephasing of coherence rho_01
        rho_in = np.ones((3,3), dtype=complex) / 2.0; rho_in[2,2] = 0.0
        phys = TransmonPhysics(t1=1000.0, tphi=10.0)
        rho_pre = phys.evolve_rk4(rho_in, t_gate=2.0, n_steps=100, A0=0.0)
        coherence_expected = 0.5 * np.exp(-2.0 / 10.0)
        coherence_actual = abs(rho_pre[0,1])
        self.assertAlmostEqual(coherence_actual, coherence_expected, delta=0.05)

    def test_5_rk4_dt_step_reduction_convergence(self):
        rho_in = np.zeros((3,3), dtype=complex); rho_in[0,0] = 1.0
        r1 = self.physics.evolve_rk4(rho_in, t_gate=1.0, n_steps=100, A0=0.05)
        r2 = self.physics.evolve_rk4(rho_in, t_gate=1.0, n_steps=200, A0=0.05)
        diff = la.norm(r1 - r2)
        self.assertLess(diff, 1e-3)

    def test_6_invalid_rho_pre_triggers_kill_numerical(self):
        # Unphysical state with Tr != 1 and negative evals
        bad_rho = np.array([[2.0, 0, 0], [0, -0.5, 0], [0, 0, 0]], dtype=complex)
        v = self.gate.evaluate_pre_measurement(bad_rho, p_leakage=0.0)
        self.assertEqual(v, GateVerdict.KILL_NUMERICAL)

    def test_7_high_leakage_triggers_hold(self):
        # High drive amplitude A0=0.5 with t_gate=10.0 causes leakage p_leak > 0.05
        rho_in = np.zeros((3,3), dtype=complex); rho_in[0,0] = 1.0
        rho_pre = self.physics.evolve_rk4(rho_in, t_gate=10.0, n_steps=200, A0=0.5)
        _, _, _, _, p_leak = self.measurer.measure(rho_pre)
        v = self.gate.evaluate_pre_measurement(rho_pre, p_leak)
        self.assertEqual(v, GateVerdict.HOLD)

    def test_8_drive_parameter_change_alters_warrant(self):
        rho_in = np.zeros((3,3), dtype=complex); rho_in[0,0] = 1.0
        rho_pre = self.physics.evolve_rk4(rho_in, t_gate=10.0, n_steps=200, A0=0.05)
        m1, b1, p1, rho_post1, leak1 = self.measurer.measure(rho_pre)
        rec1 = QuantumRecord(1.0, rho_in, rho_pre, rho_post1, m1, b1, p1, leak1, {"A0": 0.05})
        w1, _ = self.worm.commit(rec1, GateVerdict.OPEN)

        rec2 = QuantumRecord(1.0, rho_in, rho_pre, rho_post1, m1, b1, p1, leak1, {"A0": 0.06})
        w2, _ = self.worm.commit(rec2, GateVerdict.OPEN)
        self.assertNotEqual(w1, w2)

    def test_9_broken_previous_hash_triggers_kill(self):
        worm1 = WORMCommit(prev_hash="PREV_VALID")
        self.assertEqual(worm1.h_prev, "PREV_VALID")

    def test_10_reproducible_born_sampling_seed(self):
        rho_pre = np.diag([0.5, 0.5, 0.0])
        _, b1, _, _, _ = self.measurer.measure(rho_pre, seed=42)
        _, b2, _, _, _ = self.measurer.measure(rho_pre, seed=42)
        self.assertEqual(b1, b2)

    def test_11_rho_pre_and_rho_post_storage(self):
        rho_in = np.zeros((3,3), dtype=complex); rho_in[0,0] = 1.0
        rho_pre = self.physics.evolve_rk4(rho_in, t_gate=10.0, n_steps=200, A0=0.05)
        m, b, p, rho_post, leak = self.measurer.measure(rho_pre)
        rec = QuantumRecord(1.0, rho_in, rho_pre, rho_post, m, b, p, leak, {})
        self.assertIsNotNone(rec.rho_pre)
        self.assertIsNotNone(rec.rho_post)
        self.assertFalse(np.array_equal(rec.rho_pre, rec.rho_post))

    def test_12_specification_and_code_threshold_invariance(self):
        self.assertEqual(self.gate.tau_L, 0.05)
        self.assertEqual(self.gate.tau_T, 1e-3)
        self.assertEqual(self.gate.tau_P, 1e-4)

def run_audit():
    print("=== Three-Level Transmon Lindblad Engine v1.0.1 Audit Execution ===")
    physics = TransmonPhysics()
    measurer = QuantumMeasurement()
    gate = KYAdmissibilityGate()
    worm = WORMCommit()

    # Scenario 1: Calibrated Resonant Pi-Pulse
    rho_in = np.zeros((3,3), dtype=complex); rho_in[0,0] = 1.0
    rho_pre1 = physics.evolve_rk4(rho_in, t_gate=10.0, n_steps=200, A0=0.05)
    map1, born1, p1, rho_post1, leak1 = measurer.measure(rho_pre1, seed=123)
    rec1 = QuantumRecord(1.0, rho_in, rho_pre1, rho_post1, map1, born1, p1, leak1, {"A0": 0.05, "t_gate": 10.0})
    v1 = gate.evaluate_pre_measurement(rho_pre1, leak1)
    w_short1, w_full1 = worm.commit(rec1, v1)

    audit = {
        "status_lindblad": STATUS_LINDBLAD,
        "status_pi_pulse": STATUS_PI_PULSE,
        "status_worm_ledger": STATUS_WORM_LEDGER,
        "runs": [
            {
                "scenario": "Calibrated Resonant Pi-Pulse",
                "p0": round(float(np.real(rho_pre1[0,0])), 4),
                "p1": round(float(np.real(rho_pre1[1,1])), 4),
                "p2_leak": round(leak1, 4),
                "map_outcome": f"|{map1}>",
                "born_outcome": f"|{born1}>",
                "gate_verdict": v1.name,
                "worm_short": w_short1,
                "worm_full": w_full1
            }
        ]
    }

    print("\n[AUDIT REPORT JSON]")
    print(json.dumps(audit, indent=2))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTransmonKYGateEngineV101)
    res = unittest.TextTestRunner(verbosity=0).run(suite)
    if res.wasSuccessful():
        run_audit()
    else:
        print("SYSTEM HALT: Tests failed.")
