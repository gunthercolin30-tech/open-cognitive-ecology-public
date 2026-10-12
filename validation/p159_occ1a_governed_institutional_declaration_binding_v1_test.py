from pathlib import Path
import json, tempfile, shutil
from ontology import occ_governed_institutional_declaration_binding as b
from ontology import occ_independent_institutional_authority_verifier as v
ROOT=Path(__file__).resolve().parents[1]

def copy_required(t):
 for rel in (v.REL,v.DOS_REL,v.DEC_REL,Path("validation/evidence/p110_final_lock_v1.json"),Path("validation/evidence/p110_postlock_verification_v1.json")):
  src=ROOT/rel; dst=t/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)

def main():
 dp=ROOT/b.DECL_REL; before=dp.read_bytes()
 m=b.materialize(ROOT); assert m["status"]=="GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_VERIFIED",m
 assert dp.read_bytes()==before and m["declaration_sha256"]==m["declaration_sha256_after"]
 q=b.verify_materialized(ROOT); assert q["status"]=="GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_VERIFIED",q
 x=v.verify(ROOT); assert x["status"]=="INDEPENDENT_AUTHORITY_VERIFICATION_OK",x
 assert x["institutional_authority_established"] is True and x["authority_activated"] is False
 assert x["adoption_performed"] is False and x["execution_performed"] is False
 assert x["occ1a_closed"] is False and x["occ1b_opened"] is False and x["p160_opened"] is False
 print("P159_OCC1A_GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_FUNCTIONAL_OK")
 with tempfile.TemporaryDirectory() as td:
  t=Path(td); copy_required(t); b.materialize(t)
  p=t/b.DECL_REL; d=json.loads(p.read_text()); d["holder"]="TAMPER"; p.write_text(json.dumps(d,sort_keys=True))
  y=v.verify(t); assert y["status"]=="INDEPENDENT_AUTHORITY_VERIFICATION_BLOCKED" and y["authority_activated"] is False
  assert "GOVERNED_DECLARATION_BINDING_INVALID" in y["blockers"]
 print("P159_OCC1A_GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_DEGRADATION_OK")
 with tempfile.TemporaryDirectory() as td:
  t=Path(td); copy_required(t); b.materialize(t)
  p=t/b.BIND_REL; d=json.loads(p.read_text()); d["authority_activated"]=True; p.write_text(json.dumps(d,sort_keys=True))
  y=v.verify(t); assert y["status"]=="INDEPENDENT_AUTHORITY_VERIFICATION_BLOCKED"
 print("P159_OCC1A_GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_NO_ACTIVATION_OK")
 a=v.verify(ROOT); c=v.verify(ROOT); assert a==c
 print("P159_OCC1A_GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_NONREGRESSION_OK")
 print("decision="+a["status"]); print("institutional_authority_established="+str(a["institutional_authority_established"]).lower())
 print("authority_activated=false"); print("occ1a_closed=false"); print("occ1b_opened=false"); print("p160_opened=false")
if __name__=="__main__": main()
