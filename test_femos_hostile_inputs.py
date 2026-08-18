#!/usr/bin/env python3
"""
====================================================================================================
FE-MO-S ADVERSARIAL & HOSTILE INPUT REGRESSION TEST SUITE v3.2 (HARDENED)
STRICT FAIL-CLOSED VALIDATION: NAN, INF, TYPE POISONING, PREDICTOR COUPLING & DISK WORM PROOFS
====================================================================================================
Author: Marius Egerhei Torjusen (ORCID: 0009-0006-0431-6637)
System: ReismannPoint Systems AS // Kreativ Systems

Tests rigorous fail-closed invariants:
  1. Empty payload -> Immediate KILL (0.0V)
  2. Missing mandatory field (including TOF) -> Immediate KILL (0.0V)
  3. NaN injection (o2_ppm, mossbauer, potential, TOF) -> Immediate KILL (0.0V)
  4. +/- Inf injection (potential, FE, TOF) -> Immediate KILL (0.0V)
  5. Type confusion (String, Bool, List instead of Float) -> Immediate KILL (0.0V)
  6. Physical envelope bounds violation -> Immediate KILL (0.0V)
  7. Predictor Viability Coupling (Invalid elements/bond orders) -> Immediate KILL (0.0V)
  8. Disk I/O Failure Handling -> Immediate Fail-Closed KILL (0.0V)
  9. RAM Ledger Cryptographic Tamper Detection -> verify_ledger() returns False
 10. DISK JSONL Ledger Cryptographic Tamper Detection -> verify_disk_ledger() returns False
====================================================================================================
"""

import sys
import os
import math
import copy
import json
from typing import Any, Dict, List

# Støtt import både fra lokal mappe og rot
try:
    from autonomous_chem_bond_engine import (
        FeMoSProtocolAdmissibilityGate,
        AutonomousFeMoSMasterEngine,
        REQUIRED_TELEMETRY_FIELDS
    )
except ImportError:
    from femos_engine import (
        FeMoSProtocolAdmissibilityGate,
        AutonomousFeMoSMasterEngine,
        REQUIRED_TELEMETRY_FIELDS
    )

# Golden baseline that normally passes
VALID_GOLDEN_TELEMETRY = {
    "o2_ppm": 0.2,
    "h2o_ppm": 0.1,
    "stoichiometry_dev_pct": 0.5,
    "mossbauer_delta_mm_s": 0.45,
    "mossbauer_eq_mm_s": 2.10,
    "cathodic_potential_v": -1.55,
    "h_d_kie_ratio": 6.2,
    "diazenido_raman_cm1": 1490.0,
    "nmr_15n_ppm": -310.0,
    "nmr_1j_coupling_hz": 73.5,
    "faradaic_efficiency_pct": 28.5,
    "turnover_frequency_h1": 14.2,
    "blank_minus_catalyst_m": 0.0,
    "blank_ar_atmosphere_m": 0.0,
    "blank_open_circuit_m": 0.0
}

