import numpy as np
import time

# --- Systemparametere (fra spesifikasjon) ---
Ts = 0.1  # Prøvetid i sekunder [cite: 32, 67]
HT_DEAD_TIME = 1.7  # sekunder [cite: 29, 34]
HT_TIME_CONSTANT = 90.0  # sekunder 

# ORS Sikkerhetsgrenser [cite: 46]
MAX_SATURATION_TIME = 5.0  
FIDELITY_THRESHOLD = 0.9999

class H2VestaSimulator:
    def __init__(self):
        self.steps_dead_time = int(HT_DEAD_TIME / Ts)
        self.history = [0.0] * self.steps_dead_time
        self.sat_timer = 0.0
        self.is_aborted = False
        
        # Diskrete koeffisienter for HT-trinn (Førsteordens system)
        self.a = np.exp(-Ts / HT_TIME_CONSTANT)
        self.b = 1 - self.a
        self.state_model = 0.0
        self.state_plant = 0.0

    def update(self, u, fidelity=1.0):
        if self.is_aborted:
            return "SYSTEM_HALT: Sticky ABORT aktiv. Manuell reset kreves." [cite: 47, 156]

        # 1. ORS Sjekk: Aktuator-metning [cite: 46]
        if u >= 1.0: # Antar 1.0 er maks pådrag
            self.sat_timer += Ts
            if self.sat_timer > MAX_SATURATION_TIME:
                self.is_aborted = True
                return "ABORT: Aktuator-metning overskredet 5s." [cite: 46, 147]
        else:
            self.sat_timer = 0.0

        # 2. ORS Sjekk: Fidelity/Koherens [cite: 46]
        if fidelity < FIDELITY_THRESHOLD:
            self.is_aborted = True
            return "ABORT: Fidelity/koherens feil." [cite: 46, 154]

        # 3. Smith Predictor logikk [cite: 29, 130]
        # Prediksjon uten dødtid
        self.state_model = self.a * self.state_model + self.b * u
        
        # Forsinket verdi (emulering av dødtid)
        delayed_u = self.history.pop(0)
        self.history.append(u)
        
        # Faktisk "Plant" respons (med dødtid)
        self.state_plant = self.a * self.state_plant + self.b * delayed_u
        
        return f"HT_Temp_Est: {self.state_model:.2f}, Plant_Actual: {self.state_plant:.2f}"

# --- Kjøring av simulering ---
sim = H2VestaSimulator()
print("Starter H2-VESTA Digital Tvilling (Ts=0.1s)...")

for i in range(100):
    # Simulerer et pådrag (u) og stabil fidelity
    result = sim.update(u=0.8, fidelity=1.0)
    print(result)
    time.sleep(0.01) # Raskere enn sanntid for test
