from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha

with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"ontology").mkdir()
    now=fixed_now()
    decision=valid_acee5_decision(root)
    stale=deepcopy(decision)
    stale["timestamp_utc"]=(now-timedelta(days=2)).isoformat().replace("+00:00","Z")
    stale["result_hash"]=_sha({k:v for k,v in stale.items() if k!="result_hash"})
    result=AceeInstallationExecutor(root=root,now_utc=now).step(stale)
    assert "manifest_stale" in result["blocking_reasons"]

    decision=valid_acee5_decision(root)
    manifest_hash=decision["installation_manifest"]["manifest_hash"]
    wrapped={"acee5_decision":decision,"admission_context":{"consumed_manifest_hashes":[manifest_hash]}}
    result=AceeInstallationExecutor(root=root,now_utc=now).step(wrapped)
    assert "manifest_replay_detected" in result["blocking_reasons"]
print("ACEE6_B1_FRESHNESS_REPLAY_OK")
