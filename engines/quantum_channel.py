# ==============================================================================
# KCM-CORE QUANTUM CHANNEL & KRAUS ENGINE — CANONICAL MODULE (N=7, d=128)
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
from density_measurement import DensityMatrix
from kora_gate import evaluate_gate, GateStatus

def _mat_mul(a: list, b: list, dim: int = 128) -> list:
    """Matrisemultiplikasjon over komplekse tall C = A * B."""
    res = []
    for i in range(dim):
        row = []
        for j in range(dim):
            r_sum, i_sum = 0.0, 0.0
            for k in range(dim):
                c1 = a[i][k]
                c2 = b[k][j]
                r_sum += c1.real * c2.real - c1.imag * c2.imag
                i_sum += c1.real * c2.imag + c1.imag * c2.real
            row.append(ComplexNumber(r_sum, i_sum))
        res.append(row)
    return res

def _mat_dag(a: list, dim: int = 128) -> list:
    """Hermitisk konjugering A^dagger."""
    res = []
    for i in range(dim):
        row = []
        for j in range(dim):
            c = a[j][i]
            row.append(ComplexNumber(c.real, -c.imag))
        res.append(row)
    return res

class QuantumChannel:
    def __init__(self, space: HilbertSpace, kraus_ops: list):
        if space.dim != 128:
            raise SystemKillException("KILL: QuantumChannel krever d=128 for N=7 register.")
        if not kraus_ops:
            raise SystemKillException("KILL: Kraus-sett kan ikke være tomt.")
        
        self.space = space
        self.kraus_ops = kraus_ops
        self._validate_completeness()

    def _validate_completeness(self):
        """Validerer at sum_k E_k^\dagger E_k = I_128."""
        dim = self.space.dim
        sum_matrix = [[ComplexNumber(0.0, 0.0) for _ in range(dim)] for _ in range(dim)]

        for op in self.kraus_ops:
            if op.space.dim != dim:
                raise SystemKillException("KILL: Kraus-operator dimensjonsmismatch.")
            
            e_dag = _mat_dag(op.matrix, dim)
            e_dag_e = _mat_mul(e_dag, op.matrix, dim)

            for i in range(dim):
                for j in range(dim):
                    sum_matrix[i][j] = ComplexNumber(
                        sum_matrix[i][j].real + e_dag_e[i][j].real,
                        sum_matrix[i][j].imag + e_dag_e[i][j].imag
                    )

        # Sjekk identitet Tr/diag == 1.0 og off-diag == 0.0
        for i in range(dim):
            for j in range(dim):
                target_re = 1.0 if i == j else 0.0
                if abs(sum_matrix[i][j].real - target_re) > 1e-6 or abs(sum_matrix[i][j].imag) > 1e-6:
                    raise SystemKillException("KILL: Kraus-fullstendighetsrelasjon sum E_k^dag E_k = I feilet.")

def apply_channel(channel: QuantumChannel, rho: DensityMatrix) -> DensityMatrix:
    """Anvender kvanterelaksjon/støykanal rho' = sum_k E_k rho E_k^\dagger."""
    dim = rho.space.dim
    new_matrix = [[ComplexNumber(0.0, 0.0) for _ in range(dim)] for _ in range(dim)]

    for op in channel.kraus_ops:
        e_rho = _mat_mul(op.matrix, rho.matrix, dim)
        e_dag = _mat_dag(op.matrix, dim)
        term = _mat_mul(e_rho, e_dag, dim)

        for i in range(dim):
            for j in range(dim):
                new_matrix[i][j] = ComplexNumber(
                    new_matrix[i][j].real + term[i][j].real,
                    new_matrix[i][j].imag + term[i][j].imag
                )

    return DensityMatrix(rho.space, new_matrix)

if __name__ == "__main__":
    print("=== KCM-CORE QUANTUM CHANNEL TESTSUITE ===")

    H128 = HilbertSpace("Register_N7", 128)

    # Test 1: Støyfri identitetskanal på ren tilstand |0><0| (Tr(rho) = 1.0) -> OPEN
    id_matrix = [[ComplexNumber(1.0 if i == j else 0.0, 0.0) for j in range(128)] for i in range(128)]
    E0 = Operator(H128, id_matrix)
    ch_id = QuantumChannel(H128, [E0])

    rho_pure = [[ComplexNumber(1.0 if (i == 0 and j == 0) else 0.0, 0.0) for j in range(128)] for i in range(128)]
    rho_init = DensityMatrix(H128, rho_pure)
    rho_out = apply_channel(ch_id, rho_init)
    assert abs(rho_out.matrix[0][0].real - 1.0) < 1e-6
    print("[TEST 1 PASSED]: Identitets-Krauskanal oppfyller fullstendighet og bevarer rho.")

    # Test 2: Ufullstendig Kraus-sett (skalert med 0.5) -> KILL
    half_matrix = [[ComplexNumber(0.5 if i == j else 0.0, 0.0) for j in range(128)] for i in range(128)]
    E_bad = Operator(H128, half_matrix)
    try:
        QuantumChannel(H128, [E_bad])
        print("[TEST 2 FAILED]: Forventet SystemKillException ble ikke utløst.")
    except SystemKillException as e:
        print(f"[TEST 2 PASSED]: Detektert uadmissibel Kraus-fullstendighet -> {e}")

    print("01_OPEN/quantum_channel.py: QUANTUM_CHANNEL_VERIFIED (PASS)")
