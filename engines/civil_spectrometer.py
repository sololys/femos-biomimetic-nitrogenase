import sys
import time
import hashlib

class CivilMossbauerValidator:
    def __init__(self):
        self.target_isomer_shift = 0.8  # Kanonisk fastpunkt epsilon = 0.8 mm/s
        self.max_o2_ppm = 0.5           # Anaerob terskel (Alpha)
        
    def ingest_payload(self, o2_level, nh3_level, measured_shift):
        print("=== INGEST: PAYLOAD INITIATED ===")
        print(f"Måleverdier innkommende strøm: O2 = {o2_level} ppm | NH3 = {nh3_level} ppm | Isomerskift = {measured_shift} mm/s")
        time.sleep(0.2)
        
        # 1. Anaerobt filter
        print("[LAG 1] Kjører anaerobt filter...")
        if o2_level >= self.max_o2_ppm:
            return "KILL", "Anaerob svikt: O2-nivå for høyt"
            
        # 2. Antropocen støydeteksjon
        print("[LAG 2] Skanner etter antropocen støy...")
        if nh3_level > 0.0:
            return "KILL", f"Antropocen kontaminering detektert: NH3 = {nh3_level} ppm"
            
        # 3. Spektral projeksjon på fastpunktet
        print("[LAG 3] Beregner spektral projeksjon på Mössbauer-baseline...")
        deviation = abs(measured_shift - self.target_isomer_shift)
        if deviation > 0.001:  # Ekstremt stram toleranse langs kjernebanen
            return "KILL", f"Spektral drift unna fastpunktet. Avvik: {deviation:.4f}"
            
        return "ALLOW", "Kanonisk fastpunkt bekreftet. Fravær av støy etablert."

    def execute_gate(self, o2, nh3, shift):
        status, reason = self.ingest_payload(o2, nh3, shift)
        print(f"\n[SPEKTRAL DOM] -> {status}")
        print(f"Årsak/Status: {reason}")
        
        if status == "ALLOW":
            # Genererer kanonisk denotasjon (CD)
            latch_data = f"CIVIL_ALLOW_{o2}_{nh3}_{shift}_{time.time()}"
            cd_seal = hashlib.sha256(latch_data.encode()).hexdigest()
            print(f"-> [LATCHED] Reaksjonsbanen godkjent. CD_v1.0 = {cd_seal}\n")
            return True
        else:
            print("-> [TERMINATED] Banen kollapset under spektral kontroll.\n")
            return False

if __name__ == "__main__":
    validator = CivilMossbauerValidator()
    
    # Test Scenario A: Kontaminert atmosfære (Antropocen støy til stede)
    print("--- SCENARIO A: INDUSTRIELL STØY ---")
    validator.execute_gate(o2=0.2, nh3=1.4, shift=0.8)
    
    # Test Scenario B: Kanonisk ren substans (Absolutt renhet på fastpunktet)
    print("--- SCENARIO B: KANONISK FROSTET ---")
    validator.execute_gate(o2=0.1, nh3=0.0, shift=0.8)
