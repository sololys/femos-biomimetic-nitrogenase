#!/usr/bin/env python3
"""
Quantum Perception (NP) & Gravitational Realization (P) Engine — Production Reference
Implements the core axiom: Reality is not generated. Reality is admitted.
"""

import math
import json
import unittest
import hashlib
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class QuantumProposalNP:
    proposal_id: str
    wave_function_amplitude: float  # |Psi|^2
    entropy_raw: float              # Unregulated candidate entropy

@dataclass
class AdmittedRealityP:
    proposal_id: str
    is_admitted: bool
    projection_residual: float
    hardware_power_watts: float
    witness_seal: str

class QuantumPerceptionEngine:
    """NP Domain: Quantum = Perception (Unregulated Candidate Proposals)."""
    @staticmethod
    def generate_perception_cloud(count: int = 5) -> List[QuantumProposalNP]:
        proposals = []
        for i in range(count):
            amp = (i + 1) * 0.18
            entropy = (count - i) * 0.25
            proposals.append(QuantumProposalNP(
                proposal_id=f"PROP_PSI_{i+1:02d}",
                wave_function_amplitude=round(amp, 4),
                entropy_raw=round(entropy, 4)
            ))
        return proposals

class GravitationalRealizationFilterP:
    """P Domain: Gravity = Realization (Structural Selection Filter Pi_K)."""
    def __init__(self, max_entropy_threshold: float = 0.50):
        self.max_entropy_threshold = max_entropy_threshold

    def evaluate_admission(self, prop: QuantumProposalNP) -> AdmittedRealityP:
        # Selection projection residual Pi_K(Phi(x))
        residual = prop.entropy_raw

        if residual <= self.max_entropy_threshold and prop.wave_function_amplitude >= 0.5:
            is_admitted = True
            power_watts = 100.0  # Hardware powered ON
            status = "ADMITTED_REALITY"
        else:
            is_admitted = False
            power_watts = 0.0    # Hardware Power Cutoff: Pi_K = 0 => u = 0 W
            status = "REJECTED_SACRED_TRASH"

        seal = "WITNESS_REALITY_" + hashlib.sha256(f"{prop.proposal_id}_{is_admitted}_{power_watts}".encode()).hexdigest()[:16].upper()

        return AdmittedRealityP(
            proposal_id=prop.proposal_id,
            is_admitted=is_admitted,
            projection_residual=round(residual, 4),
            hardware_power_watts=power_watts,
            witness_seal=seal
        )

class TestQuantumPerceptionRealizationEngine(unittest.TestCase):
    def setUp(self):
        self.filter_p = GravitationalRealizationFilterP(max_entropy_threshold=0.50)

    def test_admitted_reality(self):
        # Proposal with low entropy and high amplitude passes filter
        prop = QuantumProposalNP(proposal_id="PROP_PASS", wave_function_amplitude=0.8, entropy_raw=0.2)
        res = self.filter_p.evaluate_admission(prop)
        self.assertTrue(res.is_admitted)
        self.assertEqual(res.hardware_power_watts, 100.0)

    def test_hardware_interlock_cutoff(self):
        # Proposal exceeding entropy threshold triggers hardware power cutoff (0 W)
        prop = QuantumProposalNP(proposal_id="PROP_FAIL", wave_function_amplitude=0.9, entropy_raw=0.8)
        res = self.filter_p.evaluate_admission(prop)
        self.assertFalse(res.is_admitted)
        self.assertEqual(res.hardware_power_watts, 0.0)

def run_audit():
    print("=== Quantum Perception & Gravitational Realization Engine Audit ===")
    proposals = QuantumPerceptionEngine.generate_perception_cloud(count=5)
    filter_p = GravitationalRealizationFilterP(max_entropy_threshold=0.50)

    results = []
    for p in proposals:
        adm = filter_p.evaluate_admission(p)
        results.append({
            "proposal_id": p.proposal_id,
            "wave_amplitude_sq": p.wave_function_amplitude,
            "entropy_raw": p.entropy_raw,
            "is_admitted": adm.is_admitted,
            "hardware_power_W": adm.hardware_power_watts,
            "witness_seal": adm.witness_seal
        })

    audit = {
        "axiom": "REALITY_IS_NOT_GENERATED_REALITY_IS_ADMITTED",
        "quantum_np_domain": "PERCEPTION",
        "gravity_p_domain": "REALIZATION",
        "evaluated_proposals": results
    }

    print("\n[AUDIT REPORT JSON]")
    print(json.dumps(audit, indent=2))

if __name__ == '__main__':
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestQuantumPerceptionRealizationEngine)
    test_res = unittest.TextTestRunner(verbosity=0).run(test_suite)
    if test_res.wasSuccessful():
        run_audit()
    else:
        print("SYSTEM HALT: Tests failed.")
