# ==============================================================================
# KCM-CORE L0 FPGA HARDWARE INTERLOCK EMULATOR — CANONICAL MODULE (N=7, d=128)
# Status: REALIZED / FROZEN SURFACE — 01_OPEN
# Spesifikasjon: KCM-SPEC-2026-N7 / Circuit QED L0 Interlock
# ==============================================================================

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class L0FPGAInterlock:
    """
    Emulerer L0 Hardware FPGA-register for O(1) fail-closed portlogikk.
    Register-status: 0b01 = OPEN, 0b10 = HOLD, 0b11 = KILL
    """
    OPEN = 0b01
    HOLD = 0b10
    KILL = 0b11

    def __init__(self, dim_required: int = 128):
        self.dim_required = dim_required

    def evaluate_clock_cycle(self, dim: int, norm_valid: bool, trace_valid: bool) -> int:
        # Deterministisk kombinatorisk evaluering i en enkelt klokkesyklus
        if dim != self.dim_required:
            return self.KILL
        if not norm_valid or not trace_valid:
            return self.HOLD
        return self.OPEN

if __name__ == "__main__":
    print("=== KCM-CORE L0 FPGA INTERLOCK TESTSUITE ===")
    gate = L0FPGAInterlock(dim_required=128)

    # Test 1: Nominell operasjon (d=128, norm/trace OK) -> OPEN
    res1 = gate.evaluate_clock_cycle(128, norm_valid=True, trace_valid=True)
    assert res1 == L0FPGAInterlock.OPEN
    print("[TEST 1 PASSED]: L0 FPGA Interlock godkjente gyldig tilstand (OPEN).")

    # Test 2: Uautorisert dimensjon (d=64) -> KILL
    res2 = gate.evaluate_clock_cycle(64, norm_valid=True, trace_valid=True)
    assert res2 == L0FPGAInterlock.KILL
    print("[TEST 2 PASSED]: L0 FPGA Interlock utløste maskinvare-KILL ved feil dimensjon.")

    print("01_OPEN/l0_fpga_interlock.py: L0_FPGA_INTERLOCK_VERIFIED (PASS)")
