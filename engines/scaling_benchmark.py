#!/usr/bin/env python3
import time
import random
import sys

# Terminalestetikk
RED = "\x1b[38;5;202m"
CYAN = "\x1b[38;5;49m"
SLATE = "\x1b[38;5;244m"
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
        status = self._evaluate_clauses(assignment)
        if status is True:
            return True
        if status is False:
            self.backtracks += 1
            return False

        var = self._select_unassigned(assignment)
        if var is None:
            return True

        # Prøv True
        assignment[var] = True
        if self._dpll(assignment):
            return True

        # Prøv False
        assignment[var] = False
        if self._dpll(assignment):
            return True

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
                    return False
                all_satisfied = False
        
        return True if all_satisfied else None

    def _select_unassigned(self, assignment):
        for var in range(1, self.num_vars + 1):
            if var not in assignment:
                return var
        return None

def generate_random_3sat(n, alpha, seed=42):
    random.seed(seed)
    m = int(n * alpha)
    clauses = []
    
    while len(clauses) < m:
        # Velg 3 unike variabler fra 1 til n
        vars_chosen = random.sample(range(1, n + 1), 3)
        # Gi hver av dem tilfeldig polaritet (negasjon eller ikke)
        clause = [v if random.choice([True, False]) else -v for v in vars_chosen]
        if clause not in clauses:
            clauses.append(clause)
            
    return clauses

def run_benchmark():
    # Etablerte testfamilier fra din lagrede spesifikasjon
    test_cases = [
        (10, 6.00),
        (12, 6.00),
        (14, 5.00),
        (14, 6.00),
        (16, 4.26),
        (16, 5.00),
        (16, 6.00)
    ]
    
    print(f"{SLATE}┌─────────────────────────────────────────────────────────────────────────────┐{RESET}")
    print(f"{SLATE}│{RESET}  KY-CHEM OS // SCALING BENCHMARK RUNNER                                     {SLATE}│{RESET}")
    print(f"{SLATE}├─────────────────────────────────────────────────────────────────────────────┤{RESET}")
    print(f"{SLATE}│{RESET}  {SLATE}{'n':<4} {'α':<6} {'m':<5} {'RESULTAT':<12} {'T_verify (ms)':<16} {'BACKTRACKS':<12} {'PRUNE-RATIO':<12}{RESET} {SLATE}│{RESET}")
    print(f"{SLATE}├─────────────────────────────────────────────────────────────────────────────┤{RESET}")
    
    for n, alpha in test_cases:
        clauses = generate_random_3sat(n, alpha)
        solver = DPLLSolver(n, clauses)
        success, _, duration = solver.solve()
        
        total_space = 2 ** n
        prune_ratio = 1.0 - (solver.nodes_explored / total_space)
        
        res_str = f"{CYAN}SAT{RESET}" if success else f"{RED}UNSAT{RESET}"
        dur_ms = duration * 1000
        
        print(f"{SLATE}│{RESET}  {n:<4} {alpha:<6.2f} {len(clauses):<5} {res_str:<21} {dur_ms:<15.4f} {solver.backtracks:<12} {prune_ratio:<12.4%}{RESET} {SLATE}│{RESET}")
        
    print(f"{SLATE}└─────────────────────────────────────────────────────────────────────────────┘{RESET}")

if __name__ == "__main__":
    run_benchmark()
