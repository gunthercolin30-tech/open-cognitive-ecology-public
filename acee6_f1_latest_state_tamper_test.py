import json
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_f1_test_support import payload, seed
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    seed(root)
    value = payload(root)
    first = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=value, persist=True)
    state_path = root / "acee6_transactions" / first["transaction_id"] / "latest_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["local_validation_passed"] = False
    state_path.write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
    replay = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=value, persist=True)
    assert replay["transaction_state"] == "STATE_CORRUPTED", replay
    assert "existing_local_validation_latest_state_hash_invalid" in replay["blocking_reasons"]
print("ACEE6_F1_LATEST_STATE_TAMPER_OK")
