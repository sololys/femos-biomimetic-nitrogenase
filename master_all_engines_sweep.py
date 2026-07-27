#!/usr/bin/env python3
"""
master_all_engines_sweep.py
===========================
Total Verifikasjonssweep for alle 25 Metamorfose-motorer i systemet.
"""

import sys
import os
import subprocess
import time
from typing import List, Tuple

# Liste over alle 25 metamorfose-motorer som skal testet
METAMORPHOSIS_ENGINES = [
    "femos_metamorphosis_engine.py",
    "gscx_battery_metamorphosis_engine.py",
    "apc_g4_metamorphosis_engine.py",
    "qcs_omni_metamorphosis_engine.py",
    "rosetta_metamorphosis_engine.py",
    "arkitektens_nullpunkt_engine.py",
    "etor2_metamorphosis_engine.py",
    "omni_full_metamorphosis_engine.py",
    "iks_reversible_metamorphosis_engine.py",
    "holomorphic_holographic_metamorphosis_engine.py",
    "gko_os3_metamorphosis_engine.py",
    "cpcab_hydrogen_control_metamorphosis_engine.py",
    "cvtk_capa_metamorphosis_engine.py",
    "ky_rox_master_metamorphosis_engine.py",
    "kreativ_morandi_metamorphosis_engine.py",
    "projected_fixpoints_metamorphosis_engine.py",
    "sosionomos_digital_fortress_metamorphosis_engine.py",
    "quantum_gravity_m_theory_metamorphosis_engine.py",
    "quantum_perception_metamorphosis_engine.py",
    "forward_invariance_metamorphosis_engine.py",
    "sacl_governance_metamorphosis_engine.py",
    "raw_data_integrity_metamorphosis_engine.py",
    "formal_appendix_theorems_metamorphosis_engine.py",
    "civil_spectrometry_metamorphosis_engine.py",
    "cannibalistic_interlock_metamorphosis_engine.py"
]

def main():
    print("=========================================================================================================")
    print("=== MASTER METAMORFOSE-MOTORER VERIFIKASJONSSWEEP (25 INTEGRERTE MOTORER) ===")
    print("=========================================================================================================\n")

    base_dir = "/home/sololyset/01_OPEN"
    results = []

    print(f"{'Nr':<3} | {'Metamorfose-motor Filnavn':<54} | {'Kjøretid':<8} | Status")
    print("-" * 92)

    all_passed = True

    for idx, engine_file in enumerate(METAMORPHOSIS_ENGINES, 1):
        full_path = os.path.join(base_dir, engine_file)
        if not os.path.exists(full_path):
            full_path = os.path.join("/home/sololyset", engine_file)

        t0 = time.time()
        res = subprocess.run([sys.executable, full_path], capture_output=True, text=True)
        t_elapsed = time.time() - t0

        if res.returncode == 0:
            status = "PASSED (OK)"
        else:
            status = f"FAILED (Code {res.returncode})"
            all_passed = False

        results.append((idx, engine_file, t_elapsed, status))
        print(f"{idx:<3} | {engine_file:<54} | {t_elapsed:<7.3f}s | {status}")

    print("-" * 92)
    print(f"\n[TOTAL VERIFIKASJONSSTATUS]: {'100% SUKSESS (ALLE 25 MOTORER PASSERTE)' if all_passed else 'FEIL I MOTORER'}\n")

if __name__ == "__main__":
    main()
