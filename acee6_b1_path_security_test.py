from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha

def rebind(decision):
    manifest=decision["installation_manifest"]
    manifest["manifest_hash"]=_sha({k:v for k,v in manifest.items() if k!="manifest_hash"})
    decision["result_hash"]=_sha({k:v for k,v in decision.items() if k!="result_hash"})

with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"ontology").mkdir()
    executor=AceeInstallationExecutor(root=root,now_utc=fixed_now())
    for value in ("/tmp/outside.py", "../outside.py"):
        decision=valid_acee5_decision(root)
        decision["installation_manifest"]["target_path"]=value
        rebind(decision)
        result=executor.step(decision)
        assert result["admissible"] is False
        assert any("target_path_path_" in reason for reason in result["blocking_reasons"])
    decision=valid_acee5_decision(root)
    decision["installation_manifest"]["backup_path"]=decision["installation_manifest"]["target_path"]
    rebind(decision)
    result=executor.step(decision)
    assert "path_collision" in result["blocking_reasons"]
print("ACEE6_B1_PATH_SECURITY_OK")
