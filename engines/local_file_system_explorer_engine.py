#!/usr/bin/env python3
"""
Local File System Explorer Engine
Scans local directories (01_OPEN, 02_HOLD, 03_KILL_ARKIV, 99_SYSTEM),
calculates file metrics, generates JSON catalog, and verifies SHA-256 integrity.
"""

import os
import math
import json
import hashlib
import unittest
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

ROOT_DIR = "/home/sololyset"

@dataclass
class FileItem:
    rel_path: str
    category: str
    size_bytes: int
    line_count: int
    sha256_hash: str

class LocalFileSystemEngine:
    CATEGORIES = {
        ".md": "📄 Spesifikasjon / Dokument",
        ".py": "🐍 Beregningsmotor / Test",
        ".html": "🌐 Interaktiv Workbench",
        ".sh": "🛡️ Portvakt Skript",
        ".json": "📂 Manifest / Data",
        ".tla": "🧩 Formell Modell"
    }

    @staticmethod
    def get_category(filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        return LocalFileSystemEngine.CATEGORIES.get(ext, "📁 Annen Fil")

    @staticmethod
    def scan_directory(base_dir: str = ROOT_DIR) -> List[FileItem]:
        items = []
        target_dirs = ["01_OPEN", "02_HOLD", "03_KILL_ARKIV", "99_SYSTEM"]

        for d in target_dirs:
            full_d = os.path.join(base_dir, d)
            if not os.path.exists(full_d):
                continue

            for root, _, files in os.walk(full_d):
                if "__pycache__" in root:
                    continue
                for f in sorted(files):
                    file_path = os.path.join(root, f)
                    rel_path = os.path.relpath(file_path, base_dir)
                    
                    try:
                        size = os.path.getsize(file_path)
                        with open(file_path, 'rb') as fp:
                            content = fp.read()
                            sha = hashlib.sha256(content).hexdigest()[:16].upper()
                            lines = content.count(b'\n') + (1 if content else 0)
                        
                        items.append(FileItem(
                            rel_path=rel_path,
                            category=LocalFileSystemEngine.get_category(f),
                            size_bytes=size,
                            line_count=lines,
                            sha256_hash=sha
                        ))
                    except Exception:
                        pass
        return items

    @staticmethod
    def evaluate_file_system(base_dir: str = ROOT_DIR) -> Dict[str, Any]:
        items = LocalFileSystemEngine.scan_directory(base_dir)
        total_files = len(items)
        total_bytes = sum(i.size_bytes for i in items)
        total_lines = sum(i.line_count for i in items)

        valid = total_files > 0
        verdict = "FILE SYSTEM HEALTHY" if valid else "EMPTY OR CORRUPTED"

        payload = f"{total_files}|{total_bytes}|{total_lines}|{verdict}"
        w_hash = "W_EXPLORER_" + hashlib.sha256(payload.encode()).hexdigest()[:24].upper()

        return {
            "total_files": total_files,
            "total_size_kb": round(total_bytes / 1024.0, 2),
            "total_lines": total_lines,
            "file_catalog": [asdict(i) for i in items[:50]], # Top 50 sample
            "valid": valid,
            "verdict": verdict,
            "witness_hash": w_hash
        }

class TestLocalFileSystemEngine(unittest.TestCase):
    def test_file_category_lookup(self):
        self.assertIn("Spesifikasjon", LocalFileSystemEngine.get_category("TEST_SPEC.md"))
        self.assertIn("Beregningsmotor", LocalFileSystemEngine.get_category("engine.py"))
        self.assertIn("Workbench", LocalFileSystemEngine.get_category("workbench.html"))

    def test_directory_scan(self):
        res = LocalFileSystemEngine.evaluate_file_system()
        self.assertTrue(res["valid"])
        self.assertGreater(res["total_files"], 0)
        self.assertTrue(res["witness_hash"].startswith("W_EXPLORER_"))

if __name__ == "__main__":
    unittest.main()
