from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
OIF_PYTHON = ROOT / ".venv-oif" / "bin" / "python"

REQUIRED = (
    ROOT / "oif2a_implicit_contract_inventory.json",
    ROOT / "oif2a_contract_reconciliation_report.md",
    ROOT / "oif2a_implicit_contract_consolidation_final_lock_report.json",
    ROOT / "oif2a_implicit_contract_consolidation_non_regression_test.py",
)

for path in REQUIRED:
    assert path.is_file(), path

assert OIF_PYTHON.is_file(), OIF_PYTHON

probe = subprocess.run(
    [str(OIF_PYTHON), "-c", "from nicegui import ui; print('NICEGUI_IMPORT_OK')"],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    timeout=60,
)
assert probe.returncode == 0, probe.stdout
assert "NICEGUI_IMPORT_OK" in probe.stdout

run = subprocess.run(
    [sys.executable, str(ROOT / "oif2a_implicit_contract_consolidation_non_regression_test.py")],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    timeout=900,
)
assert run.returncode == 0, run.stdout
assert "OIF2A_NON_REGRESSION_OK" in run.stdout

inventory = json.loads(
    (ROOT / "oif2a_implicit_contract_inventory.json").read_text(encoding="utf-8")
)
assert inventory["dsl_readiness"]["oif2b_started"] is False
assert inventory["status"] == "OIF2A_IMPLICIT_CONTRACT_CONSOLIDATION_READY"

lock = json.loads(
    (ROOT / "oif2a_implicit_contract_consolidation_final_lock_report.json").read_text(
        encoding="utf-8"
    )
)
assert lock["status"] == "OIF2A_FINAL_LOCK_OK"
assert lock["oif2b_authorized"] is False

with tempfile.TemporaryDirectory() as tmp:
    fake_root = Path(tmp) / "open-cognitive-ecology"
    fake_root.mkdir(parents=True)

    source = ROOT / "oif2a_implicit_contract_consolidation_non_regression_test.py"
    target = fake_root / source.name
    shutil.copy2(source, target)

    text = target.read_text(encoding="utf-8")
    text = text.replace(
        'ROOT = Path.home() / "open-cognitive-ecology"',
        'ROOT = Path(%r)' % str(fake_root),
    )
    target.write_text(text, encoding="utf-8")

    for suite_name in (
        "oif2_3_fast_acceptance_suite.py",
        "oif2_3c_fast_acceptance_suite.py",
        "oif2_3d_fast_acceptance_suite.py",
        "oif2_3e_fast_acceptance_suite.py",
        "oif2_3f_fast_acceptance_suite.py",
    ):
        (fake_root / suite_name).write_text(
            "print('PLACEHOLDER_OK')\n",
            encoding="utf-8",
        )

    degraded = subprocess.run(
        [sys.executable, str(target)],
        cwd=str(fake_root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60,
    )
    assert degraded.returncode != 0
    assert "NiceGUI interpreter missing" in degraded.stdout

print("OIF2A_ADVERSARIAL_CROWN_OK")
