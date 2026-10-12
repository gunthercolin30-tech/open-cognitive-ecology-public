import json
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_f2_test_support import payload, seed
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    seed(root)
    request = payload(root, True)
    first = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=request,
        persist=True,
    )
    source = root / "scientific_validation_report.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    data["summary"]["overall_success"] = False
    source.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
    replay = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=request,
        persist=True,
    )
    assert replay["transaction_state"] == "STATE_CORRUPTED", replay
    assert "existing_global_validation_source_report_divergence" in replay["blocking_reasons"]

print("ACEE6_F2_SOURCE_REPORT_REPLAY_TAMPER_OK")
