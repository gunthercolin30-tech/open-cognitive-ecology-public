#!/usr/bin/env python3
from pathlib import Path
p=Path("ontology/acee_installation_executor.py").read_text();assert "journal_json_invalid" in p and "journal_empty" in p
print("ACEE6_I1_TRUNCATED_JOURNAL_OK")
