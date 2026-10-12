from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
PYTHON = ROOT / ".venv-oif/bin/python"
SUITE = ROOT / "oif2_3_fast_acceptance_suite.py"
REPORT = ROOT / "oif2_3_validation_report_adapter_final_lock_report.json"

FILES = (
    ROOT / "oif/adapters/validation_report_adapter.py",
    ROOT / "oif/application/default_providers.py",
    ROOT / "oif/ui/operational_shell.py",
    ROOT / "oif2_3_validation_report_adapter_functional_test.py",
    ROOT / "oif2_3_validation_report_adapter_degradation_test.py",
    ROOT / "oif2_3_validation_report_adapter_real_source_test.py",
    ROOT / "oif2_3_validation_report_adapter_non_regression_test.py",
    SUITE,
    ROOT / "oif2_3_validation_report_adapter_consistency_test.py",
    ROOT / "oif2_3_validation_report_adapter_atomic_replacement_test.py",
)

completed = subprocess.run(
    [str(PYTHON), str(SUITE)],
    cwd=ROOT,
    text=True,
    capture_output=True,
    timeout=1200,
    check=False,
)
assert completed.returncode == 0, completed.stdout + completed.stderr

hashes = {
    str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in FILES
}
report = {
    "milestone": "OIF2-3B",
    "primitive": "oif2_validation_report_adapter",
    "status": "locked",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "real_source_connected": True,
    "provider_count": 1,
    "zone": "science",
    "read_only": True,
    "path_containment_validated": True,
    "size_limit_validated": True,
    "schema_validation_validated": True,
        "strict_json_constants_validated": True,
        "metrological_consistency_validated": True,
        "duplicate_test_names_rejected": True,
        "atomic_replacement_read_validated": True,
    "controlled_degradation_validated": True,
    "renderer_direct_read_absent": True,
    "renderer_direct_write_absent": True,
    "legacy_review_interface_preserved": True,
    "hashes": hashes,
    "functional_conclusion_only": True,
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "phenomenology_undetermined": True,
}
REPORT.write_text(
    json.dumps(report, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(completed.stdout, end="")
print("OIF2_3_VALIDATION_REPORT_ADAPTER_FINAL_LOCK_OK")
