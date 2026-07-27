#!/usr/bin/env python3
"""
google_drive_associative_network.py
===================================
Google Drive Assosiativt Nettverk for Reismannpoint Observatorium (v1.0)

Bygger et assosiativt graf-nettverk og vektormatrise for Google Disk:
  1. Kobler de 43 Metamorfose-motorene til domener, aksiomer og 3-tier attester.
  2. Beregner Hebbisk / Cosine assosiasjonsmatrise mellom noder.
  3. Genererer uforanderlig `google_drive_associative_network.json` for Google Disk-synkronisering.
"""

import sys
import os
import json
import hashlib
import time
import math
from typing import Dict, List, Any, Tuple

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ENGINES_DIR = os.path.join(BASE_DIR, "engines")

class GoogleDriveAssociativeNetwork:
    def __init__(self, base_dir: str = BASE_DIR):
        self.base_dir = base_dir
        self.engines_dir = os.path.join(base_dir, "engines")
        self.nodes = {}
        self.edges = []
        self.association_matrix = {}

    def build_network(self) -> Dict[str, Any]:
        sys.path.insert(0, self.engines_dir)
        sys.path.insert(0, self.base_dir)
        from master_all_engines_sweep import METAMORPHOSIS_ENGINES, run_independent_3tier_sweep

        print("🧠 Bygger Assosiativt Graf-Nettverk for Google Disk...")
        sweep_data = run_independent_3tier_sweep()

        # Domene-gruppering for assosiasjoner
        categories = {
            "BIO_CATALYSIS": ["femos", "gscx", "cpcab"],
            "QUANTUM_GRAVITY": ["qcs", "quantum_gravity", "kerr", "holomorphic"],
            "GAME_THEORY_NASH": ["four_field_nash", "ky_nash", "sacl"],
            "FOUNDATIONAL_AXIOMS": ["arkitektens_nullpunkt", "cdc_complexity", "selection_ontology"],
            "NEURAL_HARDWARE": ["phronesis_neural", "phronesis_hardware", "iks_reversible"]
        }

        # 1. Opprett Noder (Engine Nodes & Domain Nodes)
        for idx, engine_file in enumerate(METAMORPHOSIS_ENGINES, 1):
            name_key = engine_file.replace(".py", "")
            node_id = f"drive_node_{idx:02d}"
            
            # Finn kategori
            assigned_cat = "GENERAL_METAMORPHOSIS"
            for cat, keywords in categories.items():
                if any(kw in name_key for kw in keywords):
                    assigned_cat = cat
                    break

            attestation = sweep_data["results"][idx - 1]
            sha256_sig = hashlib.sha256(f"{node_id}:{name_key}:{assigned_cat}".encode()).hexdigest()

            self.nodes[node_id] = {
                "id": node_id,
                "engine_file": engine_file,
                "domain_category": assigned_cat,
                "software_pass": attestation["software"]["passed"],
                "model_pass": attestation["model"]["passed"],
                "evidence_pass": attestation["evidence"]["verified"],
                "sha256_warrant": sha256_sig,
                "gdrive_metadata": {
                    "mimeType": "application/x-python",
                    "appProperties": {
                        "associative_category": assigned_cat,
                        "3tier_verdict": attestation["overall_verdict"],
                        "locus_level": "0"
                    }
                }
            }

        # 2. Bygg Assosiativ Koblingsmatrise (Edges)
        node_keys = list(self.nodes.keys())
        for i in range(len(node_keys)):
            for j in range(i + 1, len(node_keys)):
                n1 = self.nodes[node_keys[i]]
                n2 = self.nodes[node_keys[j]]

                # Hebbisk vekt: Høyere hvis de deler domene eller verifikasjonsstatus
                weight = 0.2
                if n1["domain_category"] == n2["domain_category"]:
                    weight += 0.6
                if n1["evidence_pass"] and n2["evidence_pass"]:
                    weight += 0.2

                if weight >= 0.5:
                    edge = {
                        "source": n1["id"],
                        "target": n2["id"],
                        "association_weight": round(weight, 3),
                        "relationship": "SYNAPTIC_ASSOCIATION"
                    }
                    self.edges.append(edge)

        # 3. Forsegle Nettverket med Manifest SHA-256 for Google Disk
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        raw_graph = json.dumps({"nodes": self.nodes, "edges": self.edges}, sort_keys=True)
        graph_manifest_sha256 = hashlib.sha256(raw_graph.encode("utf-8")).hexdigest()

        associative_payload = {
            "network_title": "Reismannpoint Observatorium Google Drive Associative Network",
            "version": "v1.0",
            "timestamp_iso": ts,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "graph_manifest_sha256": graph_manifest_sha256,
            "nodes": self.nodes,
            "edges": self.edges
        }

        output_file = os.path.join(self.base_dir, "google_drive_associative_network.json")
        with open(output_file, "w") as f:
            json.dump(associative_payload, f, indent=2, ensure_ascii=False)

        print(f"🔒 Assosiativt Nettverk forseglet og skrevet til: {output_file}")
        print(f"🔑 Manifest SHA-256: {graph_manifest_sha256}")
        print(f"🕸️ Noder: {len(self.nodes)} | Synaptiske Koblinger: {len(self.edges)}")

        return associative_payload


def main():
    network = GoogleDriveAssociativeNetwork()
    network.build_network()

if __name__ == "__main__":
    main()
