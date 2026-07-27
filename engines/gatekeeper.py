import sys

class OntologicalTypeException(Exception): 
    """Utløses umiddelbart ved forsøk på ontologiske typebrudd."""
    pass

class PhronesisGatekeeper:
    def __init__(self):
        self.allowed_transitions = {
            "RAW": "ESTIMATE",
            "ESTIMATE": "STRUCT",
            "STRUCT": "REALIZED"
        }

    def evaluate_transit(self, current_state, np_point_exists, p_path_valid):
        print(f"[GATE] Evaluerer overgang fra: {current_state}")
        
        if current_state != "STRUCT":
            raise OntologicalTypeException(
                f"KILL: Direkte sprang til konsekvens nektet. Gjeldende tilstand er {current_state}."
            )
        
        # NP-måleren: Eksisterer punktet i rommet?
        if not np_point_exists:
            print("[NP_METRIC] VETO: Punktet eksisterer ikke i topologien. Status -> HOLD")
            return "HOLD"
            
        # P-måleren: Finnes det en verifisert, polynomisk bane til punktet?
        if not p_path_valid:
            print("[P_METRIC] VETO: Bane mangler eller er ukjent. Status -> HOLD")
            return "HOLD"
            
        print("[GATE] Autorisasjon gitt. Transisjon til REALIZED godkjent.")
        return "REALIZED"

if __name__ == "__main__":
    gate = PhronesisGatekeeper()
    
    # Test 1: Gyldig progresjon der bane og punkt er verifisert
    print("--- TEST 1: KANONISK PROGRESJON ---")
    try:
        status = gate.evaluate_transit(current_state="STRUCT", np_point_exists=True, p_path_valid=True)
        print(f"Resultat: {status}\n")
    except OntologicalTypeException as e:
        print(f"Feil: {e}\n")

    # Test 2: Forsøk på snarvei (Typebrudd)
    print("--- TEST 2: ONTOLOGISK TYPEBRUDD ---")
    try:
        gate.evaluate_transit(current_state="RAW", np_point_exists=True, p_path_valid=True)
    except OntologicalTypeException as e:
        print(f"System-veto fanget opp: {e}")
