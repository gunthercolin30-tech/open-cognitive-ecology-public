from pathlib import Path
import hashlib,json
from ontology import occ_norm_adoption_event as adoption
from ontology import occ_independent_institutional_authority_verifier as authority

SCHEMA="oce.p159.occ1a.governed_ordinary_norm_adoption_preflight.v1"
DEC_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_human_adoption_decisions.json")
DOS_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_institutional_authority_amendment_dossier.json")
DECL_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json")
REPORT_REL=Path("validation/evidence/p159_occ1a/occ1a_governed_ordinary_norm_adoption_preflight_v1.json")
ORDINARY_LAYERS={"DNA_H","DNA_L1"}

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def audit(root=None):
 r=_root(root); d=_load(r/DEC_REL); dos=_load(r/DOS_REL); decl=_load(r/DECL_REL)
 auth=authority.verify(r)
 rows=[x for x in d.get("rows",[]) if x.get("layer") in ORDINARY_LAYERS]
 l0=[x for x in d.get("rows",[]) if x.get("layer")=="DNA_L0"]
 dossier_by={x.get("canonical_id"):x for x in dos.get("dossiers",[])}
 proposal_ok=[]; p106_ok=[]; decision_ok=[]
 for x in rows:
  decision_ok.append(x.get("decision")=="ADOPT" and x.get("out_of_band_confirmation") is True)
  got=adoption.load_registered_proposal(x.get("canonical_id"),r)
  proposal_ok.append(bool(got.get("accepted")) and got["proposal"].get("proposal_hash")==x.get("proposal_hash"))
  z=dossier_by.get(x.get("canonical_id"),{})
  p106_ok.append(z.get("dossier_human_confirmed") is True and z.get("proposal_hash")==x.get("proposal_hash"))
 declared_context=str(decl.get("context") or "")
 required_context="P159_OCC1A_NORM_ADOPTION"
 bind_path=r/Path("oif_review/campaigns/P159-OCC1A/occ1a_norm_adoption_authority_context_binding.json")
 bind=_load(bind_path) if bind_path.is_file() else {}
 bind_source_ok=bind.get("source_authority_declaration_sha256")==_sha(r/DECL_REL)
 bind_guards_ok=all(bind.get(k) is False for k in ("authority_expansion","root_override_all","dna_l0_ordinary_override","delegation","succession","authority_activated","adoption_performed","package_materialized","execution_performed","occ1a_closed","occ1b_opened","p160_opened"))
 context_explicit=(bind.get("schema")=="oce.p159.occ1a.norm_adoption_authority_context_binding.v1" and bind.get("status")=="HUMAN_CONFIRMED" and bind.get("human_confirmed") is True and bind.get("additional_context")==required_context and bind.get("binding_kind")=="EXPLICIT_CONTEXT_BINDING_ONLY" and bind_source_ok and bind_guards_ok)
 checks={
  "ordinary_set_exactly_17":len(rows)==17,
  "six_dna_l0_excluded":len(l0)==6 and all(x.get("ordinary_adoption_permitted") is False for x in l0),
  "all_human_decisions_adopt_oob":len(decision_ok)==17 and all(decision_ok),
  "all_registered_proposals_exact":len(proposal_ok)==17 and all(proposal_ok),
  "all_p106_dossiers_confirmed_and_bound":len(p106_ok)==17 and all(p106_ok),
  "institutional_authority_independently_verified":auth.get("status")=="INDEPENDENT_AUTHORITY_VERIFICATION_OK" and auth.get("institutional_authority_established") is True,
  "p095_required_adoption_context_explicitly_bound":context_explicit,
  "no_prior_adoption":d.get("adoption_performed") is False,
  "no_activation_execution":d.get("activation_performed") is False and d.get("execution_performed") is False
 }
 blockers=[]
 for k,v in checks.items():
  if not v: blockers.append(k.upper())
 if not context_explicit:
  blockers.append("NO_IMPLICIT_AUTHORITY_CONTEXT_EXPANSION")
 return {"schema":SCHEMA,
  "decision":"READY_FOR_17_ORDINARY_ADOPTIONS" if not blockers else "ADOPTION_PREFLIGHT_BLOCKED",
  "checks":checks,"blockers":sorted(set(blockers)),
  "ordinary_target_count":len(rows),"dna_l0_excluded_count":len(l0),
  "declared_authority_context":declared_context,
  "required_p095_context":required_context,
  "context_binding_must_be_human_governed":not context_explicit,
  "adoption_performed":False,"authority_activated":False,"package_materialized":False,
  "execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
  "functional_conclusion_only":True,"phenomenology_undetermined":True,
  "source_hashes":{"decisions":_sha(r/DEC_REL),"p106_dossiers":_sha(r/DOS_REL),"authority_declaration":_sha(r/DECL_REL)}}

def materialize(root=None):
 r=_root(root); x=audit(r); p=r/REPORT_REL; p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 return x
