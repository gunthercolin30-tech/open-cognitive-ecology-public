from pathlib import Path
from hashlib import sha256
import json
from ontology import occ_human_adoption_decision as d

VERSION="P159-OCC1A-human-decisions-postcampaign-audit-v1"
EXPECTED_DECIDED=17
EXPECTED_L0=6

def _h(b): return sha256(b).hexdigest()

def audit(root):
    root=Path(root)
    proposal_path=root/"oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json"
    decision_path=d.decision_path(root)
    if not proposal_path.is_file(): raise ValueError("PROPOSAL_REGISTRY_MISSING")
    if not decision_path.is_file(): raise ValueError("HUMAN_DECISION_WORKBOOK_MISSING")
    raw_before=decision_path.read_bytes()
    registry,registry_sha=d.load_registry(root)
    workbook=d.load_or_prepare(root)
    rows=workbook.get("rows",[])
    if len(rows)!=23: raise ValueError("DECISION_WORKBOOK_INCOMPLETE")
    decided=[r for r in rows if r.get("decision") is not None]
    l0=[r for r in rows if r.get("layer")=="DNA_L0"]
    ordinary=[r for r in rows if r.get("ordinary_adoption_permitted")]
    blockers=[]
    if len(decided)!=EXPECTED_DECIDED: blockers.append("EXPECTED_17_HUMAN_DECISIONS")
    if len(ordinary)!=17: blockers.append("EXPECTED_17_ORDINARY_TARGETS")
    if len(l0)!=EXPECTED_L0: blockers.append("EXPECTED_6_DNA_L0_TARGETS")
    if any(r.get("decision") is not None for r in l0): blockers.append("DNA_L0_DECISION_PRESENT")
    if any(r.get("decision")!="ADOPT" for r in ordinary): blockers.append("ORDINARY_TARGET_NOT_HUMAN_ADOPT_DECISION")
    if any(not str(r.get("decision_rationale") or "").strip() for r in decided): blockers.append("RATIONALE_MISSING")
    if any(not str(r.get("decider_id") or "").strip() for r in decided): blockers.append("DECIDER_ID_MISSING")
    if any(r.get("decider_role") not in ("principal_investigator","constitutional_authority") for r in decided): blockers.append("DECIDER_ROLE_INVALID")
    if any(not r.get("out_of_band_confirmation") for r in decided): blockers.append("SECONDARY_CONFIRMATION_MISSING")
    # Exact proposal binding is delegated to the already-hardened loader/decision model;
    # also verify all canonical IDs remain represented exactly once.
    ids=[r.get("canonical_id") for r in rows]
    if len(ids)!=len(set(ids)) or len(set(ids))!=23: blockers.append("CANONICAL_ID_SET_INVALID")
    if workbook.get("registry_sha256")!=registry_sha: blockers.append("REGISTRY_SHA_MISMATCH")
    # Audit must be read-only.
    if decision_path.read_bytes()!=raw_before: blockers.append("AUDIT_MUTATED_DECISION_WORKBOOK")
    result={
      "schema":"oce.p159.occ1a.human_decisions_postcampaign_audit.v1",
      "version":VERSION,
      "decision":"POSTCAMPAIGN_AUDIT_OK" if not blockers else "POSTCAMPAIGN_AUDIT_BLOCKED",
      "blockers":blockers,
      "proposal_count":len(registry),
      "row_count":len(rows),
      "human_decision_count":len(decided),
      "ordinary_target_count":len(ordinary),
      "dna_l0_count":len(l0),
      "dna_l0_decision_count":sum(r.get("decision") is not None for r in l0),
      "decision_workbook_sha256":_h(raw_before),
      "proposal_registry_sha256":registry_sha,
      "human_decision_is_normative_adoption":False,
      "adoption_performed":False,
      "activation_performed":False,
      "execution_performed":False,
      "occ1a_closed":False,
      "occ1b_opened":False,
      "p160_opened":False,
      "functional_only":True,
      "phenomenology_undetermined":True,
    }
    return result

def canonical_bytes(obj):
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode("utf-8")
