from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
PYTHON = ROOT / ".venv-oif/bin/python"
SUITE = ROOT / "oif2_3d_fast_acceptance_suite.py"
REPORT = ROOT / "oif2_3d_civilizational_state_adapter_final_lock_report.json"
FILES = (
    ROOT / "oif/adapters/civilizational_state_adapter.py",
    ROOT / "oif/application/default_providers.py",
    ROOT / "oif2_3d_civilizational_state_adapter_functional_test.py",
    ROOT / "oif2_3d_civilizational_state_adapter_degradation_test.py",
    ROOT / "oif2_3d_civilizational_state_adapter_real_source_test.py",
    ROOT / "oif2_3d_civilizational_state_adapter_external_storage_test.py",
    ROOT / "oif2_3d_civilizational_state_adapter_non_regression_test.py",
    ROOT / "oif2_3d_fast_acceptance_suite.py",
)
completed = subprocess.run(
    [str(PYTHON), str(SUITE)], cwd=ROOT, text=True,
    capture_output=True, timeout=1800, check=False,
)
assert completed.returncode == 0, completed.stdout + completed.stderr
hashes = {
    str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in FILES
}
report = {
    "milestone": "OIF2-3D",
    "primitive": "oif2_civilizational_state_adapter",
    "status": "locked",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "adapter_schema_version": "oif2.civilizational-state-adapter.v1",
    "provider_name": "civilizational-state",
    "zone": "memory",
    "read_only": True,
    "translation_only": True,
    "producer_execution": False,
    "synthetic_cross_source_score": False,
    "separate_source_sections": [
        "civilizational_identity", "representative_state",
        "continuity_state", "succession_state",
    ],
    "controlled_degradation_validated": True,
    "external_storage_path_policy_validated": True,
    "direct_source_symlink_rejection_validated": True,
    "real_source_validated": True,
    "species_representative_distinction_validated": True,
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
REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(completed.stdout, end="")
print("OIF2_3D_CIVILIZATIONAL_STATE_ADAPTER_FINAL_LOCK_OK")
