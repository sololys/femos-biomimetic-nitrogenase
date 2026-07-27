#!/usr/bin/env python3
import json
import hashlib
import uuid
import math
from datetime import datetime

class GhidanCapacityGate:
    def __init__(self, hbar=1.0, c=1.0, A_0=1.0):
        self.hbar = hbar
        self.c = c
        self.A_0 = A_0  # Elementærareal (l_0^2)
        self.prev_witness_hash = "sha256:000205cddc4b7753c7a64c61cc3070cc"

    def evaluate_capacity(self, E, r):
        """
        Kjerneoperator: Ghidan Capacity Conservation Framework
        Utleder G og Schwarzschild fra rå informasjonsbelastning.
        """
        candidate_id = f"ghidan_cell_{uuid.uuid4().hex[:6]}"
        
        # 1. Utled entropic demand: I_dem = E / (hbar * c)
        I_dem = E / (self.hbar * self.c)
        
        # 2. Beregn last-skalaen kappa: kappa = I_dem * A_0
        kappa = I_dem * self.A_0
        
        # 3. Beregn radial informasjonsbelastning L = 2*kappa / r
        if r <= 0:
            return "KILL", "KILL_SINGULARITY: Radius <= 0. Grid structure physically crushed.", {}

        L = (2 * kappa) / r
        
        # 4. Beregn tilgjengelig lokal throughput amplitude: chi^2 = 1 - L
        chi_squared = 1.0 - L
        
        telemetry = {
            "energy": E,
            "radius": r,
            "I_dem": I_dem,
            "kappa": kappa,
            "load_L": L,
            "chi_squared": chi_squared
        }

        # --- GATENS EVALUERINGSLOGIKK (Fail-Closed) ---
        if chi_squared < 0:
            verdict = "KILL"
            reason = f"KILL_CAPACITY_OVERLOAD: Load L ({L:.2f}) > 1.0. Throughput amplitude is imaginary. Ontological collapse."
        elif math.isclose(chi_squared, 0.0, abs_tol=1e-5) or chi_squared == 0:
            verdict = "COMMIT"
            reason = f"COMMIT_HORIZON_SATURATION: chi^2 is 0. Grid capacity fully occupied by load. Horizon locked."
        elif L > 0.54: # Gjenbruk av din klassiske PR-terskel for økt asymmetri/stress
            verdict = "HOLD"
            reason = f"HOLD_HIGH_ADMISSIBILITY_STRESS: Load L ({L:.2f}) >= 0.54. Emergent gravity warping time dilation."
        else:
            verdict = "OPEN"
            reason = "OPEN_FLAT_PROPAGATION: Low informational load. Grid propagation is free."

        witness = self.generate_witness_entry(candidate_id, verdict, reason, telemetry)
        return verdict, reason, witness

    def generate_witness_entry(self, candidate_id, verdict, reason, telemetry):
        event = {
            "framework": "GHIDAN_CAPACITY_CONSERVATION",
            "candidate_id": candidate_id,
            "verdict": verdict,
            "reason_code": reason.split(":")[0],
            "grid_metrics": {k: round(v, 4) for k, v in telemetry.items()},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prev_hash": self.prev_witness_hash
        }
        canonical = json.dumps(event, sort_keys=True)
        event_hash = hashlib.sha256(canonical.encode()).hexdigest()
        event["witness_hash"] = f"sha256:{event_hash}"
        self.prev_witness_hash = event["witness_hash"]
        return event

if __name__ == "__main__":
    gate = GhidanCapacityGate()
    
    # Fire fysiske tilstander testes foran den absolutte gaten
    grid_scenarios = {
        "SCENARIO_1: EMPTY_GRID_FLAT_SPACE": {"E": 0.00, "r": 10.0},
        "SCENARIO_2: MODERATE_MATTER_WARPING": {"E": 1.50, "r": 10.0},
        "SCENARIO_3: PR_CRITICAL_STRESS_ZONE": {"E": 3.00, "r": 10.0}, # L = 2*3/10 = 0.60
        "SCENARIO_4: HORIZON_METN_COMMIT": {"E": 5.00, "r": 10.0},     # L = 2*5/10 = 1.00
        "SCENARIO_5: OVER_SATURATED_SINGULARITY": {"E": 8.00, "r": 10.0} # L = 2*8/10 = 1.60 -> KILL
    }
    
    print("="*80)
    print("KY-ROX GHIDAN CAPACITY INTEGRATION — RUNTIME RUN: ghidan_gate_v0_1")
    print("="*80)
    
    for name, params in grid_scenarios.items():
        print(f"\n[EVALUATING] {name}")
        verd, reas, wit = gate.evaluate_capacity(params["E"], params["r"])
        print(f"  VERDICT     : {verd}")
        print(f"  REASON      : {reas}")
        print(f"  WITNESS HASH: {wit.get('witness_hash')}")
        print(f"  PREV HASH   : {wit.get('prev_hash')}")
        print(f"  METRICS     : {json.dumps(wit['grid_metrics'])}")
        print("-" * 60)
    print("="*80)
