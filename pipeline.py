import math
import time
from civil_spectrometer import CivilMossbauerValidator
from fork_simulator import TheForkSimulation
from hpis_latch import TheThirdSpaceRegulator as HPISLatch
from reversible_core import ReversibleEpistemicCore as ReversibleCore

class AtlasPipelineOrchestrator:
    def __init__(self):
        self.spectrometer = CivilMossbauerValidator()
        self.fork = TheForkSimulation()
        self.hpis = HPISLatch()
        self.engine = ReversibleCore()

    def execute_full_cycle(self, o2, nh3, shift, flux):
        print("========================================================")
        print("=== INITIATION: SAMLET ATLAS REALISERINGKPIPELINE ===")
        print("========================================================")
        
        # LAG 1: CIVIL Spektral & Anaerob Kontroll
        print("\n[FASE 1/4] Kjører CIVIL Fe-Mo-S Spektral-Validator...")
        status, reason = self.spectrometer.ingest_payload(o2, nh3, shift)
        if status != "ALLOW":
            print(f"!! BRUDD I FASE 1: {reason}. Avbryter pipeline.")
            return "PIPELINE_KILL_LAYER_1"
            
        # LAG 2: Forgreningsdivergens & Amputasjonssjekk
        print("\n[FASE 2/4] Evaluerer divergenseffekt i forgreningen (The Fork)...")
        raw_path = self.fork.phi_evolution()
        shadow_A = self.fork.projection_k_a(raw_path)
        shadow_B = self.fork.projection_k_b(raw_path)
        divergence = math.sqrt(sum((a - b)**2 for a, b in zip(shadow_A, shadow_B)))
        print(f"  -> Målt ΔM: {divergence:.6f}")

        # LAG 2: Fail-closed dom over forgreningen (Kalibrert til 0.07)
        if divergence > 0.07:
            return "PIPELINE_HOLD_LAYER_2"

        # LAG 3: Det Tredje Rommet & Meta-stabilitet (Hamiltonian-sjekk)
        print("\n[FASE 3/4] Beregner master-Hamiltonian H_φ i det Tredje Rommet...")
        self.hpis.b12_buffer += 0.5 # Akkumulert spenning i tomrommet
        H_phi = self.hpis.calculate_hamiltonian(flux)
        print(f"  -> H_φ: {H_phi:.4f} | Buffer-arr: {self.hpis.b12_buffer:.3f}")
        if H_phi > 1.0:
            print("!! BRUDD I FASE 3: Stabilitetsbrudd detektert!")
            self.hpis.trigger_hpis_guillotine()
            return "PIPELINE_HPIS_TRIPPED"

        # LAG 4: Endelig Ω-gate Commit & WORM Vitneføring
        print("\n[FASE 4/4] Innretter endelig Ω-gate audit og uforanderlig commit...")
        result_state = self.engine.execute_transition(initial_state=shift, risk=flux, action="ATLAS_INTEGRATED_NODE")
        success = (result_state == "COMMIT_SUCCESS")
        
        if success:
            print("========================================================")
            print(">>> SUCCESS: CD ER REALISERT OVER HELE ATLAS-ATLASEN <<<")
            print("========================================================")
            return "ATLAS_REALIZED_SUCCESS"
        else:
            return f"PIPELINE_HOLD_LAYER_4 ({result_state})"

if __name__ == "__main__":
    orchestrator = AtlasPipelineOrchestrator()
    orchestrator.execute_full_cycle(o2=0.1, nh3=0.0, shift=0.8, flux=0.3)
