from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha

def rebind(d):
 m=d["installation_manifest"]; m["manifest_hash"]=_sha({k:v for k,v in m.items() if k!="manifest_hash"}); d["result_hash"]=_sha({k:v for k,v in d.items() if k!="result_hash"})
with TemporaryDirectory() as t, TemporaryDirectory() as o:
 r=Path(t); (r/"ontology").mkdir(); (r/"ontology"/"linked").symlink_to(Path(o),target_is_directory=True)
 d=valid_acee5_decision(r); d["installation_manifest"]["target_path"]="ontology/linked/candidate.py"; rebind(d)
 x=AceeInstallationExecutor(root=r,now_utc=fixed_now()).step(d)
 assert not x["admissible"] and any("outside_root" in q for q in x["blocking_reasons"])
print("ACEE6_B1_PARENT_SYMLINK_ESCAPE_OK")
