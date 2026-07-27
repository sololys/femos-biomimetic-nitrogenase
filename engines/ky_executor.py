import hashlib
import json
import uuid
from typing import List, Dict, Any, Optional

class KYSyntaxError(Exception): pass
class KYTypeError(Exception): pass
class KYAdmissibilityError(Exception): pass

class StrictKYParser:
    TOKEN_MAP = {"○": "RAW", "◇": "ESTIMATE", "□": "STRUCT", "⬡": "VIABILITY", "◉": "COMMITTED"}
    GATE_MAP = {"▶": "REQUEST_COMMIT", "⏸": "HOLD", "✕": "KILL"}

    def __init__(self, expression: str):
        self.expr = expression.replace(" ", "")
        self.pos = 0

    def peek(self) -> str:
        return self.expr[self.pos] if self.pos < len(self.expr) else ""

    def consume(self, expected: str = None) -> str:
        char = self.peek()
        if not char:
            raise KYSyntaxError("KILL/SYNTAX_VIOLATION: Uventet slutt på uttrykk.")
        if expected and char != expected:
            raise KYSyntaxError(f"KILL/SYNTAX_VIOLATION: Forventet '{expected}', fikk '{char}'")
        self.pos += 1
        return char

    def parse(self) -> Dict[str, Any]:
        try:
            self.consume("⟲")
            self.consume("(")
            
            nodes = []
            char = self.consume()
            if char not in self.TOKEN_MAP:
                raise KYSyntaxError(f"KILL/SYNTAX_VIOLATION: Ugyldig nodetegn: '{char}'")
            nodes.append(self.TOKEN_MAP[char])

            while self.peek() == "→":
                self.consume("→")
                char = self.consume()
                if char not in self.TOKEN_MAP:
                    raise KYSyntaxError(f"KILL/SYNTAX_VIOLATION: Ugyldig nodetegn etter pil: '{char}'")
                nodes.append(self.TOKEN_MAP[char])

            self.consume(")")

            modifiers = []
            while self.peek() in ("#", "!"):
                modifiers.append(self.consume())

            gate_char = self.consume()
            if gate_char not in self.GATE_MAP:
                raise KYSyntaxError(f"KILL/SYNTAX_VIOLATION: Ugyldig gate-avslutning: '{gate_char}'")
            
            if self.pos < len(self.expr):
                raise KYSyntaxError(f"KILL/SYNTAX_VIOLATION: Uventet støy etter gate-terminering")

            return {
                "nodes": nodes,
                "modifiers": modifiers,
                "declared_gate": self.GATE_MAP[gate_char]
            }
        except Exception as e:
            raise KYSyntaxError(str(e))

class KYExecutor:
    LEGAL_TRANSITIONS = {
        ("RAW", "ESTIMATE"), ("ESTIMATE", "STRUCT"), 
        ("STRUCT", "VIABILITY"), ("VIABILITY", "COMMITTED")
    }

    def __init__(self):
        pass

    def run_pipeline(self, raw_input: Dict[str, Any], ky_expression: str, audit_evidence: Optional[Dict] = None, witness_evidence: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            parser = StrictKYParser(ky_expression)
            ast = parser.parse()
        except KYSyntaxError as e:
            return {"GATE": "KILL", "Delta_K": 1, "STATE": "KILL", "ERROR": str(e)}

        nodes = ast["nodes"]

        # Valider hele transaksjonssekvensen strengt før mutasjon
        current_check = nodes[0]
        for next_check in nodes[1:]:
            if (current_check, next_check) not in self.LEGAL_TRANSITIONS:
                return {"GATE": "KILL", "Delta_K": 1, "STATE": "KILL", "ERROR": f"KILL/TYPE_VIOLATION: {current_check} -> {next_check}"}
            current_check = next_check

        commit_requested = "COMMITTED" in nodes
        loop_nodes = [n for n in nodes if n != "COMMITTED"] if commit_requested else nodes

        current_state = "RAW"
        history_log = []
        prev_hash = "0" * 64  # 64 heksadesimale tegn genesis-hash

        for i, next_state in enumerate(loop_nodes):
            if i > 0:
                current_state = next_state

            canonical_payload = json.dumps({
                "sequence_no": len(history_log) + 1,
                "state": current_state,
                "prev_hash": prev_hash
            }, sort_keys=True)
            
            payload_hash = hashlib.sha256(canonical_payload.encode()).hexdigest()
            event_hash = hashlib.sha256(f"{prev_hash}{payload_hash}".encode()).hexdigest()
            
            history_log.append({
                "sequence_no": len(history_log) + 1,
                "prev_hash": prev_hash,
                "payload_hash": payload_hash,
                "event_hash": event_hash,
                "state": current_state
            })
            prev_hash = event_hash

        proposed_fields = raw_input.get("fields", [])
        admissible_fields = [f for f in proposed_fields if not f.startswith("invalid_")]
        delta_k = len(proposed_fields) - len(admissible_fields)

        audit_pass = audit_evidence is not None and audit_evidence.get("valid", False)
        witness_valid = witness_evidence is not None and witness_evidence.get("signature") == "VERIFIED_WITNESS"
        
        gate_status = "HOLD"
        if delta_k == 0 and ast["declared_gate"] == "REQUEST_COMMIT":
            if audit_pass and witness_valid:
                gate_status = "OPEN"
            else:
                gate_status = "HOLD"
        elif delta_k > 0 or ast["declared_gate"] == "KILL":
            gate_status = "KILL"

        if gate_status == "OPEN" and commit_requested:
            current_state = "COMMITTED"
            canonical_payload = json.dumps({
                "sequence_no": len(history_log) + 1,
                "state": current_state,
                "prev_hash": prev_hash
            }, sort_keys=True)
            payload_hash = hashlib.sha256(canonical_payload.encode()).hexdigest()
            event_hash = hashlib.sha256(f"{prev_hash}{payload_hash}".encode()).hexdigest()
            history_log.append({
                "sequence_no": len(history_log) + 1,
                "prev_hash": prev_hash,
                "payload_hash": payload_hash,
                "event_hash": event_hash,
                "state": current_state
            })
            prev_hash = event_hash

        return {
            "GATE": gate_status,
            "Delta_K": delta_k,
            "STATE": current_state,
            "LOG_SIZE": len(history_log),
            "LAST_HASH": prev_hash
        }
