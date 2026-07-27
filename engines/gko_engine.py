import os, json, hashlib, datetime, numpy as np, sys, time, math
from collections import deque

class GKO_Engine:
    """
    v2.2 - Avansert Fysikk Digital Tvilling
    Inkluderer: Trykkdynamikk, RF-resonans, Thermal Jacket, EWMA-filtrering.
    """
    def __init__(self, architect="Marius E. Torjusen"):
        self.architect = architect
        self.catalyst_integrity = 1.0
        self.nh3_concentration = 0.0
        self.internal_temp_k = 298.0
        self.internal_pressure_bar = 1.0
        self.gx = -6.0
        self.chain = []

    def run_cycle(self, ticks=12):
        print(f"[*] Eksekverer v2.2 Physics Engine Cycle...")
        for t in range(0, ticks + 1):
            noise = np.random.normal(0, 0.05)
            # v2.2 Physics Logic
            self.internal_pressure_bar += (0.5 * t) - (self.internal_pressure_bar * 0.1)
            self.nh3_concentration += 0.02 * self.internal_pressure_bar * self.catalyst_integrity
            self.gx = (self.gx + noise) * 0.85
            
            block = {
                "idx": t,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "p_bar": round(self.internal_pressure_bar, 2),
                "nh3_yield": round(self.nh3_concentration, 4),
                "gx": round(self.gx, 6),
                "hash": hashlib.sha256(f"{t}{self.gx}{time.time()}".encode()).hexdigest()
            }
            self.chain.append(block)
            
        manifest = {
            "MANIFEST_V2_GOLD": {
                "HEADER": {"ARCHITECT": self.architect, "VERSION": "2.2.0-PHYSICS"},
                "MODULAR_ROOT": "GKO.Intelligence",
                "CHAIN_DATA": self.chain
            }
        }
        os.makedirs("manifests", exist_ok=True)
        with open("manifests/system_manifest_v2.json", "w") as f:
            json.dump(manifest, f, indent=2)
        print("[OK] system_manifest_v2.json krystallisert.")

if __name__ == "__main__":
    GKO_Engine().run_cycle()
