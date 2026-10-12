from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from ontology import occ_human_adoption_decision as x
def ck(v,n):
 if not v: raise AssertionError(n)
 print(n)
w=x.prepare(ROOT);ck(len(w["rows"])==23,"P159_OCC1A_HUMAN_DECISION_23_PROPOSALS_OK");ck(sum(r["layer"]=="DNA_L0" for r in w["rows"])==6,"P159_OCC1A_HUMAN_DECISION_6_L0_OK")
r=x.decide(w,"DNA.H1","ADOPT","human governed decision","Colin Gunther","principal_investigator",True);ck(r["accepted"] and not r["adoption_performed"],"P159_OCC1A_HUMAN_DECISION_IS_NOT_ADOPTION_OK")
w=x.prepare(ROOT);r=x.decide(w,"DNA.H1","ADOPT","human governed decision","Colin Gunther","principal_investigator",False);ck(not r["accepted"] and r["reason"]=="OUT_OF_BAND_CONFIRMATION_REQUIRED","P159_OCC1A_HUMAN_DECISION_OOB_REQUIRED_OK")
w=x.prepare(ROOT);r=x.decide(w,"DNA.L0.1","ADOPT","attempt","Colin Gunther","constitutional_authority",True);ck(not r["accepted"] and r["reason"]=="DNA_L0_REFOUNDING_OR_FORK_REQUIRED","P159_OCC1A_HUMAN_DECISION_L0_BLOCKED_OK")
m=x.manifest();ck(not m["adoption_performed"] and not m["activation_performed"] and not m["execution_performed"],"P159_OCC1A_HUMAN_DECISION_NO_NORMATIVE_EFFECT_OK");ck(not m["occ1a_closed"] and not m["occ1b_opened"] and not m["p160_opened"],"P159_OCC1A_HUMAN_DECISION_STAGE_BOUNDARY_OK")
print("P159_OCC1A_HUMAN_ADOPTION_DECISION_V1_OK")
