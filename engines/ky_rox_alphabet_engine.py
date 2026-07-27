"""
=====================================================================
KY–ROX ALPHABET v0.1 :: State Machine, Validator & Grammar Engine
Modul: ky_rox_alphabet.py
Formål: Deterministisk tilstandsovergang og ROX-symmetrivalidering
=====================================================================
"""

from enum import Enum, auto
import hashlib
import time

class State(Enum):
    RAW = "○"          # Uformet inngang
    CANDIDATE = "◇"    # Kandidat generert av dynamikk / ROX
    STRUCT = "□"       # Strukturert og grammatisk admissibel kandidat
    AUTHORIZED = "⬡"   # Autorisert, commit-klar struktur
    REALIZED = "◉"     # Realisert konsekvens. Witness-forseglet
    KILLED = "⊥"       # Terminert kandidatbane. Ingen videre realisering

class Decision(Enum):
    OPEN = auto()
    HOLD = auto()
    KILL = auto()
    COMMIT = auto()

class KYRoxGrammarEngine:
    def __init__(self, tau_open=0.4, tau_kill=0.85):
        self.current_state = State.RAW
        self.tau_open = tau_open
        self.tau_kill = tau_kill
        self.witness_ledger = []
        self.readmission_pending = False

    def rox_transform(self, x: int, mask: int) -> int:
        """ROX_m(x) = x ^ m"""
        return x ^ mask

    def check_rox_identity(self, x: int, mask_pass1: int, mask_pass2: int) -> tuple[bool, bool]:
        """
        Sjekker ROX_OK: ROX_m(ROX_m(x)) == x
        og MASK_FROZEN: mask_pass1 == mask_pass2
        """
        mask_frozen = (mask_pass1 == mask_pass2)
        c_t = self.rox_transform(x, mask_pass1)
        returned_x = self.rox_transform(c_t, mask_pass2)
        rox_ok = (returned_x == x) and mask_frozen
        return rox_ok, mask_frozen

    def evaluate_plasma_risk(self, pi_t: float) -> str:
        """
        Plasma-laget:
        pi_t < tau_open         => PLASMA_OPEN
        tau_open <= pi_t < kill => PLASMA_HOLD
        pi_t >= tau_kill        => PLASMA_KILL
        """
        if pi_t < self.tau_open:
            return "PLASMA_OPEN"
        elif pi_t < self.tau_kill:
            return "PLASMA_HOLD"
        else:
            return "PLASMA_KILL"

    def step_transition(self, next_state: State, x: int, mask_p1: int, mask_p2: int, pi_t: float) -> tuple[Decision, State, str]:
        """
        Kanonisk overgangsform og valideringsregel:
        Overgang er gyldig bare hvis:
        1. transition in T_KY (step-by-step)
        2. MASK_FROZEN == True
        3. ROX_OK == True
        4. PLASMA_KILL == False
        5. Omega gir OPEN for realisering, eller HOLD for re-admission
        """
        # Ulovlige overganger (Shortcut traps)
        valid_map = {
            State.RAW: [State.CANDIDATE, State.KILLED],
            State.CANDIDATE: [State.STRUCT, State.KILLED],
            State.STRUCT: [State.AUTHORIZED, State.KILLED],
            State.AUTHORIZED: [State.REALIZED, State.KILLED],
            State.REALIZED: [],
            State.KILLED: []
        }

        # Sjekk 1: Lovlig KY-bane
        if next_state not in valid_map[self.current_state]:
            reason = f"INVALID_SHORTCUT ({self.current_state.value} -> {next_state.value})"
            self.current_state = State.KILLED
            return Decision.KILL, State.KILLED, reason

        # Sjekk 2 & 3: ROX-identitet & Frossen maske
        rox_ok, mask_frozen = self.check_rox_identity(x, mask_p1, mask_p2)
        if not mask_frozen:
            self.current_state = State.KILLED
            return Decision.KILL, State.KILLED, "ROX_FAIL: MASK_MUTATED"
        if not rox_ok:
            self.current_state = State.KILLED
            return Decision.KILL, State.KILLED, "ROX_FAIL: IDENTITY_MISMATCH"

        # Sjekk 4: Plasma-risiko
        plasma_verdict = self.evaluate_plasma_risk(pi_t)
        if plasma_verdict == "PLASMA_KILL":
            self.current_state = State.KILLED
            return Decision.KILL, State.KILLED, "PLASMA_KILL_THRESHOLD_EXCEEDED"

        if plasma_verdict == "PLASMA_HOLD":
            self.readmission_pending = True
            return Decision.HOLD, self.current_state, "PLASMA_HOLD: RE_ADMISSION_REQUIRED"

        # Sjekk 5: Re-admission sjekk hvis frosset i HOLD
        if self.readmission_pending and next_state == State.REALIZED:
            # Kan ikke gå direkte til REALIZED fra HOLD uten ny godkjenning
            self.current_state = State.KILLED
            return Decision.KILL, State.KILLED, "INVALID_DELAYED_OPEN_WITHOUT_READMISSION"

        # Alle sjekker PASS -> OPEN & Advance State
        self.readmission_pending = False
        self.current_state = next_state

        if self.current_state == State.REALIZED:
            # Commit & Witness-forsegling
            self.seal_witness(x, pi_t)
            return Decision.COMMIT, State.REALIZED, "AUTHORIZED_COMMIT_WITNESS_SEALED"

        return Decision.OPEN, self.current_state, "KY_ROX_VALIDATED"

    def seal_witness(self, x: int, pi_t: float):
        timestamp = time.time_ns()
        payload = f"{timestamp}:{x}:{pi_t}:{self.current_state.value}"
        seal_hash = hashlib.sha256(payload.encode()).hexdigest()
        witness_entry = {
            "timestamp": timestamp,
            "state": self.current_state.value,
            "x": x,
            "pi_t": pi_t,
            "seal_hash": seal_hash
        }
        self.witness_ledger.append(witness_entry)

