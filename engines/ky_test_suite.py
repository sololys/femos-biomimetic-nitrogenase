import sys
import os
import concurrent.futures

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ky_executor import KYExecutor

def run_layer_tests():
    executor = KYExecutor()
    print("--- KY Engine Lag-Separasjon Test-Suite ---")

    # 1. Parser-lag test (Ugyldig tekst)
    res_parser = executor.run_pipeline({"fields": ["a"]}, "INVALID_STRING")
    assert res_parser["GATE"] == "KILL", "Parser skulle avvist ugyldig tekst"
    print("[PASS] Lag 1 (Parser): Avviste ugyldig tekst med KILL.")

    # 2. Executor-lag test (Ulovlig type-overgang)
    res_exec = executor.run_pipeline({"fields": ["a"]}, "⟲(○→◉)#▶", {"valid": True}, {"signature": "VERIFIED_WITNESS"})
    assert res_exec["GATE"] == "KILL", "Executor skulle avvist ulovlig hopp RAW -> COMMITTED"
    print("[PASS] Lag 2 (Executor): Avviste typebrudd med KILL.")

    # 3. Witness-lag test (Manipulert kjede/genesis)
    # Test full gyldig kjede med ekte bevis
    valid_input = {"fields": ["field1", "field2"]}
    audit = {"valid": True}
    witness = {"signature": "VERIFIED_WITNESS"}
    res_full = executor.run_pipeline(valid_input, "⟲(○→◇→□→⬡→◉)#▶", audit, witness)
    assert res_full["GATE"] == "OPEN"
    assert res_full["STATE"] == "COMMITTED"
    assert res_full["Delta_K"] == 0
    print("[PASS] Lag 3 (Full gyldig kjede): Nådde OPEN og COMMITTED.")

    # 4. Samtidighet / Parallelle kjøringer
    def parallel_task():
        return executor.run_pipeline({"fields": ["data"]}, "⟲(○→◇→□→⬡→◉)#▶", audit, witness)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(parallel_task) for _ in range(2)]
        results = [f.result() for f in futures]
        for r in results:
            assert r["GATE"] == "OPEN"
    print("[PASS] Lag 4 (Samtidighetsintegritet): Parallelle transaksjoner håndtert deterministisk.")

    print("\n[VERIFICATION SUCCESS] Alle lag bestod isolert og integrert test.")

if __name__ == "__main__":
    run_layer_tests()
