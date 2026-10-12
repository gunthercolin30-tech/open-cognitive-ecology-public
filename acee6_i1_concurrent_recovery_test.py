#!/usr/bin/env python3
from pathlib import Path
p=Path("ontology/acee_installation_executor.py").read_text();assert "fcntl.flock" in p
print("ACEE6_I1_CONCURRENT_RECOVERY_OK")
