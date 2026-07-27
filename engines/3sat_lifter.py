#!/usr/bin/env python3
import sys
import time
import json

# Terminalestetikk
BLUE = "\x1b[38;5;33m"
SLATE = "\x1b[38;5;244m"
CYAN = "\x1b[38;5;49m"
RED = "\x1b[38;5;202m"
RESET = "\x1b[0m"

class DPLLSolver:
    def __init__(self, num_vars, clauses):
        self.num_vars = num_vars
        self.clauses = clauses
        self.backtracks = 0
        self.nodes_explored = 0

    def solve(self):
        assignment = {}
        start_time = time.perf_counter()
        success = self._dpll(assignment)
        end_time = time.perf_counter()
        return success, assignment, end_time - start_time

    def _dpll(self, assignment):
        self.nodes_explored += 1
        
        # Sjekk om alle klausuler er oppfylt, eller om vi har en kollaps (False)
        status = self._evaluate_clauses(assignment)
        if status is True:
            return True
        if status is False:
            self.backtracks += 1
            return False

        # Finn neste uassignede variabel (q_i)
        var = self._select_unassigned(assignment)
        if var is None:
            return True

        # Prøv True (Konstruktiv forgrening)
        assignment[var] = True
        if self._dpll(assignment):
            return True

        # Prøv False (Destruktiv forgrening)
        assignment[var] = False
        if self._dpll(assignment):
            return True

        # Backtrack
        del assignment[var]
        return False

    def _evaluate_clauses(self, assignment):
        all_satisfied = True
        for clause in self.clauses:
            clause_satisfied = False
            unassigned_literals = 0
            for lit in clause:
                var = abs(lit)
                sign = lit > 0
                if var in assignment:
                    if assignment[var] == sign:
                        clause_satisfied = True
                        break
                else:
                    unassigned_literals += 1
            
            if not clause_satisfied:
                if unassigned_literals == 0:
                    return False  # Konflikt: Ingen mulighet til å tilfredsstille denne klausulen
                all_satisfied = False
        
        return True if all_satisfied else None

    def _select_unassigned(self, assignment):
        for var in range(1, self.num_vars + 1):
            if var not in assignment:
                return var
        return None

def lift_path_to_3sat(path_len):
    # Genererer en 3SAT-instans som representerer en gyldig bane
    # Variabler: q_1, q_2, ..., q_n
    t_start = time.perf_counter()
    
    # Eksempel på en bane-labyrint (overgangsbegrensninger)
    # Klausulene tvinger frem en gyldig sekvens
    clauses = [
        [1, 2, -3],
        [-1, 3, 4],
        [-2, -3, -4],
        [1, -4, 5],
        [-1, -2, 5]
    ]
    num_vars = 5
    t_end = time.perf_counter()
    return num_vars, clauses, (t_end - t_start)

def render_3sat_matrix(n, m, path_len, t_const, t_verify, backtracks, prune_ratio, success, witness):
    status_str = "OPEN / VALID_PATH" if success else "KILL / NO_SATISFYING_PATH"
    v_color = CYAN if success else RED
    
    print(f"{SLATE}┌──[ KY-CHEM OS v0.1 // 3SAT PATH LIFT ]──────────────────────────────────────┐{RESET}")
    print(f"{SLATE}│{RESET} [LIFT_ENGINE: DPLL] [DIMENSION: 3-CNF] [STATUS: {v_color}{status_str:<26}{RESET}] {SLATE}│{RESET}")
    print(f"{SLATE}├─────────────────────────────────────────────────────────────────────────────┤{RESET}")
    print(f"{SLATE}│{RESET} PARAMETERE:                                                                 {SLATE}│{RESET}")
    print(f"{SLATE}│{RESET}   Variabler (n)   : {n:<10}  Klausuler (m) : {m:<10}  Bane (|γ|) : {path_len:<8} {SLATE}│{RESET}")
    print(f"{SLATE}├─────────────────────────────────────────────────────────────────────────────┤{RESET}")
    print(f"{SLATE}│{RESET} YTELSESMETRIKKER:                                                           {SLATE}│{RESET}")
    print(f"{SLATE}│{RESET}   T_construct     : {t_const*1000:.6f} ms                                        {SLATE}│{RESET}")
    print(f"{SLATE}│{RESET}   T_verify        : {t_verify*1000:.6f} ms                                        {SLATE}│{RESET}")
    print(f"{SLATE}│{RESET}   Backtracks      : {backtracks:<10}  Prune-Ratio   : {prune_ratio:.4f}                     {SLATE}│{RESET}")
    print(f"{SLATE}├─────────────────────────────────────────────────────────────────────────────┤{RESET}")
    if success:
        witness_str = ", ".join([f"q_{k}={v}" for k, v in sorted(witness.items())])
        print(f"{SLATE}│{RESET} VITNE (w):                                                                  {SLATE}│{RESET}")
        print(f"{SLATE}│{RESET}   {CYAN}{witness_str:<72}{RESET} {SLATE}│{RESET}")
    print(f"{SLATE}└─────────────────────────────────────────────────────────────────────────────┘{RESET}")

if __name__ == "__main__":
    path_length = 6  # Modellerer en bane n=6
    
    # 1. Konstruksjon
    n, clauses, t_construct = lift_path_to_3sat(path_length)
    
    # 2. Verifisering (DPLL-søk)
    solver = DPLLSolver(n, clauses)
    success, witness, t_verify = solver.solve()
    
    # Beregn pruning ratio: 1 - (utforskede noder / totalt søkerom 2^n)
    total_search_space = 2 ** n
    prune_ratio = 1.0 - (solver.nodes_explored / total_search_space)
    
    # 3. Presentasjon
    render_3sat_matrix(n, len(clauses), path_length, t_construct, t_verify, solver.backtracks, prune_ratio, success, witness)
