from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np

# Try importing Qiskit, fallback to NumPy Density Matrix if not installed
try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector, DensityMatrix
    HAS_QISKIT = True
except ImportError:
    HAS_QISKIT = False

@dataclass
class ArmResult:
    name: str
    dk: float
    counts_standard: Dict[str, float]
    counts_soft: Dict[str, float]
    counts_engineered: Dict[str, float]

class FallbackDensityMatrix:
    def __init__(self, data):
        self.data = np.array(data, dtype=complex)

def make_arm_a():
    """Short admissible path (Bell state |00> + |11> / sqrt(2))."""
    history_len = 2
    if HAS_QISKIT:
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        return qc, history_len
    return "ARM_A_CIRCUIT", history_len

def make_arm_b(loop_pairs: int = 5000):
    """Long path asymmetry (5000 identity CX loops)."""
    history_len = 2 + 2 * loop_pairs
    if HAS_QISKIT:
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        for _ in range(loop_pairs):
            qc.cx(0, 1)
            qc.cx(0, 1)
        return qc, history_len
    return "ARM_B_CIRCUIT", history_len

def kernel_drift(history_len: int, ref_len: int = 2, eps: float = 1e-12) -> float:
    return abs(history_len - ref_len) / (abs(ref_len) + eps)

def e_k(dk: float, alpha: float = 5.0) -> float:
    return math.exp(-alpha * dk * dk)

def engineered_gate_probs(base_probs: Dict[str, float], dk: float, eta: float = 0.5) -> Dict[str, float]:
    if dk > eta:
        return {"KILL": 1.0}
    return dict(base_probs)

def soft_gate_probs(base_probs: Dict[str, float], dk: float, alpha: float = 5.0) -> Dict[str, float]:
    weight = e_k(dk, alpha=alpha)
    out = {k: weight * v for k, v in base_probs.items()}
    out["NULL"] = 1.0 - weight
    return out

def run_arm(name: str, qc, history_len: int, ref_len: int = 2, eta: float = 0.5, alpha: float = 5.0) -> ArmResult:
    if HAS_QISKIT and not isinstance(qc, str):
        state = Statevector.from_instruction(qc)
        rho = DensityMatrix(state)
        diag = np.real(np.diag(rho.data))
        probs = {"00": float(diag[0]), "01": float(diag[1]), "10": float(diag[2]), "11": float(diag[3])}
    else:
        # Ideal Bell state probabilities
        probs = {"00": 0.5, "01": 0.0, "10": 0.0, "11": 0.5}

    dk = kernel_drift(history_len=history_len, ref_len=ref_len)

    return ArmResult(
        name=name,
        dk=dk,
        counts_standard=probs,
        counts_soft=soft_gate_probs(probs, dk=dk, alpha=alpha),
        counts_engineered=engineered_gate_probs(probs, dk=dk, eta=eta),
    )

def main() -> None:
    print("=== KVANTE APC SIMULATOR & KJERNE-DRIFT TEST ===")
    qc_a, hist_a = make_arm_a()
    qc_b, hist_b = make_arm_b(loop_pairs=5000)

    arm_a = run_arm("ARM A (Kort Sti)", qc_a, hist_a, eta=0.5, alpha=5.0)
    arm_b = run_arm("ARM B (Lang Sti Asymmetri)", qc_b, hist_b, eta=0.5, alpha=5.0)

    print(f"\nARM A (Kort Godkjent Sti): D_K = {arm_a.dk:.6f}")
    print(f"  Standard QM Resultat: {arm_a.counts_standard}")
    print(f"  Engineered Omega Gate: {arm_a.counts_engineered}")

    print(f"\nARM B (5000 Løkkers Stiasymmetri): D_K = {arm_b.dk:.6f}")
    print(f"  Standard QM Resultat: {arm_b.counts_standard}")
    print(f"  Engineered Omega Gate: {arm_b.counts_engineered}")

    print("\n-> Kvante-APC Verifikasjon Fullført: Arm B utløser uomstøtelig KILL på grunn av stiasymmetri!")

if __name__ == "__main__":
    main()
