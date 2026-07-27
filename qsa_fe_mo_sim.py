kimport os
import json
import numpy as np
import scipy.linalg as la

# 1. Definer Fysisk System for QSA
dt = 4e-9  # 4 ns samplingtid
N_STATE = 15
N_CTRL = 6
q24_scale = 2**24

# T1 = 50us, T2 = 30us
gamma_1 = 1.0 / 50e-6
gamma_2 = 1.0 / 30e-6

# Bygg kontinuerlig A_c (15x15 diagonal)
diag_A = [-gamma_2, -gamma_2, -gamma_1, -gamma_2, -gamma_2, -gamma_1] + \
         [-2*gamma_2]*4 + [-gamma_1 - gamma_2]*4 + [-2*gamma_1]
A_c = np.diag(diag_A)

# Parasittisk ZZ-kobling
zeta_zz = 2 * np.pi * 50e3
A_c[6, 7] = zeta_zz
A_c[7, 6] = -zeta_zz

# Diskretiser planten
A_d = np.eye(N_STATE) + A_c * dt

# Bygg kontinuerlig B_c (15x6)
rabi_rate = 2 * np.pi * 20e6
B_c = np.zeros((N_STATE, N_CTRL))
np.fill_diagonal(B_c, rabi_rate)
np.random.seed(42)
B_c += np.random.normal(0, rabi_rate * 0.05, (N_STATE, N_CTRL))
B_d = B_c * dt

# 2. Last inn JSON ELLER bruk Matematisk Fallback
try:
    with open('k_lut_levels.json', 'r') as f:
        lut_data = json.load(f)
    print("[ OK ] Lastet LUT fra fil.\n")
except Exception as e:
    print(f"[ ADVARSEL ] JSON-feil: {e}")
    print("[ INFO ] Filen er trolig avkortet av terminalen (2.9K er for lite).")
    print("[ INFO ] FALLBACK: Syntetiserer Riccati-baserte K-matriser for analysen...\n")
    
    # Beregner ideell LQR-gain som proxy for H_inf
    Q_pen = np.eye(N_STATE) * 1e8
    R_pen = np.eye(N_CTRL) * 1.0
    P = la.solve_continuous_are(A_c, B_c, Q_pen, R_pen)
    K_ideal = la.inv(R_pen) @ B_c.T @ P
    
    lut_data = {"levels": {"nominal": {"K_q24": []}, "thermal": {"K_q24": []}, "shock": {"K_q24": []}}}
    for k_idx in range(16):
        # Skalerer ideal-gain for å simulere bankene
        lut_data["levels"]["nominal"]["K_q24"].append((K_ideal * (1.0 - k_idx*0.01) * q24_scale).astype(int).tolist())
        lut_data["levels"]["thermal"]["K_q24"].append((K_ideal * (0.7 - k_idx*0.02) * q24_scale).astype(int).tolist())
        lut_data["levels"]["shock"]["K_q24"].append((K_ideal * (0.3 - k_idx*0.015) * q24_scale).astype(int).tolist())

regimes = ["nominal", "thermal", "shock"]
results = {}

# 3 & 4. Løkke over regimer for lukket-sløyfe analyse
print(f"{'Regime':<10} | {'Idx':<3} | {'Rho (Spektralrad)':<20} | {'Margin':<10} | {'Kondisjonstall (V)'}")
print("-" * 75)

for regime in regimes:
    results[regime] = []
    K_matrices_q24 = np.array(lut_data["levels"][regime]["K_q24"])
    
    for k_idx, K_q24 in enumerate(K_matrices_q24):
        K_float = K_q24 / q24_scale
        A_cl = A_d - B_d @ K_float
        
        eigvals, eigvecs = la.eig(A_cl)
        spectral_radius = np.max(np.abs(eigvals))
        margin = 1.0 - spectral_radius
        cond_v = np.linalg.cond(eigvecs)
        
        results[regime].append({"rho": spectral_radius, "V": eigvecs})
        
        if k_idx in [0, 7, 15]: # Printer bare noen indekser for å holde output rent
            print(f"{regime:<10} | {k_idx:<3} | {spectral_radius:<20.6f} | {margin:<10.6f} | {cond_v:<15.2f}")

print("-" * 75)

# 5. Transient Growth Factor
V_nom = results["nominal"][7]["V"]
V_therm = results["thermal"][10]["V"]
V_shock = results["shock"][2]["V"]

growth_nom_to_therm = np.linalg.norm(la.inv(V_therm) @ V_nom, ord=2)
growth_therm_to_shock = np.linalg.norm(la.inv(V_shock) @ V_therm, ord=2)

print(f"Transient Amplification (Nominal -> Thermal): {growth_nom_to_therm:.2f}")
print(f"Transient Amplification (Thermal -> Shock):   {growth_therm_to_shock:.2f}")
