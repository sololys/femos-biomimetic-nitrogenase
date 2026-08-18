#!/usr/bin/env python3
"""
====================================================================================================
FE-MO-S ADVERSARIAL & HOSTILE INPUT REGRESSION TEST SUITE
STRICT FAIL-CLOSED VALIDATION: NAN, INF, TYPE POISONING & TAMPER PROOFS
====================================================================================================
Author: Marius Egerhei Torjusen (ORCID: 0009-0006-0431-6637)
System: ReismannPoint Systems AS // Kreativ Systems

Tests rigorous fail-closed invariants:
  1. Empty payload -> Immediate KILL (0.0V)
  2. Missing mandatory field -> Immediate KILL (0.0V)
  3. NaN injection (o2_ppm, mossbauer, potential) -> Immediate KILL (0.0V)
  4. +/- Inf injection -> Immediate KILL (0.0V)
  5. Type confusion (String, Bool, List instead of Float) -> Immediate KILL (0.0V)
  6. Physical envelope bounds violation -> Immediate KILL (0.0V)
  7. WORM Ledger Cryptographic Tamper Detection -> verify_ledger() returns False
====================================================================================================
"""

import sys
import math
import copy
from typing import Any, Dict, List
from autonomous_chem_bond_engine import (
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
    "blank_minus_catalyst_m": 0.0,
    "blank_ar_atmosphere_m": 0.0,
    "blank_open_circuit_m": 0.0
}

def run_hostile_regression_suite():
    print("=" * 95)
    print("🛡️  FE-MO-S ADVERSARIAL & HOSTILE INPUT REGRESSION TEST SUITE")
    print("   STRICT FAIL-CLOSED: ZERO DEFAULTS, NO NAN/INF, TYPE SANITIZATION & WORM INTEGRITY")
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
        print(f"[{test_count:02d}] {sym} | {test_name:<45} -> {dec:<5} ({v}V) | {reason[:35]}")
        
        if not ok:
            failures += 1

    # 1. Empty and non-dict inputs
    assert_fail_closed("Tom Dictionary Payload {}", {})
    assert_fail_closed("NoneType Payload", None)
    assert_fail_closed("String Payload instead of Dict", "O2=0.0;H2O=0.0")
    assert_fail_closed("List Payload instead of Dict", [0.2, 0.1, 0.5])

    # 2. Missing mandatory fields
    for field in REQUIRED_TELEMETRY_FIELDS.keys():
        bad_payload = copy.deepcopy(VALID_GOLDEN_TELEMETRY)
        del bad_payload[field]
        assert_fail_closed(f"Mangler obligatorisk felt '{field}'", bad_payload)

    # 3. NaN Poisoning
    for field in ["o2_ppm", "mossbauer_delta_mm_s", "cathodic_potential_v", "h_d_kie_ratio"]:
        bad_payload = copy.deepcopy(VALID_GOLDEN_TELEMETRY)
        bad_payload[field] = float("nan")
        assert_fail_closed(f"NaN-injeksjon i felt '{field}'", bad_payload)

    # 4. Infinity Poisoning
    for field in ["cathodic_potential_v", "faradaic_efficiency_pct"]:
        bad_payload = copy.deepcopy(VALID_GOLDEN_TELEMETRY)
        bad_payload[field] = float("inf")
        assert_fail_closed(f"+Inf-injeksjon i felt '{field}'", bad_payload)
        
        bad_payload[field] = float("-inf")
        assert_fail_closed(f"-Inf-injeksjon i felt '{field}'", bad_payload)

    # 5. Type Confusion (String, Bool)
    bad_payload = copy.deepcopy(VALID_GOLDEN_TELEMETRY)
    bad_payload["o2_ppm"] = "0.00" # String
    assert_fail_closed("String Type-forvirring i o2_ppm", bad_payload)

    bad_payload = copy.deepcopy(VALID_GOLDEN_TELEMETRY)
    bad_payload["o2_ppm"] = False # Boolean False == 0.0 in Python!
    assert_fail_closed("Boolean Type-forvirring (False som float)", bad_payload)

    # 6. Physical Envelope Out-of-Bounds
    bad_payload = copy.deepcopy(VALID_GOLDEN_TELEMETRY)
    bad_payload["faradaic_efficiency_pct"] = 150.0 # > 100%
    assert_fail_closed("Fysisk umulig Faradaic Efficiency (150%)", bad_payload)

    # 7. WORM Ledger Tamper Resistance Test
    test_count += 1
    engine = AutonomousFeMoSMasterEngine()
    engine.evaluate_protocol_candidate("CAND-01", "Fe", "N", 2.0, copy.deepcopy(VALID_GOLDEN_TELEMETRY))
    engine.evaluate_protocol_candidate("CAND-02", "Mo", "S", 1.5, copy.deepcopy(VALID_GOLDEN_TELEMETRY))
    
    # Audit before tamper
    tamper_audit_before = engine.verify_ledger()
    
    # Manually tamper with block 1 payload in memory
    engine.witness_chain[0]["gate_decision"] = "TAMPERED_OPEN"
    tamper_audit_after = engine.verify_ledger()
    
    worm_ok = (tamper_audit_before is True and tamper_audit_after is False)
    sym = "✅ PASS" if worm_ok else "❌ FAIL"
    print(f"[{test_count:02d}] {sym} | WORM Tamper-oppdagelse (Endring i historikk) -> Avslørt: {not tamper_audit_after}")
    if not worm_ok:
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
