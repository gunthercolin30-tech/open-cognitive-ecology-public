import json
import sys
from pathlib import Path

from acee6_f1_test_support import payload as f1_payload, seed


def install_fake_full_validation(root: Path, success: bool = True) -> None:
    package = root / "validation"
    package.mkdir(exist_ok=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    diagnostics = {
        "error_count": 0 if success else 1,
        "failed_calls": 0 if success else 1,
        "timeouts": 0,
        "failed_modules": [] if success else ["sample"],
        "modules_discovered": 1,
    }
    report = {
        "validation_mode": "full_isolated",
        "diagnostics": diagnostics,
        "summary": {"overall_success": success},
    }
    body = (
        "import json\n"
        "from pathlib import Path\n"
        f"REPORT = {report!r}\n"
        "Path('scientific_validation_report.json').write_text(json.dumps(REPORT, sort_keys=True), encoding='utf-8')\n"
        f"raise SystemExit({0 if success else 1})\n"
    )
    (package / "main.py").write_text(body, encoding="utf-8")


def payload(root: Path, success: bool = True):
    install_fake_full_validation(root, success=success)
    value = f1_payload(root)
    context = dict(value["admission_context"])
    context["requested_stage"] = "ACEE6-F2"
    context["global_validation_timeout_seconds"] = 30
    value["admission_context"] = context
    return value
