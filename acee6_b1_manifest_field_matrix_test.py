from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor, REQUIRED_MANIFEST_FIELDS, _sha
with TemporaryDirectory() as t:
 r=Path(t); (r/"ontology").mkdir(); base=valid_acee5_decision(r); e=AceeInstallationExecutor(root=r,now_utc=fixed_now())
 for field in REQUIRED_MANIFEST_FIELDS:
  d=deepcopy(base); d["installation_manifest"].pop(field,None); m=d["installation_manifest"];
  if field!="manifest_hash": m["manifest_hash"]=_sha({k:v for k,v in m.items() if k!="manifest_hash"})
  d["result_hash"]=_sha({k:v for k,v in d.items() if k!="result_hash"}); x=e.step(d); assert not x["admissible"] and "manifest_field_missing:"+field in x["blocking_reasons"]
print("ACEE6_B1_MANIFEST_FIELD_MATRIX_OK")
