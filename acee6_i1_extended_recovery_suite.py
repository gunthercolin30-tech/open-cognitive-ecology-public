#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
TESTS=['acee6_i1_state_matrix_test.py', 'acee6_i1_audit_immutability_test.py', 'acee6_i1_restart_idempotence_test.py', 'acee6_i1_rollback_truthfulness_test.py', 'acee6_i1_journal_latest_state_divergence_test.py', 'acee6_i1_truncated_journal_test.py', 'acee6_i1_concurrent_recovery_test.py', 'acee6_i1_scan_isolation_test.py', 'acee6_i1_quarantine_failure_test.py', 'acee6_i1_public_contract_test.py']
for n in TESTS:subprocess.run([sys.executable,n],check=True)
print("ACEE6_I1_EXTENDED_RECOVERY_SUITE_OK")
