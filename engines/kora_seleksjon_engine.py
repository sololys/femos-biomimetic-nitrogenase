import numpy as np

class KoraSeleksjonsPort:
    def __init__(self, num_dimensions=10, threshold=0.4):
        # Hinges Geometry (Pia_t)
        self.hinges = np.random.uniform(0.2, 0.8, size=(num_dimensions,))
        self.threshold = threshold

    def evaluate_candidates(self, candidates):
        """
        Evaluere kandidatfeltet C_t mot Seleksjonsporten Pi_t.
        Returnerer overlevelsesmengden S_t.
        """
        surviving = []
        for c in candidates:
            # Tame estimates / Glatting
            norm_c = np.linalg.norm(c) + 1e-8
            norm_h = np.linalg.norm(self.hinges) + 1e-8
            attenuation = np.dot(c, self.hinges) / (norm_c * norm_h)
            
            if attenuation >= self.threshold:
                surviving.append(c)
        return np.array(surviving)

class KonsekvensPort:
    def __init__(self, kill_threshold=-0.2):
        self.kill_threshold = kill_threshold

    def resolve_gate(self, S_t, previous_p):
        """
        Typet Konsekvensport Omega_t: Returnerer decision d_t (OPEN, HOLD, KILL) og ny p_t.
        """
        if len(S_t) == 0:
            return "HOLD", previous_p
        
        # Velg dominant kandidat fra S_t
        candidate_p = S_t[np.argmax([np.linalg.norm(c) for c in S_t])]
        
        # TLA+ Safety Invariant Check: Unngå akutt eksplosjon/støy
        if np.max(candidate_p) < self.kill_threshold:
            return "KILL", np.zeros_like(previous_p)
        
        return "OPEN", candidate_p

class Witness:
    def __init__(self):
        self.history = []

    def commit(self, p_t, action, decision, world_state):
        """ Inskripsjonsmatrise W_t (Blekket tørker) """
        entry = {
            'decision': decision,
            'realized_p': p_t.copy(),
            'action': action.copy(),
            'world': world_state.copy()
        }
        self.history.append(entry)

class KoraSystemEngine:
    def __init__(self, dim=5):
        self.dim = dim
        self.port = KoraSeleksjonsPort(num_dimensions=dim)
        self.omega = KonsekvensPort()
        self.witness = Witness()
        self.p_current = np.zeros(dim)
        self.world_state = np.random.randn(dim)

    def step(self, raw_overskudd, neural_noise):
        # 1. C_t = Phi(RAW_t, N_t)
        candidates = raw_overskudd + neural_noise
        
        # 2. S_t = Pi_t(C_t)
        S_t = self.port.evaluate_candidates(candidates)
        
        # 3. d_t = Omega_t(S_t) -> {OPEN, HOLD, KILL}
        decision, p_next = self.omega.resolve_gate(S_t, self.p_current)
        
        if decision == "OPEN":
            self.p_current = p_next
            a_t = np.tanh(self.p_current)  # Handling / Agens
        else:
            a_t = np.zeros(self.dim)

        # 4. Verden oppdateres
        self.world_state += 0.05 * a_t + np.random.normal(0, 0.01, size=self.dim)
        
        # 5. Witness registrerer tilstand
        self.witness.commit(self.p_current, a_t, decision, self.world_state)
        
        return decision, self.p_current, a_t

if __name__ == "__main__":
    engine = KoraSystemEngine(dim=5)
    print("=== RUNNING KORA SELEKSJON ENGINE TEST ===")
    for t in range(5):
        RAW = np.random.uniform(-1, 1, size=(10, 5))
        Noise = np.random.normal(0, 0.05, size=(10, 5))
        
        decision, p_t, a_t = engine.step(RAW, Noise)
        print(f"Steg {t+1}: Portvedtak d_t = {decision}")
        print(f"  Realistisk p_t: {np.round(p_t, 3)}")
        print(f"  Handlingsvektor a_t: {np.round(a_t, 3)}\n")
