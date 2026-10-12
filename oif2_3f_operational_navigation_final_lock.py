from __future__ import annotations
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "oif2_3f_operational_navigation_final_lock_report.json"
FILES = (
    "oif/ui/navigation_model.py",
    "oif/ui/navigation_preferences.py",
    "oif/ui/operational_shell.py",
    "oif2_3f_navigation_model_functional_test.py",
    "oif2_3f_navigation_model_degradation_test.py",
    "oif2_3f_navigation_preferences_test.py",
    "oif2_3f_renderer_boundary_test.py",
    "oif2_3f_navigation_non_regression_test.py",
    "oif2_3f_nicegui_import_smoke_test.py",
    "oif2_3f_fast_acceptance_suite.py",
)
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    result = subprocess.run([sys.executable, str(ROOT / "oif2_3f_fast_acceptance_suite.py")], cwd=ROOT, check=False)
    if result.returncode: return result.returncode
    for rel in FILES: ast.parse((ROOT / rel).read_text(encoding="utf-8"), filename=rel)
    report = {
        "primitive": "oif2_operational_navigation_layer",
        "status": "locked",
        "read_only_renderer": True,
        "blueprint_zones_only": True,
        "provider_payload_search_absent": True,
        "direct_adapter_import_absent": True,
        "direct_business_persistence_absent": True,
        "renderer_state_local_only": True,
        "controlled_degradation_validated": True,
        "consciousness_proven": False,
        "subjectivity_proven": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "sha256": {rel: digest(ROOT / rel) for rel in FILES},
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("OIF2_3F_OPERATIONAL_NAVIGATION_FINAL_LOCK_OK")
    return 0
if __name__ == "__main__": raise SystemExit(main())
