from pathlib import Path
import json,tempfile,shutil
from ontology import occ_governed_version_binding_resolver as v
ROOT=Path(__file__).resolve().parents[1]
def main():
 x=v.resolve(ROOT)
 assert x["status"]=="GOVERNED_VERSION_BINDINGS_RESOLVED",x
 assert x["constitution_version"].startswith("P110:CONSTITUTIONAL_FINAL_LOCK_OK:")
 assert x["governance_version"].startswith("P110:GOVERNANCE_ENGINE_VALIDATED:")
 assert x["p110_final_lock_identity_sha256"]=="da56dde746fcb7f6154b4aac99879d727e30645a77564f35bbc5bca6102269bc",x
 assert x["authority_activated"] is False and x["occ1b_opened"] is False and x["p160_opened"] is False
 print("P159_OCC1A_GOVERNED_VERSION_BINDING_FUNCTIONAL_OK")
 with tempfile.TemporaryDirectory() as td:
  t=Path(td); (t/"validation").mkdir()
  # No P110 evidence must fail closed.
  y=v.resolve(t)
  assert y["status"]=="GOVERNED_VERSION_BINDINGS_BLOCKED"
  assert "P110_FINAL_LOCK_NOT_UNIQUE" in y["blockers"]
 print("P159_OCC1A_GOVERNED_VERSION_BINDING_DEGRADATION_OK")
 assert v.resolve(ROOT)==v.resolve(ROOT)
 print("P159_OCC1A_GOVERNED_VERSION_BINDING_NONREGRESSION_OK")
 print("constitution_version="+x["constitution_version"])
 print("governance_version="+x["governance_version"])
if __name__=="__main__": main()
