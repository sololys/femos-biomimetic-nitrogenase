import re
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class EvalResult:
    syntax: str
    type_status: str
    admissibility: str
    gate: str
    reasons: List[str] = field(default_factory=list)

class KYParser:
    """
    K-C3 Protocol Directorate: Formal KY v1.0 Parser.
    Implements strict structural, temporal, and gating checks.
    """
    NODES = {'○': 0, '◇': 1, '□': 2, 'Δ': 3, 'O': 4, '•': 5}
    FLOWS = ['→', '~', '⇒']
    VALIDITY = ['∈K', '∉K', '≠']
    AUDIT = ['#', '!']
    GATES = {'►': 'OPEN', '⏸': 'HOLD', 'X': 'KILL'}
    
    def __init__(self):
        # Regex to tokenize the strict EBNF structure
        self.expr_pattern = re.compile(
            r'^(?P<val_prefix>☑)?\((?P<chain>[○◇□ΔO•→~⇒]+)\)(?P<val_suffix>∈K|∉K|≠)?(?P<audit>[#!τ]*)\s*(?P<gate>[►⏸X])$'
        )

    def evaluate(self, expression: str) -> EvalResult:
        expression = expression.strip()
        match = self.expr_pattern.match(expression)
        
        if not match:
            return EvalResult('invalid', 'invalid', 'kill', 'KILL', ['Syntax Error: Does not match KY EBNF format.'])

        parts = match.groupdict()
        reasons = []
        
        # 1. Type & Chain Check
        chain = parts['chain']
        type_valid, chain_reasons = self._check_chain_types(chain)
        reasons.extend(chain_reasons)
        
        # 2. Admissibility & Audit Check
        is_admissible = True
        calc_gate = 'OPEN'
        
        if parts['val_suffix'] == '∉K':
            is_admissible = False
            reasons.append('Inadmissible mark (∉K) forces KILL.')
            calc_gate = 'KILL'
            
        elif parts['val_suffix'] == '≠':
            is_admissible = False
            reasons.append('Structural breakdown (≠) forces KILL.')
            calc_gate = 'KILL'

        # Audit Law
        if ('•' in chain or '⇒' in chain) and not parts['audit']:
            is_admissible = False
            reasons.append('Audit Law Violation: Irreversible node/flow lacks witness (# or !).')
            calc_gate = 'KILL'

        # 3. Consolidate logic for HOLD vs OPEN
        if not type_valid and calc_gate != 'KILL':
            calc_gate = 'KILL'
            is_admissible = False
            
        if calc_gate == 'OPEN' and ('~' in chain or parts['gate'] == '⏸'):
            # Allow explicit HOLDs if the chain is otherwise valid but paused
            calc_gate = 'HOLD'
            if parts['gate'] == '⏸':
                reasons.append('Expression explicitly marked for HOLD.')

        # 4. Gate Matching
        declared_gate = self.GATES[parts['gate']]
        if declared_gate != calc_gate:
            reasons.append(f'Gate Mismatch: Evaluated to {calc_gate}, but declared as {declared_gate}.')
            calc_gate = 'KILL' # Fail-closed on mismatch
        else:
            reasons.append('Gate matches computed structural status.')

        return EvalResult(
            syntax='valid',
            type_status='valid' if type_valid else 'invalid',
            admissibility='pass' if is_admissible and calc_gate == 'OPEN' else ('hold' if calc_gate == 'HOLD' else 'kill'),
            gate=calc_gate,
            reasons=reasons
        )

    def _check_chain_types(self, chain: str):
        reasons = []
        # Extract nodes (ignoring flows for the basic strict rank check)
        nodes_in_chain = [char for char in chain if char in self.NODES]
        
        for i in range(len(nodes_in_chain) - 1):
            curr_rank = self.NODES[nodes_in_chain[i]]
            next_rank = self.NODES[nodes_in_chain[i+1]]
            
            if next_rank == curr_rank:
                continue # Loop/Drift is type-safe
            elif (curr_rank == 0 and next_rank == 5) or next_rank < curr_rank or (next_rank - curr_rank > 2):
                reasons.append(f"Type Error: Illegal transition from {nodes_in_chain[i]} to {nodes_in_chain[i+1]}.")
                return False, reasons
                
        return True, reasons
