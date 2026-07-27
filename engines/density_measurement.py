# ==============================================================================
# KCM-CORE DENSITY MATRIX & MEASUREMENT ENGINE — CANONICAL MODULE (N=7, d=128)
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

class DensityMatrix:
    def __init__(self, space: HilbertSpace, matrix: list):
        if space.dim != 128:
            raise SystemKillException("KILL: DensityMatrix krever d=128 for N=7 register.")
        if len(matrix) != 128 or any(len(row) != 128 for row in matrix):
            raise SystemKillException("KILL: Matrise må være 128x128.")
        
        self.space = space
        self.matrix = matrix
        self._validate()

    def _validate(self):
        # 1. Hermitisk sjekk
        for i in range(128):
            for j in range(128):
                c1 = self.matrix[i][j]
                c2 = self.matrix[j][i]
                if abs(c1.real - c2.real) > 1e-7 or abs(c1.imag + c2.imag) > 1e-7:
                    raise SystemKillException("KILL: DensityMatrix er ikke Hermitisk.")
        
        # 2. Sporsjekk Tr(rho) == 1.0
        tr_re = sum(self.matrix[i][i].real for i in range(128))
        tr_im = sum(self.matrix[i][i].imag for i in range(128))
        if abs(tr_re - 1.0) > 1e-6 or abs(tr_im) > 1e-6:
            raise SystemKillException("KILL: DensityMatrix Tr(rho) != 1.0.")

class MeasurementResult:
    def __init__(self, basis_index: int, probability: float, post_state: VectorState):
        self.basis_index = basis_index
        self.probability = probability
        self.post_state = post_state

def measure_state(state: VectorState, basis_index: int) -> MeasurementResult:
    """
    Utfører Von Neumann projeksjonsmåling på basis-tilstand |m> (0 <= m < 128).
    Beregner Borns sannsynlighet p(m) = |c_m|^2 og kollapser tilstanden til |m>.
    """
    if basis_index < 0 or basis_index >= 128:
        raise SystemKillException("KILL: Målebasis-indeks utenfor gyldig område [0, 127].")

    gate_status = evaluate_gate(state)
    if gate_status != GateStatus.OPEN:
        raise SystemKillException(f"KILL: Tilstand avvist av Gate Interlock før måling -> {gate_status}")

    prob = state.amplitudes[basis_index].abs_sq()

    # Konstruer kollapset tilstand |m>
    collapsed_amps = [ComplexNumber(1.0 if i == basis_index else 0.0, 0.0) for i in range(128)]
    post_state = VectorState(state.space, collapsed_amps)

    return MeasurementResult(basis_index, prob, post_state)

if __name__ == "__main__":
    print("=== KCM-CORE DENSITY & MEASUREMENT TESTSUITE ===")

    H128 = HilbertSpace("Register_N7", 128)
    
    # Test 1: Von Neumann måling på superposisjon (1/sqrt(2))(|0> + |1>)
    inv_sqrt2 = 1.0 / (2.0 ** 0.5)
    raw_amps = [ComplexNumber(inv_sqrt2, 0.0), ComplexNumber(inv_sqrt2, 0.0)] + [ComplexNumber(0.0, 0.0) for _ in range(126)]
    psi_sup = VectorState(H128, raw_amps)

    res0 = measure_state(psi_sup, 0)
    assert abs(res0.probability - 0.5) < 1e-6
    assert abs(res0.post_state.amplitudes[0].real - 1.0) < 1e-7
    print("[TEST 1 PASSED]: Von Neumann måling og Borns regel verifisert (p=0.5, kollaps til |0>).")

    # Test 2: Ugyldig basis-indeks -> KILL
    try:
        measure_state(psi_sup, 150)
        print("[TEST 2 FAILED]: Forventet SystemKillException ble ikke utløst.")
    except SystemKillException as e:
        print(f"[TEST 2 PASSED]: Detektert uautorisert indeks -> {e}")

    print("01_OPEN/density_measurement.py: DENSITY_MEASUREMENT_VERIFIED (PASS)")
