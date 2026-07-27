# ==============================================================================
# KORA GATE INTERLOCK (CDC Ω) — CANONICAL MODULE (N=7, d=128)
# Status: REALIZED / FROZEN SURFACE — 01_OPEN
# Spesifikasjon: KCM-SPEC-2026-N7 / KORA v0.6
# ==============================================================================

import sys
import os

# Sikre import fra 01_OPEN
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quantum_kernel import (
    HilbertSpace, VectorState, Operator, ComplexNumber,
    apply_operator, QuantumSystemError, SystemKillException, SystemHoldException
)

class GateStatus:
    OPEN = "OPEN"
    HOLD = "HOLD"
    KILL = "KILL"

def evaluate_gate(state: VectorState, operator: Operator = None) -> str:
    """
    Fail-closed autorisasjonsport (Gate Interlock Ω).
    Evaluere tilstandsvektor og valfri operator mot invarianter for N=7 (d=128).
    Returnerer: OPEN, HOLD, eller KILL.
    """
    try:
        # 1. Hilbert-rom og dimensjonskontroll
        if state.space.dim != 128:
            raise SystemKillException("KILL: Romdimensjon feil for N=7 register (krever d=128).")

        # 2. Sjekk normering
        norm_sq = sum(a.abs_sq() for a in state.amplitudes)
        if abs(norm_sq - 1.0) > 1e-6:
            if norm_sq < 1e-15:
                raise SystemHoldException("HOLD: Nullvektor eller degenerert tilstand.")
            raise SystemHoldException("HOLD: Normfeil utenfor toleranse [1.0 ± 1e-6].")

        # 3. Sjekk operator (hvis oppgitt)
        if operator is not None:
            if operator.space.dim != state.space.dim:
                raise SystemKillException("KILL: Dimensjonsmismatch mellom operator og tilstand.")
            if not operator.is_hermitian():
                raise SystemKillException("KILL: Operator bryter Hermitisitet.")

        return GateStatus.OPEN

    except SystemHoldException as e:
        return f"{GateStatus.HOLD}: {e}"
    except SystemKillException as e:
        return f"{GateStatus.KILL}: {e}"
    except Exception as e:
        return f"{GateStatus.KILL}: Uventet systemfeil -> {e}"

if __name__ == "__main__":
    print("=== KORA GATE INTERLOCK (Ω) TESTSUITE ===")
    
    # Test 1: Nominell tilstand og identitetsoperator -> OPEN
    H128 = HilbertSpace("Register_N7", 128)
    raw_amps = [ComplexNumber(1, 0)] + [ComplexNumber(0, 0) for _ in range(127)]
    psi0 = VectorState(H128, raw_amps)
    
    id_matrix = [[ComplexNumber(1.0 if i == j else 0.0, 0.0) for j in range(128)] for i in range(128)]
    IdentityOp = Operator(H128, id_matrix)
    
    res1 = evaluate_gate(psi0, IdentityOp)
    assert res1 == GateStatus.OPEN
    print("[TEST 1 PASSED]: Gate Interlock status OPEN.")

    # Test 2: Ugyldig dimensjon -> KILL
    H_bad = HilbertSpace("SmallSpace", 64)
    psi_bad = VectorState(H_bad, [ComplexNumber(1, 0)] + [ComplexNumber(0, 0) for _ in range(63)])
    res2 = evaluate_gate(psi_bad)
    assert GateStatus.KILL in res2
    print(f"[TEST 2 PASSED]: Detektert uautorisert dimensjon -> {res2}")

    print("01_OPEN/kora_gate.py: GATE_INTERLOCK_VERIFIED (PASS)")
