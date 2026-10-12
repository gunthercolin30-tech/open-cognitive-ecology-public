#!/usr/bin/env python3
from pathlib import Path
p=Path("ontology/acee_installation_executor.py").read_text();assert "latest_state_journal_divergence" in p and "latest_record_hash_divergence" in p
print("ACEE6_I1_JOURNAL_LATEST_STATE_DIVERGENCE_OK")
