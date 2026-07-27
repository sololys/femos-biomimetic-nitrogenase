# ==============================================================================
# KCM-CORE CANONICAL TEST RUNNER — FROZEN SURFACE (01_OPEN)
# Status: GOLDEN MASTER / REALIZED — 01_OPEN
# Spesifikasjon: KCM-SPEC-2026-N7 / KORA v0.6
# ==============================================================================

import subprocess
import sys

MODULES = [
    "quantum_kernel.py",
    "kora_gate.py",
    "time_evolution.py",
    "density_measurement.py",
    "quantum_channel.py",
    "simulator.py",
    "l0_fpga_interlock.py"
]

def run_suite():
    print("==================================================================")
    print("   KCM-CORE (N=7, d=128) FULL SYSTEM VERIFICATION RUNNER")
    print("==================================================================")
    
    all_passed = True
    for mod in MODULES:
        cmd = [sys.executable, f"01_OPEN/{mod}"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(res.stdout.strip())
        if res.returncode != 0 or "VERIFIED (PASS)" not in res.stdout:
            print(f"[CRITICAL FAIL]: {mod} feilet verifikasjon.")
            if res.stderr:
                print(res.stderr.strip())
            all_passed = False
            break

    print("------------------------------------------------------------------")
    if all_passed:
        print("GOLDEN MASTER STATUS: 01_OPEN IS FULLY REALIZED AND VERIFIED (PASS)")
    else:
        print("GOLDEN MASTER STATUS: VERIFICATION FAILED (KILL)")
        sys.exit(1)

if __name__ == "__main__":
    run_suite()
