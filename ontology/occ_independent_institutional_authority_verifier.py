from pathlib import Path
import hashlib, json
from ontology.human_reserved_authority_registry import InitialDevelopmentAuthoritySpec, RESERVED_CLASSES, INITIAL_DEVELOPMENT_HOLDER, INITIAL_DEVELOPMENT_ROLE, INITIAL_DEVELOPMENT_REGIME, INITIAL_DEVELOPMENT_CONTINUITY
from ontology import constitutional_amendment_protocol as p106
from ontology import occ_p106_bulk_prefill_review as bulk
from ontology import occ_governed_institutional_declaration_binding as binding

SCHEMA="oce.p159.occ1a.independent_institutional_authority_verifier.v2"
REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json")
DOS_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_institutional_authority_amendment_dossier.json")
DEC_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_human_adoption_decisions.json")

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _result(checks,blockers,hashes=None):
 blockers=sorted(set(blockers)); ok=not blockers
 return {"schema":SCHEMA,"status":"INDEPENDENT_AUTHORITY_VERIFICATION_OK" if ok else "INDEPENDENT_AUTHORITY_VERIFICATION_BLOCKED",
 "checks":checks,"blockers":blockers,"hashes":hashes or {},"institutional_authority_established":ok,
 "authority_activated":False,"adoption_performed":False,"execution_performed":False,"occ1a_closed":False,
 "occ1b_opened":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}

def verify(root=None):
 r=_root(root); blockers=[]; checks={}; sp,dp,decp=r/REL,r/DOS_REL,r/DEC_REL
 for p,label in ((sp,"DECLARATION"),(dp,"P106_DOSSIER"),(decp,"DECISIONS")):
  if not p.is_file(): blockers.append(label+"_MISSING")
 if blockers: return _result(checks,blockers)
 w=_load(sp); dw=_load(dp); decisions=_load(decp)
 def check(name,cond,blocker):
  checks[name]=bool(cond)
  if not cond: blockers.append(blocker)
 check("schema",w.get("schema")=="oce.p159.occ1a.p095.initial_development_authority_materialization.v1","DECLARATION_SCHEMA_INVALID")
 check("status",w.get("status")=="READY_FOR_INDEPENDENT_VERIFICATION","DECLARATION_NOT_READY")
 check("holder",w.get("holder")==INITIAL_DEVELOPMENT_HOLDER,"HOLDER_MISMATCH")
 check("regime",w.get("regime")==INITIAL_DEVELOPMENT_REGIME,"REGIME_MISMATCH")
 check("role",w.get("role")==INITIAL_DEVELOPMENT_ROLE,"ROLE_MISMATCH")
 check("context",w.get("context")=="DEVELOPMENT","CONTEXT_MISMATCH")
 check("scope",tuple(w.get("scope",()))==tuple(RESERVED_CLASSES),"P095_SCOPE_MISMATCH")
 check("continuity",w.get("continuity")==INITIAL_DEVELOPMENT_CONTINUITY,"CONTINUITY_MISMATCH")
 check("human_confirmation",w.get("human_confirmed") is True and w.get("confirmation_phrase")=="CONFIRM INITIAL DEVELOPMENT HUMAN AUTHORITY","HUMAN_CONFIRMATION_INVALID")
 check("authenticated_assertion",w.get("authenticated") is True,"AUTHENTICATION_ASSERTION_MISSING")
 check("no_root_override",w.get("root_override_all") is False,"ROOT_OVERRIDE_ALL_FORBIDDEN")
 check("no_dna_l0_override",w.get("dna_l0_ordinary_override") is False,"DNA_L0_ORDINARY_OVERRIDE_FORBIDDEN")
 check("no_artificial_expansion",w.get("artificial_authority_expansion") is False,"ARTIFICIAL_AUTHORITY_EXPANSION_FORBIDDEN")
 check("no_effects",all(w.get(k) is False for k in ("institutional_authority_established","authority_activated","adoption_performed","execution_performed","occ1a_closed","occ1b_opened","p160_opened")),"PREMATURE_NORMATIVE_EFFECT")
 bv=binding.verify_materialized(r); check("governed_binding",bv.get("status")=="GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_VERIFIED","GOVERNED_DECLARATION_BINDING_INVALID")
 b=bv.get("binding",{}) if checks["governed_binding"] else {}
 cv=b.get("constitution_version"); gv=b.get("governance_version")
 check("concrete_constitution_version",isinstance(cv,str) and cv.startswith("P110:CONSTITUTIONAL_FINAL_LOCK_OK:"),"CONSTITUTION_VERSION_UNRESOLVED")
 check("concrete_governance_version",isinstance(gv,str) and gv.startswith("P110:GOVERNANCE_ENGINE_VALIDATED:"),"GOVERNANCE_VERSION_UNRESOLVED")
 try:
  spec=InitialDevelopmentAuthoritySpec(authority_id=w["authority_id"],provenance=w["provenance"],mandate=w["mandate"],
   valid_from=w["valid_from"],valid_until=w["valid_until"],constitution_version=cv,governance_version=gv,
   context=w["context"],authenticated=w["authenticated"])
  ok,reason=spec.validate()
 except Exception:
  ok,reason=False,"spec_construction_failed"
 check("p095_spec",ok,"P095_SPEC_INVALID:"+reason)
 try:
  expected=bulk.build_prefilled(r); by_id={x["canonical_id"]:x for x in expected["dossiers"]}; rows=dw.get("dossiers",[])
  p106_ok=(len(rows)==17 and set(by_id)=={x.get("canonical_id") for x in rows})
  if p106_ok:
   for row in rows:
    exp=by_id[row["canonical_id"]]
    if row.get("dossier_human_confirmed") is not True or row.get("p106")!=exp.get("p106"): p106_ok=False; break
    res=p106.evaluate_amendment(route=p106.DNA,target_layer=p106.DNA,proposer="HUMAN",evidence=row["p106"])
    if res.status!="ADMISSIBLE_FOR_DECISION" or res.authority_granted or res.execution_performed: p106_ok=False; break
 except Exception: p106_ok=False
 check("p106_chain",p106_ok,"P106_CHAIN_INVALID")
 rows=decisions.get("rows",[]); ordinary=[x for x in rows if x.get("decision")=="ADOPT" and x.get("layer") in ("DNA_H","DNA_L1")]
 check("decision_chain",len(ordinary)==17 and all(x.get("out_of_band_confirmation") is True for x in ordinary),"DECISION_CHAIN_INVALID")
 check("legacy_dossier_no_authority_effect",dw.get("institutional_authority_established") is False and dw.get("adoption_performed") is False and dw.get("activation_performed") is False and dw.get("execution_performed") is False,"LEGACY_DOSSIER_EFFECT_FORBIDDEN")
 hashes={"declaration_sha256":_sha(sp),"p106_dossier_sha256":_sha(dp),"decision_sha256":_sha(decp)}
 if (r/binding.BIND_REL).is_file(): hashes["binding_sha256"]=_sha(r/binding.BIND_REL)
 return _result(checks,blockers,hashes)

def manifest():
 return {"schema":SCHEMA,"read_only":True,"calls_p095_registration":False,"calls_p104_persistence":False,
 "calls_p106_evaluation":True,"authority_activated":False,"adoption_performed":False,"execution_performed":False,
 "functional_only":True,"phenomenology_undetermined":True}
