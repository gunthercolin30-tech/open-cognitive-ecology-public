from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from pathlib import Path
from hashlib import sha256
import json, os, tempfile

SCHEMA="oce.p159.occ1a.institutional_authority_amendment_dossier.v1"
REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_institutional_authority_amendment_dossier.json")
DEC_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_human_adoption_decisions.json")
ORDINARY_LAYERS={"DNA_H","DNA_L1"}
P106_FIELDS=("incompatibility_analysis","rights_impact","adversarial_review",
             "long_form_human_governance","fork_or_migration_decision","provenance")

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _canon(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def _hash(x): return sha256(_canon(x).encode()).hexdigest()
def path(root=None): return _root(root)/REL

def prepare(root=None):
 r=_root(root); d=json.loads((r/DEC_REL).read_text(encoding="utf-8"))
 rows=[]
 for x in d["rows"]:
  if x.get("decision")=="ADOPT" and x.get("layer") in ORDINARY_LAYERS:
   rows.append({"canonical_id":x["canonical_id"],"candidate_definition":x["candidate_definition"],
    "proposal_hash":x["proposal_hash"],"dossier_hash":x["dossier_hash"],
    "evidence_ids":x["evidence_ids"],"human_decision_rationale":x["decision_rationale"],
    "p106":{"proposal":x["candidate_definition"],"rationale":x["decision_rationale"],
            **{k:"" for k in P106_FIELDS}},
    "dossier_human_confirmed":False})
 if len(rows)!=17: raise ValueError("EXPECTED_17_HUMAN_ADOPT_DECISIONS")
 return {"schema":SCHEMA,"status":"INSTITUTIONAL_INPUT_REQUIRED",
  "source_decision_sha256":sha256((r/DEC_REL).read_bytes()).hexdigest(),
  "authority":{"authority_id":"","human_identity":"","authenticated":False,"role":"constitutional_authority",
   "mandate":"","scope":["CONSTITUTIONAL_CHANGE"],"contexts":["P159_OCC1A"],
   "valid_from":None,"valid_until":None,"constitution_version":"","governance_version":"",
   "authority_human_confirmed":False},
  "independent_domains":[],"authority_provenance":"","authority_evidence":"",
  "dossiers":rows,"institutional_authority_established":False,
  "p106_admissibility_established":False,"adoption_performed":False,
  "activation_performed":False,"execution_performed":False,
  "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
  "functional_only":True,"phenomenology_undetermined":True}

def load_or_prepare(root=None):
 p=path(root)
 if not p.exists(): return prepare(root)
 w=json.loads(p.read_text(encoding="utf-8"))
 if w.get("schema")!=SCHEMA: raise ValueError("SCHEMA_MISMATCH")
 current=prepare(root)
 if w.get("source_decision_sha256")!=current["source_decision_sha256"]: raise ValueError("SOURCE_DECISION_DRIFT")
 return w

def validate(w):
 blockers=[]
 a=w.get("authority",{})
 required=("authority_id","human_identity","mandate","constitution_version","governance_version")
 for k in required:
  if not str(a.get(k) or "").strip(): blockers.append("AUTHORITY_"+k.upper()+"_REQUIRED")
 if a.get("role")!="constitutional_authority": blockers.append("CONSTITUTIONAL_AUTHORITY_ROLE_REQUIRED")
 if "CONSTITUTIONAL_CHANGE" not in a.get("scope",[]): blockers.append("CONSTITUTIONAL_CHANGE_SCOPE_REQUIRED")
 if "P159_OCC1A" not in a.get("contexts",[]): blockers.append("P159_OCC1A_CONTEXT_REQUIRED")
 if a.get("authenticated") is not True: blockers.append("AUTHENTICATION_ASSERTION_REQUIRED")
 if a.get("authority_human_confirmed") is not True: blockers.append("AUTHORITY_HUMAN_CONFIRMATION_REQUIRED")
 vf,vu=a.get("valid_from"),a.get("valid_until")
 if not isinstance(vf,int) or not isinstance(vu,int) or vu<=vf: blockers.append("VALID_MANDATE_WINDOW_REQUIRED")
 if not str(w.get("authority_provenance") or "").strip(): blockers.append("AUTHORITY_PROVENANCE_REQUIRED")
 if not str(w.get("authority_evidence") or "").strip(): blockers.append("AUTHORITY_EVIDENCE_REQUIRED")
 if not w.get("independent_domains"): blockers.append("INDEPENDENCE_DOMAIN_REQUIRED")
 # Optional governed quorum evidence, enforced only when explicitly declared.
 rq=a.get("required_quorum")
 if rq is not None:
  if not isinstance(rq,int) or isinstance(rq,bool) or rq < 1:
   blockers.append("VALID_REQUIRED_QUORUM_REQUIRED")
  else:
   approvals=w.get("authority_approvals")
   if not isinstance(approvals,list):
    blockers.append("AUTHORITY_APPROVALS_REQUIRED")
   else:
    usable=[x for x in approvals if isinstance(x,dict) and x.get("authenticated") is True and str(x.get("human_identity") or "").strip()]
    identities={str(x["human_identity"]).strip() for x in usable}
    if len(identities) < rq: blockers.append("MULTI_PARTY_QUORUM_EVIDENCE_REQUIRED")
 ds=w.get("dossiers",[])
 if len(ds)!=17: blockers.append("EXPECTED_17_DOSSIERS")
 for row in ds:
  p=row.get("p106",{})
  for k in ("proposal","rationale")+P106_FIELDS:
   if not str(p.get(k) or "").strip(): blockers.append(row.get("canonical_id","?")+":"+k.upper()+"_REQUIRED")
  if row.get("dossier_human_confirmed") is not True:
   blockers.append(row.get("canonical_id","?")+":HUMAN_CONFIRMATION_REQUIRED")
 return {"status":"READY_FOR_GOVERNED_EVALUATION" if not blockers else "INSTITUTIONAL_INPUT_REQUIRED",
         "blockers":blockers,"authority_record_ready":not any(x.startswith("AUTHORITY_") or x in ("AUTHENTICATION_ASSERTION_REQUIRED","CONSTITUTIONAL_AUTHORITY_ROLE_REQUIRED","CONSTITUTIONAL_CHANGE_SCOPE_REQUIRED","P159_OCC1A_CONTEXT_REQUIRED","VALID_MANDATE_WINDOW_REQUIRED","INDEPENDENCE_DOMAIN_REQUIRED") for x in blockers),
         "p106_dossiers_ready":not any(":" in x for x in blockers),
         "adoption_performed":False,"activation_performed":False,"execution_performed":False}

def save_human_inputs(w,root=None,filesystem_effect_context=None):
 # Persist declarations only; never call P095/P106/P104 here.
 v=validate(w); w=dict(w); w["status"]=v["status"]
 w["institutional_authority_established"]=False
 w["p106_admissibility_established"]=False
 for k in ("adoption_performed","activation_performed","execution_performed","occ1a_closed","occ1b_opened","p160_opened"): w[k]=False
 p=path(root)
 data=(json.dumps(w,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
 if filesystem_effect_context is None: raise RuntimeError("governed_filesystem_effect_context_required")
 filesystem_effect_context.execute_path("human_inputs_parent_create","FS_CREATE_DIRS",p.parent)
 filesystem_effect_context.execute_path("human_inputs_write_replace","FS_WRITE_REPLACE_BYTES",p,data)
 return v

def manifest():
 return {"schema":SCHEMA,"human_input_only":True,"calls_p095":False,"calls_p106":False,"calls_p104":False,
 "creates_authority":False,"creates_adoption":False,"real_execution_enabled":False,
 "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
 "functional_only":True,"phenomenology_undetermined":True}
