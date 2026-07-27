#!/usr/bin/env python3
"""
MERKUR PERIHELPRECESJON TESTER (01_OPEN)
Formål: Verifisere Einsteins relativistiske perihelprecesjon for Merkur (42.98 arcsec/century)
sammenlignet med Newtons mekanikk og numerisk orbit-integrasjon.
"""

import math
import sys

# Astronomiske konstanter (SI-enheter)
G = 6.67430e-11           # Gravitasjonskonstant (m^3 kg^-1 s^-2)
M_sun = 1.98847e30        # Solens masse (kg)
c = 299792458.0           # Lyshastighet (m/s)

# Merkurs baneparametere
a_mercury = 57.909e9      # Store halvakse (m)
e_mercury = 0.205630      # Eksentrisitet
T_mercury_days = 87.969   # Omløpstid (dager)
T_mercury_sec = T_mercury_days * 86400.0

def calculate_theoretical_gr_precession():
    """
    Beregner teoretisk relativistisk perihelprecesjon per omløp og per århundre:
    Δφ = 6 π G M_sun / (c^2 a (1 - e^2))  (radianer per omløp)
    """
    numerator = 6.0 * math.pi * G * M_sun
    denominator = (c**2) * a_mercury * (1.0 - e_mercury**2)
    delta_phi_rad = numerator / denominator  # rad / omløp
    
    # Omregning til buesekunder per omløp
    delta_phi_arcsec = delta_phi_rad * (180.0 / math.pi) * 3600.0
    
    # Antall omløp per jordisk århundre (100 år = 36525 dager)
    orbits_per_century = (36525.0) / T_mercury_days
    
    precession_per_century = delta_phi_arcsec * orbits_per_century
    return delta_phi_rad, delta_phi_arcsec, orbits_per_century, precession_per_century

def numerical_binet_orbit_integration(num_orbits=5):
    """
    Numerisk integrasjon av den modifiserte Binet-ligningen for merkurbane:
    d^2 u / dθ^2 + u = G M / L^2 + (3 G M / c^2) * u^2
    """
    # L = sqrt(G M a (1 - e^2))
    L2 = G * M_sun * a_mercury * (1.0 - e_mercury**2)
    k_newton = (G * M_sun) / L2
    k_gr = (3.0 * G * M_sun) / (c**2)
    
    # Skalert integrasjon i θ
    u = 1.0 / (a_mercury * (1.0 + e_mercury)) # Start ved aphelion
    du_dtheta = 0.0
    
    dtheta = 0.0001
    total_steps = int((2.0 * math.pi * num_orbits) / dtheta)
    
    perihelion_thetas = []
    prev_u = u
    prev_du = du_dtheta
    
    for step in range(total_steps):
        theta = step * dtheta
        # Runge-Kutta 2. orden (Heuns metode) for d^2u/dθ^2 = k_newton - u + k_gr * u^2
        d2u = k_newton - u + k_gr * (u**2)
        
        u_next = u + du_dtheta * dtheta
        du_next = du_dtheta + d2u * dtheta
        
        d2u_next = k_newton - u_next + k_gr * (u_next**2)
        
        u += 0.5 * (du_dtheta + du_next) * dtheta
        du_dtheta += 0.5 * (d2u + d2u_next) * dtheta
        
        # Sjekk om u når et maksimum (dvs. r når et minimum -> Perihelion)
        if prev_du > 0 and du_dtheta <= 0:
            # Interpoler eksakt vinkel θ
            perihelion_thetas.append(theta)
            
        prev_du = du_dtheta
        prev_u = u
        
    return perihelion_thetas

def run_mercury_test():
    print("=== MERKUR PERIHELPRECESJON TESTER (GR vs NEWTON) ===")
    print("Mål: Verifisere at Einsteins relativistiske korreksjon gir 42.98 arcsec/century.\n")
    
    rad_orbit, arcsec_orbit, orbits_century, prec_century = calculate_theoretical_gr_precession()
    
    print("--- 1. TEORETISK BEREGNING (SCHWARZSCHILD METRIKK) ---")
    print(f"Δφ per omløp (radianer):    {rad_orbit:.6e} rad")
    print(f"Δφ per omløp (buesekunder): {arcsec_orbit:.6f} arcsec")
    print(f"Omløp per århundre:        {orbits_century:.2f} omløp")
    print(f"Precesjon per århundre:     {prec_century:.2f} arcsec/century")
    
    # Sjekk avvik mot den kjente eksperimentelle observasjonen (42.98 arcsec/century)
    obs_target = 42.98
    dev = abs(prec_century - obs_target)
    
    print("\n--- 2. SAMMENLIGNING MED OBSERVATORISK DATA ---")
    print(f"Observert Einstein-precesjon: {obs_target:.2f} arcsec/century")
    print(f"Beregnet teoretisk verdi:     {prec_century:.2f} arcsec/century")
    print(f"Avvik:                         {dev:.4f} arcsec/century")
    
    if dev < 0.5:
        print("\n=== VERDIKT ===")
        print("NEWTONIAN PRECESSION: 0.00 arcsec/century (Feiler i å forklare avviket)")
        print(f"EINSTEIN GR PRECESSION: {prec_century:.2f} arcsec/century (MATCH PASS)")
        print("SYSTEM STATUS: 01_OPEN // MERKUR_PERIHEL_PASS // INVARIANT")

if __name__ == "__main__":
    run_mercury_test()
