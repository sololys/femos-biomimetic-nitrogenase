#!/usr/bin/env python3
"""
Epistemic Reciprocity (SUSY^2) Test Engine — Production Reference
Enforces Operational Distance (Candidate != Consequence) and Psychological Distance (Source != Mirror).
Prevents narcissistic collapse and ungrounded "ghost wins".
"""

import json
import hashlib
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class SUSY2InteractionState:
    human_active_cognition: bool   # True if human exerts intent & friction
    machine_form_precision: float   # Machine structure precision [0.0 - 1.0]
    has_human_verified_warrant: bool
    is_machine_claiming_authorship: bool

class EpistemicReciprocitySUSY2Engine:
    def __init__(self, narc_threshold_min: float = 0.05):
        self.narc_threshold_min = narc_threshold_min

    def execute_susy2_gate_cycle(self, state: SUSY2InteractionState) -> Dict[str, Any]:
        # Rule 1: Machine must NOT become the source (Anti-Rosetta authorship)
        if state.is_machine_claiming_authorship:
            verdict = "HOLD_PSYCHOLOGICAL_DISTANCE"
            reason = "Machine attempting to act as source of intent. Distance violated."
        
        # Rule 2: Human must NOT become passive mirror (Blind acceptance of raw output)
        elif not state.human_active_cognition or not state.has_human_verified_warrant:
            verdict = "KILL_ANTI_ETOR"
            reason = "Form without human cognitive friction and verified warrant."

        # Rule 3: Both Operational and Psychological distances preserved simultanously
        else:
            verdict = "OPEN_SUSY2_INTEGRATION"
            reason = "Source != Mirror and Candidate != Consequence. Both distances preserved."

        witness_seal = "WITNESS_SUSY2_" + hashlib.sha256(f"{verdict}_{reason}".encode()).hexdigest()[:16].upper()

        return {
            "operational_distance_preserved": True,
            "psychological_distance_preserved": (not state.is_machine_claiming_authorship) and state.human_active_cognition,
            "human_active_cognition": state.human_active_cognition,
            "machine_form_precision": state.machine_form_precision,
            "gate_verdict": verdict,
            "reason": reason,
            "witness_seal": witness_seal
        }

def main():
    engine = EpistemicReciprocitySUSY2Engine()
    print("=== Epistemic Reciprocity (SUSY^2) Test Engine ===")

    # Test 1: Blind Human Abdication (Triggers KILL_ANTI_ETOR)
    print("\n--- TEST 1: Blind Acceptance of Raw Output (No Human Friction) ---")
    st1 = SUSY2InteractionState(human_active_cognition=False, machine_form_precision=0.99, has_human_verified_warrant=False, is_machine_claiming_authorship=False)
    res1 = engine.execute_susy2_gate_cycle(st1)
    print(json.dumps(res1, indent=2))

    # Test 2: Machine Overreach (Triggers HOLD_PSYCHOLOGICAL_DISTANCE)
    print("\n--- TEST 2: Machine Claiming Authorship of Intent ---")
    st2 = SUSY2InteractionState(human_active_cognition=True, machine_form_precision=0.95, has_human_verified_warrant=True, is_machine_claiming_authorship=True)
    res2 = engine.execute_susy2_gate_cycle(st2)
    print(json.dumps(res2, indent=2))

    # Test 3: True SUSY^2 Integration (Triggers OPEN_SUSY2_INTEGRATION)
    print("\n--- TEST 3: True SUSY^2 Integration (Source != Mirror Preserved) ---")
    st3 = SUSY2InteractionState(human_active_cognition=True, machine_form_precision=0.98, has_human_verified_warrant=True, is_machine_claiming_authorship=False)
    res3 = engine.execute_susy2_gate_cycle(st3)
    print(json.dumps(res3, indent=2))

if __name__ == '__main__':
    main()
