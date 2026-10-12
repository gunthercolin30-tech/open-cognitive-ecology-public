from __future__ import annotations
from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, Sequence
from ontology import constitutional_amendment_protocol as p106
from ontology import constitutional_decision_ledger as p104
from ontology import human_reserved_authority_registry as p095

PRIMITIVE="occ_norm_adoption_event"
VERSION="P159-OCC1A-governed-adoption-hardening-v4"
STATUS="GOVERNED_ADOPTION_HARDENED_NOT_ADOPTED"
DNA_TARGETS=tuple([f"DNA.H{i}" for i in range(1,10)]+[f"DNA.L0.{i}" for i in range(1,7)]+[f"DNA.L1.{i}" for i in range(1,9)])
REG_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json")

def _canon(v:Any)->str:
 return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(v:Any)->str:
 return sha256(_canon(v).encode("utf-8")).hexdigest()
def _root(root=None)->Path:
 return Path(root) if root is not None else Path.home()/"open-cognitive-ecology"

def prepare_workbook(bindings):
 rows=[{"canonical_id":c,"historical_id":None,"candidate_definition":None,"state":"DRAFT","human_governance_required":True,"machine_assignment_normative":False,"authority_event":None,"runtime_authority_granted":False,"execution_performed":False} for c in DNA_TARGETS]
 return {"schema":"oce.p159.occ1a.governed_adoption_workbook.v1","status":STATUS,"genesis":{"canonical_id":"GENESIS.G0","state":"DRAFT","resolution":"CONCEPTUAL_SOURCE_PRESENT_SERIALIZATION_REQUIRES_GOVERNED_REVIEW","pdf_extraction_must_not_define_machine_semantics":True},"historical_sources":[{"historical_id":k,"definition":bindings[k].get("definition"),"canonical_targets":bindings[k].get("canonical_targets",[])} for k in sorted(bindings,key=lambda x:int(x[1:]))],"dna_rows":rows,"automatic_assignment_permitted":False,"automatic_adoption_permitted":False,"automatic_activation_permitted":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def load_registered_proposal(canonical_id:str,root=None)->dict[str,Any]:
 if canonical_id not in DNA_TARGETS:return {"accepted":False,"reason":"UNKNOWN_DNA_TARGET"}
 p=_root(root)/REG_REL
 if not p.is_file():return {"accepted":False,"reason":"NUMBERED_PROPOSAL_REGISTRY_MISSING"}
 reg=json.loads(p.read_text(encoding="utf-8"))
 if reg.get("proposal_count")!=23:return {"accepted":False,"reason":"NUMBERED_PROPOSAL_REGISTRY_INCOMPLETE"}
 row=(reg.get("proposals") or {}).get(canonical_id)
 if not isinstance(row,dict):return {"accepted":False,"reason":"REGISTERED_PROPOSAL_MISSING"}
 if row.get("status")!="PROPOSED_NOT_ADOPTED":return {"accepted":False,"reason":"REGISTERED_PROPOSAL_NOT_PROPOSABLE"}
 if any(row.get(k) is not False for k in ("binding_created","adoption_performed","activation_performed","execution_performed")):
  return {"accepted":False,"reason":"REGISTERED_PROPOSAL_STAGE_CONFLATION"}
 required=("proposal_hash","dossier_hash","evidence_snapshot_hash","candidate_definition","proposal_rationale","evidence_ids")
 if any(not row.get(k) for k in required):return {"accepted":False,"reason":"REGISTERED_PROPOSAL_PROVENANCE_INCOMPLETE"}
 return {"accepted":True,"proposal":deepcopy(row),"registry_sha256":sha256(p.read_bytes()).hexdigest()}


def verify_registered_proposal(record:Mapping[str,Any],root=None)->dict[str,Any]:
 if not isinstance(record,Mapping):
  return {"accepted":False,"reason":"REGISTERED_PROPOSAL_RECORD_REQUIRED"}
 cid=record.get("canonical_id")
 got=load_registered_proposal(str(cid),root)
 if not got.get("accepted"):
  return got
 p=got["proposal"]
 for k in ("proposal_hash","dossier_hash","evidence_snapshot_hash",
           "candidate_definition","proposal_rationale","evidence_ids"):
  if record.get(k)!=p.get(k):
   return {"accepted":False,"reason":"REGISTERED_PROPOSAL_RECORD_DRIFT","field":k}
 seal_payload={"canonical_id":cid,"proposal_hash":p["proposal_hash"],
  "dossier_hash":p["dossier_hash"],"evidence_snapshot_hash":p["evidence_snapshot_hash"],
  "candidate_definition":p["candidate_definition"],"evidence_ids":list(p["evidence_ids"]),
  "proposal_rationale":p["proposal_rationale"],"registry_sha256":got["registry_sha256"]}
 expected=_hash(seal_payload)
 if record.get("registry_sha256")!=got["registry_sha256"]:
  return {"accepted":False,"reason":"REGISTERED_PROPOSAL_REGISTRY_DRIFT"}
 if record.get("registered_proposal_seal")!=expected:
  return {"accepted":False,"reason":"REGISTERED_PROPOSAL_SEAL_MISMATCH"}
 return {"accepted":True,"proposal":deepcopy(p),"registered_proposal_seal":expected,
         "registry_sha256":got["registry_sha256"]}

def propose_binding(record,historical_id,definition,rationale):
 # Legacy preparation API retained, but it can never establish normative binding.
 r=deepcopy(record)
 if r.get("canonical_id") not in DNA_TARGETS:return {"accepted":False,"reason":"UNKNOWN_DNA_TARGET"}
 if not historical_id or not definition or not rationale:return {"accepted":False,"reason":"SOURCE_DEFINITION_RATIONALE_REQUIRED"}
 r.update({"historical_id":historical_id,"candidate_definition":definition,"candidate_rationale":rationale,"state":"PROPOSED"})
 return {"accepted":True,"record":r,"normative_binding_created":False}

def bind_registered_proposal(canonical_id:str,*,proposal_hash:str,dossier_hash:str,evidence_snapshot_hash:str,
 candidate_definition:str,evidence_ids:Sequence[str],root=None)->dict[str,Any]:
 got=load_registered_proposal(canonical_id,root)
 if not got.get("accepted"):return got
 p=got["proposal"]
 exact={"proposal_hash":proposal_hash,"dossier_hash":dossier_hash,"evidence_snapshot_hash":evidence_snapshot_hash,
        "candidate_definition":candidate_definition,"evidence_ids":list(evidence_ids)}
 for k,v in exact.items():
  if p.get(k)!=v:return {"accepted":False,"reason":"REGISTERED_PROPOSAL_EXACT_BINDING_MISMATCH","field":k}
 seal_payload={"canonical_id":canonical_id,**exact,"proposal_rationale":p["proposal_rationale"],
               "registry_sha256":got["registry_sha256"]}
 seal=_hash(seal_payload)
 record=deepcopy(p)
 record.update({"state":"PROPOSED","registered_proposal_seal":seal,
                "registry_sha256":got["registry_sha256"],"normative_binding_created":False})
 return {"accepted":True,"record":record,"registered_proposal_seal":seal,"normative_binding_created":False}

def _layer(canonical_id:str)->str:
 return "DNA-L0" if canonical_id.startswith("DNA.L0.") else ("DNA-H" if canonical_id.startswith("DNA.H") else "DNA-L1")

def build_action_manifest(record:Mapping[str,Any],*,nonce:str,created_at:int)->p095.ActionManifest:
 seal=record.get("registered_proposal_seal")
 if not seal:raise ValueError("REGISTERED_PROPOSAL_SEAL_REQUIRED")
 return p095.ActionManifest(
  action_id="OCC1A:"+str(record["canonical_id"])+":"+str(record["proposal_hash"]),
  action_class="CONSTITUTIONAL_CHANGE",object_id=str(record["canonical_id"]),
  context="P159_OCC1A_NORM_ADOPTION",constitutional_layer=_layer(str(record["canonical_id"])),
  irreversible=False,high_impact=True,
  risk_summary="Normative adoption proposal; does not activate or execute runtime authority.",
  material_objections=("Norm adoption requires independent review; proposal is not legitimacy.",),
  evidence_sources=(str(record["dossier_hash"]),str(record["evidence_snapshot_hash"])),
  nonce=nonce,created_at=int(created_at))

def _precheck_authority_scope(registry,authority_ids,manifest,now):
 store=getattr(registry,"authorities",None)
 if not isinstance(store,Mapping): return {"accepted":False,"reason":"P095_AUTHORITY_STORE_UNAVAILABLE"}
 for aid in authority_ids:
  a=store.get(aid)
  if a is None: return {"accepted":False,"reason":"P095_AUTHORITY_UNKNOWN"}
  if manifest.action_class not in tuple(getattr(a,"scope",()) or ()): return {"accepted":False,"reason":"P095_ACTION_CLASS_SCOPE_MISMATCH"}
  if manifest.context not in tuple(getattr(a,"contexts",()) or ()): return {"accepted":False,"reason":"P095_CONTEXT_SCOPE_MISMATCH"}
  vf=getattr(a,"valid_from",None); vt=getattr(a,"valid_until",None)
  if vf is not None and now < vf: return {"accepted":False,"reason":"P095_AUTHORITY_NOT_YET_VALID"}
  if vt is not None and now > vt: return {"accepted":False,"reason":"P095_AUTHORITY_EXPIRED"}
 return {"accepted":True}

def authorize_registered_proposal(record:Mapping[str,Any],registry:p095.P095Canonical,*,
 authority_ids:Sequence[str],independent_domains:Sequence[str],now:int,nonce:str,
 rationale:str,explicit_confirmation:bool,out_of_band:bool,
 conflict_of_interest_disclosed:bool=True)->dict[str,Any]:
 verified=verify_registered_proposal(record)
 if not verified.get("accepted"):
  return {"status":p095.UNDETERMINED,"reason":verified.get("reason","REGISTERED_PROPOSAL_VERIFICATION_FAILED"),"authority_proof_valid":False}
 manifest=build_action_manifest(record,nonce=nonce,created_at=now)
 scope_check=_precheck_authority_scope(registry,authority_ids,manifest,now)
 if not scope_check.get("accepted"):
  return {"status":p095.FAIL,"reason":scope_check["reason"],"authority_proof_valid":False,"registered_proposal_seal":record["registered_proposal_seal"]}
 raw=registry.authorize(manifest,authority_ids,independent_domains,now,rationale,explicit_confirmation,
                        out_of_band=out_of_band,emergency=False,
                        conflict_of_interest_disclosed=conflict_of_interest_disclosed)
 if raw.get("status")!=p095.PASS:
  return {**raw,"authority_proof_valid":False,"registered_proposal_seal":record["registered_proposal_seal"]}
 proof_payload={"proposal_seal":record["registered_proposal_seal"],"manifest":asdict(manifest),
                "authority_ids":list(raw.get("authority_ids",())),"status":raw["status"],"reason":raw.get("reason")}
 return {**raw,"authority_proof_valid":True,"registered_proposal_seal":record["registered_proposal_seal"],
         "action_manifest":asdict(manifest),"authority_proof_hash":_hash(proof_payload)}

def amendment_gate(record,evidence,proposer="HUMAN"):
 # Compatibility API. Hardened decision construction will reject this unsealed result.
 if record.get("state")!="PROPOSED":return {"accepted":False,"reason":"PROPOSAL_REQUIRED"}
 x=p106.evaluate_amendment(route=p106.DNA,target_layer=p106.DNA,proposer=proposer,evidence=evidence)
 return {"accepted":x.status=="ADMISSIBLE_FOR_DECISION","p106_status":x.status,"next_action":x.next_action,"missing_evidence":list(x.missing_evidence),"authority_granted":False,"execution_performed":False}

def evaluate_registered_amendment(record:Mapping[str,Any],evidence:Mapping[str,Any],proposer="HUMAN")->dict[str,Any]:
 verified=verify_registered_proposal(record)
 if not verified.get("accepted"):
  return {"accepted":False,"reason":verified.get("reason","REGISTERED_PROPOSAL_VERIFICATION_FAILED")}
 seal=verified["registered_proposal_seal"]
 # Evidence is bound to the exact canonically re-verified proposal.
 bound=dict(evidence)
 if bound.get("proposal_hash")!=record.get("proposal_hash"):return {"accepted":False,"reason":"P106_PROPOSAL_HASH_MISMATCH"}
 if bound.get("registered_proposal_seal")!=seal:return {"accepted":False,"reason":"P106_PROPOSAL_SEAL_MISMATCH"}
 if _layer(str(record["canonical_id"]))=="DNA-L0":
  return {"accepted":False,"reason":"REFOUNDING_OR_FORK_REQUIRED","p106_status":"ROUTE_BLOCKED_FOR_ORDINARY_ADOPTION",
          "authority_granted":False,"execution_performed":False,"registered_proposal_seal":seal}
 x=p106.evaluate_amendment(route=p106.DNA,target_layer=p106.DNA,proposer=proposer,evidence=bound)
 payload={"proposal_seal":seal,"proposal_hash":record["proposal_hash"],"evidence":bound,
          "status":x.status,"next_action":x.next_action,"missing_evidence":list(x.missing_evidence)}
 return {"accepted":x.status=="ADMISSIBLE_FOR_DECISION","p106_status":x.status,"next_action":x.next_action,
         "missing_evidence":list(x.missing_evidence),"authority_granted":False,"execution_performed":False,
         "registered_proposal_seal":seal,"amendment_proof_hash":_hash(payload)}

def _build_adoption_decision_verified(record,authority_result,amendment_result,decision_id,decision_time):
 if record.get("state")!="PROPOSED":return {"status":"UNDETERMINED","reason":"PROPOSAL_REQUIRED"}
 verified=verify_registered_proposal(record)
 if not verified.get("accepted"):return {"status":"UNDETERMINED","reason":verified.get("reason","REGISTERED_PROPOSAL_VERIFICATION_FAILED")}
 seal=verified["registered_proposal_seal"]
 if authority_result.get("status")!=p095.PASS or authority_result.get("authority_proof_valid") is not True:return {"status":"UNDETERMINED","reason":"P095_AUTHORITY_NOT_PROVEN"}
 if authority_result.get("registered_proposal_seal")!=seal or not authority_result.get("authority_proof_hash"):return {"status":"UNDETERMINED","reason":"P095_PROPOSAL_BINDING_MISMATCH"}
 if not amendment_result.get("accepted") or amendment_result.get("p106_status")!="ADMISSIBLE_FOR_DECISION":return {"status":"UNDETERMINED","reason":"P106_AMENDMENT_NOT_ADMISSIBLE"}
 if amendment_result.get("registered_proposal_seal")!=seal or not amendment_result.get("amendment_proof_hash"):return {"status":"UNDETERMINED","reason":"P106_PROPOSAL_BINDING_MISMATCH"}
 if _layer(str(record["canonical_id"]))=="DNA-L0":return {"status":"UNDETERMINED","reason":"REFOUNDING_OR_FORK_REQUIRED"}
 payload={"decision_id":decision_id,"problem_id":"OCC1A:"+record["canonical_id"],"decision_type":"NORM_ADOPTION",
 "recommendations_considered":list(record.get("evidence_ids",[])),"decision_authority":authority_result,
 "authorization":"P095_VALIDATED_AND_PROPOSAL_BOUND","applicable_DNA":[record["canonical_id"]],
 "applicable_constitution":["P159_OCC1A"],"applicable_governance":["P095","P106"],
 "evidence":{"proposal_hash":record["proposal_hash"],"dossier_hash":record["dossier_hash"],"evidence_snapshot_hash":record["evidence_snapshot_hash"],"registered_proposal_seal":seal,"definition":record["candidate_definition"],"authority_proof_hash":authority_result["authority_proof_hash"],"amendment_proof_hash":amendment_result["amendment_proof_hash"]},
 "uncertainty":"HUMAN_GOVERNED_ADOPTION_NOT_RUNTIME_ACTIVATION","affected_entities":["OCE_NORMATIVE_SOURCE_PACKAGE"],
 "result":"ADOPTION_DECISION_ELIGIBLE","challenge_status":"OPEN","appeal_status":"OPEN","decision_time":decision_time,
 "normative_status":"PASS","authority_expanded":False,"stage_conflation":False,
 "provenance":{"adapter":PRIMITIVE,"source_state":"PROPOSED","proposal_seal":seal}}
 return p104.build_record(payload)

def build_adoption_decision(record,authority_result,amendment_result,decision_id,decision_time):
 return {"status":"UNDETERMINED","reason":"CALLER_SUPPLIED_PROOFS_NOT_AUTHORITATIVE","persisted":False,"authority_granted":False,"execution_performed":False}

def build_adoption_decision_from_authoritative_inputs(record,registry,*,authority_ids,independent_domains,now,nonce,rationale,explicit_confirmation,out_of_band,amendment_evidence,decision_id,decision_time,proposer="HUMAN",conflict_of_interest_disclosed=True):
 verified=verify_registered_proposal(record)
 if not verified.get("accepted"):return {"status":"UNDETERMINED","reason":verified.get("reason","REGISTERED_PROPOSAL_VERIFICATION_FAILED")}
 if _layer(str(record["canonical_id"]))=="DNA-L0":return {"status":"UNDETERMINED","reason":"REFOUNDING_OR_FORK_REQUIRED"}
 authority_result=authorize_registered_proposal(record,registry,authority_ids=authority_ids,independent_domains=independent_domains,now=now,nonce=nonce,rationale=rationale,explicit_confirmation=explicit_confirmation,out_of_band=out_of_band,conflict_of_interest_disclosed=conflict_of_interest_disclosed)
 if authority_result.get("status")!=p095.PASS:return {"status":"UNDETERMINED","reason":"P095_AUTHORITY_NOT_PROVEN","p095_reason":authority_result.get("reason"),"persisted":False}
 verified2=verify_registered_proposal(record)
 if not verified2.get("accepted"):return {"status":"UNDETERMINED","reason":verified2.get("reason","REGISTERED_PROPOSAL_VERIFICATION_FAILED")}
 amendment_result=evaluate_registered_amendment(record,amendment_evidence,proposer=proposer)
 if not amendment_result.get("accepted"):return {"status":"UNDETERMINED","reason":"P106_AMENDMENT_NOT_ADMISSIBLE","p106_reason":amendment_result.get("reason"),"persisted":False}
 verified3=verify_registered_proposal(record)
 if not verified3.get("accepted"):return {"status":"UNDETERMINED","reason":verified3.get("reason","REGISTERED_PROPOSAL_VERIFICATION_FAILED")}
 return _build_adoption_decision_verified(record,authority_result,amendment_result,decision_id,decision_time)

def manifest():
 return {"primitive":PRIMITIVE,"version":VERSION,"status":STATUS,
 "reuse":{"P095":"human_reserved_authority_registry","P104":"constitutional_decision_ledger","P106":"constitutional_amendment_protocol"},
 "dna_target_count":23,"genesis_separate":True,"registered_proposal_exact_binding_required":True,"canonical_reverification_before_p095_p106_p104":True,"occ_exact_authority_scope_precheck":True,
 "caller_supplied_unsealed_p095_rejected":True,"caller_supplied_unsealed_p106_rejected":True,"caller_supplied_proof_objects_cannot_create_eligibility":True,"authoritative_p095_p106_orchestration_required":True,
 "dna_l0_ordinary_adoption_forbidden":True,"machine_assignment_permitted":False,"machine_adoption_permitted":False,
 "machine_activation_permitted":False,"real_execution_enabled":False,"occ1a_closed":False,"occ1b_opened":False,
 "p160_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
