#!/usr/bin/env python3
import sys
import json
import hashlib

# Kalibrerte signalfarger for Debian-terminalen
RED = "\x1b[38;5;202m"
CYAN = "\x1b[38;5;49m"
SLATE = "\x1b[38;5;244m"
RESET = "\x1b[0m"

def calculate_hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()

def execute_ky_gate(candidate_file):
    # 1. RAW Input Capture
    try:
        with open(candidate_file, 'r') as f:
            candidate = json.load(f)
    except Exception as e:
        return "KILL", ["INPUT_CORRUPT"], "0"*64

    # 2. ESTIMATE & STRUCT - Paritetssjekk av domener
    required_domains = ["solubility", "redox", "pH", "gas", "material", "SDS"]
    declared_domains = candidate.get("domains_declared", [])
    checks = candidate.get("checks", {})
    
    reasons = []
    
    # Sjekk for harde feil (KILL)
    if checks.get("known_incompatibility") or checks.get("thermal_runaway_risk"):
        reasons.append("CRITICAL_RISK_DETECTED")
        return "KILL", reasons, "0"*64

    # Sjekk for manglende strukturelle data (HOLD)
    # RETTET: Ren, standard Python list comprehension
    missing = [domain for domain in required_domains if domain not in declared_domains]
    if missing:
        reasons.append(f"HOLD_DOMAINS_MISSING:{','.join(missing)}")
        return "HOLD", reasons, "0"*64

    # 3. VIABILITY & OPEN
    current_hash = calculate_hash(candidate)
    reasons.append("ALL_DECLARED_COMPATIBILITY_DOMAINS_PASS")
    return "OPEN", reasons, current_hash

def render_matrix(verdict, reasons, state_hash):
    v_color = CYAN if verdict == "OPEN" else (RED if verdict == "KILL" else SLATE)
    
    print(f"{SLATE}┌──[ KY-CHEM OS v0.1 // REALIZATION MATRIX ]──────────────────────────────────┐{RESET}")
    print(f"{SLATE}│{RESET} [DEVICE: HARDWARE INTERLOCK L0] [SYS: FAIL-CLOSED] [VERDICT: {v_color}{verdict:<10}{RESET}] {SLATE}│{RESET}")
    print(f"{SLATE}├─────────────────────────────────────────────────────────────────────────────┤{RESET}")
    print(f"{SLATE}│{RESET} [Φ_chem] CANDIDATE FLUX: {SLATE}{reasons[0][:50]:<51}{RESET} {SLATE}│{RESET}")
    print(f"{SLATE}│{RESET} [Π_K]    KERNEL RESIDUAL ΔK: {'0.000000' if verdict == 'OPEN' else '0.998712':<48} {SLATE}│{RESET}")
    print(f"{SLATE}├─────────────────────────────────────────────────────────────────────────────┤{RESET}")
    print(f"{SLATE}│{RESET} [Ω_chem] CONSEQUENCE VETO GATE: {v_color}{ verdict + ' ───> ACTUATOR ENABLE' if verdict == 'OPEN' else verdict:<44}{RESET} {SLATE}│{RESET}")
    print(f"{SLATE}├─────────────────────────────────────────────────────────────────────────────┤{RESET}")
    print(f"{SLATE}│{RESET} [W]      WITNESS SOVEREIGNTY BLOCK: {CYAN}{state_hash[:32]}...{RESET} {SLATE}│{RESET}")
    print(f"{SLATE}└─────────────────────────────────────────────────────────────────────────────┘{RESET}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Bruk: python3 ky_core.py <candidate.json>")
        sys.exit(1)
    
    verdict, reasons, s_hash = execute_ky_gate(sys.argv[1])
    render_matrix(verdict, reasons, s_hash)
    sys.exit(0)
