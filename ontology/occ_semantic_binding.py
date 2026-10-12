from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib, json
from ontology import ccad_specification as ccad
from ontology import occ_atomic_ordinary_norm_adoption_transaction as atomic

PRIMITIVE="occ_semantic_binding"
VERSION="P159-OCC1A-canonical-semantic-binding-v2"
STATUS="EXPLICIT_48_DISPOSITION_COMPLETE_PACKAGE_NOT_POPULATED"
DIRECT="DIRECT_EXPLICIT_SOURCE_BINDING"
GOVERNED_ADOPTED="GOVERNED_ADOPTED_SEMANTIC_BINDING"
PROTECTED_CONSTITUTIVE="PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION"
HUMAN_REQUIRED="HUMAN_JUDGMENT_REQUIRED"
TARGETS=("GENESIS.G0",)+tuple(f"DNA.H{i}" for i in range(1,10))+tuple(f"DNA.L0.{i}" for i in range(1,7))+tuple(f"DNA.L1.{i}" for i in range(1,9))+tuple(f"CCAD.P{i}" for i in range(14))+tuple(f"CCAD.AR{i}" for i in range(1,11))
PROPOSALS=Path("oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json")
LEDGER=atomic.LEDGER_REL
P155="validation/evidence/p155_constitutional_architecture_v2/p155_historical_dna_semantic_binding_v2.json"
P156="ontology/ccad_specification.py"
GENESIS_SOURCE="validation/evidence/p155_constitutional_architecture_v2/p155_constitutional_architecture_v2.json"

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def _ledger_state(root):
    p=root/LEDGER
    try: v=atomic.verify_ledger(p)
    except Exception as e: return {"valid":False,"reason":"LEDGER_VERIFY_EXCEPTION:"+type(e).__name__}
    return v

def binding_table(root=None):
    r=_root(root)
    proposals=_load(r/PROPOSALS).get("proposals",{})
    ledger=_ledger_state(r)
    committed=set()
    if ledger.get("valid") is True and ledger.get("status")=="COMMITTED_VALID":
        x=_load(r/LEDGER)
        committed={e.get("canonical_id") for e in x.get("transaction",{}).get("events",[]) if e.get("state")=="ADOPTED"}
    out={}
    out["GENESIS.G0"]={
      "canonical_id":"GENESIS.G0","level":"GENESIS","binding_status":HUMAN_REQUIRED,
      "source_object_id":"P155_GENESIS_CONCEPTUAL_SOURCE","source_path":GENESIS_SOURCE,
      "text":None,"formalization":"F0_HUMAN_INTERPRETIVE","executable_semantics":None,
      "runtime_authority_granted":False,"ordinary_adoption_applicable":False,
      "reason":"Conceptual Genesis source is present, but exact machine serialization is intentionally not inferred; governed human review remains required."}
    for cid in TARGETS[1:24]:
        p=proposals.get(cid)
        if not isinstance(p,dict):
            out[cid]={"canonical_id":cid,"level":"DNA_L0" if cid.startswith("DNA.L0") else "DNA_H" if cid.startswith("DNA.H") else "DNA_L1",
              "binding_status":"UNRESOLVED_MISSING_GOVERNED_PROPOSAL","source_object_id":None,"source_path":str(PROPOSALS),
              "text":None,"formalization":"F0_HUMAN_INTERPRETIVE","executable_semantics":None,
              "runtime_authority_granted":False,"reason":"Governed numbered proposal missing."}
            continue
        evid=tuple(p.get("evidence_ids") or ())
        base={"canonical_id":cid,"level":"DNA_L0" if cid.startswith("DNA.L0") else "DNA_H" if cid.startswith("DNA.H") else "DNA_L1",
          "source_object_id":"+".join(evid) if evid else None,"source_path":str(PROPOSALS),
          "historical_source_path":P155,"text":p.get("candidate_definition"),"formalization":"F1_STRUCTURED",
          "executable_semantics":None,"runtime_authority_granted":False,"proposal_hash":p.get("proposal_hash"),
          "evidence_ids":evid}
        if cid.startswith("DNA.L0"):
            base.update({"binding_status":PROTECTED_CONSTITUTIVE,"ordinary_adoption_applicable":False,
              "governance_route":p.get("governance_route"),
              "reason":"Explicit governed semantic mapping is retained as protected constitutive provenance. Ordinary adoption is forbidden; refounding/fork is required only for an actual L0 change, not for preserving the inherited binding."})
        else:
            ok=cid in committed
            base.update({"binding_status":GOVERNED_ADOPTED if ok else "UNRESOLVED_ADOPTION_NOT_COMMITTED",
              "ordinary_adoption_applicable":True,"adoption_evidence_path":str(LEDGER),
              "reason":"Semantic mapping is backed by governed proposal and committed ordinary adoption." if ok else "Governed proposal exists but committed adoption evidence is absent."})
        out[cid]=base
    for sid,text in ccad.PRINCIPLES.items():
        cid="CCAD."+sid
        out[cid]={"canonical_id":cid,"binding_status":DIRECT,"source_object_id":sid,"source_path":P156,"level":"CCAD",
          "text":text,"formalization":"F1_STRUCTURED","executable_semantics":None,"runtime_authority_granted":False,
          "ordinary_adoption_applicable":False,"reason":"P156 exposes the same numbered principle explicitly."}
    for sid,text in ccad.ARBITRATION_RULES.items():
        cid="CCAD.AR"+sid.split("-",1)[1]
        out[cid]={"canonical_id":cid,"binding_status":DIRECT,"source_object_id":sid,"source_path":P156,"level":"CCAD",
          "text":text,"formalization":"F1_STRUCTURED","executable_semantics":None,"runtime_authority_granted":False,
          "ordinary_adoption_applicable":False,"reason":"P156 exposes the same numbered arbitration rule explicitly."}
    return tuple(deepcopy(out[x]) for x in TARGETS)

def manifest(root=None):
    rows=binding_table(root)
    explicit={DIRECT,GOVERNED_ADOPTED,PROTECTED_CONSTITUTIVE,HUMAN_REQUIRED}
    unresolved=[x["canonical_id"] for x in rows if x["binding_status"] not in explicit]
    h9=next(x for x in rows if x["canonical_id"]=="DNA.H9")
    return {"primitive":PRIMITIVE,"version":VERSION,"status":STATUS,"target_count":48,
      "explicit_disposition_count":48-len(unresolved),"unresolved_ids":unresolved,
      "direct_ccad_bindings":sum(x["binding_status"]==DIRECT for x in rows),
      "governed_adopted_dna_bindings":sum(x["binding_status"]==GOVERNED_ADOPTED for x in rows),
      "protected_constitutive_l0_bindings":sum(x["binding_status"]==PROTECTED_CONSTITUTIVE for x in rows),
      "human_judgment_required_bindings":sum(x["binding_status"]==HUMAN_REQUIRED for x in rows),
      "invented_bindings":0,"bindings":rows,
      "h9_f12_f17_distinct":tuple(h9.get("evidence_ids") or ())==("F12","F17"),
      "f18_bound_to_h9": "F18" in tuple(h9.get("evidence_ids") or ()),
      "semantic_disposition_complete":not unresolved,
      "package_population_performed":False,"source_lineage_resolved":False,"package_state_changed":False,
      "authority_activated":False,"execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
