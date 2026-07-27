import unittest
import numpy as np

# Innebygd klasse for å sikre deterministisk import-hygiene
class KerrInterfaceHamiltonian:
    def __init__(self, mass, spin, admissibility_threshold, epsilon_c):
        self.M = mass
        self.a = spin
        self.R_c = admissibility_threshold
        self.eps_c = epsilon_c
        
    def measure_gate(self, R, R_dot, eps, E_h, E_I):
        # 1. Input Hygiene: Fail-closed ved ugyldig geometri
        if not (np.isfinite(R) and np.isfinite(R_dot)):
            return "KILL"
            
        # 2. H_break trigger: Fail-closed ved horisont/admissibilitetsbrudd
        if R >= self.R_c and R_dot >= 0:
            return "KILL"
            
        # 3. Epistemisk HOLD
        elif eps >= self.eps_c:
            return "HOLD"
            
        # 4. ENABLE (kun ved fullstendig konsistens)
        elif np.isclose(E_h, E_I):
            return "ENABLE"
            
        # 5. Default fail-closed
        else:
            return "KILL"

class TestKerrInterfaceContract(unittest.TestCase):
    def setUp(self):
        self.interface = KerrInterfaceHamiltonian(mass=1.0, spin=0.5, admissibility_threshold=2.0, epsilon_c=0.1)

    def test_baseline_open(self):
        self.assertEqual(self.interface.measure_gate(1.5, -0.1, 0.05, 1.0, 1.0), "ENABLE")

    def test_epistemic_hold(self):
        self.assertEqual(self.interface.measure_gate(1.5, -0.1, 0.2, 1.0, 1.0), "HOLD")

    def test_radial_kill(self):
        self.assertEqual(self.interface.measure_gate(2.5, 0.5, 0.01, 1.0, 1.0), "KILL")

    def test_invalid_input_kill(self):
        self.assertEqual(self.interface.measure_gate(float('nan'), 0.0, 0.0, 1.0, 1.0), "KILL")

if __name__ == '__main__':
    unittest.main()
