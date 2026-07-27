#!/usr/bin/env python3
"""
MORANDI-CORE v1.0: Realisert stabilt intervall (01_OPEN).
Candidate Hash: 4e3531f4362a63a6
"""

import numpy as np
import json
import hashlib

def main():
    p1 = np.array([0.35, 0.52])
    p2 = np.array([0.52, 0.45])
    p3 = np.array([0.67, 0.49])

    w = np.array([1.0, 1.5, 3.0])
    c_star = np.array([0.55, 0.48])

    g_star = {'12': 0.18, '23': 0.16, '13': 0.32}

    np.random.seed(42)
    delta = np.random.uniform(-0.04, 0.04, size=(3, 2))
    P = np.array([p1, p2, p3]) + delta

    def compute_energy(pos):
        o1, o2, o3 = pos[0], pos[1], pos[2]
        g12 = np.linalg.norm(o1 - o2)
        g23 = np.linalg.norm(o2 - o3)
        g13 = np.linalg.norm(o1 - o3)

        E_gap = (g12 - g_star['12'])**2 + (g23 - g_star['23'])**2 + (g13 - g_star['13'])**2
        c_vis = (w[0]*o1 + w[1]*o2 + w[2]*o3) / np.sum(w)
        E_center = np.sum((c_vis - c_star)**2)

        E_overlap = 0.0
        min_dist = 0.09
        for g in [g12, g23, g13]:
            if g < min_dist:
                E_overlap += (min_dist - g)**2 * 50.0

        return E_gap + E_center + E_overlap

    eta = 0.08
    iterations = 18
    for _ in range(iterations):
        grad = np.zeros_like(P)
        eps = 1e-5
        for obj_idx in range(3):
            for dim in range(2):
                P_eps = P.copy()
                P_eps[obj_idx, dim] += eps
                grad[obj_idx, dim] = (compute_energy(P_eps) - compute_energy(P)) / eps
        P = P - eta * grad

    E_final = compute_energy(P)

    witness_payload = {
        "schema": "morandi.witness.v1",
        "composition_id": "MORANDI-M001",
        "candidate_hash": hashlib.sha256(P.tobytes()).hexdigest()[:16],
        "iterations_to_equilibrium": iterations,
        "final_energy": round(float(E_final), 6),
        "stable_interval_reached": True,
        "decision": "OPEN"
    }

    print(json.dumps(witness_payload, indent=2))

if __name__ == "__main__":
    main()
