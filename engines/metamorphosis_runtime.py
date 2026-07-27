"""
=====================================================================
METAMORPHOSIS TRANSITION RUNTIME (v0.2.1)
Universal Governed State Transition Engine & Adapter Architecture
Modul: metamorphosis_runtime.py
=====================================================================
"""

from enum import Enum, auto
import hashlib
import time
import uuid
import numpy as np

class AuthorityDecision(Enum):
    OPEN = "OPEN"
    HOLD = "HOLD"
    KILL = "KILL"

class ContainmentMode(Enum):
    NONE = "NONE"
    ISOLATE = "ISOLATE"
    QUARANTINE = "QUARANTINE"

class LifecycleStage(Enum):
    HOT = "HOT"       # Active state in memory
    WARM = "WARM"     # History log / cache
    COLD = "COLD"     # Immutable long-term archive (GDPR / Audit)

class RosettaBinding:
    """Binder brukerhandling, matematisk objekt, kernel-operasjon og audit-logg til én ubrytelig ID."""
    def __init__(self, user_intent: str, math_object: dict, kernel_op: str):
        self.binding_id = str(uuid.uuid4())
        self.user_intent = user_intent
        self.math_object = math_object
        self.kernel_op = kernel_op
        self.timestamp = time.time_ns()
        
        # Calculate cryptographic Rosetta Signature
        raw = f"{self.binding_id}:{self.user_intent}:{self.kernel_op}:{self.timestamp}"
        self.rosetta_signature = hashlib.sha256(raw.encode()).hexdigest()

class OrphanBuffer:
    """Isolerer kandidater som refererer til manglende avhengigheter (Dependency Engine)."""
    def __init__(self):
        self.buffer = {}

    def register_candidate(self, candidate_id: str, dependencies: list[str]) -> bool:
        missing = [dep for dep in dependencies if dep not in self.buffer and not dep.startswith("RESOLVED_")]
        if missing:
            self.buffer[candidate_id] = {"dependencies": missing, "status": "ORPHANED"}
            return False # Missing dependencies -> Orphaned
        self.buffer[candidate_id] = {"dependencies": [], "status": "READY"}
        return True

    def resolve_dependency(self, dep_id: str):
        resolved_key = f"RESOLVED_{dep_id}"
        for cand_id, data in self.buffer.items():
            if dep_id in data["dependencies"]:
                data["dependencies"].remove(dep_id)
                if not data["dependencies"]:
                    data["status"] = "READY"

class SourceBackpressureController:
    """Måler tilførselstrykk per kilde og stenger vinduet ved overproduksjon (ZERO_WINDOW)."""
    def __init__(self, max_rate_per_sec=20):
        self.max_rate = max_rate_per_sec
        self.source_rates = {}

    def check_capacity(self, source_id: str) -> bool:
        now = time.time()
        if source_id not in self.source_rates:
            self.source_rates[source_id] = []
        
        # Prune calls older than 1 second
        self.source_rates[source_id] = [t for t in self.source_rates[source_id] if now - t < 1.0]

        if len(self.source_rates[source_id]) >= self.max_rate:
            return False # ZERO_WINDOW triggered
        
        self.source_rates[source_id].append(now)
        return True

class DualPhaseWitnessLedger:
    """
    Dual-Phase Witness:
    W_pre  = Authorization witness seal (before execution boundary)
    W_post = Observed runtime result seal (after execution boundary)
    Ensures non-repudiable audit trails without causal backreaction (W_post !-> W_pre).
    """
    def __init__(self):
        self.ledger = []

    def commit_pre_witness(self, binding: RosettaBinding, decision: AuthorityDecision, containment: ContainmentMode) -> str:
        timestamp = time.time_ns()
        raw = f"PRE:{timestamp}:{binding.rosetta_signature}:{decision.value}:{containment.value}"
        w_pre_hash = hashlib.sha256(raw.encode()).hexdigest()
        self.ledger.append({
            "phase": "PRE",
            "binding_id": binding.binding_id,
            "w_pre_hash": w_pre_hash,
            "decision": decision.value,
            "containment": containment.value,
            "timestamp": timestamp
        })
        return w_pre_hash

    def commit_post_witness(self, w_pre_hash: str, runtime_observation: dict) -> str:
        timestamp = time.time_ns()
        raw = f"POST:{timestamp}:{w_pre_hash}:{runtime_observation}"
        w_post_hash = hashlib.sha256(raw.encode()).hexdigest()
        self.ledger.append({
            "phase": "POST",
            "w_pre_hash": w_pre_hash,
            "w_post_hash": w_post_hash,
            "observation": runtime_observation,
            "timestamp": timestamp
        })
        return w_post_hash