def run_hostile_regression_suite():
    print("=" * 95)
    print("🛡️  FE-MO-S ADVERSARIAL & HOSTILE INPUT REGRESSION TEST SUITE v3.2")
    print("   STRICT FAIL-CLOSED: ZERO DEFAULTS, PREDICTOR COUPLING, DISK-WORM PERSISTENCE & TAMPER PROOFS")
    print("=" * 95)

    failures = 0
    test_count = 0

    def assert_fail_closed(test_name: str, payload: Any, expected_dec: str = "KILL", expected_v: float = 0.0):
        nonlocal test_count, failures
        test_count += 1
        gate = FeMoSProtocolAdmissibilityGate()
        dec, reason, v, _ = gate.evaluate_protocol_candidate(payload)
        
        ok = (dec == expected_dec and v == expected_v)
        sym = "✅ PASS" if ok else "❌ FAIL"
        print(f"[{test_count:02d}] {sym} | {test_name:<50} -> {dec:<5} ({v}V) | {reason[:30]}")
        
        if not ok:
            failures += 1

    # 1. Empty and non-dict inputs
    assert_fail_closed("Tom Dictionary Payload {}", {})
    assert_fail_closed("NoneType Payload", None)
    assert_fail_closed("String Payload instead of Dict", "O2=0.0;H2O=0.0")
    assert_fail_closed("List Payload instead of Dict", [0.2, 0.1, 0.5])

    # 2. Missing mandatory fields (including TOF)
    for field in REQUIRED_TELEMETRY_FIELDS.keys():
        bad_payload = copy.deepcopy(VALID_GOLDEN_TELEMETRY)
        del bad_payload[field]
        assert_fail_closed(f"Mangler obligatorisk felt '{field}'", bad_payload)

    # 3. NaN Poisoning
    for field in ["o2_ppm", "mossbauer_delta_mm_s", "cathodic_potential_v", "h_d_kie_ratio", "turnover_frequency_h1"]:
        bad_payload = copy.deepcopy(VALID_GOLDEN_TELEMETRY)
        bad_payload[field] = float("nan")
        assert_fail_closed(f"NaN-injeksjon i felt '{field}'", bad_payload)

    # 4. Infinity Poisoning
    for field in ["cathodic_potential_v", "faradaic_efficiency_pct", "turnover_frequency_h1"]:
        bad_payload = copy.deepcopy(VALID_GOLDEN_TELEMETRY)
        bad_payload[field] = float("inf")
        assert_fail_closed(f"+Inf-injeksjon i felt '{field}'", bad_payload)
        
        bad_payload[field] = float("-inf")
        assert_fail_closed(f"-Inf-injeksjon i felt '{field}'", bad_payload)

    # 5. Type Confusion (String, Bool)
    bad_payload = copy.deepcopy(VALID_GOLDEN_TELEMETRY)
    bad_payload["turnover_frequency_h1"] = "12.0_FAST"
    assert_fail_closed("String Type-forvirring i turnover_frequency_h1", bad_payload)

    bad_payload = copy.deepcopy(VALID_GOLDEN_TELEMETRY)
    bad_payload["turnover_frequency_h1"] = True
    assert_fail_closed("Boolean Type-forvirring (True som TOF float)", bad_payload)

    # 6. Physical Envelope Out-of-Bounds
    bad_payload = copy.deepcopy(VALID_GOLDEN_TELEMETRY)
    bad_payload["faradaic_efficiency_pct"] = 150.0 # > 100%
    assert_fail_closed("Fysisk umulig Faradaic Efficiency (150%)", bad_payload)

    # 7. Predictor-to-Gate Direct Coupling Tests
    test_count += 1
    engine = AutonomousFeMoSMasterEngine()
    rec_bad_atom = engine.evaluate_protocol_candidate("CAND-UNVIABLE-ATOM", "Kryptonite", "N", 1.0, copy.deepcopy(VALID_GOLDEN_TELEMETRY))
    coupled_atom_ok = (rec_bad_atom["gate_decision"] == "KILL" and rec_bad_atom["actuator_relay_voltage_v"] == 0.0)
    sym = "✅ PASS" if coupled_atom_ok else "❌ FAIL"
    print(f"[{test_count:02d}] {sym} | Prediktor-kobling: Ugyldig element (Kryptonite)    -> {rec_bad_atom['gate_decision']:<5} ({rec_bad_atom['actuator_relay_voltage_v']}V) | {rec_bad_atom['decision_reason'][:30]}")
    if not coupled_atom_ok:
        failures += 1

    test_count += 1
    rec_bad_bo = engine.evaluate_protocol_candidate("CAND-UNVIABLE-BO", "Fe", "N", float("nan"), copy.deepcopy(VALID_GOLDEN_TELEMETRY))
    coupled_bo_ok = (rec_bad_bo["gate_decision"] == "KILL" and rec_bad_bo["actuator_relay_voltage_v"] == 0.0)
    sym = "✅ PASS" if coupled_bo_ok else "❌ FAIL"
    print(f"[{test_count:02d}] {sym} | Prediktor-kobling: NaN Bindingsorden              -> {rec_bad_bo['gate_decision']:<5} ({rec_bad_bo['actuator_relay_voltage_v']}V) | {rec_bad_bo['decision_reason'][:30]}")
    if not coupled_bo_ok:
        failures += 1

    # 8. Disk I/O Write Failure Handling (Fail-Closed)
    test_count += 1
    # Bruk en ulovlig katalogsti som gir disk write error
    engine_bad_disk = AutonomousFeMoSMasterEngine(ledger_file="/proc/sys/kernel/forbidden_femos_ledger.jsonl")
    rec_disk_err = engine_bad_disk.evaluate_protocol_candidate("CAND-DISK-FAIL", "Fe", "N", 2.0, copy.deepcopy(VALID_GOLDEN_TELEMETRY))
    disk_fail_closed_ok = (rec_disk_err["gate_decision"] == "KILL" and rec_disk_err["actuator_relay_voltage_v"] == 0.0)
    sym = "✅ PASS" if disk_fail_closed_ok else "❌ FAIL"
    print(f"[{test_count:02d}] {sym} | Disk I/O Skrivefeil -> Tvunget Fail-Closed KILL     -> {rec_disk_err['gate_decision']:<5} ({rec_disk_err['actuator_relay_voltage_v']}V) | {rec_disk_err['decision_reason'][:30]}")
    if not disk_fail_closed_ok:
        failures += 1

    # 9. RAM Ledger Cryptographic Tamper Detection
    test_count += 1
    engine_tamper = AutonomousFeMoSMasterEngine()
    engine_tamper.evaluate_protocol_candidate("CAND-01", "Fe", "N", 2.0, copy.deepcopy(VALID_GOLDEN_TELEMETRY))
    engine_tamper.evaluate_protocol_candidate("CAND-02", "Mo", "S", 1.5, copy.deepcopy(VALID_GOLDEN_TELEMETRY))
    
    tamper_ram_before = engine_tamper.verify_ledger()
    engine_tamper.witness_chain[0]["gate_decision"] = "TAMPERED_OPEN" # Forfalsket i minnet
    tamper_ram_after = engine_tamper.verify_ledger()
    
    ram_tamper_ok = (tamper_ram_before is True and tamper_ram_after is False)
    sym = "✅ PASS" if ram_tamper_ok else "❌ FAIL"
    print(f"[{test_count:02d}] {sym} | RAM WORM Tamper-oppdagelse (Endring i minnekjede)  -> Avslørt: {not tamper_ram_after}")
    if not ram_tamper_ok:
        failures += 1

    # 10. DISK JSONL Ledger Cryptographic Tamper Detection Across Restarts
    test_count += 1
    disk_test_file = "/tmp/femos_disk_tamper_suite.jsonl"
    if os.path.exists(disk_test_file):
        os.remove(disk_test_file)
        
    engine_disk = AutonomousFeMoSMasterEngine(ledger_file=disk_test_file)
    engine_disk.evaluate_protocol_candidate("CAND-01", "Fe", "N", 2.0, copy.deepcopy(VALID_GOLDEN_TELEMETRY))
    engine_disk.evaluate_protocol_candidate("CAND-02", "Mo", "S", 1.5, copy.deepcopy(VALID_GOLDEN_TELEMETRY))
    
    disk_before = AutonomousFeMoSMasterEngine.verify_disk_ledger(disk_test_file)
    
    # Manipuler den rå JSONL-filen på disk
    with open(disk_test_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    tampered_entry = json.loads(lines[0])
    tampered_entry["target"] = "FORGED_BOND (Order 3.0)"
    lines[0] = json.dumps(tampered_entry) + "\n"
    
    with open(disk_test_file, "w", encoding="utf-8") as f:
        f.writelines(lines)
        
    disk_after = AutonomousFeMoSMasterEngine.verify_disk_ledger(disk_test_file)
    
    disk_tamper_ok = (disk_before is True and disk_after is False)
    sym = "✅ PASS" if disk_tamper_ok else "❌ FAIL"
    print(f"[{test_count:02d}] {sym} | DISK JSONL Tamper-oppdagelse (Filmanipulasjon)     -> Avslørt: {not disk_after}")
    if not disk_tamper_ok:
        failures += 1

    print("=" * 95)
    if failures == 0:
        print(f"✅ ALLE {test_count} ADVERSARIELLE OG FIENDTLIGE INPUT-TESTER BESTÅTT MED 100% DETERMINISME")
    else:
        print(f"❌ REGRESJONSTEST FEILET: {failures} av {test_count} tester feilet!")
    print("=" * 95)

    if failures > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_hostile_regression_suite()
