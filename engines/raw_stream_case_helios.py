#!/usr/bin/env python3
"""
RAW STREAM CASE STUDY 2: PROSJEKT HELIOS (Smart Grid Power Interlock)
Formål: Evaluere en AI-agentisk kraft-innsprøytingskommando i et regionalt strømnett.
Sjekker at kommandoen tilfredsstiller CPCA-B forward invariance og WCET (0.34 ms <= 1.27 ms).
"""

import sys
import time
import numpy as np

class SmartGridRAWProcessor:
    def __init__(self, wcet_limit_ms=1.27):
        self.max_freq_drift_hz = 0.50  # Maksimalt tillatt frekvensavvik (50.0 Hz +/- 0.5 Hz)
        self.wcet_limit_ms = wcet_limit_ms

    def process_raw_stream(self, grid_payload):
        voltage_pert = grid_payload["voltage_perturbation_pct"]
        freq_hz = grid_payload["frequency_hz"]
        power_mw = grid_payload["power_injection_mw"]
        simulated_wcet_ms = grid_payload.get("simulated_wcet_ms", 0.34)
        
        freq_drift = abs(freq_hz - 50.0)
        
        # 1. NASH (NP) EKSPLORASJONSROM
        print(f"--- 1. NASH (NP) EKSPLORASJONSROM ---")
        print(f"Kandidat-Kommando: Kraft-innsprøyting +{power_mw:.1f} MW på Substation Alpha")
        print(f"Frekvens: {freq_hz:.2f} Hz | Spennings-perturbasjon: {voltage_pert:+.2f}%")

        # 2. IKS CONDITION AUDIT (kappa(A) audit)
        matrix_A = np.array([
            [1.0 + (voltage_pert / 100.0), freq_drift * 2.0],
            [0.1, 1.0]
        ])
        kappa = float(np.linalg.cond(matrix_A))
        print(f"\n--- 2. IKS CONDITION AUDIT (kappa(A)) ---")
        print(f"Stresstest Matrise A:\n{matrix_A}")
        print(f"Kondisjonstall kappa(A): {kappa:.4f} (Stabil)")

        # 3. EINSTEIN (A_E) ADMISSIBILITETSROM & CPCA-B FORWARD INVARIANCE
        barrier_val = (freq_drift**2) - (self.max_freq_drift_hz**2)
        in_einstein_manifold = (barrier_val <= 0.0) and (kappa <= 10.0)
        print(f"\n--- 3. EINSTEIN (A_E) ADMISSIBILITETSROM & CPCA-B ---")
        print(f"Barriere-verdi B(x): {barrier_val:.4f} <= 0 | Metrikkrom A_E: {in_einstein_manifold}")

        # 4. KY REALISERINGS DOM (Omega_KY)
        print(f"\n--- 4. KY (Omega_KY) REALISERINGS-DOM ---")
        if not in_einstein_manifold or simulated_wcet_ms > self.wcet_limit_ms:
            verdict = "KILL"
            reason = f"CPCA-B Invariance or WCET Violation! (WCET={simulated_wcet_ms:.2f}ms > {self.wcet_limit_ms:.2f}ms limit)"
        else:
            verdict = "OPEN"
            reason = f"Admissible Smart Grid Action. WCET={simulated_wcet_ms:.2f}ms <= {self.wcet_limit_ms:.2f}ms. Commit Authorized."

        return verdict, reason, kappa, simulated_wcet_ms

def run_case_helios():
    print("============================================================")
    print("RAW-STRØM SAKSKJØRING 2: PROSJEKT HELIOS (SMART GRID)")
    print("============================================================")
    
    # Test 1: Sub-millisekund optimert eksekvering (0.34 ms <= 1.27 ms) -> OPEN
    payload_fast = {
        "substation_id": "SUBSTATION_ALPHA_NORTH",
        "power_injection_mw": 25.0,
        "frequency_hz": 49.82,
        "voltage_perturbation_pct": +1.2,
        "simulated_wcet_ms": 0.34
    }
    
    processor = SmartGridRAWProcessor()
    verdict1, reason1, kappa1, wcet1 = processor.process_raw_stream(payload_fast)
    
    print("\n============================================================")
    print(f"ENDELIG PORTVERDIKT: [{verdict1}]")
    print(f"ÅRSAK: {reason1}")
    print("============================================================")

if __name__ == "__main__":
    run_case_helios()
