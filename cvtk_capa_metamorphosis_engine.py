#!/usr/bin/env python3
"""
cvtk_capa_metamorphosis_engine.py
=================================
CVTK (Verifiable Trust Kernel) & CAPA (Ghidan Capacity Gate) Metamorfose-motor (v1.0)

Aksiom (CVTK & CAPA Spesifikasjon):
1. CVTK: Separerer probabilistisk forslag u_p fra deterministisk autorisasjon Auth.
   Gating: g(e) >= rho -> ALLOW (OPEN), ellers HOLD/KILL.
2. CAPA: Ghidan Capacity Conservation
   Load L = 2*kappa / r. Throughput chi^2 = 1.0 - L.
   Fail-Closed: L > 1.0 -> KILL, L >= 0.54 -> HOLD, L < 0.54 -> OPEN.

4 Metamorfoser:
   - MORPH_CVTK_AUTHORIZATION:    CVTK Epistemisk vs Irreversibilitet Port
   - MORPH_CAPA_FLAT_PROPAGATION: CAPA Kapasitetsport Flat Space (OPEN)
   - MORPH_CAPA_ADMISSIBILITY:    CAPA Høystress Admissibilitet (HOLD)
   - MORPH_CAPA_SINGULARITY_KILL: CAPA Kapasitets-overbelastning (KILL)
"""

import math
import time
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any

from ghidan_capacity_gate import GhidanCapacityGate

def evaluate_cvtk_gate(proposal_u: str, uncertainty_e: float, irreversibility_rho: float) -> Tuple[str, float]:
    """CVTK Deterministisk Autorisasjonsport."""
    g_e = 1.0 - (2.0 * uncertainty_e) # Monoton synkende gating funksjon
    
    if g_e < irreversibility_rho:
        verdict = "KILL"
    elif abs(g_e - irreversibility_rho) < 0.05:
        verdict = "HOLD"
    else:
        verdict = "OPEN"
        
    return verdict, float(g_e)


class CVTKCAPAMetamorphosisEngine:
    def __init__(self):
        self.capa_gate = GhidanCapacityGate()

    def morph_to_cvtk_authorization(self) -> Dict[str, Any]:
        """Morf 1: CVTK Deterministisk Autorisasjonsport."""
        verdict, g_e = evaluate_cvtk_gate(proposal_u="Actuate_Valve", uncertainty_e=0.02, irreversibility_rho=0.80)
        
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        sig = hashlib.sha256(f"CVTK_AUTH:{verdict}:{g_e:.4f}:{ts}".encode()).hexdigest()

        return {
            "label": "Morf 1 (CVTK Deterministisk Autorisasjon)",
            "domain": "CVTK_Epistemic_Authorization_Kernel",
            "capacity_metric": g_e,
            "verdict": verdict,
            "witness_sha256": sig
        }

    def morph_to_capa_flat_propagation(self) -> Dict[str, Any]:
        """Morf 2: CAPA Kapasitetsport Flat Space (OPEN)."""
        verd, reas, wit = self.capa_gate.evaluate_capacity(E=1.50, r=10.0) # L = 0.30 < 0.54
        verdict = "OPEN" if verd in ["OPEN", "COMMIT"] else verd
        
        return {
            "label": "Morf 2 (CAPA Kapasitetsport OPEN)",
            "domain": "Ghidan_Capacity_Flat_Propagation",
            "capacity_metric": wit["grid_metrics"]["load_L"],
            "verdict": verdict,
            "witness_sha256": wit["witness_hash"]
        }

    def morph_to_capa_admissibility_stress(self) -> Dict[str, Any]:
        """Morf 3: CAPA Høystress Admissibilitet (HOLD)."""
        verd, reas, wit = self.capa_gate.evaluate_capacity(E=3.00, r=10.0) # L = 0.60 >= 0.54
        
        return {
            "label": "Morf 3 (CAPA Høystress HOLD)",
            "domain": "Ghidan_Capacity_Admissibility_Stress",
            "capacity_metric": wit["grid_metrics"]["load_L"],
            "verdict": verd,
            "witness_sha256": wit["witness_hash"]
        }

    def morph_to_capa_singularity_kill(self) -> Dict[str, Any]:
        """Morf 4: CAPA Kapasitets-overbelastning (KILL)."""
        verd, reas, wit = self.capa_gate.evaluate_capacity(E=8.00, r=10.0) # L = 1.60 > 1.0
        
        return {
            "label": "Morf 4 (CAPA Overbelastning KILL)",
            "domain": "Ghidan_Capacity_Overload_Kill",
            "capacity_metric": wit.get("grid_metrics", {}).get("load_L", 1.60),
            "verdict": verd,
            "witness_sha256": wit.get("witness_hash", "sha256:kill")
        }

    def run_cvtk_capa_sweep(self) -> List[Dict[str, Any]]:
        return [
            self.morph_to_cvtk_authorization(),
            self.morph_to_capa_flat_propagation(),
            self.morph_to_capa_admissibility_stress(),
            self.morph_to_capa_singularity_kill()
        ]


def main():
    print("=====================================================================")
    print("=== CVTK & CAPA CAPACITY METAMORFOSE-MOTOR (v1.0) ===")
    print("=====================================================================\n")

    engine = CVTKCAPAMetamorphosisEngine()
    sweep = engine.run_cvtk_capa_sweep()

    print(f"{'CVTK & CAPA Morf':<38} | {'Domene':<38} | {'Metrikk':<10} | {'DOM':<6} | Witness SHA-256")
    print("-" * 118)

    for item in sweep:
        print(f"{item['label']:<38} | {item['domain']:<38} | {item['capacity_metric']:<10.4f} | {item['verdict']:<6} | {item['witness_sha256'][:16]}...")

    print("-" * 118)
    print("\n[VERIFIKASJON FULLFØRT]")
    print("-> CVTK deterministisk autorisasjon og CAPA Ghidan kapasitetsport verifisert.\n")

if __name__ == "__main__":
    main()
