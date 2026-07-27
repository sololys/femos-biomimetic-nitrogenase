import numpy as np

# --- 1. Tilstandspreparering ---
# Vi definerer en maksimalt sammenfiltret Bell-tilstand: |Psi+> = 1/sqrt(2) * (|00> + |11>)
psi = np.array([1.0, 0.0, 0.0, 1.0]) / np.sqrt(2)
rho = np.outer(psi, psi.conj())

# Standard Pauli-matriser
I = np.eye(2)
X = np.array([[0.0, 1.0], [1.0, 0.0]])
Z = np.array([[1.0, 0.0], [0.0, -1.0]])

# Projektorer for standard målinger
# Innstilling 0 (Z-basis):
P_Z0 = np.array([[1.0, 0.0], [0.0, 0.0]])
P_Z1 = np.array([[0.0, 0.0], [0.0, 1.0]])
# Innstilling 1 (X-basis):
P_X0 = 0.5 * np.array([[1.0, 1.0], [1.0, 1.0]])
P_X1 = 0.5 * np.array([[1.0, -1.0], [-1.0, 1.0]])

# --- 2. Relasjonelle Historie-Kjerner (K_gamma) ---
D_K_Alice = 0.35  # Avvik akkumulert i Alice sin arm
D_K_Bob   = 0.12  # Avvik akkumulert i Bob sin arm

# Dempningsfunksjon g(D_K) = exp(-D_K)
def g(D):
    return np.exp(-D)

# --- 3. Lokalt Normaliserte KDM-POVM Elementer ---
def get_kdm_povm(P0, P1, D):
    # Moduler rå projektorer med historie-dempingen
    E0_raw = g(D * 0.5) * P0
    E1_raw = g(D * 1.5) * P1  # Ulik dempning på utfallene
    
    # Finn sum-operatoren
    S = E0_raw + E1_raw
    
    # KORREKT MATRISE-INVERS-KVADRATROT (S^{-1/2}) via spektraldekomposisjon
    # Siden S er real-symmetrisk og positiv-definit, bruker vi eigh
    vals, vecs = np.linalg.eigh(S)
    S_inv_sqrt = vecs @ np.diag(1.0 / np.sqrt(vals)) @ vecs.T
    
    # De ferdige, lokalt normaliserte POVM-elementene (E0 + E1 = I er nå garantert!)
    E0 = S_inv_sqrt @ E0_raw @ S_inv_sqrt
    E1 = S_inv_sqrt @ E1_raw @ S_inv_sqrt
    return E0, E1

# Beregn POVM for Alice under innstilling 0 (Z) og 1 (X)
A_Z0, A_Z1 = get_kdm_povm(P_Z0, P_Z1, D_K_Alice)
A_X0, A_X1 = get_kdm_povm(P_X0, P_X1, D_K_Alice)

# Beregn POVM for Bob under innstilling 0 (Z)
B_Z0, B_Z1 = get_kdm_povm(P_Z0, P_Z1, D_K_Bob)

# --- 4. Beregning av Sannsynligheter ---
def calculate_joint(A_ops, B_ops):
    probs = np.zeros((2, 2))
    for a in range(2):
        for b in range(2):
            M = np.kron(A_ops[a], B_ops[b])
            probs[a, b] = np.real(np.trace(M @ rho))
    return probs

# Scenario 1: Alice velger Z-basis (x=0)
probs_Z = calculate_joint([A_Z0, A_Z1], [B_Z0, B_Z1])

# Scenario 2: Alice velger X-basis (x=1)
probs_X = calculate_joint([A_X0, A_X1], [B_Z0, B_Z1])

# --- 5. No-Signalling Sjekk ---
bob_marginal_Z = np.sum(probs_Z, axis=0)
bob_marginal_X = np.sum(probs_X, axis=0)

print("====================================================================")
print(" KDM NO-SIGNALLING VERIFICATION MOTOR")
print("====================================================================")
print(f"Alice's history drift (D_K_A): {D_K_Alice}")
print(f"Bob's history drift (D_K_B)  : {D_K_Bob}")
print("--------------------------------------------------------------------")
print(f"Joint Probs (Alice=Z, Bob=Z):\n{probs_Z}")
print(f"Joint Probs (Alice=X, Bob=Z):\n{probs_X}")
print("--------------------------------------------------------------------")
print(f"Bob's Marginal when Alice chose Z: {bob_marginal_Z}")
print(f"Bob's Marginal when Alice chose X: {bob_marginal_X}")

# Numerisk toleransetest
diff = np.max(np.abs(bob_marginal_Z - bob_marginal_X))
print("--------------------------------------------------------------------")
print(f"Absolute Marginal Difference: {diff:.16e}")

if diff < 1e-15:
    print("STATUS: PASS (No-Signalling is mathematically preserved!)")
else:
    print("STATUS: FAIL (Causality violation detected!)")
print("====================================================================")
