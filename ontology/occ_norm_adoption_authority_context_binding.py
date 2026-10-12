from pathlib import Path
import json, hashlib
SCHEMA="oce.p159.occ1a.norm_adoption_authority_context_binding.v1"
DECL_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json")
BIND_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_norm_adoption_authority_context_binding.json")
REQUIRED_CONTEXT="P159_OCC1A_NORM_ADOPTION"
CONFIRMATION="I explicitly bind P159_OCC1A_NORM_ADOPTION to the existing bounded initial development authority for OCC-1A ordinary normative adoption only; this creates no new authority, no ROOT_OVERRIDE_ALL, no DNA-L0 ordinary override, no delegation, no succession, no activation, and no execution."

def root(r=None): return Path(r) if r else Path.home()/"open-cognitive-ecology"
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def build(root_path=None):
 r=root(root_path); d=load(r/DECL_REL)
 return {
  "schema":SCHEMA,"status":"AWAITING_HUMAN_CONFIRMATION",
  "binding_kind":"EXPLICIT_CONTEXT_BINDING_ONLY",
  "source_authority_declaration_sha256":sha(r/DECL_REL),
  "holder":d.get("holder"),"source_regime":d.get("regime"),
  "source_context":d.get("context"),"additional_context":REQUIRED_CONTEXT,
  "purpose":"OCC-1A ordinary normative adoption only",
  "human_confirmed":False,"human_confirmation_text":None,
  "new_human_holder":False,"new_reserved_function":False,"new_action_class":False,
  "authority_expansion":False,"root_override_all":False,"dna_l0_ordinary_override":False,
  "delegation":False,"succession":False,"authority_activated":False,
  "adoption_performed":False,"package_materialized":False,"execution_performed":False,
  "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
  "required_exact_confirmation":CONFIRMATION,
  "functional_conclusion_only":True,"phenomenology_undetermined":True}

def validate(x, source):
 invariants=("new_human_holder","new_reserved_function","new_action_class","authority_expansion",
 "root_override_all","dna_l0_ordinary_override","delegation","succession","authority_activated",
 "adoption_performed","package_materialized","execution_performed","occ1a_closed","occ1b_opened","p160_opened")
 return (x.get("schema")==SCHEMA and x.get("binding_kind")=="EXPLICIT_CONTEXT_BINDING_ONLY"
  and x.get("additional_context")==REQUIRED_CONTEXT
  and x.get("source_authority_declaration_sha256")==sha(source)
  and all(x.get(k) is False for k in invariants)
  and ((x.get("human_confirmed") is False and x.get("status")=="AWAITING_HUMAN_CONFIRMATION")
    or (x.get("human_confirmed") is True and x.get("status")=="HUMAN_CONFIRMED"
        and x.get("human_confirmation_text")==CONFIRMATION)))

def materialize(root_path=None):
 r=root(root_path); p=r/BIND_REL; p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():
  x=load(p)
  if not validate(x,r/DECL_REL): raise ValueError("INVALID_OR_TAMPERED_EXISTING_CONTEXT_BINDING")
  return x
 x=build(r); p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8"); return x
