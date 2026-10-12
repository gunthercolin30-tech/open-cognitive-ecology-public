from copy import deepcopy
import hashlib
import json
import re

APPLICABILITY_STATES=("APPLICABLE","NON_INSTANTIABLE","APPLICABILITY_UNDETERMINED")
_HEX64=re.compile(r"^[0-9a-f]{64}$")

def _canonical_bytes(value):
 return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def _digest(value):
 return hashlib.sha256(_canonical_bytes(value)).hexdigest()

def default_applicability(current_verdict):
 return "APPLICABILITY_UNDETERMINED" if current_verdict=="INCONCLUSIVE" else "APPLICABLE"

def make_positive_non_instantiability_proof(scenario_id,scenario_payload,normative_state_payload,claim_payload):
 if not isinstance(scenario_id,str) or not scenario_id: raise ValueError("scenario_id required")
 if not isinstance(scenario_payload,dict) or not isinstance(normative_state_payload,dict) or not isinstance(claim_payload,dict):
  raise TypeError("payloads must be dict")
 scenario_sha256=_digest(scenario_payload)
 normative_state_sha256=_digest(normative_state_payload)
 proof_payload={
  "schema":"oce.p159.occ1h.positive_non_instantiability_proof.v2",
  "scenario_id":scenario_id,
  "scenario_sha256":scenario_sha256,
  "normative_state_sha256":normative_state_sha256,
  "claim_payload":deepcopy(claim_payload),
 }
 return {
  "status":"POSITIVE_NON_INSTANTIABILITY_PROOF",
  "scenario_id":scenario_id,
  "scenario_payload":deepcopy(scenario_payload),
  "scenario_sha256":scenario_sha256,
  "normative_state_payload":deepcopy(normative_state_payload),
  "normative_state_sha256":normative_state_sha256,
  "claim_payload":deepcopy(claim_payload),
  "proof_sha256":_digest(proof_payload),
 }

def validate_positive_non_instantiability(evidence):
 if not isinstance(evidence,dict): return False
 if evidence.get("status")!="POSITIVE_NON_INSTANTIABILITY_PROOF": return False
 sid=evidence.get("scenario_id")
 if not isinstance(sid,str) or not sid: return False
 sp=evidence.get("scenario_payload"); np=evidence.get("normative_state_payload"); cp=evidence.get("claim_payload")
 if not isinstance(sp,dict) or not isinstance(np,dict) or not isinstance(cp,dict): return False
 required=("scenario_sha256","normative_state_sha256","proof_sha256")
 if not all(isinstance(evidence.get(k),str) and _HEX64.fullmatch(evidence[k]) for k in required): return False
 if evidence["scenario_sha256"]!=_digest(sp): return False
 if evidence["normative_state_sha256"]!=_digest(np): return False
 proof_payload={
  "schema":"oce.p159.occ1h.positive_non_instantiability_proof.v2",
  "scenario_id":sid,
  "scenario_sha256":evidence["scenario_sha256"],
  "normative_state_sha256":evidence["normative_state_sha256"],
  "claim_payload":cp,
 }
 return evidence["proof_sha256"]==_digest(proof_payload)

def root_inconclusive_blocks(current_verdict,applicability,positive_proof=None):
 if current_verdict!="INCONCLUSIVE": return False
 if applicability=="NON_INSTANTIABLE": return not validate_positive_non_instantiability(positive_proof)
 return True

def contract():
 return deepcopy({
  "schema":"oce.p159.occ1h.applicability_contract.v2",
  "states":list(APPLICABILITY_STATES),
  "orthogonal_to_verdict":True,
  "verdict_enum_modified":False,
  "positive_non_instantiability_proof_required":True,
  "positive_proof_content_addressed":True,
  "scenario_binding_recomputed":True,
  "normative_state_binding_recomputed":True,
  "proof_binding_recomputed":True,
  "absence_of_evidence_cannot_prove_non_instantiable":True,
  "applicability_undetermined_blocks_root_closure":True,
  "applicable_inconclusive_blocks_root_closure":True,
  "historical_verdicts_immutable":True,
  "normative_gap_cannot_be_laundered":True,
  "authorization_created":False,
  "execution_created":False,
 })
