import subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parent
tests = [
    "acee6_d3_restart_replay_test.py",
    "acee6_d3_compilation_report_tamper_test.py",
    "acee6_d3_latest_state_tamper_test.py",
    "acee6_d3_bytecode_tamper_test.py",
    "acee6_d3_bytecode_symlink_test.py",
    "acee6_d3_no_pycache_test.py",
    "acee6_d3_source_divergence_replay_test.py",
]
for name in tests:
    result = subprocess.run([sys.executable, str(root / name)], cwd=str(root), timeout=90)
    assert result.returncode == 0, name
print("ACEE6_D3_SECOND_CROWN_OK")
