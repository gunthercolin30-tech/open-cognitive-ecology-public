from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
PYTHON = ROOT / ".venv-oif/bin/python"
SUITE = ROOT / "oif2_3c_fast_acceptance_suite.py"
REPORT = ROOT / "oif2_3c_runtime_health_adapter_final_lock_report.json"

FILES = (
    ROOT / "oif/adapters/runtime_health_adapter.py",
    ROOT / "oif/application/default_providers.py",
    ROOT / "oif2_3_validation_report_adapter_real_source_test.py",
    ROOT / "oif2_3c_runtime_health_adapter_functional_test.py",
    ROOT / "oif2_3c_runtime_health_adapter_degradation_test.py",
    ROOT / "oif2_3c_runtime_health_adapter_real_source_test.py",
    ROOT / "oif2_3c_runtime_health_adapter_external_storage_test.py",
    ROOT / "oif2_3c_runtime_health_adapter_long_duration_status_test.py",
    ROOT / "oif2_3c_runtime_health_adapter_non_regression_test.py",
    ROOT / "oif2_3c_fast_acceptance_suite.py",
)

completed = subprocess.run(
    [str(PYTHON), str(SUITE)],
    cwd=ROOT,
    text=True,
    capture_output=True,
    timeout=1800,
    check=False,
)
assert completed.returncode == 0, completed.stdout + completed.stderr

hashes = {
    str(path.relative_to(ROOT)): hashlib.sha256(
        path.read_bytes()
    ).hexdigest()
    for path in FILES
}

report = {
    "milestone": "OIF2-3C",
    "primitive": "oif2_runtime_health_adapter",
    "status": "locked",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "adapter_schema_version": "oif2.runtime-health-adapter.v1",
    "provider_name": "runtime-health",
    "zone": "runtime",
    "read_only": True,
    "translation_only": True,
    "producer_execution": False,
    "synthetic_cross_source_score": False,
    "separate_source_sections": [
        "runtime_service",
        "long_duration_runtime",
        "hardware_health",
    ],
    "controlled_degradation_validated": True,
    "external_storage_path_policy_validated": True,
    "direct_source_symlink_rejection_validated": True,
    "long_duration_status_contract_validated": True,
    "real_source_validated": True,
    "renderer_direct_read_absent": True,
    "renderer_direct_write_absent": True,
    "source_immutability_validated": True,
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
print("OIF2_3C_RUNTIME_HEALTH_ADAPTER_FINAL_LOCK_OK")
