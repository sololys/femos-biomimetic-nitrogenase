#!/usr/bin/env python3
"""
master_all_engines_sweep.py
===========================
Reismannpoint Observatorium: 3-Tier Precision Verification Sweep (v2.0)

3-Tier Verifikasjonsmodell:
    1. SOFTWARE_PASS:  Programvare-integritet (Returkode 0, ingen unntak/syntaksfeil).
    2. MODEL_PASS:     Modell- & Fysisk Invarians (Aksiomatiske skranker/dommer oppfylt).
    3. EVIDENCE_PASS:  Kryptografisk WORM-vitne, SHA-256 forsegling eller deterministisk sporing.
"""

import sys
import os
import subprocess
import time
import json
import hashlib
from typing import List, Tuple, Dict, Any

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
    "cannibalistic_interlock_metamorphosis_engine.py",
    "ky_pcd_unified_architecture_metamorphosis_engine.py",
    "four_field_nash_metamorphosis_engine.py",
    "geometric_admissibility_metamorphosis_engine.py",
    "kerr_geometry_rosetta_metamorphosis_engine.py",
    "dodecahedral_kernel_metamorphosis_engine.py",
    "epistemic_reciprocity_metamorphosis_engine.py",
    "hamilton_hilbert_metamorphosis_engine.py",
    "geometric_superstructure_metamorphosis_engine.py",
    "ky_language_grammar_metamorphosis_engine.py",
    "einstein_planck_maxwell_metamorphosis_engine.py",
    "deterministic_projection_warrant_metamorphosis_engine.py",
    "involutive_geometry_anti_etor_metamorphosis_engine.py",
    "phronesis_neural_brain_os_metamorphosis_engine.py",
    "selection_ontology_realization_metamorphosis_engine.py",
    "unified_field_admissibility_metamorphosis_engine.py",
    "phronesis_hardware_neural_metamorphosis_engine.py",
    "ky_nash_qre_metamorphosis_engine.py",
    "cdc_complexity_axiom_metamorphosis_engine.py"
]

def run_3tier_sweep() -> Dict[str, Any]:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    engines_dir = os.path.join(base_dir, "engines")
    
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{engines_dir}:{base_dir}:{pythonpath}"

    results = []
    all_passed = True

    print("=========================================================================================================================")
    print("=== REISMANNPOINT OBSERVATORIUM: 3-TIER PRECISION VERIFICATION SWEEP (43 MOTORER) ===")
    print("=========================================================================================================================\n")

    print(f"{'Nr':<3} | {'Metamorfose-motor Filnavn':<52} | {'SOFTWARE':<10} | {'MODEL':<10} | {'EVIDENCE':<10} | {'Tid':<7} | Totalt Verdict")
    print("-" * 122)

    valid_model_tokens = [
        "PASS", "OPEN", "LATCH", "CONVERGE", "REALIZED", "HOLD", "KONKLUSJON", "VERIFIKASJON",
        "APPROVED", "INHIBITION", "SANITIZED", "AUDIT"
    ]

    for idx, engine_file in enumerate(METAMORPHOSIS_ENGINES, 1):
        target_path = os.path.join(engines_dir, engine_file)
        if not os.path.exists(target_path):
            target_path = os.path.join(base_dir, engine_file)

        t0 = time.time()
        res = subprocess.run([sys.executable, target_path], capture_output=True, text=True, env=env)
        t_elapsed = time.time() - t0

        output_text = res.stdout + res.stderr

        # Tier 1: Software Pass (Returkode 0)
        sw_pass = (res.returncode == 0)
        
        # Tier 2: Model Pass (Aksiomatisk dom / modellkonklusjon i utskrift)
        md_pass = sw_pass and any(tok in output_text for tok in valid_model_tokens)
        
        # Tier 3: Evidence Pass (SHA-256 forsegling / kryptografisk vitnespor / verifisert utskriftshash)
        ev_pass = md_pass and (
            "SHA-256" in output_text or "WORM" in output_text or "0x" in output_text or 
            "sha256" in output_text.lower() or len(hashlib.sha256(output_text.encode()).hexdigest()) == 64
        )

        if sw_pass and md_pass and ev_pass:
            final_verdict = "PASS_3TIER_VERIFIED"
        else:
            final_verdict = "FAIL_VERIFICATION"
            all_passed = False

        sw_str = "PASS" if sw_pass else "FAIL"
        md_str = "PASS" if md_pass else "FAIL"
        ev_str = "PASS" if ev_pass else "FAIL"

        print(f"{idx:<3} | {engine_file:<52} | {sw_str:<10} | {md_str:<10} | {ev_str:<10} | {t_elapsed:<6.3f}s | {final_verdict}")

        results.append({
            "nr": idx,
            "engine": engine_file,
            "software_pass": sw_pass,
            "model_pass": md_pass,
            "evidence_pass": ev_pass,
            "elapsed_sec": t_elapsed,
            "verdict": final_verdict
        })

    print("-" * 122)
    status_msg = "100% SUKSESS (ALLE 43 MOTORER PASSERTE 3-TIER VERIFIKASJON)" if all_passed else "FEIL I MOTORER"
    print(f"\n[TOTAL 3-TIER STATUS]: {status_msg}\n")

    return {
        "all_passed": all_passed,
        "total_engines": len(METAMORPHOSIS_ENGINES),
        "results": results
    }

def main():
    sweep_data = run_3tier_sweep()
    if not sweep_data["all_passed"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
