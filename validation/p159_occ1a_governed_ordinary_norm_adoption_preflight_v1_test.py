from pathlib import Path
import hashlib,json
from ontology import occ_governed_ordinary_norm_adoption_preflight as q
ROOT=Path(__file__).resolve().parents[1]
def main():
 paths=[ROOT/q.DEC_REL,ROOT/q.DOS_REL,ROOT/q.DECL_REL]
 before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
 x=q.audit(ROOT)
 after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
 assert before==after
 assert x["ordinary_target_count"]==17
 assert x["dna_l0_excluded_count"]==6
 assert x["checks"]["all_human_decisions_adopt_oob"] is True
 assert x["checks"]["all_registered_proposals_exact"] is True
 assert x["checks"]["all_p106_dossiers_confirmed_and_bound"] is True
 assert x["checks"]["institutional_authority_independently_verified"] is True
 # Fail closed: DEVELOPMENT must not silently become P159_OCC1A_NORM_ADOPTION.
 if x["declared_authority_context"]=="DEVELOPMENT":
  assert x["decision"]=="ADOPTION_PREFLIGHT_BLOCKED"
  assert "NO_IMPLICIT_AUTHORITY_CONTEXT_EXPANSION" in x["blockers"]
 assert x["adoption_performed"] is False and x["authority_activated"] is False
 assert x["package_materialized"] is False and x["execution_performed"] is False
 assert x["occ1a_closed"] is False and x["occ1b_opened"] is False and x["p160_opened"] is False
 assert q.audit(ROOT)==x
 print("P159_OCC1A_GOVERNED_ORDINARY_NORM_ADOPTION_PREFLIGHT_FUNCTIONAL_OK")
 print("P159_OCC1A_GOVERNED_ORDINARY_NORM_ADOPTION_PREFLIGHT_NONMUTATION_OK")
 print("P159_OCC1A_GOVERNED_ORDINARY_NORM_ADOPTION_PREFLIGHT_DETERMINISM_OK")
 print("decision="+x["decision"])
 print("declared_authority_context="+x["declared_authority_context"])
 print("required_p095_context="+x["required_p095_context"])
 for b in x["blockers"]: print("BLOCKER="+b)
 print("adoption_performed=false");print("authority_activated=false");print("package_materialized=false")
 print("execution_performed=false");print("occ1a_closed=false");print("occ1b_opened=false");print("p160_opened=false")
if __name__=="__main__":main()
