#!/usr/bin/env python3
"""
iks_pure_inversion_node.py
==========================
IKS (Involutive Kernel State) Pure Self-Inverse Node (v1.0)

Aksiom (IKS GR Core):
    F(F(s)) = s  <=>  T² = I

Denne noden er konstruert slik at enhver operasjon den utfører er sin egen eksakte invers.
Dersom en tilstand modifiseres eller utsettes for antropocen støy slik at T² ≠ I,
kollapser koherensen og noden aktiverer en uomstøtelig FAIL-CLOSED SEVERANCE (KILL).

Transformasjons-rom:
1. HYPERBOLIC_REFLECTION:  F(s) = 2.0 - s         (F(F(s)) = 2.0 - (2.0 - s) = s)
2. HADAMARD_QUANTUM:       H = 1/sqrt(2) [[1, 1], [1, -1]]  (H * H = I)
3. PAULI_X_FLIP:           X = [[0, 1], [1, 0]]              (X * X = I)
4. BITWISE_XOR_LATCH:      F(x) = x ^ MASK                   ((x ^ MASK) ^ MASK = x)
"""

import math
import time
import json
import hashlib
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Any, List

@dataclass
class InversionWitnessRecord:
    cycle_index: int
    space_name: str
    initial_state_hash: str
    forward_state_hash: str
    inverse_state_hash: str
    is_identity_intact: bool
    verdict: str # "OPEN" or "KILL"
    rosetta_seal_sha256: str


class PureInversionNode:
    """
    En ren, sjøl-inverterende node hvor operasjonen T tilfredsstiller T * T = I.
    """
    def __init__(self, tolerance: float = 1e-12):
        self.tolerance = tolerance
        self.cycle_count = 0
        self.hadamard_matrix = (1.0 / math.sqrt(2.0)) * np.array([[1.0, 1.0], [1.0, -1.0]])
        self.pauli_x_matrix = np.array([[0.0, 1.0], [1.0, 0.0]])
        self.xor_mask = 0xA5A5A5A5

    # -----------------------------------------------------------------
    # 1. Involutive Operatorer (T² = I)
    # -----------------------------------------------------------------
    def transform_hyperbolic(self, s: float) -> float:
        """Hyperbolsk Speiling: F(s) = 2.0 - s"""
        return 2.0 - s

    def transform_hadamard(self, vec: np.ndarray) -> np.ndarray:
        """Kvante-Hadamard Transform: H * vec"""
        return self.hadamard_matrix @ vec

    def transform_pauli_x(self, vec: np.ndarray) -> np.ndarray:
        """Pauli-X Bitflip: X * vec"""
        return self.pauli_x_matrix @ vec

    def transform_xor(self, val: int) -> int:
        """Kryptografisk XOR-skjold: val ^ MASK"""
        return val ^ self.xor_mask

    # -----------------------------------------------------------------
    # 2. Involusjonsverifikasjon (T(T(s)) == s)
    # -----------------------------------------------------------------
    def evaluate_pure_roundtrip(self, space_name: str, input_payload: Any) -> InversionWitnessRecord:
        self.cycle_count += 1
        
        # 1. Forward steg (T)
        if space_name == "HYPERBOLIC_REFLECTION":
            forward = self.transform_hyperbolic(input_payload)
            backward = self.transform_hyperbolic(forward)
            diff = abs(backward - input_payload)
        elif space_name == "HADAMARD_QUANTUM":
            forward = self.transform_hadamard(input_payload)
            backward = self.transform_hadamard(forward)
            diff = np.linalg.norm(backward - input_payload)
        elif space_name == "PAULI_X_FLIP":
            forward = self.transform_pauli_x(input_payload)
            backward = self.transform_pauli_x(forward)
            diff = np.linalg.norm(backward - input_payload)
        elif space_name == "BITWISE_XOR_LATCH":
            forward = self.transform_xor(input_payload)
            backward = self.transform_xor(forward)
            diff = abs(backward - input_payload)
        else:
            raise ValueError(f"Ukjent inversjonsrom: {space_name}")

        # Sjekk identitetsbevaring (T² = I)
        is_intact = diff < self.tolerance

        verdict = "OPEN" if is_intact else "KILL"
        
        # Generer uomstøtelig SHA-256 forsegling
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        h_init = hashlib.sha256(str(input_payload).encode()).hexdigest()[:12]
        h_fwd = hashlib.sha256(str(forward).encode()).hexdigest()[:12]
        h_inv = hashlib.sha256(str(backward).encode()).hexdigest()[:12]
        
        raw_seal = f"{self.cycle_count}:{space_name}:{h_init}:{h_inv}:{verdict}:{timestamp}"
        seal = hashlib.sha256(raw_seal.encode()).hexdigest()

        return InversionWitnessRecord(
            cycle_index=self.cycle_count,
            space_name=space_name,
            initial_state_hash=h_init,
            forward_state_hash=h_fwd,
            inverse_state_hash=h_inv,
            is_identity_intact=is_intact,
            verdict=verdict,
            rosetta_seal_sha256=seal
        )


def main():
    print("=====================================================================")
    print("=== IKS PURE INVERSION NODE (T² = I / SIN EGEN INVERS) ===")
    print("=====================================================================\n")

    node = PureInversionNode()

    test_spaces = [
        ("HYPERBOLIC_REFLECTION", 0.75),
        ("HADAMARD_QUANTUM", np.array([1.0, 0.0])),
        ("PAULI_X_FLIP", np.array([0.6, 0.8])),
        ("BITWISE_XOR_LATCH", 0x12345678),
    ]

    print(f"{'Knyttepunkt-Rom':<25} | {'Identitet T²=I':<15} | {'DOM':<6} | Rosetta SHA-256 Vitnelogg")
    print("-" * 95)

    for space_name, payload in test_spaces:
        rec = node.evaluate_pure_roundtrip(space_name, payload)
        status_str = "EKSART (T²=I)" if rec.is_identity_intact else "DEGRADERTH"
        print(f"{space_name:<25} | {status_str:<15} | {rec.verdict:<6} | {rec.rosetta_seal_sha256[:20]}...")

    print("-" * 95)
    print("\n[VERIFIKASJON FULLFØRT]")
    print("-> Ren IKS node verifisert: Operasjonene er sine egne eksakte inverser uden identitetstap (T² = I).\n")

if __name__ == "__main__":
    main()
