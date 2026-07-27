import numpy as np

def analyze_holomorphic_gate(matrix_raw, tau_h=0.25):
    """
    Måler holomorf regularitet (Pi_H) ved å teste brudd på Cauchy-Riemann.
    Følger livssyklusen: STRUCT (Lag 2) -> GATE.
    """
    N = matrix_raw.shape[0]
    # Konverter til diskrete tilstander
    a = np.where(matrix_raw == 1, 1, -1)
    
    # Generer det komplekse planet over matrisens rutenett
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    
    # Konstruer polynomial-feltet F_Q(z, w) basert på matrisens konfigurasjon
    F_Q = np.zeros((N, N), dtype=complex)
    for i in range(N):
        for j in range(N):
            F_Q += a[i, j] * (Z**i) * (Z.conj()**j)
            
    # Beregn partielle derivater via numeriske endelige differanser
    dF_dx = np.gradient(F_Q, x, axis=1)
    dF_dy = np.gradient(F_Q, y, axis=0)
    
    # Anti-holomorf derivat-operator: d_bar = 0.5 * (dF_dx + i * dF_dy)
    d_bar_F = 0.5 * (dF_dx + 1j * dF_dy)
    
    # Evaluer brudd-metrikken D_bar = |d_bar F| / |F|
    eps = 1e-9  # Reguleringsfaktor mot singulariteter
    deviation_field = np.abs(d_bar_F) / (np.abs(F_Q) + eps)
    D_bar_partial = float(np.mean(deviation_field))
    
    # GATE LOGIKK: Fail-closed med absolutte terskler
    if D_bar_partial > tau_h * 2.0:
        decision = "KILL"
    elif D_bar_partial > tau_h:
        decision = "HOLD"
    else:
        decision = "OPEN"
        
    return decision, D_bar_partial

if __name__ == "__main__":
    # Gjenbruker eksakt matrisen fra din forrige spektralkjøring
    realized_matrix = np.array([
        [0, 1, 0, 0, 0, 1],
        [0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1],
        [1, 0, 1, 0, 1, 1],
        [1, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 0]
    ])
    
    print("--- ATLAS QR HOLOMORPHIC RUNTIME v0.2 ---")
    
    # Kjør metrikken gjennom det holomorfe filteret
    decision, d_bar = analyze_holomorphic_gate(realized_matrix)
    
    print("\n--- GATE RESOLUTION (Lag 2: Pi_H) ---")
    print(f"Beslutning:                {decision}")
    print(f"Cauchy-Riemann avvik:      {d_bar:.4f}")
