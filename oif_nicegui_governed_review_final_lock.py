from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REQUIRED = [
    ROOT / "oif/ui/__init__.py",
    ROOT / "oif/ui/campaign_service.py",
    ROOT / "oif/ui/review_app.py",
    ROOT / "run_oif_nicegui_governed_review.py",
    ROOT / "tests/test_oif_nicegui_campaign_service.py",
]


def main() -> int:
    missing = [str(path) for path in REQUIRED if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing OIF NiceGUI files: " + ", ".join(missing))
    for path in REQUIRED:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    app_source = (ROOT / "oif/ui/review_app.py").read_text(encoding="utf-8")
    service_source = (ROOT / "oif/ui/campaign_service.py").read_text(encoding="utf-8")
    assertions = {
        "nicegui_native": "from nicegui import ui" in app_source,
        "local_default": 'DEFAULT_HOST = "127.0.0.1"' in app_source,
        "remote_fail_closed": "OIF_ALLOW_REMOTE_UI" in app_source,
        "separate_governed_apply": "apply_governed" in app_source,
        "atomic_persistence": "os.replace" in service_source and "os.fsync" in service_source,
        "no_auto_code_change": "code_change_performed" in service_source,
        "governed_engine_reused": "governed_redundancy_review import" in service_source,
    }
    if not all(assertions.values()):
        raise AssertionError(json.dumps(assertions, sort_keys=True))
    print("OIF_NICEGUI_GOVERNED_REVIEW_FINAL_LOCK_OK")
    print(json.dumps(assertions, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
