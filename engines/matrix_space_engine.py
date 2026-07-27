import numpy as np
from scipy.linalg import cholesky, solve_triangular, expm, logm, norm

class VrengtHilbertEngine:
    def __init__(self, G_matrix):
        self.G = np.array(G_matrix, dtype=complex)
        self.eigenvalues_G = None

    def validate_gram_positivity(self):
        self.eigenvalues_G = np.linalg.eigvalsh(self.G)
        min_lambda = np.min(self.eigenvalues_G)
        if min_lambda < 0:
            return "KILL", min_lambda
        if np.isclose(min_lambda, 0.0, atol=1e-7):
            return "QUOTIENT", min_lambda
        return "ADMISSIBLE", min_lambda

    def verify_involution_chain(self, A_analytic, h_inv=0.005):
        eps = np.finfo(float).eps
        L = cholesky(self.G, lower=True)
        
        # Hvitning: B = L^-1 A L^-*
        Y = solve_triangular(L, A_analytic, lower=True)
        B = solve_triangular(L, Y.conj().T, lower=True).conj().T
        
        b_herm_defect = norm(B - B.conj().T, "fro") / max(norm(B, "fro"), eps)
        B = 0.5 * (B + B.conj().T)
        
        gamma = np.linalg.eigvalsh(B)
        branch_margin = np.pi - h_inv * np.max(np.abs(gamma))
        
        if branch_margin <= 0 or b_herm_defect > 1e-10:
            return "HOLD_FAIL", {}

        # Involusjonsløkke: Punkt -> Bane -> Punkt
        V = expm(-1j * h_inv * B)
        B_return = (1j / h_inv) * logm(V)
        
        generator_return_defect = norm(B_return - B, "fro") / max(norm(B, "fro"), eps)
        A_return = L @ B_return @ L.conj().T
        form_return_defect = norm(A_return - A_analytic, "fro") / max(norm(A_analytic, "fro"), eps)
        
        metrics = {
            "herm_defect": b_herm_defect,
            "branch_margin": branch_margin,
            "gen_return_defect": generator_return_defect,
            "form_return_defect": form_return_defect,
            "gammas": gamma
        }
        
        if max(generator_return_defect, form_return_defect) < 1e-9:
            return "OPEN", metrics
        return "HOLD_PRECISION_LOSS", metrics

    def evaluate_stone_determinant(self, z, gamma_candidates):
        pos_gammas = gamma_candidates[gamma_candidates > 0]
        if len(pos_gammas) == 0:
            return 0.0
        factor = z**2 + 0.25
        terms = 1.0 - factor / (pos_gammas**2 + 0.25)
        return np.prod(terms)
