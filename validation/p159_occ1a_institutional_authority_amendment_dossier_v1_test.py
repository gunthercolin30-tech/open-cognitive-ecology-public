from pathlib import Path
import copy,sys,tempfile,json,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from ontology import occ_institutional_authority_amendment_dossier as m
def ck(x,n):
 assert x,n;print(n)
w=m.prepare(ROOT)
ck(len(w["dossiers"])==17,"P159_OCC1A_INSTITUTIONAL_17_DOSSIERS_OK")
v=m.validate(w)
ck(v["status"]=="INSTITUTIONAL_INPUT_REQUIRED","P159_OCC1A_INSTITUTIONAL_FAIL_CLOSED_OK")
ck(not m.manifest()["calls_p095"] and not m.manifest()["calls_p106"] and not m.manifest()["calls_p104"],"P159_OCC1A_INSTITUTIONAL_NO_AUTHORITY_SIDE_EFFECT_OK")
x=copy.deepcopy(w);a=x["authority"]
a.update({"authority_id":"test","human_identity":"test-human","authenticated":True,"mandate":"test-only",
"valid_from":1,"valid_until":2,"constitution_version":"test","governance_version":"test","authority_human_confirmed":True})
x["authority_provenance"]="test";x["authority_evidence"]="test";x["independent_domains"]=["test-domain"]
for r in x["dossiers"]:
 for k in m.P106_FIELDS:r["p106"][k]="test"
 r["dossier_human_confirmed"]=True
ck(m.validate(x)["status"]=="READY_FOR_GOVERNED_EVALUATION","P159_OCC1A_INSTITUTIONAL_COMPLETE_FIXTURE_OK")
x["dossiers"][0]["p106"]["rights_impact"]=""
ck(m.validate(x)["status"]=="INSTITUTIONAL_INPUT_REQUIRED","P159_OCC1A_INSTITUTIONAL_DEGRADATION_OK")
ck(not w["adoption_performed"] and not w["activation_performed"] and not w["execution_performed"],"P159_OCC1A_INSTITUTIONAL_NO_NORMATIVE_EFFECT_OK")
print("P159_OCC1A_INSTITUTIONAL_AUTHORITY_AMENDMENT_DOSSIER_V1_OK")
