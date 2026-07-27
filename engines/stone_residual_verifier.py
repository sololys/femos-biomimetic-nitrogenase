import sys
import numpy as np
sys.path.append('01_OPEN')
from matrix_space_engine import VrengtHilbertEngine

def run_stone_residual_scan():
    print("=== EVALUERING AV STONE-GENERERT RESIDUALFELT r_16(z) ===")
    n = 16
    alpha = 4.26
    rho_w = 0.00001526
    
    # 1. Gjenopprett metrikken G
    t = np.linspace(1, 5, n)
    T1, T2 = np.meshgrid(t, t)
    H_base = (alpha / (1.0 + np.abs(T1 - T2))) + complex(0, rho_w)
    np.fill_diagonal(H_base, alpha)
    G = (H_base + H_base.conj().T) / 2.0
    
    # 2. Gjenopprett den eksakte analytiske derivatmatrisen A
    A_raw = np.zeros((n, n), dtype=complex)
    for i in range(n):
        for j in range(n):
            if i != j:
                A_raw[i, j] = complex(0, (i - j) / (1.0 + (i - j)**2))
    
    A_analytic = (A_raw - A_raw.conj().T) / 2.0 * complex(0, 1)
    np.fill_diagonal(A_analytic, 10.0 * np.arange(1, n + 1))
    
    # 3. Beregn frekvenser via motoren
    engine = VrengtHilbertEngine(G)
    gammas, defect, eigen_res = engine.compute_exact_stone_frequencies(A_analytic)
    
    # Test-grid for uavhengig Xi-kontroll
    z_grid = np.array([1.0, 2.0, 3.5, 5.0])
    xi_ref = {1.0: 0.9604, 2.0: 0.8920, 3.5: 0.7412, 5.0: 0.5823}
    
    print(f"Generator Defekt  : {defect:.4e}")
    print(f"Eigen Residual    : {eigen_res:.4e}\n")
    print(f"{'z_lokus':<10} | {'D_16_Stone(z)':<15} | {'2*Xi(z)':<15} | {'r_16(z)':<15}")
    print("-" * 65)
    
    for z in z_grid:
        d16_stone = engine.evaluate_stone_determinant(z, gammas)
        two_xi = xi_ref[z]
        residual = d16_stone - two_xi
        print(f"{z:<10.2f} | {d16_stone:<15.7f} | {two_xi:<15.7f} | {residual:<15.7f}")

if __name__ == "__main__":
    run_stone_residual_scan()
