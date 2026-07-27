# ==============================================================================
# KCM-CORE TIME EVOLUTION ENGINE — CANONICAL MODULE (N=7, d=128)
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

class Hamiltonian:
    def __init__(self, space: HilbertSpace, op: Operator):
        if space.dim != 128:
            raise SystemKillException("KILL: Hamilton-operator krever d=128 for N=7 register.")
        if not op.is_hermitian():
            raise SystemKillException("KILL: Hamilton-operator må være Hermitisk.")
        self.space = space
        self.operator = op

def evolve_state(state: VectorState, h: Hamiltonian, dt: float) -> VectorState:
    """
    Tidsutvikling under Hamilton-operator H over tidssteg dt.
    Inkluderer fail-closed Gate Interlock-evaluering før og etter evolusjonssteget.
    """
    # 1. Evaluering før evolusjon
    gate_in = evaluate_gate(state, h.operator)
    if gate_in != GateStatus.OPEN:
        raise SystemKillException(f"KILL: Inngangstilstand avvist av Gate Interlock -> {gate_in}")

    # 2. Rå matrise-vektor multiplikasjon: H * |ψ⟩ (uten normaliseringskrav på tangentvektor)
    dim = state.space.dim
    new_amps = []
    for i in range(dim):
        r_sum, i_sum = 0.0, 0.0
        for j in range(dim):
            a = h.operator.matrix[i][j]
            b = state.amplitudes[j]
            r_sum += a.real * b.real - a.imag * b.imag
            i_sum += a.real * b.imag + a.imag * b.real
        
        # |ψ(t+dt)⟩ = |ψ(t)⟩ - (i/ħ) H |ψ(t)⟩ dt  (ħ = 1.0)
        # -i (r_sum + i i_sum) = i_sum - i r_sum
        re_part = state.amplitudes[i].real + dt * i_sum
        im_part = state.amplitudes[i].imag - dt * r_sum
        new_amps.append(ComplexNumber(re_part, im_part))

    next_state = VectorState(state.space, new_amps)

    # 3. Evaluering etter evolusjon
    gate_out = evaluate_gate(next_state)
    if gate_out != GateStatus.OPEN:
        raise SystemKillException(f"KILL: Utgangstilstand avvist av Gate Interlock -> {gate_out}")

    return next_state

if __name__ == "__main__":
    print("=== KCM-CORE TIME EVOLUTION TESTSUITE ===")

    # Test 1: Null-Hamiltonian evolusjon (Identitetsbevaring)
    H128 = HilbertSpace("Register_N7", 128)
    raw_amps = [ComplexNumber(1, 0)] + [ComplexNumber(0, 0) for _ in range(127)]
    psi0 = VectorState(H128, raw_amps)

    zero_matrix = [[ComplexNumber(0.0, 0.0) for _ in range(128)] for _ in range(128)]
    ZeroOp = Operator(H128, zero_matrix)
    H_zero = Hamiltonian(H128, ZeroOp)

    psi_t1 = evolve_state(psi0, H_zero, dt=0.01)
    assert abs(psi_t1.amplitudes[0].real - 1.0) < 1e-7
    print("[TEST 1 PASSED]: Tidsutvikling med null-Hamiltonian bevarer tilstand (OPEN).")

    print("01_OPEN/time_evolution.py: TIME_EVOLUTION_VERIFIED (PASS)")
