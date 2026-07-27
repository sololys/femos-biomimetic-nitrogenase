import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize

class HamiltonianLearningEngine:
    def __init__(self, basis_operators):
        # E_a basis-operatorer (Hermitiske matriser)
        self.E = [np.array(op, dtype=complex) for op in basis_operators]
        self.M = len(self.E)
        self.dim = self.E[0].shape[0]
        
    def forward_trajectory(self, lambdas, time_grid, rho_0, observable):
        # H(lambda) = sum(lambda_a * E_a)
        H = np.zeros((self.dim, self.dim), dtype=complex)
        for a in range(self.M):
            H += lambdas[a] * self.E[a]
            
        path = []
        for t in time_grid:
            # U(t) = exp(-i * H * t)  [hbar = 1]
            U = expm(-1j * H * t)
            rho_t = U @ rho_0 @ U.conj().T
            expectation = np.real(np.trace(rho_t @ observable))
            path.append(expectation)
            
        return np.array(path)

    def reconstruct_parameters(self, true_path, time_grid, rho_0, observable):
        # Klassisk læringslag: Rekonstruerer punktet fra banen
        def loss_function(lambdas_guess):
            guess_path = self.forward_trajectory(lambdas_guess, time_grid, rho_0, observable)
            return np.sum((true_path - guess_path) ** 2)
            
        initial_guess = np.zeros(self.M)
        res = minimize(loss_function, initial_guess, method='Nelder-Mead')
        return res.x, res.fun

if __name__ == "__main__":
    print("=== RUNNING HAMILTONIAN LEARNING & PHASE COUPLING ===")
    
    # 2-nivå kvantesystem (Pauli-matriser som basis)
    E0 = [[0, 1], [1, 0]]   # Sigma_x
    E1 = [[0, -1j], [1j, 0]] # Sigma_y
    
    # Sann parameter-lokus (De ukjente kandidatpunktene)
    true_lambdas = np.array([1.5, 0.8])
    hbar = 1.0
    
    # Initialtilstand rho_0 og målobservabel O
    rho_0 = np.array([[1, 0], [0, 0]], dtype=complex) # |0><0|
    O_meas = np.array([[1, 0], [0, -1]], dtype=complex) # Sigma_z
    
    time_grid = np.linspace(0.0, 2.0, 50)
    
    engine = HamiltonianLearningEngine([E0, E1])
    
    # 1. Generer observerbar P-bane
    observable_path = engine.forward_trajectory(true_lambdas, time_grid, rho_0, O_meas)
    
    # 2. Klassisk parameterlæring (Rekonstruksjon av NP-punkt)
    estimated_lambdas, loss = engine.reconstruct_parameters(observable_path, time_grid, rho_0, O_meas)
    
    # 3. Beregn dimensjonsløse kvantefaser theta_a ved t_max
    t_max = time_grid[-1]
    thetas = (estimated_lambdas * t_max) / hbar
    
    print(f"Sanne parametere (lambda)  : {true_lambdas}")
    print(f"Estimerte punkter (hat_lambda): {estimated_lambdas}")
    print(f"Læringsresidual (L2 Loss)  : {loss:.6e}")
    print(f"Akkumulert kvantefase theta: {thetas}")
    
    # Port-sjekk for admissibilitet
    if loss < 1e-5:
        print("STATUS: HAMILTONIAN_COUPLING_VALIDATION = OPEN")
    else:
        print("STATUS: ADMISSIBILITY = REJECTED")
