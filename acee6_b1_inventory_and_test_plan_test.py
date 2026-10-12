from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha
def bind(d):
 m=d["installation_manifest"]; m["manifest_hash"]=_sha({k:v for k,v in m.items() if k!="manifest_hash"}); d["result_hash"]=_sha({k:v for k,v in d.items() if k!="result_hash"})
with TemporaryDirectory() as t:
 r=Path(t); (r/"ontology").mkdir(); e=AceeInstallationExecutor(root=r,now_utc=fixed_now()); b=valid_acee5_decision(r)
 d=deepcopy(b); d["installation_manifest"]["test_paths"]*=2; bind(d); assert "test_paths_duplicate" in e.step(d)["blocking_reasons"]
 d=deepcopy(b); d["installation_manifest"]["inventory_targets"]*=2; bind(d); assert "inventory_targets_duplicate" in e.step(d)["blocking_reasons"]
 d=deepcopy(b); d["installation_manifest"]["test_paths"]=["../x.py"]; bind(d); assert "test_path_invalid" in e.step(d)["blocking_reasons"]
print("ACEE6_B1_INVENTORY_TEST_PLAN_OK")
