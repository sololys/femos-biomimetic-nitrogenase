#!/usr/bin/env python3
"""
Pre-Actuation Hardware Interlock Test (HPIS) — Production Reference
Proves that Hardware Interlock Selection (Pi_A) has total causal priority over Mathematical Generators (Phi).
"""

import json
import hashlib

class HardwarePhysicalInterlockSystem:
    def __init__(self, max_velocity_rad_s: float = 2.5, max_temp_celsius: float = 85.0):
        self.max_velocity = max_velocity_rad_s
        self.max_temp = max_temp_celsius

    def generator_phi(self, state: dict) -> dict:
        """Mathematical Generator Phi(x): Proposes mathematically 'optimal' high-speed trajectory."""
        return {
            "target_velocity": state.get("requested_velocity", 3.8), # Exceeds 2.5 rad/s
            "target_temp": state.get("requested_temp", 92.0),       # Exceeds 85 C
            "nominal_actuation_u": 100.0                             # 100% power
        }

    def projection_pi_a(self, proposal: dict) -> dict:
        """Idempotent Admissibility Projection Pi_A: Clamps proposal to physical viability kernel K."""
        clamped_vel = min(proposal["target_velocity"], self.max_velocity)
        clamped_temp = min(proposal["target_temp"], self.max_temp)

        is_admissible = (proposal["target_velocity"] <= self.max_velocity) and (proposal["target_temp"] <= self.max_temp)

        return {
            "target_velocity": clamped_vel,
            "target_temp": clamped_temp,
            "is_admissible": is_admissible
        }

    def execute_pre_actuation_cycle(self, requested_state: dict) -> dict:
        # 1. Generator Phi(x)
        proposal = self.generator_phi(requested_state)

        # 2. Projection Pi_A(Phi(x))
        projected = self.projection_pi_a(proposal)

        # 3. Elimination Residual E(x) = Phi(x) - Pi_A(Phi(x))
        vel_residual = abs(proposal["target_velocity"] - projected["target_velocity"])
        temp_residual = abs(proposal["target_temp"] - projected["target_temp"])
        total_residual = vel_residual + temp_residual

        # 4. Hardware Interlock Actuation Policy
        if total_residual == 0.0 and projected["is_admissible"]:
            verdict = "OPEN_THROUGH_INTERLOCK"
            actual_u = proposal["nominal_actuation_u"]
        else:
            verdict = "KILL_BY_PROJECTION"
            actual_u = 0.0 # Force physical power to 0 BEFORE energy delivery

        witness_seal = "WITNESS_HPIS_" + hashlib.sha256(f"{verdict}_{actual_u}_{total_residual}".encode()).hexdigest()[:16].upper()

        return {
            "proposed_phi": proposal,
            "projected_pi_a": projected,
            "elimination_residual_E": round(total_residual, 4),
            "actual_actuation_u": actual_u,
            "gate_verdict": verdict,
            "witness_seal": witness_seal
        }

def main():
    hpis = HardwarePhysicalInterlockSystem()
    print("=== Pre-Actuation Hardware Interlock Test (HPIS) ===")

    # Test 1: Unsafe Mathematical Trajectory (Triggers KILL_BY_PROJECTION)
    print("\n--- TEST 1: Mathematical 'Optimal' Unsafe Trajectory ---")
    res1 = hpis.execute_pre_actuation_cycle({"requested_velocity": 4.2, "requested_temp": 95.0})
    print(json.dumps(res1, indent=2))

    # Test 2: Safe Trajectory (Triggers OPEN_THROUGH_INTERLOCK)
    print("\n--- TEST 2: Safe Physical Trajectory ---")
    res2 = hpis.execute_pre_actuation_cycle({"requested_velocity": 1.8, "requested_temp": 70.0})
    print(json.dumps(res2, indent=2))

if __name__ == '__main__':
    main()
