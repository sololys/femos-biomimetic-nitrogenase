# ==============================================================================
# KCM-CORE KVANTEMEKANISK KJERNEMOTOR — CANONICAL MODULE (N=7, d=128)
# Status: REALIZED / FROZEN SURFACE — 01_OPEN
# Spesifikasjon: KCM-SPEC-2026-N7
# ==============================================================================

class QuantumSystemError(Exception): pass
class SystemKillException(QuantumSystemError): pass
class SystemHoldException(QuantumSystemError): pass

class ComplexNumber:
    def __init__(self, real: float, imag: float):
        self.real = float(real)
        self.imag = float(imag)
    
    def abs_sq(self) -> float:
        return self.real**2 + self.imag**2

    def __repr__(self):
        return f"({self.real:.4f} + {self.imag:.4f}i)"

class HilbertSpace:
    def __init__(self, name: str, dim: int):
        if dim < 1 or dim > 128:
            raise SystemKillException("KILL: Dimensjon utenfor gyldig område [1, 128]")
        self.name = name
        self.dim = dim

class VectorState:
    def __init__(self, space: HilbertSpace, amplitudes: list):
        if len(amplitudes) != space.dim:
            raise SystemKillException("KILL: Amplitudelengde matcher ikke dimensjon.")
        
        self.space = space
        norm_sq = sum(a.abs_sq() for a in amplitudes)
        
        if norm_sq < 1e-15:
            raise SystemHoldException("HOLD: Nullvektor kan ikke normaliseres.")
        
        norm = norm_sq ** 0.5
        self.amplitudes = [ComplexNumber(a.real / norm, a.imag / norm) for a in amplitudes]

class Operator:
    def __init__(self, space: HilbertSpace, matrix: list):
        if len(matrix) != space.dim or any(len(row) != space.dim for row in matrix):
            raise SystemKillException("KILL: Operatormatrise må være kvadratisk lik space.dim")
        self.space = space
        self.matrix = matrix

    def is_hermitian(self) -> bool:
        for i in range(self.space.dim):
            for j in range(self.space.dim):
                c1 = self.matrix[i][j]
                c2 = self.matrix[j][i]
                if abs(c1.real - c2.real) > 1e-7 or abs(c1.imag + c2.imag) > 1e-7:
                    return False
        return True

def apply_operator(op: Operator, state: VectorState) -> VectorState:
    if op.space.dim != state.space.dim:
        raise SystemKillException("KILL: Dimensjonsmismatch mellom operator og tilstand")
    
    new_amps = []
    for i in range(op.space.dim):
        r_sum, i_sum = 0.0, 0.0
        for j in range(op.space.dim):
            a = op.matrix[i][j]
            b = state.amplitudes[j]
            r_sum += a.real * b.real - a.imag * b.imag
            i_sum += a.real * b.imag + a.imag * b.real
        new_amps.append(ComplexNumber(r_sum, i_sum))
        
    return VectorState(state.space, new_amps)

if __name__ == "__main__":
    H128 = HilbertSpace("Register_N7", 128)
    raw_amps = [ComplexNumber(1, 0)] + [ComplexNumber(0, 0) for _ in range(127)]
    psi0 = VectorState(H128, raw_amps)
    
    id_matrix = [[ComplexNumber(1.0 if i == j else 0.0, 0.0) for j in range(128)] for i in range(128)]
    IdentityOp = Operator(H128, id_matrix)
    
    if not IdentityOp.is_hermitian():
        raise SystemKillException("KILL: Operator ikke Hermitisk")
        
    psi_next = apply_operator(IdentityOp, psi0)
    assert abs(psi_next.amplitudes[0].real - 1.0) < 1e-7
    print("01_OPEN/quantum_kernel.py: CANONICAL_VERIFIED (PASS)")
