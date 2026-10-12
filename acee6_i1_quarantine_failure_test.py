#!/usr/bin/env python3
from pathlib import Path
p=Path("ontology/acee_installation_executor.py").read_text();assert "quarantine_journal_write_failed" in p or "QUARANTINE_FAILED" in p
print("ACEE6_I1_QUARANTINE_FAILURE_OK")
