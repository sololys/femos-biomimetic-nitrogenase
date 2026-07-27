#!/usr/bin/env python3
"""
ky_parser.py
============
KY-Grammar State Realization Parser & Gate Verifier (v1.0)

Lifecycle State Transition Chain:
  ○ (RAW) -> ◇ (BOUND) -> □ (VERIFIED) -> O (STAGED) -> • (COMMITTED)

Grammar Syntax & Rules:
  1. Enclosure Rule: Core state chain must be enclosed in parentheses '(...)'
  2. Audit Prefix: '☑' indicates verified audit prefix.
  3. Gate Claim Marks (at end):
       '►' ==> Claims OPEN
       '⏸' ==> Claims HOLD
       'X' ==> Claims KILL
  4. Inadmissibility Mark:
       '∉K' ==> Marks state sequence as outside admissible set K (Forces KILL).
  5. Audit Law:
       If sequence reaches COMMITTED '•', it MUST possess both witness hash '#'
       and attestation mark '!' before the gate claim.
  6. Gate Mismatch Law:
       Claimed gate ('►', '⏸', 'X') MUST match computed gate. Mismatch forces KILL.
"""

import re
from typing import List, Optional

class KYParseResult:
    def __init__(self, syntax: str = 'valid', type_status: str = 'valid', 
                 admissibility: str = 'open', gate: str = 'OPEN', reasons: Optional[List[str]] = None):
        self.syntax = syntax
        self.type_status = type_status
        self.admissibility = admissibility
        self.gate = gate
        self.reasons = reasons if reasons is not None else []

class KYParser:
    VALID_STATES = ['○', '◇', '□', 'O', '•']
    STATE_INDEX = {s: i for i, s in enumerate(VALID_STATES)}

    def evaluate(self, expr: str) -> KYParseResult:
        expr = expr.strip()
        reasons = []

        # 1. Syntax Check: Check for parenthesized chain '(...)'
        chain_match = re.search(r'\(([^)]+)\)', expr)
        if not chain_match:
            return KYParseResult(
                syntax='invalid',
                type_status='invalid',
                admissibility='inadmissible',
                gate='KILL',
                reasons=['Syntax Error: Missing parentheses enclosing state chain']
            )

        chain_str = chain_match.group(1).strip()
        
        # 2. Extract Claimed Gate Mark
        claimed_gate_symbol = None
        if expr.endswith('►'):
            claimed_gate_symbol = '►'
        elif expr.endswith('⏸'):
            claimed_gate_symbol = '⏸'
        elif expr.endswith('X'):
            claimed_gate_symbol = 'X'

        # 3. Check for Inadmissible Mark '∉K'
        is_inadmissible = '∉K' in expr

        # 4. Check for Audit Marks ('#' and '!')
        has_hash = '#' in expr
        has_excl = '!' in expr
        has_audit_prefix = '☑' in expr

        # 5. Parse State Chain Transitions (split by '→' or '~')
        # Replace '~' with '→' for transition splitting
        normalized_chain = chain_str.replace('~', '→')
        raw_nodes = [s.strip() for s in normalized_chain.split('→') if s.strip()]

        type_status = 'valid'
        # Check transitions
        for i in range(len(raw_nodes) - 1):
            curr_s = raw_nodes[i]
            next_s = raw_nodes[i+1]

            if curr_s not in self.STATE_INDEX or next_s not in self.STATE_INDEX:
                type_status = 'invalid'
                reasons.append(f"Type Error: Unknown state symbol '{curr_s}' or '{next_s}'")
                break

            curr_idx = self.STATE_INDEX[curr_s]
            next_idx = self.STATE_INDEX[next_s]

            # Transition rule: Step size must be 1 (e.g. ○->◇) or same level
            if next_idx - curr_idx > 1 or next_idx < curr_idx:
                type_status = 'invalid'
                reasons.append(f"Type Error: Invalid shortcut transition '{curr_s}' -> '{next_s}'")
                break

        # Compute Expected Gate
        reaches_committed = ('•' in raw_nodes)
        is_hold = ('~' in chain_str or claimed_gate_symbol == '⏸') and not reaches_committed

        # Apply Inadmissible Overrides
        if is_inadmissible:
            reasons.append("Inadmissible mark ∉K present")

        # Apply Audit Law on Committed State
        audit_law_violation = False
        if reaches_committed and not (has_hash and has_excl):
            audit_law_violation = True
            reasons.append("Audit Law Violation: Committed state '•' requires '#' and '!'")

        # Determine Logical Gate
        if type_status == 'invalid' or is_inadmissible or audit_law_violation:
            computed_gate = 'KILL'
        elif is_hold:
            computed_gate = 'HOLD'
        else:
            computed_gate = 'OPEN'

        # Check Gate Mismatch (if claimed gate does not match computed gate)
        if claimed_gate_symbol == '►' and computed_gate != 'OPEN':
            reasons.append(f"Gate Mismatch: Claimed '►' (OPEN) but computed '{computed_gate}'")
            computed_gate = 'KILL'
        elif claimed_gate_symbol == '⏸' and computed_gate != 'HOLD':
            reasons.append(f"Gate Mismatch: Claimed '⏸' (HOLD) but computed '{computed_gate}'")
            computed_gate = 'KILL'
        elif claimed_gate_symbol == 'X' and computed_gate != 'KILL':
            reasons.append(f"Gate Mismatch: Claimed 'X' (KILL) but computed '{computed_gate}'")

        admissibility = 'hold' if computed_gate == 'HOLD' else ('open' if computed_gate == 'OPEN' else 'inadmissible')
        syntax = 'valid' if type_status == 'valid' else 'invalid'

        return KYParseResult(
            syntax=syntax,
            type_status=type_status,
            admissibility=admissibility,
            gate=computed_gate,
            reasons=reasons
        )
