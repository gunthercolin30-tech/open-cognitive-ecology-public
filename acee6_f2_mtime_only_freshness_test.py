import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_f2_test_support import payload, seed
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    seed(root)
    request = payload(root, True)
    source = root / "scientific_validation_report.json"
    canonical = {
        "validation_mode": "full_isolated",
        "diagnostics": {
            "error_count": 0,
            "failed_calls": 0,
            "timeouts": 0,
            "failed_modules": [],
        },
        "summary": {"overall_success": True},
    }
    source.write_text(json.dumps(canonical, sort_keys=True), encoding="utf-8")
    main = root / "validation" / "main.py"
    main.write_text(
        "import os\nfrom pathlib import Path\n"
        "p=Path('scientific_validation_report.json')\n"
        "os.utime(p, None)\n",
        encoding="utf-8",
    )
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=request,
        persist=True,
    )
    assert result["transaction_state"] == "ROLLED_BACK", result
    report = json.loads(Path(result["global_validation_report_path"]).read_text())
    assert report["source_report_replaced"] is False

print("ACEE6_F2_MTIME_ONLY_FRESHNESS_OK")