if __name__ == "__main__":
    print("=== RUNNING KY–ROX ALPHABET v0.1 GRAMMAR TEST ===")
    engine = KYRoxGrammarEngine()

    x_val = 0x4A7F
    mask = 0x99B3

    # Steg 1: RAW -> CANDIDATE (○ -> ◇)
    d1, s1, r1 = engine.step_transition(State.CANDIDATE, x_val, mask, mask, pi_t=0.1)
    print(f"Steg 1 (○ -> ◇): {d1.name} | Tilstand: {s1.value} ({s1.name}) | Årsak: {r1}")

    # Steg 2: CANDIDATE -> STRUCT (◇ -> □)
    d2, s2, r2 = engine.step_transition(State.STRUCT, x_val, mask, mask, pi_t=0.2)
    print(f"Steg 2 (◇ -> □): {d2.name} | Tilstand: {s2.value} ({s2.name}) | Årsak: {r2}")

    # Steg 3: STRUCT -> AUTHORIZED (□ -> ⬡)
    d3, s3, r3 = engine.step_transition(State.AUTHORIZED, x_val, mask, mask, pi_t=0.15)
    print(f"Steg 3 (□ -> ⬡): {d3.name} | Tilstand: {s3.value} ({s3.name}) | Årsak: {r3}")

    # Steg 4: AUTHORIZED -> REALIZED (⬡ -> ◉) (Commit & Witness)
    d4, s4, r4 = engine.step_transition(State.REALIZED, x_val, mask, mask, pi_t=0.1)
    print(f"Steg 4 (⬡ -> ◉): {d4.name} | Tilstand: {s4.value} ({s4.name}) | Årsak: {r4}")
    print(f"  Witness-forsegling hash: {engine.witness_ledger[-1]['seal_hash']}")

    print("\n--- TESTER SHORTCUT-FELT (INVALID STEP ○ -> ⬡) ---")
    engine2 = KYRoxGrammarEngine()
    d_err, s_err, r_err = engine2.step_transition(State.AUTHORIZED, x_val, mask, mask, pi_t=0.1)
    print(f"Ulovlig Snarvei (○ -> ⬡): {d_err.name} | Tilstand: {s_err.value} ({s_err.name}) | Årsak: {r_err}")
