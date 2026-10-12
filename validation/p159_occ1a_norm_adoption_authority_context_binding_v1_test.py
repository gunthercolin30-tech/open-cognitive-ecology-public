from pathlib import Path
import json, tempfile, shutil
from ontology import occ_norm_adoption_authority_context_binding as q
ROOT=Path(__file__).resolve().parents[1]
def main():
 x=q.build(ROOT)
 assert q.validate(x,ROOT/q.DECL_REL)
 assert x["status"]=="AWAITING_HUMAN_CONFIRMATION" and x["human_confirmed"] is False
 for k in ("authority_expansion","root_override_all","dna_l0_ordinary_override","delegation","succession",
           "authority_activated","adoption_performed","package_materialized","execution_performed",
           "occ1a_closed","occ1b_opened","p160_opened"): assert x[k] is False
 y=dict(x); y["human_confirmed"]=True;y["status"]="HUMAN_CONFIRMED";y["human_confirmation_text"]=q.CONFIRMATION
 assert q.validate(y,ROOT/q.DECL_REL)
 z=dict(y);z["dna_l0_ordinary_override"]=True
 assert not q.validate(z,ROOT/q.DECL_REL)
 z=dict(y);z["human_confirmation_text"]="yes"
 assert not q.validate(z,ROOT/q.DECL_REL)
 print("P159_OCC1A_NORM_ADOPTION_AUTHORITY_CONTEXT_BINDING_FUNCTIONAL_OK")
 print("P159_OCC1A_NORM_ADOPTION_AUTHORITY_CONTEXT_BINDING_DNA_L0_GUARD_OK")
 print("P159_OCC1A_NORM_ADOPTION_AUTHORITY_CONTEXT_BINDING_EXACT_CONFIRMATION_OK")
 print("authority_activated=false");print("adoption_performed=false");print("execution_performed=false")
 print("occ1a_closed=false");print("occ1b_opened=false");print("p160_opened=false")
if __name__=="__main__":main()
