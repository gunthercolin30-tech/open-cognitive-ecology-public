import json
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_e_test_support import seed,payload
from acee6_b1_test_support import fixed_now
from ontology.acee_installation_executor import AceeInstallationExecutor

cases = [
    ("inventory_snapshot_manifest.json", "existing_inventory_snapshot_manifest_missing"),
    ("inventory_update_manifest.json", "existing_inventory_update_manifest_missing"),
    ("inventory_validation_report.json", "existing_inventory_validation_report_missing"),
]
for filename, reason in cases:
    with TemporaryDirectory() as tmp:
        root=Path(tmp); seed(root); p=payload(root)
        first=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True)
        tx=root/"acee6_transactions"/first["transaction_id"]
        (tx/filename).unlink()
        replay=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True)
        assert replay["transaction_state"]=="STATE_CORRUPTED", replay
        assert reason in replay["blocking_reasons"], replay
with TemporaryDirectory() as tmp:
    root=Path(tmp); seed(root); p=payload(root)
    first=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True)
    tx=root/"acee6_transactions"/first["transaction_id"]
    path=tx/"inventory_snapshot_manifest.json"
    data=json.loads(path.read_text()); data["files"]=[]
    path.write_text(json.dumps(data,sort_keys=True))
    replay=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True)
    assert "existing_inventory_snapshot_manifest_hash_invalid" in replay["blocking_reasons"]
print("ACEE6_E_MANIFEST_INTEGRITY_OK")
