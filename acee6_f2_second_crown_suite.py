import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESTS = [
    "acee6_f2_strict_schema_test.py",
    "acee6_f2_mtime_only_freshness_test.py",
    "acee6_f2_non_benign_warning_test.py",
    "acee6_f2_benign_warning_test.py",
    "acee6_f2_source_report_replay_tamper_test.py",
    "acee6_f2_source_report_symlink_test.py",
]
for name in TESTS:
    result = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), timeout=300)
    assert result.returncode == 0, name
print("ACEE6_F2_SECOND_CROWN_OK")
