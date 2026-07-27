import numpy as np


class APCSimulator:
    def __init__(self, K_threshold):
        self.K_threshold = K_threshold

    def phi_dynamics(self, x):
        return x + 0.1 * np.sin(x)

    def pi_k_projection(self, x):
        if abs(x) > self.K_threshold:
            return None
        return x

    def omega_gate(self, x):
        if x is None:
            return "KILL"
        return "OPEN"

    def step(self, x):
        candidate = self.phi_dynamics(x)
        admissible = self.pi_k_projection(candidate)
        state = self.omega_gate(admissible)
        return state, admissible


def main():
    sim = APCSimulator(K_threshold=1.5)
    test_inputs = [0.0, 0.5, 1.2, 2.0]

    for x in test_inputs:
        gate_status, val = sim.step(x)
        print(f"Input: {x} -> Gate: {gate_status}, Realisert verdi: {val}")


if __name__ == "__main__":
    main()
