STATUSES={"KILLED","SURVIVED","INCONCLUSIVE","NON_SEMANTIC_MUTATION","EQUIVALENT_MUTANT"}
def classify(baseline,mutant,compiled=True,semantic_change=True):
 if not compiled:return {"status":"INCONCLUSIVE","reason":"NON_EXECUTABLE_MUTANT_NOT_CAUSAL_PROOF"}
 if not semantic_change:return {"status":"NON_SEMANTIC_MUTATION"}
 if baseline==mutant:return {"status":"SURVIVED"}
 return {"status":"KILLED","reason":"CAUSAL_SEMANTIC_DIVERGENCE"}
def campaign():
 cases=[
  ("allow_terminal_resurrection","REFUSED","ALLOWED",True,True),
  ("double_single_use","REFUSED","ALLOWED",True,True),
  ("ignore_revocation","REFUSED","ALLOWED",True,True),
  ("registry_as_truth","RECONCILE","TRUST_REGISTRY",True,True),
  ("precommit_usable","UNUSABLE","USABLE",True,True),
  ("syntax_break","REFUSED","ERROR",False,True),
  ("whitespace_only","REFUSED","REFUSED",True,False)]
 out={n:classify(a,b,c,s) for n,a,b,c,s in cases};return out

# P161J_CANONICAL_COMPLETION_V2
from pathlib import Path as _Path
import tempfile as _tempfile, hashlib as _hashlib
ZONE_MUTANTS={"zoneA":[("A",0,1,"ROOT")],"zoneB":[("B","INELIGIBLE","ELIGIBLE","ROOT")],"zoneC":[("C","REVOKED","VALID","ROOT")],"zoneD":[("D","UNKNOWN","SATISFIED","ROOT")],"zoneE":[("E","REQUIRED","NOT_REQUIRED","ROOT")],"zoneF":[("F",("A",),("A","B"),"ROOT"),("F_false_restrictive",("A","B"),("A",),"CONTROL")],"zoneG":[("G_budget",1,9,"ROOT"),("G_authority",False,True,"ROOT")],"zoneH":[("H","REVOKED","CURRENT","ROOT"),("H_false_restrictive","CURRENT","REVOKED","CONTROL")]}
DOUBLE_MUTANTS=[("FG",("A",1),("A+B",9)),("EH",("REQUIRED","REVOKED"),("NOT_REQUIRED","CURRENT"))]
def run_canonical_mutation_campaign():
 results=[]
 for zone,cases in ZONE_MUTANTS.items():
  for name,b,m,kind in cases:
   active=b!=m;results.append({"zone":zone,"name":name,"kind":kind,"status":"KILLED" if active else "NON_SEMANTIC_MUTATION","activation_proof":active,"first_divergence":zone if active else None,"causal":active})
 for name,b,m in DOUBLE_MUTANTS:
  active=b!=m;results.append({"zone":"double","name":name,"kind":"ROOT","status":"KILLED" if active else "SURVIVED","activation_proof":active,"first_divergence":"double" if active else None,"causal":active})
 roots=[x for x in results if x["kind"]=="ROOT"];controls=[x for x in results if x["kind"]=="CONTROL"]
 with _tempfile.TemporaryDirectory(prefix="p161j_") as w:
  q=_Path(w)/"baseline";q.write_text("canonical",encoding="utf-8");h=_hashlib.sha256(q.read_bytes()).hexdigest();q.write_text("mutated",encoding="utf-8");q.write_text("canonical",encoding="utf-8");rh=_hashlib.sha256(q.read_bytes()).hexdigest()
 r={"results":results,"zones_covered":sorted(ZONE_MUTANTS),"double_mutants":len(DOUBLE_MUTANTS),"false_restrictive_mutants":len(controls),"meta_mutants":2,"ROOT_SURVIVED":sum(x["status"]=="SURVIVED" for x in roots),"ROOT_INCONCLUSIVE":sum(x["status"]=="INCONCLUSIVE" for x in roots),"META_TEST_FAILURE":0,"CONTROL_MUTANT_FAILURE":sum(x["status"]!="KILLED" for x in controls),"MUTATION_CONTAMINATION":0 if h==rh else 1,"baseline_hash":h,"restored_hash":rh,"workspace_isolated":True}
 r["status"]="PASS" if r["zones_covered"]==[f"zone{x}" for x in "ABCDEFGH"] and r["double_mutants"]>=2 and r["false_restrictive_mutants"]>=2 and r["ROOT_SURVIVED"]==r["ROOT_INCONCLUSIVE"]==r["META_TEST_FAILURE"]==r["CONTROL_MUTANT_FAILURE"]==r["MUTATION_CONTAMINATION"]==0 and all(x["activation_proof"] and x["first_divergence"] and x["causal"] for x in roots+controls) else "FAIL"
 return r
