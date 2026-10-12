import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESTS = [
    "acee6_f1_failure_matrix_test.py",
    "acee6_f1_timeout_stop_test.py",
    "acee6_f1_blocked_command_test.py",
    "acee6_f1_restart_replay_test.py",
    "acee6_f1_latest_state_tamper_test.py",
    "acee6_f1_preexisting_candidate_rollback_test.py",
]
for name in TESTS:
    result = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), timeout=300)
    assert result.returncode == 0, name
print("ACEE6_F1_SECOND_CROWN_OK")
