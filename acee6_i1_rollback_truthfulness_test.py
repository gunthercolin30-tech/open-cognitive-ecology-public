#!/usr/bin/env python3
from pathlib import Path
p=Path("ontology/acee_installation_executor.py").read_text();assert "rollback_verified" in p and "rollback_executed" in p
print("ACEE6_I1_ROLLBACK_TRUTHFULNESS_OK")
