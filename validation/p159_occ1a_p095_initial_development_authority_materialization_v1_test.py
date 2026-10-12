import tempfile
from pathlib import Path
from ontology.occ_initial_development_authority_materialization import prepare,validate,save_human_inputs,load_or_prepare
def run():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td); x=prepare(root)
  assert validate(x)["status"]=="HUMAN_INSTITUTIONAL_CONFIRMATION_REQUIRED"
  x.update({"provenance":"human-supplied constituent/development provenance","authority_evidence":"human-supplied institutional evidence",
  "constitution_version":"human-confirmed-version","governance_version":"human-confirmed-version","valid_from":1,"valid_until":2,
  "authenticated":True,"human_confirmed":True,"confirmation_phrase":"CONFIRM INITIAL DEVELOPMENT HUMAN AUTHORITY"})
  r=save_human_inputs(x,root)
  assert r["status"]=="READY_FOR_INDEPENDENT_VERIFICATION" and not r["institutional_authority_established"] and not r["authority_activated"]
  y=load_or_prepare(root); assert y["root_override_all"] is False and y["dna_l0_ordinary_override"] is False
  y["root_override_all"]=True; assert "ROOT_OVERRIDE_ALL_FORBIDDEN" in validate(y)["blockers"]
  y=load_or_prepare(root); y["scope"]=["*"]; assert "EXACT_CURRENT_RESERVED_SCOPE_REQUIRED" in validate(y)["blockers"]
  print("P159_OCC1A_P095_AUTHORITY_MATERIALIZATION_FUNCTIONAL_OK")
  print("P159_OCC1A_P095_AUTHORITY_MATERIALIZATION_DEGRADATION_OK")
  print("P159_OCC1A_P095_AUTHORITY_MATERIALIZATION_NONREGRESSION_OK")
  print("institutional_authority_established=false"); print("authority_activated=false")
  print("occ1a_closed=false"); print("occ1b_opened=false"); print("p160_opened=false")
if __name__=="__main__": run()
