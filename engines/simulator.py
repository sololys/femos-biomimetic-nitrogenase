# ==============================================================================
# KCM-CORE END-TO-END SIMULATOR ORCHESTRATOR — CANONICAL MODULE (N=7, d=128)
# Status: REALIZED / FROZEN SURFACE — 01_OPEN
# Spesifikasjon: KCM-SPEC-2026-N7 / KORA v0.6
# ==============================================================================

import sys
import os

# Sikre import fra 01_OPEN
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quantum_kernel import (
    HilbertSpace, VectorState, Operator, ComplexNumber,
    QuantumSystemError, SystemKillException, SystemHoldException
)
from kora_gate import evaluate_gate, GateStatus
from time_evolution import Hamiltonian, evolve_state
from density_measurement import measure_state

def run_simulation(init_state: VectorState, hamiltonian: Hamiltonian, steps: int, dt: float) -> list:
    """
    Kjører en end-to-end simuleringstrajektor under gate-overvåking (Ω).
    Returnerer en liste over validerte VectorState-instanser for hvert tidssteg.
    """
    trajectory = [init_state]
    current_state = init_state

    for step in range(steps):
        # 1. Gate Interlock validering før evolusjonssteg
        status = evaluate_gate(current_state, hamiltonian.operator)
        if status != GateStatus.OPEN:
            if GateStatus.HOLD in status:
                print(f"[SIMULATOR HOLD]: Suspendert ved steg {step} -> {status}")
                break
            else:
                raise SystemKillException(f"KILL: Simulering avbrutt ved steg {step} -> {status}")

        # 2. Utfør tidssteg
        current_state = evolve_state(current_state, hamiltonian, dt)
        trajectory.append(current_state)

    return trajectory

if __name__ == "__main__":
    print("=== KCM-CORE END-TO-END SIMULATOR TESTSUITE ===")

    H128 = HilbertSpace("Register_N7", 128)
    raw_amps = [ComplexNumber(1, 0)] + [ComplexNumber(0, 0) for _ in range(127)]
    psi0 = VectorState(H128, raw_amps)

    zero_matrix = [[ComplexNumber(0.0, 0.0) for _ in range(128)] for _ in range(128)]
    ZeroOp = Operator(H128, zero_matrix)
    H_zero = Hamiltonian(H128, ZeroOp)

    # Test 1: 10-stegs nominal simulering
    traj = run_simulation(psi0, H_zero, steps=10, dt=0.001)
    assert len(traj) == 11
    assert abs(traj[-1].amplitudes[0].real - 1.0) < 1e-6
    print("[TEST 1 PASSED]: 10-stegs simuleringstidsrekke generert og verifisert i 01_OPEN.")

    print("01_OPEN/simulator.py: SIMULATOR_VERIFIED (PASS)")
