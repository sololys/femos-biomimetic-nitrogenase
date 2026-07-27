import time
import math
import numpy as np

# --- KONSTANTER ---
OMEGA_Q = 5.0 * 2 * math.pi
GAMMA_1 = 0.01
GAMMA_2 = 0.02
SYSTEM_MASK = 17

# --- KJERNEFUNKSJONER ---
def verify_rox_identity(data, mask):
    return (int(data) ^ mask ^ mask) == int(data)

def check_admissibility(uncertainty):
    # Forenklet for løkken: Vi sjekker kun usikkerheten mot en streng max-terskel (0.015)
    u_max = 0.015
    return uncertainty <= u_max

def compute_jacobian_F(theta, omega_d, dt):
    sx, sy, sz, d_omega = theta
    total_omega = OMEGA_Q + d_omega
    F_c = np.array([
        [-GAMMA_2,     -total_omega,   0,        -sy],
        [total_omega,  -GAMMA_2,       -2*omega_d, sx],
        [0,            2*omega_d,      -GAMMA_1,   0],
        [0,            0,              0,          0]
    ])
    return np.eye(4) + F_c * dt

# --- OMNI LØKKE ---
def run_omni_loop(cycles=50):
    print("==================================================")
    print(" INITIATING K_ORA OMNI-LOOP | INJECTING NOISE")
    print("==================================================")
    
    # Startverdier
    theta_t = np.array([0.0, 0.0, 1.0, 0.05])
    omega_d = 0.1
    dt = 0.001
    
    for step in range(1, cycles + 1):
        # 1. Rått trykk (simulert sensorinput)
        raw_signal = np.random.randint(40, 50)
        
        # 2. ROX Identitetssjekk
        if not verify_rox_identity(raw_signal, SYSTEM_MASK):
            print(f"[CYCLUS {step:02d}] ✗ FAIL-CLOSED: ROX asymmetri. Latch aktivert.")
            break
            
        # 3. EKF Estimeringssteg
        F_t = compute_jacobian_F(theta_t, omega_d, dt)
        
        # 4. Injisere stokastisk støy (Miljøet prøver å rive systemet i stykker)
        noise = np.random.normal(0, 0.002, 4) 
        theta_t = (F_t @ theta_t) + noise
        
        # 5. Admissibility Gate (Måler støyens innvirkning)
        # Hvis drift-støyen blir for voldsom, må vi stenge porten.
        current_uncertainty = abs(noise[3]) 
        
        if not check_admissibility(current_uncertainty):
            print(f"[CYCLUS {step:02d}] ≢ KILL: Epistemisk støy ({current_uncertainty:.4f}) overstiger u_max. Symmetri brutt.")
            print("==================================================")
            print(" SYSTEM TERMINERT SIKKERT. VARMEREST DISSIPERT.")
            break
            
        # 6. Commit (Porten sier OPEN)
        print(f"[CYCLUS {step:02d}] ≡ REALIZED | sz: {theta_t[2]:.4f} | d_omega: {theta_t[3]:.4f}")
        time.sleep(0.05) # Liten pause for visuell flyt i terminalen

    else:
        print("==================================================")
        print(f" LØKKE FULLFØRT: {cycles} SYKLUSER OVERLEVD.")
        print(" WITNESS-REGISTER FORSEGLET.")

if __name__ == "__main__":
    run_omni_loop()
