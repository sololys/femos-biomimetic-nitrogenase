import hashlib
import time

class ETOR2_HardwareLatch:
    def __init__(self):
        # Fail-closed: HPIS starter alltid død (0)
        self.hpis_latch = 0
        self.witness_ledger = hashlib.sha256(b"GENESIS_ETOR2").hexdigest()
        
        # Hardkodede fysiske skranker fra Sovereign Codex
        self.TAU = 0.05       # Maksimal epistemisk risiko (pi < tau)
        self.DELTA_R = 0.01   # Maksimal irreversibilitetsrate (dR/dt < delta_R)
        
        print("==================================================")
        print(" [E-TOR²] PHYSICAL AUTHORIZATION REGIME ONLINE")
        print(" [E-TOR²] Status: LATCHED (0) | WORM-Chain Armed")
        print("==================================================")

    def request_actuation(self, payload, quorum_valid, risk_pi, dR_dt):
        """Den uknuselige 5-trinns verifikasjonsporten (O(1) kompleksitet)"""
        
        print(f"\n--- [KLOKKEPULS] Evaluering: {payload} ---")
        
        # 1. QUORUM (BFT Authority)
        if not quorum_valid:
            return self._trigger_kill("QUORUM_FAIL", "Mangler autoritet.")
            
        # 2. EPISTEMISK TERSKEL (pi < tau)
        if risk_pi >= self.TAU:
            return self._trigger_kill("EPISTEMIC_OVERLOAD", f"Risiko {risk_pi} overstiger TAU {self.TAU}.")
            
        # 3. IRREVERSIBILITETSMARGIN (dR/dt < delta_R)
        if dR_dt >= self.DELTA_R:
            return self._trigger_kill("THERMODYNAMIC_BREACH", f"Irreversibilitetsrate {dR_dt} overstiger DELTA_R {self.DELTA_R}.")
            
        # 4. PRE-COMMIT WITNESS² (Historieforsegling FØR aktuering)
        # Hash-kjeden låser parametrene. Hvis denne feiler, aktiveres aldri HPIS.
        pre_commit_data = f"{payload}|Q:1|pi:{risk_pi}|dR:{dR_dt}|PREV:{self.witness_ledger}".encode('utf-8')
        self.witness_ledger = hashlib.sha256(pre_commit_data).hexdigest()
        
        # 5. HPIS (Fysisk energi-frigjøring)
        self.hpis_latch = 1
        print(">> [WITNESS²]  : FORSEGLET FØR AKTUERING.")
        print(f">> [WITNESS²]  : W_k = {self.witness_ledger[:16]}...")
        print(">> [HPIS LATCH]: 1 -> ENERGI FRIGITT. REALITET INNRØMMET (OPEN).")
        
        return self.hpis_latch

    def _trigger_kill(self, error_code, detail):
        """Terminal Sink - jording av signal ved ontologisk smerte"""
        self.hpis_latch = 0
        print(f">> [RC-701]    : {error_code} - {detail}")
        print(">> [WITNESS²]  : FORSEGLING AVBRUTT. INGEN HISTORISK VEKT.")
        print(">> [HPIS LATCH]: 0 -> STRØM BRUTT. DISSIPERT TIL D_REG (KILL).")
        return self.hpis_latch


if __name__ == "__main__":
    engine = ETOR2_HardwareLatch()
    
    time.sleep(1)
    # Test A: Perfekt overgang (Alt innenfor grensen)
    engine.request_actuation("Kandidat_A_Gyldig", quorum_valid=True, risk_pi=0.02, dR_dt=0.005)
    
    time.sleep(1)
    # Test B: Epistemisk brudd (For mye støy)
    engine.request_actuation("Kandidat_B_Støy", quorum_valid=True, risk_pi=0.08, dR_dt=0.005)
    
    time.sleep(1)
    # Test C: Termodynamisk brudd (Tvinger for hardt)
    engine.request_actuation("Kandidat_C_Tvunget", quorum_valid=True, risk_pi=0.03, dR_dt=0.05)
    
    time.sleep(1)
    # Test D: Autoritetssvikt
    engine.request_actuation("Kandidat_D_Rogue", quorum_valid=False, risk_pi=0.01, dR_dt=0.001)
