#!/usr/bin/env python3
import sys
import json
import hashlib
import os

# Kalibrerte signalfarger for Debian-terminalen
RED = "\x1b[38;5;202m"
CYAN = "\x1b[38;5;49m"
SLATE = "\x1b[38;5;244m"
RESET = "\x1b[0m"

LEDGER_FILE = "witness_ledger.json"

def calculate_block_hash(block):
    # Generer en deterministisk hash av hele blokken unntatt selve hashfeltet
    block_copy = {k: v for k, v in block.items() if k != "hash"}
    return hashlib.sha256(json.dumps(block_copy, sort_keys=True).encode('utf-8')).hexdigest()

def init_ledger():
    if not os.path.exists(LEDGER_FILE):
        genesis = {
            "index": 0,
            "previous_hash": "0" * 64,
            "event_data": {"event": "GENESIS_REALIZATION_ROOT"},
            "hash": ""
        }
        genesis["hash"] = calculate_block_hash(genesis)
        with open(LEDGER_FILE, 'w') as f:
            json.dump([genesis], f, indent=2)

def append_witness(event_data):
    init_ledger()
    with open(LEDGER_FILE, 'r+') as f:
        ledger = json.load(f)
        prev_block = ledger[-1]
        
        new_block = {
            "index": len(ledger),
            "previous_hash": prev_block["hash"],
            "event_data": event_data,
            "hash": ""
        }
        new_block["hash"] = calculate_block_hash(new_block)
        ledger.append(new_block)
        
        f.seek(0)
        json.dump(ledger, f, indent=2)
        f.truncate()
    return new_block["hash"]

def verify_ledger():
    if not os.path.exists(LEDGER_FILE):
        return True, "No ledger found. Clean genesis implied."
    
    with open(LEDGER_FILE, 'r') as f:
        ledger = json.load(f)
        
    for i in range(len(ledger)):
        block = ledger[i]
        # Verifiser egen-hash
        recalculated = calculate_block_hash(block)
        if recalculated != block["hash"]:
            return False, f"Block {i} hash corrupted! Expected: {block['hash'][:8]}... Got: {recalculated[:8]}..."
        
        # Verifiser lenken bakover
        if i > 0:
            prev_block = ledger[i-1]
            if block["previous_hash"] != prev_block["hash"]:
                return False, f"Chain broken at Block {i}! Prev block hash changed."
                
    return True, f"Kjede intakt over {len(ledger)} blokker."

def tamper_ledger(index, corrupted_key, corrupted_value):
    if not os.path.exists(LEDGER_FILE):
        print("No ledger to tamper.")
        return
    with open(LEDGER_FILE, 'r+') as f:
        ledger = json.load(f)
        if index < len(ledger):
            ledger[index]["event_data"][corrupted_key] = corrupted_value
            f.seek(0)
            json.dump(ledger, f, indent=2)
            f.truncate()
            print(f"{RED}[!] TAMPER_INJECTED:{RESET} Manipulerte blokk {index}: set '{corrupted_key}' -> '{corrupted_value}'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Bruk:")
        print("  python3 witness_manager.py append <event_msg>")
        print("  python3 witness_manager.py verify")
        print("  python3 witness_manager.py tamper <index> <key> <val>")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "append":
        msg = sys.argv[2] if len(sys.argv) > 2 else "DEFAULT_REALIZATION"
        h = append_witness({"event": msg})
        print(f"La til Witness. Ny tilstandshash: {CYAN}{h[:32]}...{RESET}")
    elif cmd == "verify":
        ok, msg = verify_ledger()
        if ok:
            print(f"{CYAN}┌──[ WITNESS CHAIN: VERIFIED ]──────────────────────────────────────────────┐{RESET}")
            print(f"{CYAN}│{RESET} STATUS: OPEN / SECURE                                                     {CYAN}│{RESET}")
            print(f"{CYAN}│{RESET} MESSAGE: {msg:<64} {CYAN}│{RESET}")
            print(f"{CYAN}└────────────────────────────────────────────────────────────────────────────┘{RESET}")
        else:
            print(f"{RED}┌──[ !!! SYSTEM LOCKDOWN: RC-701 !!! ]────────────────────────────────────────┐{RESET}")
            print(f"{RED}│{RESET} STATUS: FAIL_LOCK / CAUSAL CHAIN BREACH                                    {RED}│{RESET}")
            print(f"{RED}│{RESET} FAULT: {msg[:66]:<67} {RED}│{RESET}")
            print(f"{RED}└────────────────────────────────────────────────────────────────────────────┘{RESET}")
            sys.exit(1)
    elif cmd == "tamper":
        idx = int(sys.argv[2])
        k = sys.argv[3]
        v = sys.argv[4]
        tamper_ledger(idx, k, v)
