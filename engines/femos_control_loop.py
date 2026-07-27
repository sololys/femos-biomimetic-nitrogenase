from dataclasses import dataclass
from math import isfinite

@dataclass
class Candidate:
    name: str
    kie: float
    delta_delta: float
    stability: float   # 0.0 bad, 1.0 excellent
    fe: float          # Faradaic efficiency, 0-1
    delta_E_mV: float  # improvement in mV
    recovery_30s: float # drift after perturbation, 0-1

def kie_gate(kie):
    if kie < 2.0:
        return "KILL", "KIE below PCET threshold"
    if kie > 7.0:
        return "HOLD", "KIE suggests tunneling/anomaly"
    return "PASS", "PCET-plausible"

def mossbauer_zone(delta):
    if not isfinite(delta):
        return "HOLD", "invalid Δδ"
    if -0.04 <= delta <= 0.04:
        return "NO_MUTATION", "isometric null zone"
    if 0.04 < delta <= 0.10:
        return "PERIPHERAL_INDUCTION", "moderate electron deficit"
    if delta > 0.10:
        return "ASYMMETRIC_DONATION", "strong electron deficit"
    if -0.10 <= delta < -0.04:
        return "APICAL_ELECTRON_DRAIN", "moderate electron excess"
    if delta < -0.10:
        return "GLOBAL_ELECTRON_DRAIN", "extreme electron excess"
    return "HOLD", "unclassified zone"

def performance_gate(c):
    if c.delta_E_mV < 100:
        return "KILL", "insufficient potential improvement"
    if c.fe < 0.85:
        return "KILL", "insufficient faradaic efficiency"
    return "PASS", "performance acceptable"

def perturbation_gate(c):
    if c.recovery_30s > 0.05:
        return "KILL", "failed perturbation recovery"
    if c.stability < 0.80:
        return "KILL", "latent structural instability"
    return "PASS", "perturbation recovery acceptable"

def realization_energy(c):
    e_kie = max(0, 2.0 - c.kie) + max(0, c.kie - 7.0)
    e_delta = abs(c.delta_delta)
    e_stability = max(0, 0.80 - c.stability)
    e_fe = max(0, 0.85 - c.fe)
    e_E = max(0, 100 - c.delta_E_mV) / 100
    e_recovery = max(0, c.recovery_30s - 0.05)
    return (
        2.0 * e_kie**2 +
        5.0 * e_delta**2 +
        3.0 * e_stability**2 +
        3.0 * e_fe**2 +
        2.0 * e_E**2 +
        4.0 * e_recovery**2
    )

def evaluate(c):
    trace = []

    verdict, reason = kie_gate(c.kie)
    trace.append(("KIE", verdict, reason))
    if verdict != "PASS":
        return c.name, verdict, realization_energy(c), trace

    zone, reason = mossbauer_zone(c.delta_delta)
    trace.append(("MOSSBAUER", zone, reason))

    verdict, reason = performance_gate(c)
    trace.append(("PERFORMANCE", verdict, reason))
    if verdict != "PASS":
        return c.name, verdict, realization_energy(c), trace

    verdict, reason = perturbation_gate(c)
    trace.append(("PERTURBATION", verdict, reason))
    if verdict != "PASS":
        return c.name, verdict, realization_energy(c), trace

    if zone == "NO_MUTATION":
        return c.name, "OPEN", realization_energy(c), trace
    return c.name, "HOLD", realization_energy(c), trace

candidates = [
    Candidate("A_low_KIE", 1.4, 0.02, 0.95, 0.90, 140, 0.02),
    Candidate("B_recalibrate", 3.8, 0.07, 0.92, 0.88, 130, 0.03),
    Candidate("C_open", 4.2, 0.01, 0.96, 0.91, 150, 0.02),
    Candidate("D_false_convergence", 4.5, 0.00, 0.55, 0.90, 150, 0.02),
    Candidate("E_bad_FE", 4.0, -0.06, 0.90, 0.60, 160, 0.03),
    Candidate("F_fragile", 4.0, 0.01, 0.90, 0.90, 160, 0.12),
]

for c in candidates:
    name, verdict, V, trace = evaluate(c)
    print(f"\n{name}: {verdict} | V={V:.6f}")
    for stage, local_verdict, reason in trace:
        print(f"  {stage:12s} -> {local_verdict:22s} | {reason}")
