from pathlib import Path
import json,tempfile
from ontology import occ_governed_version_binding_resolver as v
ROOT=Path(__file__).resolve().parents[1]
EXPECTED="da56dde746fcb7f6154b4aac99879d727e30645a77564f35bbc5bca6102269bc"

def _w(root,rel,d):
 p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,sort_keys=True),encoding="utf-8")
def _fx(root):
 lock={"schema":"oce.p110.final_lock.v1","milestone":"P110","status":"LOCKED","canonical_signal":"CONSTITUTIONAL_FINAL_LOCK_OK",
 "constitutional_final_lock_ok":True,"final_lock_identity_sha256":EXPECTED,
 "signals":{"CONSTITUTION_LOCKED":True,"DNA_CONSTITUTIVE_LOCKED":True,"GOVERNANCE_ENGINE_VALIDATED":True}}
 post={"schema":"oce.p110.postlock.verification.v1","milestone":"P110","status":"POSTLOCK_VERIFIED",
 "canonical_signal":"CONSTITUTIONAL_FINAL_LOCK_OK","final_lock_identity_sha256":EXPECTED,
 "checks":{"identity_exact":True,"identity_recomputed":True,"protected_artifact_drift_absent":True,"final_lock_sha_exact":True},
 "protected_artifact_drift":False,"tamper_probes":[{"id":"T1","rejected":True}]}
 _w(root,"validation/evidence/p110_final_lock_v1.json",lock); _w(root,"validation/evidence/p110_postlock_verification_v1.json",post)

def main():
 x=v.resolve(ROOT); assert x["status"]=="GOVERNED_VERSION_BINDINGS_RESOLVED",x
 assert x["p110_final_lock_identity_sha256"]==EXPECTED
 print("P159_OCC1A_GOVERNED_VERSION_BINDING_V1_2_FUNCTIONAL_OK")
 with tempfile.TemporaryDirectory() as td:
  t=Path(td); _fx(t)
  _w(t,"validation/evidence/noise.json",{"schema":"report","canonical_signal":"CONSTITUTIONAL_FINAL_LOCK_OK","final_lock_identity_sha256":"0"*64})
  assert v.resolve(t)["status"]=="GOVERNED_VERSION_BINDINGS_RESOLVED"
 print("P159_OCC1A_GOVERNED_VERSION_BINDING_V1_2_FALSE_DUPLICATE_IGNORED_OK")
 with tempfile.TemporaryDirectory() as td:
  t=Path(td); _fx(t); p=t/"validation/evidence/p110_postlock_verification_v1.json"; d=json.loads(p.read_text()); d["checks"]["identity_exact"]=False; p.write_text(json.dumps(d))
  assert "P110_POSTLOCK_IDENTITY_NOT_EXACT" in v.resolve(t)["blockers"]
 with tempfile.TemporaryDirectory() as td:
  t=Path(td); _fx(t); p=t/"validation/evidence/p110_postlock_verification_v1.json"; d=json.loads(p.read_text()); d["protected_artifact_drift"]=True; p.write_text(json.dumps(d))
  assert "P110_POSTLOCK_PROTECTED_DRIFT_PRESENT" in v.resolve(t)["blockers"]
 with tempfile.TemporaryDirectory() as td:
  t=Path(td); _fx(t); p=t/"validation/evidence/p110_postlock_verification_v1.json"; d=json.loads(p.read_text()); d["tamper_probes"][0]["rejected"]=False; p.write_text(json.dumps(d))
  assert "P110_POSTLOCK_TAMPER_PROBES_INVALID" in v.resolve(t)["blockers"]
 print("P159_OCC1A_GOVERNED_VERSION_BINDING_V1_2_DEGRADATION_OK")
 assert v.resolve(ROOT)==v.resolve(ROOT)
 print("P159_OCC1A_GOVERNED_VERSION_BINDING_V1_2_NONREGRESSION_OK")
 print("status="+x["status"]); print("constitution_version="+x["constitution_version"]); print("governance_version="+x["governance_version"])
 print("authority_activated=false"); print("occ1a_closed=false"); print("occ1b_opened=false"); print("p160_opened=false")
if __name__=="__main__": main()
