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
    external = root / "external_report.json"
    external.write_text("{}", encoding="utf-8")
    source = root / "scientific_validation_report.json"
    os.symlink(external, source)
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=request,
        persist=True,
    )
    assert result["transaction_state"] == "ROLLED_BACK", result
    report = json.loads(Path(result["global_validation_report_path"]).read_text())
    assert report["source_report_path_safe"] is False

print("ACEE6_F2_SOURCE_REPORT_SYMLINK_OK")
