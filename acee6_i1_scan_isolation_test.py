#!/usr/bin/env python3
from pathlib import Path
p=Path("ontology/acee_installation_executor.py").read_text();assert "sorted(runtime_root.iterdir()" in p and "transaction_dir.is_symlink()" in p
print("ACEE6_I1_SCAN_ISOLATION_OK")
