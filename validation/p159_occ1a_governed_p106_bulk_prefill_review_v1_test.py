from pathlib import Path
import copy,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from ontology import occ_p106_bulk_prefill_review as m
def ck(v,n): assert v,n;print(n)
w=m.build_prefilled(ROOT);ck(len(w["dossiers"])==17,"P159_OCC1A_P106_BULK_17_OK");ck(m.summary(w)["all_prefilled"],"P159_OCC1A_P106_BULK_PREFILL_OK");ck(not m.summary(w)["all_confirmed"],"P159_OCC1A_P106_REVIEW_REQUIRED_OK")
ck("F18" in w["dossiers"][8]["p106"]["incompatibility_analysis"],"P159_OCC1A_P106_H9_F18_EXCLUSION_OK")
try:m.confirm(w,"wrong");raise AssertionError
except ValueError:print("P159_OCC1A_P106_BAD_CONFIRMATION_REJECTED_OK")
c=m.confirm(w,"CONFIRM 17 P106 DOSSIERS ONLY");ck(m.summary(c)["all_confirmed"],"P159_OCC1A_P106_BULK_CONFIRM_OK")
ck(not c["institutional_authority_established"] and not c["p106_admissibility_established"],"P159_OCC1A_P106_NO_AUTHORITY_OR_ADMISSIBILITY_OK")
ck(not c["adoption_performed"] and not c["activation_performed"] and not c["execution_performed"],"P159_OCC1A_P106_NO_NORMATIVE_EFFECT_OK")
x=copy.deepcopy(w);x["dossiers"][0]["p106"]["rights_impact"]=""
try:m.confirm(x,"CONFIRM 17 P106 DOSSIERS ONLY");raise AssertionError
except ValueError:print("P159_OCC1A_P106_DEGRADATION_OK")
man=m.manifest();ck(not man["calls_p095"] and not man["calls_p106"] and not man["calls_p104"],"P159_OCC1A_P106_NO_ENGINE_CALL_OK")
print("P159_OCC1A_GOVERNED_P106_BULK_PREFILL_REVIEW_V1_OK")
