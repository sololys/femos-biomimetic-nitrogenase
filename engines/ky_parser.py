import hashlib
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional, Set

@dataclass(frozen=True)
class TransitionPlan:
    nodes: Tuple[str, ...]
    modifiers: Set[str]
    declared_gate: str

class KYParserV3:
    LEGAL_TRANSITIONS = {
        ("RAW", "ESTIMATE"),
        ("ESTIMATE", "STRUCT"),
        ("STRUCT", "VIABILITY"),
        ("VIABILITY", "COMMITTED")
    }
    
    SYMBOL_MAP = {
        "○": "RAW",
        "◇": "ESTIMATE",
        "□": "STRUCT",
        "⬡": "VIABILITY",
        "◉": "COMMITTED"
    }

    def parse(self, expression: str) -> TransitionPlan:
        expr = expression.strip()
        
        # 1. EBNF-streng sjekk for startoperatør og parenteser
        if not expr.startswith("⟲"):
            raise ValueError("KILL/SYNTAX_VIOLATION: Mangler start-operatør ⟲")
        
        if expr.count("(") != 1 or expr.count(")") != 1:
            raise ValueError("KILL/MALFORMED_PIPELINE: Ubalanserte parenteser")
        
        paren_start = expr.index("(")
        paren_end = expr.index(")")
        if paren_start > paren_end:
            raise ValueError("KILL/MALFORMED_PIPELINE")

        body = expr[paren_start + 1:paren_end].strip()
        modifiers_part = expr[paren_end + 1:].strip()

        # 2. Tokenisering av noder via piler
        parts = [p.strip() for p in body.split("→")]
        nodes = []
        for p in parts:
            if p not in self.SYMBOL_MAP:
                raise ValueError(f"KILL/SYNTAX_VIOLATION: Ukjent token '{p}'")
            nodes.append(self.SYMBOL_MAP[p])

        if len(nodes) < 2:
            raise ValueError("KILL/TYPE_VIOLATION: For få noder i sekvensen")

        # 3. Validering mot overgangsmatrisen
        for i in range(len(nodes) - 1):
            trans = (nodes[i], nodes[i+1])
            if trans not in self.LEGAL_TRANSITIONS:
                raise ValueError(f"KILL/TYPE_VIOLATION: Ulovlig overgang {trans[0]} -> {trans[1]}")

        # 4. Modifikator-parser
        mods = set()
        for char in modifiers_part:
            if char in {"#", "!", "▶"}:
                mods.add(char)
            elif char.isspace():
                continue
            else:
                raise ValueError(f"KILL/SYNTAX_VIOLATION: Ukjent modifikator '{char}'")

        if "▶" in mods and "!" not in mods:
            raise ValueError("KILL/GATE_BYPASS: Utførelse uten portdeklarasjon (!)")

        if "◉" in nodes and "#" not in mods:
            raise ValueError("KILL/WITNESS_REQUIRED: COMMITTED krever gyldig witness (#)")

        return TransitionPlan(nodes=tuple(nodes), modifiers=mods, declared_gate="OPEN" if "!" in mods else "HOLD")

class KYRuntimeV3:
    def __init__(self):
        self.event_log: List[Dict[str, Any]] = []
        self.sequence_no = 0

    def _compute_delta_k(self, audit_pass: bool) -> float:
        # Reell beregning: Hvis audit feiler, er residualen positiv (1.0). Ellers 0.0.
        return 0.0 if audit_pass else 1.0

    def execute(self, expression: str, audit_payload: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        parser = KYParserV3()
        try:
            plan = parser.parse(expression)
        except ValueError as e:
            print(f"[CRITICAL TERMINATION] {e}")
            print("GATE=KILL")
            print("DELTA_K=1.0")
            print("STATE=KILL")
            return {"GATE": "KILL", "DELTA_K": "1.0", "STATE": "KILL"}

        audit_pass = audit_payload is not None and audit_payload.get("valid", False)
        witness_valid = "#" in plan.modifiers and audit_payload is not None and "witness_signature" in audit_payload

        delta_k = self._compute_delta_k(audit_pass)

        # Omega-port evaluering
        if delta_k > 0.0 or not audit_pass:
            print("GATE=HOLD")
            print(f"DELTA_K={delta_k}")
            print("STATE=HOLD")
            return {"GATE": "HOLD", "DELTA_K": str(delta_k), "STATE": "HOLD"}

        if plan.nodes[-1] == "COMMITTED" and not witness_valid:
            print("[CRITICAL TERMINATION] KILL/WITNESS_REQUIRED: Ugyldig eller manglende witness-signatur")
            print("GATE=KILL")
            print("DELTA_K=1.0")
            print("STATE=KILL")
            return {"GATE": "KILL", "DELTA_K": "1.0", "STATE": "KILL"}

        # WORM Append-only Logg med full hendelsestrack
        self.sequence_no += 1
        prev_hash = self.event_log[-1]["event_hash"] if self.event_log else "0" * 64
        payload = f"{self.sequence_no}:{plan.nodes[-1]}:OPEN:{delta_k}"
        payload_hash = hashlib.sha256(payload.encode()).hexdigest()
        event_hash = hashlib.sha256(f"{prev_hash}{payload_hash}".encode()).hexdigest()

        self.event_log.append({
            "sequence_no": self.sequence_no,
            "prev_hash": prev_hash,
            "payload_hash": payload_hash,
            "event_hash": event_hash
        })

        print("GATE=OPEN")
        print(f"DELTA_K={delta_k}")
        print(f"STATE={plan.nodes[-1]}")
        return {"GATE": "OPEN", "DELTA_K": str(delta_k), "STATE": plan.nodes[-1]}

if __name__ == "__main__":
    runtime = KYRuntimeV3()
    print("--- Test: Gyldig kjede ---")
    runtime.execute("⟲ (○ → ◇ → □ → ⬡ → ◉) # ! ▶", {"valid": True, "witness_signature": "SIG_99"})
