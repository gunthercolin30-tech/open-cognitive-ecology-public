from __future__ import annotations
import hashlib,json
from copy import deepcopy
from typing import Any,Mapping
PRIMITIVE="capability_invocation_request_builder"; VERSION="P162-A-v1.1"
ENVIRONMENTS={"PRODUCTION","SHADOW","SIMULATION","TEST","RECOVERY"}
UNKNOWN={None,"","UNKNOWN","UNRESOLVED","INCONCLUSIVE"}
def canonical_json(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
def canonical_sha256(x): return hashlib.sha256(canonical_json(x).encode()).hexdigest()
def _known(x):
 try:return x not in UNKNOWN
 except TypeError:return x is not None
def _m(x):return x if isinstance(x,Mapping) else {}
def manifest():return {"primitive":PRIMITIVE,"version":VERSION,"laws":["INVOCATION_REQUEST!=AUTHORIZATION","INVOCATION_REQUEST!=CAPABILITY_ACCESS","INVOCATION_REQUEST!=EXECUTION","INVOCATION_SCOPE<=AUTHORIZATION_TOKEN_SCOPE","CALLER_AUTHORIZED!=CALLEE_AUTOMATICALLY_AUTHORIZED","FUNCTIONAL_EQUIVALENCE!=AUTHORIZATION_EQUIVALENCE","TECHNICAL_DEPENDENCY!=AUTHORITY","WORLD_MODEL!=AUTHORITY"],"authorization_created":False,"capability_accessed":False,"execution_performed":False,"functional_only":True,"phenomenology_undetermined":True}
def build_runtime_invocation_context(**k):
 req=("runtime_id","executor_instance_id","host_id","environment","time","capability_registry_version","authorization_registry_version","policy_version","world_state_fingerprint","resource_state_fingerprint","security_state_fingerprint")
 if k.get("environment") not in ENVIRONMENTS or any(not _known(k.get(x)) for x in req):raise ValueError("INVALID_RUNTIME_INVOCATION_CONTEXT")
 x={"schema":"oce.p162a.runtime_invocation_context.v1",**{a:deepcopy(k[a]) for a in req}};x["context_hash"]=canonical_sha256(x);return x
def build_composition_envelope(*,parent_invocation_id,allowed_child_capabilities,allowed_child_operations,allowed_child_targets,allowed_child_purposes,resource_budget,depth,fanout):
 if not _known(parent_invocation_id) or not isinstance(resource_budget,Mapping) or not resource_budget or not isinstance(depth,int) or depth<0 or not isinstance(fanout,int) or fanout<0:raise ValueError("INVALID_COMPOSITION_ENVELOPE")
 x={"schema":"oce.p162a.capability_composition_envelope.v1","parent_invocation_id":parent_invocation_id,"allowed_child_capabilities":sorted(set(allowed_child_capabilities)),"allowed_child_operations":sorted(set(allowed_child_operations)),"allowed_child_targets":sorted(list(allowed_child_targets),key=canonical_json),"allowed_child_purposes":sorted(set(allowed_child_purposes)),"resource_budget":deepcopy(dict(resource_budget)),"depth":depth,"fanout":fanout};x["composition_envelope_hash"]=canonical_sha256(x);return x
def build_invocation_request(*,authorization_token,requester,executor_id,executor_instance_id,capability_id,capability_version,capability_manifest_hash,operation_id,action_digest,target_binding,target_fingerprint,purpose_id,environment,arguments,requested_resources,budget,runtime_context,world_state_ref,world_state_fingerprint,requested_at,invocation_nonce,expected_preconditions=None,expected_postconditions=None,composition_envelope=None,parent_invocation=None,effect_class_claim=None,governed_effector_id=None,capability_implementation_id=None,material_defaults_resolved=None):
 tok=dict(_m(authorization_token));body=dict(_m(tok.get("body")));tid=body.get("token_id");th=tok.get("token_hash")
 if not _known(tid) or not _known(th):return {"status":"TOKEN_REFERENCE_MISSING",**manifest()}
 rc=dict(_m(runtime_context));rch=rc.pop("context_hash",None)
 if runtime_context.get("schema")!="oce.p162a.runtime_invocation_context.v1" or rch!=canonical_sha256(rc):return {"status":"INVALID_CANONICALIZATION","reason":"RUNTIME_CONTEXT_INVALID",**manifest()}
 if runtime_context.get("executor_instance_id")!=executor_instance_id:return {"status":"MISSING_BINDING","reason":"EXECUTOR_CONTEXT_MISMATCH",**manifest()}
 if environment not in ENVIRONMENTS or runtime_context.get("environment")!=environment:return {"status":"MISSING_BINDING","reason":"ENVIRONMENT_CONTEXT_MISMATCH",**manifest()}
 required=(requester,executor_id,executor_instance_id,capability_id,capability_version,capability_implementation_id,capability_manifest_hash,operation_id,action_digest,target_fingerprint,purpose_id,world_state_ref,world_state_fingerprint,requested_at,invocation_nonce)
 if any(not _known(x) for x in required) or not isinstance(arguments,Mapping):return {"status":"MISSING_BINDING",**manifest()}
 if requester==executor_id:return {"status":"MISSING_BINDING","reason":"REQUESTER_EXECUTOR_NOT_DISTINCT",**manifest()}
 if material_defaults_resolved is not True:return {"status":"MISSING_BINDING","reason":"MATERIAL_DEFAULTS_NOT_RESOLVED",**manifest()}
 if not isinstance(budget,Mapping) or not budget:return {"status":"MISSING_BINDING","reason":"BOUNDED_RESOURCE_BUDGET_REQUIRED",**manifest()}
 for actual,expected,reason in [(action_digest,body.get("action_digest"),"ACTION_DIGEST_BINDING_MISMATCH"),(target_binding,body.get("target"),"TARGET_BINDING_MISMATCH"),(purpose_id,body.get("purpose"),"PURPOSE_BINDING_MISMATCH")]:
  if expected is not None and actual!=expected:return {"status":"MISSING_BINDING","reason":reason,**manifest()}
 if body.get("capabilities") and capability_id not in body["capabilities"]:return {"status":"MISSING_BINDING","reason":"CAPABILITY_OUTSIDE_TOKEN",**manifest()}
 scope=_m(body.get("scope"));ppre=deepcopy(scope.get("preconditions",[]));ppost=deepcopy(scope.get("postconditions",[]));pre=deepcopy(ppre if expected_preconditions is None else expected_preconditions);post=deepcopy(ppost if expected_postconditions is None else expected_postconditions)
 if any(x not in pre for x in ppre):return {"status":"MISSING_BINDING","reason":"P161_PRECONDITION_DROPPED",**manifest()}
 if any(x not in post for x in ppost):return {"status":"MISSING_BINDING","reason":"P161_POSTCONDITION_DROPPED",**manifest()}
 if parent_invocation is not None:
  e=_m(composition_envelope)
  if e.get("schema")!="oce.p162a.capability_composition_envelope.v1":return {"status":"MISSING_BINDING","reason":"CHILD_COMPOSITION_ENVELOPE_REQUIRED",**manifest()}
  if e.get("parent_invocation_id")!=parent_invocation.get("invocation_request_id"):return {"status":"MISSING_BINDING","reason":"PARENT_INVOCATION_MISMATCH",**manifest()}
  if capability_id not in e.get("allowed_child_capabilities",[]) or operation_id not in e.get("allowed_child_operations",[]) or target_binding not in e.get("allowed_child_targets",[]) or purpose_id not in e.get("allowed_child_purposes",[]):return {"status":"MISSING_BINDING","reason":"CHILD_SCOPE_NOT_EXPLICITLY_ALLOWED",**manifest()}
 args=deepcopy(dict(arguments));ad=canonical_sha256(args)
 r={"schema":"oce.p162a.capability_invocation_request.v1","status":"REQUESTED","authorization_token_id":tid,"authorization_token_hash":th,"requester":requester,"executor_id":executor_id,"executor_instance_id":executor_instance_id,"capability_id":capability_id,"capability_version":capability_version,"capability_implementation_id":capability_implementation_id,"capability_manifest_hash":capability_manifest_hash,"operation_id":operation_id,"action_digest":action_digest,"target_binding":deepcopy(target_binding),"target_fingerprint":target_fingerprint,"purpose_id":purpose_id,"environment":environment,"arguments":args,"arguments_digest":ad,"material_defaults_resolved":True,"requested_resources":deepcopy(dict(requested_resources or {})),"budget":deepcopy(dict(budget)),"runtime_context_fingerprint":runtime_context["context_hash"],"world_state_ref":world_state_ref,"world_state_fingerprint":world_state_fingerprint,"expected_preconditions":pre,"expected_postconditions":post,"requested_at":requested_at,"invocation_nonce":invocation_nonce}
 r["invocation_request_id"]="IR-"+canonical_sha256(r)[:24];r["invocation_request_hash"]=canonical_sha256(r)
 b={"schema":"oce.p162a.invocation_binding_manifest.v1","token":{"token_id":tid,"token_hash":th},"executor":{"executor_id":executor_id,"executor_instance_id":executor_instance_id},"capability":{"capability_id":capability_id,"version":capability_version,"implementation_id":capability_implementation_id,"manifest_hash":capability_manifest_hash,"functional_equivalence_is_authorization_equivalence":False},"operation":{"operation_id":operation_id,"action_digest":action_digest},"target":{"binding":deepcopy(target_binding),"fingerprint":target_fingerprint},"purpose":{"purpose_id":purpose_id},"environment":{"environment":environment},"arguments":{"digest":ad},"resources":{"requested":deepcopy(dict(requested_resources or {})),"budget":deepcopy(dict(budget))},"world_state":{"ref":world_state_ref,"fingerprint":world_state_fingerprint},"conditions":{"preconditions":pre,"postconditions":post,"p161_conditions_preserved":True}};b["binding_manifest_hash"]=canonical_sha256(b)
 return {"status":"REQUESTED","request":r,"binding_manifest":b,"runtime_context":deepcopy(dict(runtime_context)),"composition_envelope":deepcopy(composition_envelope),"effect_binding":{"effect_class_claim":effect_class_claim or "UNDETERMINED","governed_effector_id":governed_effector_id,"pure_claim_is_gate_bypass":False,"registry_verification_deferred_to":"P162-B"},"authorization_verified":False,"capability_registry_verified":False,"capability_accessed":False,"execution_performed":False,"functional_only":True,"phenomenology_undetermined":True}
def assert_requested_immutable(before,after):
 if before.get("status")!="REQUESTED":return {"status":"NOT_APPLICABLE"}
 b=deepcopy(dict(before));a=deepcopy(dict(after));same=b.get("invocation_request_id")==a.get("invocation_request_id") and b.get("invocation_request_hash")==a.get("invocation_request_hash")
 for x in (b,a):x.pop("invocation_request_id",None);x.pop("invocation_request_hash",None)
 changed=canonical_json(b)!=canonical_json(a);return {"status":"FAIL" if changed and same else "PASS","material_change":changed,"identity_reused":changed and same,"authorization_created":False,"capability_accessed":False,"execution_performed":False}
