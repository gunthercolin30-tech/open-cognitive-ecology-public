from pathlib import Path
import json,tempfile
from ontology import occ_independent_institutional_authority_verifier as v
ROOT=Path(__file__).resolve().parents[1]
def main():
 x=v.verify(ROOT)
 assert x["status"]=="INDEPENDENT_AUTHORITY_VERIFICATION_BLOCKED",x
 assert "CONSTITUTION_VERSION_SYMBOLIC_UNRESOLVED" in x["blockers"]
 assert "GOVERNANCE_VERSION_SYMBOLIC_UNRESOLVED" in x["blockers"]
 assert x["checks"]["p106_chain"] and x["checks"]["decision_chain"] and x["checks"]["p095_spec"] and x["checks"]["scope"] and x["checks"]["no_effects"]
 assert x["authority_activated"] is False
 print("P159_OCC1A_INDEPENDENT_AUTHORITY_VERIFIER_FUNCTIONAL_OK")
 with tempfile.TemporaryDirectory() as td:
  t=Path(td)
  for rel in (v.REL,v.DOS_REL,v.DEC_REL):
   src=ROOT/rel; dst=t/rel; dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(src.read_bytes())
  p=t/v.REL; w=json.loads(p.read_text(encoding="utf-8")); w["root_override_all"]=True
  p.write_text(json.dumps(w,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
  y=v.verify(t)
  assert "ROOT_OVERRIDE_ALL_FORBIDDEN" in y["blockers"] and y["authority_activated"] is False
 print("P159_OCC1A_INDEPENDENT_AUTHORITY_VERIFIER_DEGRADATION_OK")
 a=v.verify(ROOT); b=v.verify(ROOT); assert a==b
 assert a["institutional_authority_established"] is False and a["adoption_performed"] is False and a["execution_performed"] is False
 assert a["occ1b_opened"] is False and a["p160_opened"] is False
 print("P159_OCC1A_INDEPENDENT_AUTHORITY_VERIFIER_NONREGRESSION_OK")
 print("decision="+a["status"]); print("blockers="+",".join(a["blockers"]))
 print("institutional_authority_established=false"); print("authority_activated=false")
 print("occ1a_closed=false"); print("occ1b_opened=false"); print("p160_opened=false")
if __name__=="__main__": main()
