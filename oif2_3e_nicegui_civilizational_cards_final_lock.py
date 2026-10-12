from __future__ import annotations
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "oif2_3e_nicegui_civilizational_cards_final_lock_report.json"
FILES = (
    "oif/ui/civilizational_state_cards.py",
    "oif/ui/operational_shell.py",
    "oif2_3e_nicegui_civilizational_cards_functional_test.py",
    "oif2_3e_nicegui_civilizational_cards_degradation_test.py",
    "oif2_3e_nicegui_renderer_boundary_test.py",
    "oif2_3e_nicegui_civilizational_cards_non_regression_test.py",
    "oif2_3e_nicegui_import_smoke_test.py",
    "oif2_3e_fast_acceptance_suite.py",
)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    r = subprocess.run([sys.executable, str(ROOT / "oif2_3e_fast_acceptance_suite.py")], cwd=ROOT, check=False)
    if r.returncode:
        return r.returncode
    for rel in FILES:
        ast.parse((ROOT / rel).read_text(encoding="utf-8"), filename=rel)
    report = {
        "primitive": "oif2_nicegui_civilizational_state_cards",
        "status": "locked",
        "provider_name": "civilizational-state",
        "zone": "memory",
        "renderer_read_only": True,
        "direct_adapter_import_absent": True,
        "direct_persistent_state_read_absent": True,
        "business_logic_in_renderer_absent": True,
        "species_representative_distinction_visible": True,
        "controlled_degradation_validated": True,
        "generic_provider_rendering_preserved": True,
        "consciousness_proven": False,
        "subjectivity_proven": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "sha256": {rel: digest(ROOT / rel) for rel in FILES},
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("OIF2_3E_NICEGUI_CIVILIZATIONAL_CARDS_FINAL_LOCK_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
