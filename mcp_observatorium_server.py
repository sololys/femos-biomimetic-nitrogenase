#!/usr/bin/env python3
"""
mcp_observatorium_server.py
===========================
Model Context Protocol (MCP) Server for Reismannpoint Observatorium (v1.0)

Eksponerer Observatoriets 43 Metamorfose-Motorer og 3-Tier Attestasjon til GitHub Copilot / Antigravity:
  - Tools:
      1. list_metamorphosis_engines()
      2. run_3tier_precision_sweep()
      3. verify_single_engine(engine_name)
      4. export_sealed_manifest()
"""

import sys
import os
import json
import hashlib
import time
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ENGINES_DIR = os.path.join(BASE_DIR, "engines")

def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id", 1)

    sys.path.insert(0, ENGINES_DIR)
    sys.path.insert(0, BASE_DIR)
    from master_all_engines_sweep import METAMORPHOSIS_ENGINES, run_independent_3tier_sweep, verify_engine_attestation

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "list_metamorphosis_engines",
                        "description": "Lister alle 43 metamorfose-motorer i Reismannpoint Observatorium.",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "run_3tier_precision_sweep",
                        "description": "Kjører uavhengig 3-tier presisjonssweep (Software, Model, Evidence) for alle 43 motorer.",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "verify_single_engine",
                        "description": "Verifiserer en spesifikk metamorfose-motor under 3-tier kontroll.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "engine_name": {"type": "string", "description": "Filnavn på motoren (f.eks. cdc_complexity_axiom_metamorphosis_engine.py)"}
                            },
                            "required": ["engine_name"]
                        }
                    },
                    {
                        "name": "export_sealed_manifest",
                        "description": "Eksporterer en uforanderlig, SHA-256 forseglet 3-tier attestasjonsrapport.",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        args = params.get("arguments", {})

        if tool_name == "list_metamorphosis_engines":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(METAMORPHOSIS_ENGINES, indent=2)}]
                }
            }

        elif tool_name == "run_3tier_precision_sweep":
            sweep_data = run_independent_3tier_sweep()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(sweep_data, indent=2, ensure_ascii=False)}]
                }
            }

        elif tool_name == "verify_single_engine":
            engine_name = args.get("engine_name", "cdc_complexity_axiom_metamorphosis_engine.py")
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{ENGINES_DIR}:{BASE_DIR}:{env.get('PYTHONPATH', '')}"
            att = verify_engine_attestation(1, engine_name, BASE_DIR, ENGINES_DIR, env)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(att, indent=2, ensure_ascii=False)}]
                }
            }

        elif tool_name == "export_sealed_manifest":
            sweep_data = run_independent_3tier_sweep()
            ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            raw_payload = json.dumps(sweep_data["results"], sort_keys=True)
            manifest_sha256 = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

            sealed_report = {
                "observatorium_version": "v3.0",
                "genesis_timestamp_iso": ts,
                "master_manifest_sha256": manifest_sha256,
                "all_passed": sweep_data["all_passed"],
                "total_engines": sweep_data["total_engines"],
                "results": sweep_data["results"]
            }
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(sealed_report, indent=2, ensure_ascii=False)}]
                }
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Ukjent metode eller verktøy: {method}"}
    }

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("=== MCP SERVER DEMO MODE ===")
        # Test tools/list
        req_list = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        res_list = handle_mcp_request(req_list)
        print(f"1. Registered Tools: {len(res_list['result']['tools'])} verktøy funnet.")

        # Test single engine verify call
        req_call = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "verify_single_engine", "arguments": {"engine_name": "cdc_complexity_axiom_metamorphosis_engine.py"}}
        }
        res_call = handle_mcp_request(req_call)
        print("2. Call 'verify_single_engine' Result:")
        print(res_call["result"]["content"][0]["text"][:300] + "...\n")
        return

    # Standard MCP Stdio Loop
    print("MCP Server Online (STDIO). Enter JSON-RPC request:")
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            resp = handle_mcp_request(req)
            print(json.dumps(resp))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": f"Parse error: {e}"}}))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
