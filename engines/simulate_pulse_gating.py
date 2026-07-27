import numpy as np
import matplotlib.pyplot as plt

# --- Systemkonstanter ---
STEPS = 120
TIME = np.linspace(0, 12, STEPS)    # Nanosekunder (Tidsakse for RF-pulsen)
D_THRESHOLD = 0.5                   # Grenseverdi for admissibilitet (tau)
RABI_GAIN = 0.4                     # Rotasjonshastighet per tidsenhet under RF-drive

def simulate_qubit_gating(drift_rate):
    """
    Simulerer EKF-måling av avdrift (D_K), FPGA interlock status,
    og resulterende Rabi-rotasjon (theta) på qubit-systemet.
    """
    D_K = 0.0
    theta = 0.0
    
    d_k_history = []
    fpga_enable = []
    rf_envelope = []
    qubit_rotation = []
    
    for t in TIME:
        # 1. EKF akkumulerer avdrift (historie-koherens brytes ned over tid)
        # Drift_rate simulerer system-støy eller fase-feil på linjen
        noise = np.random.normal(0, 0.015)
        D_K += (drift_rate * 0.015) + noise
        D_K = max(0.0, D_K)
        
        # 2. Pi_K Gating Operator (FPGA Interlock)
        # Hvis avdriften krysser grensen, kutter FPGA-en RF-pulsen fysisk
        enable = 1.0 if D_K < D_THRESHOLD else 0.0
        
        # 3. Nominell mikrobølge-puls u_nom(t) (Kanonisk Gaussisk konfigurasjon)
        u_nom = np.exp(-((t - 6.0) ** 2) / (2.0 * 1.5 ** 2))
        
        # 4. Realisert fysisk RF-energi u_real(t) (Gated av FPGA-linjen)
        u_real = u_nom * enable
        
        # 5. Qubit-evolusjon (Rabi-oscillering drevet av realisert RF-felt)
        theta += u_real * RABI_GAIN
        
        # Logg rammetilstander
        d_k_history.append(D_K)
        fpga_enable.append(enable)
        rf_envelope.append(u_real)
        qubit_rotation.append(theta)
        
    return d_k_history, fpga_enable, rf_envelope, qubit_rotation

# --- Kjør Simuleringen for begge banene ---
print("Simulerer Path A (Admissibel tidsutvikling - normal koherens)...")
D_A, gate_A, rf_A, theta_A = simulate_qubit_gating(drift_rate=0.2)

print("Simulerer Path B (Inadmissibel tidsutvikling - fatal faseavdrift)...")
D_B, gate_B, rf_B, theta_B = simulate_qubit_gating(drift_rate=1.9)

# --- Plott timingdiagrammer ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11, 9), sharex=True, facecolor='#111111')

for ax in [ax1, ax2, ax3]:
    ax.set_facecolor('#1a1a1a')
    ax.tick_params(colors='#888888', labelsize=10)
    ax.grid(True, color='#333333', linestyle=':', linewidth=0.8)

# Plott 1: EKF Historie-Avvik D_K
ax1.plot(TIME, D_A, color='#80ff80', linewidth=2, label='Path A (Stable D_K)')
ax1.plot(TIME, D_B, color='#ff8080', linewidth=2, label='Path B (Drifting D_K)')
ax1.axhline(D_THRESHOLD, color='#ff3333', linestyle='--', linewidth=1.2, label='Pi_K Boundary (Threshold)')
ax1.set_title("Extended Kalman Filter (EKF) Structural Drift Tracking", color='#ffffff', fontsize=12, fontweight='bold')
ax1.set_ylabel("Drift Metrikk (D_K)", color='#cccccc', fontsize=10)
ax1.legend(facecolor='#111111', edgecolor='none', labelcolor='#cccccc', loc='upper left')

# Plott 2: FPGA Enable Line & RF Envelope u_real(t)
ax2.fill_between(TIME, rf_A, color='#ffffff', alpha=0.3, label='Realized RF Pulse (Path A)')
ax2.plot(TIME, rf_A, color='#ffffff', linewidth=1.5)
ax2.fill_between(TIME, rf_B, color='#ff3333', alpha=0.15, label='Realized RF Pulse (Path B - Gated!)')
ax2.plot(TIME, rf_B, color='#ff3333', linewidth=1.5, linestyle=':')
ax2.set_title("FPGA-Gated Physical Microwave Envelopes (u_real)", color='#ffffff', fontsize=12, fontweight='bold')
ax2.set_ylabel("Puls Amplitude", color='#cccccc', fontsize=10)
ax2.legend(facecolor='#111111', edgecolor='none', labelcolor='#cccccc', loc='upper left')

# Plott 3: Rabi Qubit Rotation (Theta)
ax3.plot(TIME, theta_A, color='#80ff80', linewidth=2.5, label='Qubit A Phase State (Realisert)')
ax3.plot(TIME, theta_B, color='#ff8080', linewidth=2.5, linestyle='--', label='Qubit B Phase State (Blokkert)')
ax3.axhline(np.pi, color='#ffcc00', linestyle=':', linewidth=1.2, label='Target Pi-Pulse (State Flip)')
ax3.set_title("Target Qubit Physical State Evolution (Rabi Rotation)", color='#ffffff', fontsize=12, fontweight='bold')
ax3.set_xlabel("Tid (Nanosekunder)", color='#cccccc', fontsize=10)
ax3.set_ylabel("Rabi Rotasjon (rad)", color='#cccccc', fontsize=10)
ax3.legend(facecolor='#111111', edgecolor='none', labelcolor='#cccccc', loc='upper left')

plt.suptitle("OMNI-GATING LAB PROTOCOL VERIFICATION", color='#ffffff', fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig("pulse_gating_comparison.png", dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
print("Kjøring vellykket. Puls-plott eksportert til 'pulse_gating_comparison.png'.")
