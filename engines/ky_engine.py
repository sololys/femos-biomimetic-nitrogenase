import hashlib
import json
import sys

TRANSITIONS = {
    "RAW": "ESTIMATE",
    "ESTIMATE": "STRUCT",
    "STRUCT": "VIABILITY",
    "VIABILITY": "COMMITTED"
}

class KYEngine:
    def __init__(self):
        self.state = "RAW"
        self.history = []

    def transition(self, target_state):
        expected = TRANSITIONS.get(self.state)
        if target_state != expected:
            self.state = "KILL"
            return False
        self.state = target_state
        return True

    def evaluate_omega(self, candidate_data, delta_k):
        if self.state != "STRUCT":
            self.state = "KILL"
            return {"GATE": "KILL", "Delta K": delta_k, "STATE": self.state}

        if delta_k > 0:
            self.state = "KILL"
            return {"GATE": "KILL", "Delta K": delta_k, "STATE": self.state}
        elif delta_k == 0:
            if self.transition("VIABILITY") and self.transition("COMMITTED"):
                record = {"data": candidate_data, "delta_k": delta_k}
                prev_hash = self.history[-1]["hash"] if self.history else "0" * 64
                block = json.dumps(record, sort_keys=True) + prev_hash
                h = hashlib.sha256(block.encode()).hexdigest()
                self.history.append({"record": record, "hash": h})
                return {"GATE": "OPEN", "Delta K": delta_k, "STATE": self.state}
        
        self.state = "HOLD"
        return {"GATE": "HOLD", "Delta K": delta_k, "STATE": self.state}

if __name__ == "__main__":
    engine = KYEngine()
    engine.transition("ESTIMATE")
    engine.transition("STRUCT")
    res = engine.evaluate_omega({"vector": "P_eq_NP_candidate"}, delta_k=0.0)
    print(f"GATE={res['GATE']}, Delta K={res['Delta K']}, STATE={res['STATE']}")