class MetamorphosisCoreEngine:
    def __init__(self):
        self.orphan_buffer = OrphanBuffer()
        self.backpressure = SourceBackpressureController(max_rate_per_sec=15)
        self.witness_ledger = DualPhaseWitnessLedger()
        self.re_admission_pool = {}

    def evaluate_transition(self, source_id: str, binding: RosettaBinding, dependencies: list[str], pi_risk: float, is_bot=False) -> dict:
        """
        Full Metamorphosis State Transition Pipeline
        """
        # 1. Backpressure Check
        if not self.backpressure.check_capacity(source_id):
            # ZERO_WINDOW triggered
            w_pre = self.witness_ledger.commit_pre_witness(binding, AuthorityDecision.HOLD, ContainmentMode.QUARANTINE)
            return {
                "decision": AuthorityDecision.HOLD.value,
                "containment": ContainmentMode.QUARANTINE.value,
                "reason_code": "ZERO_WINDOW_BACKPRESSURE",
                "reason_detail": "Source production rate exceeded capacity window",
                "w_pre": w_pre
            }

        # 2. Dependency & Orphan Check
        is_ready = self.orphan_buffer.register_candidate(binding.binding_id, dependencies)
        if not is_ready:
            w_pre = self.witness_ledger.commit_pre_witness(binding, AuthorityDecision.HOLD, ContainmentMode.QUARANTINE)
            return {
                "decision": AuthorityDecision.HOLD.value,
                "containment": ContainmentMode.QUARANTINE.value,
                "reason_code": "ORPHANED_DEPENDENCY",
                "reason_detail": "Candidate isolated due to unresolved antecedent state dependencies",
                "w_pre": w_pre
            }

        # 3. Authority Gate & Adversarial Typing (Human vs Bot)
        if is_bot and pi_risk > 0.5:
            # Adversarial source -> Minimal response, isolated in shadow DAG
            w_pre = self.witness_ledger.commit_pre_witness(binding, AuthorityDecision.KILL, ContainmentMode.ISOLATE)
            return {
                "decision": AuthorityDecision.KILL.value,
                "containment": ContainmentMode.ISOLATE.value,
                "reason_code": "ADVERSARIAL_ISOLATION",
                "reason_detail": "Minimal silent containment engaged",
                "w_pre": w_pre
            }

        # Human / Validated Operator Evaluation
        if pi_risk < 0.4:
            decision = AuthorityDecision.OPEN
            containment = ContainmentMode.NONE
            reason_code = "TRANSITION_AUTHORIZED"
            reason_detail = "State transformation passed all policy invariants"
        elif pi_risk < 0.8:
            decision = AuthorityDecision.HOLD
            containment = ContainmentMode.QUARANTINE
            reason_code = "RISK_COOLING_HOLD"
            reason_detail = "Transition held for re-admission or manual review"
            self.re_admission_pool[binding.binding_id] = binding
        else:
            decision = AuthorityDecision.KILL
            containment = ContainmentMode.ISOLATE
            reason_code = "EPISOMIC_RISK_KILL"
            reason_detail = "Type safety invariant breach"

        # 4. Pre-Commit Witness
        w_pre_hash = self.witness_ledger.commit_pre_witness(binding, decision, containment)

        # 5. Execution Boundary & Post-Commit Witness
        runtime_obs = {"executed": (decision == AuthorityDecision.OPEN), "pi_risk": pi_risk}
        w_post_hash = self.witness_ledger.commit_post_witness(w_pre_hash, runtime_obs)

        return {
            "decision": decision.value,
            "containment": containment.value,
            "reason_code": reason_code,
            "reason_detail": reason_detail,
            "w_pre": w_pre_hash,
            "w_post": w_post_hash,
            "rosetta_signature": binding.rosetta_signature
        }

# --- VERTICAL ADAPTER IMPLEMENTATIONS ---

class MetamorphosisShadowPilotAdapter:
    """Primary Commercial Pilot Mode: Read-only / Dry-run audit service."""
    def __init__(self, core_engine: MetamorphosisCoreEngine):
        self.core = core_engine

    def audit_external_transition(self, source_id: str, intent: str, state_payload: dict, pi_risk=0.1) -> dict:
        binding = RosettaBinding(user_intent=intent, math_object=state_payload, kernel_op="SHADOW_AUDIT_DRY_RUN")
        return self.core.evaluate_transition(source_id, binding, dependencies=[], pi_risk=pi_risk)

class FinancePaymentStateAdapter:
    """Fail-Closed Transaction Double-Check & Payment Locking."""
    def __init__(self, core_engine: MetamorphosisCoreEngine):
        self.core = core_engine

    def authorize_payment(self, source_account: str, dest_account: str, amount: float, pi_risk: float) -> dict:
        payload = {"from": source_account, "to": dest_account, "amount": amount}
        binding = RosettaBinding(user_intent="PAYMENT_TRANSFER", math_object=payload, kernel_op="FINANCE_TX_LOCK")
        return self.core.evaluate_transition(source_account, binding, dependencies=[], pi_risk=pi_risk)

if __name__ == "__main__":
    print("=== TESTING METAMORPHOSIS TRANSITION RUNTIME v0.2.1 ===")
    engine = MetamorphosisCoreEngine()
    shadow_adapter = MetamorphosisShadowPilotAdapter(engine)
    finance_adapter = FinancePaymentStateAdapter(engine)

    # Test 1: Shadow Pilot Read-Only Audit
    res1 = shadow_adapter.audit_external_transition("client_tenant_99", "UPDATE_USER_ROLE", {"user": "alice", "role": "admin"})
    print("\nTest 1 (Shadow Audit Pilot):")
    print(f"  Decision: {res1['decision']} | Containment: {res1['containment']}")
    print(f"  Pre-Witness:  {res1['w_pre'][:16]}...")
    print(f"  Post-Witness: {res1['w_post'][:16]}...")

    # Test 2: Finance Payment Authorization
    res2 = finance_adapter.authorize_payment("ACC_001", "ACC_002", 50000.0, pi_risk=0.15)
    print("\nTest 2 (Finance Payment Adapter):")
    print(f"  Decision: {res2['decision']} | Reason: {res2['reason_code']}")
    print(f"  Rosetta Binding: {res2['rosetta_signature'][:16]}...")

    # Test 3: Adversarial Bot Injection (Minimal response & ISOLATE containment)
    binding_bot = RosettaBinding("SPAM_ATTACK", {"payload": "bot_data"}, "AGENT_INJECTION")
    res3 = engine.evaluate_transition("bot_ip_666", binding_bot, dependencies=[], pi_risk=0.9, is_bot=True)
    print("\nTest 3 (Adversarial Bot Containment):")
    print(f"  Decision: {res3['decision']} | Containment: {res3['containment']}")
    print(f"  Reason Detail: {res3['reason_detail']}")
