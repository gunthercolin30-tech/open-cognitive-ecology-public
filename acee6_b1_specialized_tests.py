from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha

with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"ontology").mkdir()
    executor=AceeInstallationExecutor(root=root,now_utc=fixed_now())
    decision=valid_acee5_decision(root)
    for field in ("proposal_id","module_name","candidate_content_sha256","validation_report_sha256"):
        mutated=deepcopy(decision)
        mutated["installation_manifest"].pop(field,None)
        manifest=mutated["installation_manifest"]
        manifest["manifest_hash"]=_sha({k:v for k,v in manifest.items() if k!="manifest_hash"})
        mutated["result_hash"]=_sha({k:v for k,v in mutated.items() if k!="result_hash"})
        result=executor.step(mutated)
        assert result["admissible"] is False
        assert "manifest_field_missing:"+field in result["blocking_reasons"]
print("ACEE6_B1_SPECIALIZED_OK")
