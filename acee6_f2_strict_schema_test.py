import json
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_f2_test_support import payload, seed
from ontology.acee_installation_executor import AceeInstallationExecutor

CASES = [
    ("error_count", None),
    ("failed_calls", None),
    ("timeouts", None),
    ("error_count", "0"),
    ("failed_calls", False),
    ("timeouts", 0.0),
]

for field, value in CASES:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        request = payload(root, True)
        main = root / "validation" / "main.py"
        report = {
            "validation_mode": "full_isolated",
            "diagnostics": {
                "error_count": 0,
                "failed_calls": 0,
                "timeouts": 0,
                "failed_modules": [],
            },
            "summary": {"overall_success": True},
        }
        if value is None:
            report["diagnostics"].pop(field)
        else:
            report["diagnostics"][field] = value
        main.write_text(
            "import json\nfrom pathlib import Path\n"
            f"REPORT={report!r}\n"
            "Path('scientific_validation_report.json').write_text("
            "json.dumps(REPORT, sort_keys=True), encoding='utf-8')\n",
            encoding="utf-8",
        )
        result = AceeInstallationExecutor(
            root=root,
            now_utc=fixed_now(),
        ).step(inputs=request, persist=True)
        assert result["transaction_state"] == "ROLLED_BACK", (field, value, result)

print("ACEE6_F2_STRICT_SCHEMA_OK")
