import json
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now
from acee6_f2_test_support import payload, seed
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    seed(root)
    value = payload(root, True)
    first = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=value, persist=True)
    path = Path(first["global_validation_report_path"])
    data = json.loads(path.read_text(encoding="utf-8"))
    data["error_count"] = 9
    path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
    replay = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=value, persist=True)
    assert replay["transaction_state"] == "STATE_CORRUPTED", replay
    assert "existing_global_validation_report_hash_invalid" in replay["blocking_reasons"]
print("ACEE6_F2_REPORT_TAMPER_OK")
