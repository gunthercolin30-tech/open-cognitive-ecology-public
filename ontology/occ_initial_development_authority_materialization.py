from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from pathlib import Path
from hashlib import sha256
import json, os, tempfile
SCHEMA="oce.p159.occ1a.p095.initial_development_authority_materialization.v1"
REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json")
HOLDER="Colin Gunther"; REGIME="INITIAL_DEVELOPMENT"; ROLE="CONSTITUTIONAL_AUTHORITY"
CONTINUITY="UNTIL_EXPLICIT_GOVERNED_CHANGE"
def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def path(root=None): return _root(root)/REL
def prepare(root=None):
 from ontology.human_reserved_authority_registry import RESERVED_CLASSES
 return {"schema":SCHEMA,"status":"HUMAN_INSTITUTIONAL_CONFIRMATION_REQUIRED","regime":REGIME,
 "holder":HOLDER,"role":ROLE,"scope":list(RESERVED_CLASSES),"continuity":CONTINUITY,
 "authority_id":"OCE-HUMAN-INITIAL-001","mandate":"Initial human authority over all currently enumerated human-reserved functions during development, until explicit governed change.",
 "context":"DEVELOPMENT","provenance":"Initial human constituent/development authority supplied by Colin Gunther for the OCE development phase; bounded by the human-instituted constitutional and governance framework and replaceable only by explicit governed change.","authority_evidence":"Human institutional declaration plus the existing P095 governed authority framework; this record does not itself prove, activate, expand, delegate, or execute authority.","constitution_version":"CURRENT_GOVERNED_CONSTITUTION",
 "governance_version":"CURRENT_GOVERNED_GOVERNANCE","valid_from":0,"valid_until":253402300799,"authenticated":True,
 "human_confirmed":False,"confirmation_phrase":"","root_override_all":False,
 "dna_l0_ordinary_override":False,"artificial_authority_expansion":False,
 "institutional_authority_established":False,"authority_activated":False,
 "adoption_performed":False,"execution_performed":False,"occ1a_closed":False,
 "occ1b_opened":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
def load_or_prepare(root=None):
 p=path(root)
 if not p.exists(): return prepare(root)
 x=json.loads(p.read_text(encoding="utf-8"))
 if x.get("schema")!=SCHEMA: raise ValueError("SCHEMA_MISMATCH")
 return x
def validate(x):
 blockers=[]
 if x.get("holder")!=HOLDER: blockers.append("HOLDER_IMMUTABLE")
 if x.get("regime")!=REGIME: blockers.append("REGIME_IMMUTABLE")
 if x.get("role")!=ROLE: blockers.append("ROLE_IMMUTABLE")
 if x.get("context")!="DEVELOPMENT": blockers.append("DEVELOPMENT_CONTEXT_REQUIRED")
 from ontology.human_reserved_authority_registry import RESERVED_CLASSES
 if tuple(x.get("scope",()))!=tuple(RESERVED_CLASSES): blockers.append("EXACT_CURRENT_RESERVED_SCOPE_REQUIRED")
 if x.get("root_override_all") is not False: blockers.append("ROOT_OVERRIDE_ALL_FORBIDDEN")
 if x.get("dna_l0_ordinary_override") is not False: blockers.append("DNA_L0_ORDINARY_OVERRIDE_FORBIDDEN")
 if x.get("artificial_authority_expansion") is not False: blockers.append("ARTIFICIAL_AUTHORITY_EXPANSION_FORBIDDEN")
 for k in ("authority_id","mandate","provenance","authority_evidence","constitution_version","governance_version"):
  if not str(x.get(k) or "").strip(): blockers.append(k.upper()+"_REQUIRED")
 vf,vu=x.get("valid_from"),x.get("valid_until")
 if not isinstance(vf,int) or not isinstance(vu,int) or vu<=vf: blockers.append("VALID_MANDATE_WINDOW_REQUIRED")
 if x.get("authenticated") is not True: blockers.append("AUTHENTICATION_CONFIRMATION_REQUIRED")
 if x.get("human_confirmed") is not True: blockers.append("HUMAN_CONFIRMATION_REQUIRED")
 if x.get("confirmation_phrase")!="CONFIRM INITIAL DEVELOPMENT HUMAN AUTHORITY": blockers.append("EXACT_CONFIRMATION_PHRASE_REQUIRED")
 return {"status":"READY_FOR_INDEPENDENT_VERIFICATION" if not blockers else "HUMAN_INSTITUTIONAL_CONFIRMATION_REQUIRED","blockers":blockers}
def save_human_inputs(x,root=None,filesystem_effect_context=None):
 v=validate(x); y=dict(x); y["status"]=v["status"]
 for k in ("institutional_authority_established","authority_activated","adoption_performed","execution_performed","occ1a_closed","occ1b_opened","p160_opened"): y[k]=False
 p=path(root)
 raw=(json.dumps(y,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
 if filesystem_effect_context is None: raise RuntimeError("governed_filesystem_effect_context_required")
 filesystem_effect_context.execute_path("human_inputs_parent_create","FS_CREATE_DIRS",p.parent)
 filesystem_effect_context.execute_path("human_inputs_write_replace","FS_WRITE_REPLACE_BYTES",p,raw)
 return dict(v,sha256=sha256(raw).hexdigest(),institutional_authority_established=False,authority_activated=False)
def manifest():
 return {"schema":SCHEMA,"human_input_only":True,"calls_p095":False,"calls_p106":False,"calls_p104":False,
 "creates_authority":False,"activates_authority":False,"root_override_all":False,
 "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
