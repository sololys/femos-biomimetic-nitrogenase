import numpy as np

def verify_dimensionless_profile():
    print("=== EVALUERING AV DIMENSJONSLØS INTERAKSJONSSTRUKTUR ===")
    
    kappa = 0.01
    tau = 0.002
    g_max = kappa / tau
    chi_values = np.array([0.1, 1.0, 10.0, 100.0])
    
    print(f"Maksimal koblingsstyrke (g_max) = {g_max:.4f}")
    print("-" * 75)
    print(f"{'Chi (omega*tau)':<16} | {'Forsterkning g_DI':<18} | {'Filterfase phi_L':<16} | {'Totalfase phi_D':<16}")
    print("-" * 75)
    
    for chi in chi_values:
        g_di = g_max * (chi / np.sqrt(1.0 + chi**2))
        
        # Separering av faselagene
        phi_l = -np.degrees(np.arctan(chi))
        phi_d = -90.0 + phi_l
        
        print(f"{chi:<16.1f} | {g_di:<18.6f} | {phi_l:<15.2f}° | {phi_d:<15.2f}°")

if __name__ == "__main__":
    verify_dimensionless_profile()
