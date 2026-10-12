from copy import deepcopy
from ontology.p161_authorization_token_binding import issue_authorization_token,dependency_vector,authorization_event
from ontology.p161_authorization_token_lifecycle import initialize_lifecycle
from ontology.capability_invocation_request_builder import build_runtime_invocation_context,build_invocation_request
from ontology.token_point_of_use_verifier import verify_at_point_of_use,sha

KEY=b"p162c-test-key"
REQ={"authorization_request_id":"AR1","request_hash":"RQH","normative_decision_id":"ND1","action_digest":"act","runtime_context_fingerprint":"RF","constitutional_snapshot_hash":"CS","compiled_profile_hash":"CP"}
ND={"decision_id":"ND1","artifact_hash":"NDH"}; AU={"status":"VALID","receipt_hash":"AUH"}; EV={"status":"SATISFIED","evidence_bundle_hash":"EVH"}; HI={"status":"NOT_REQUIRED","receipt_hash":"HIH"}
SE={"status":"CONSTRUCTED","authorization_request_id":"AR1","normative_decision_id":"ND1","scope":{"preconditions":["pre"],"postconditions":["post"]},"capabilities":["cap.echo"],"target":{"id":"T1"},"purpose":"P1","validity":{"not_before":"2026-10-01T00:00:00Z","not_after":"2026-10-02T00:00:00Z"},"requested_use_policy":"SINGLE_USE","scope_envelope_hash":"SEH"}
def fx():
 v=dependency_vector(REQ,ND,AU,EV,HI,SE)
 tok=issue_authorization_token(REQ,ND,AU,EV,HI,SE,current_dependency_vector=v,signer_id="ISSUER-1",signing_key=KEY,issued_at="2026-10-01T10:00:00Z")["token"]
 lc=initialize_lifecycle(tok)
 rc=build_runtime_invocation_context(runtime_id="R1",executor_instance_id="EI1",host_id="H1",environment="TEST",time="2026-10-01T10:00:00Z",capability_registry_version="CR1",authorization_registry_version="ARV1",policy_version="PV1",world_state_fingerprint="W1",resource_state_fingerprint="RS1",security_state_fingerprint="SS1")
 a=build_invocation_request(authorization_token=tok,requester="REQ",executor_id="EX",executor_instance_id="EI1",capability_id="cap.echo",capability_version="1",capability_implementation_id="impl.echo.v1",capability_manifest_hash="MH",operation_id="echo",action_digest="act",target_binding={"id":"T1"},target_fingerprint="TF",purpose_id="P1",environment="TEST",arguments={"x":1},requested_resources={"cpu":1},budget={"cpu":1},runtime_context=rc,world_state_ref="WS",world_state_fingerprint="W1",requested_at="2026-10-01T10:00:00Z",invocation_nonce="N1",material_defaults_resolved=True)
 ev=authorization_event(tok["body"]["token_id"],tok["token_hash"],"slot","ISSUER-1",{"ISSUER-1":{"environments":["TEST"]}},"TEST")
 cb={"verification_status":"BOUND_VERIFIED","binding_receipt_hash":"CBH","capability_id":a["request"]["capability_id"],"capability_version":a["request"]["capability_version"],"implementation_identity":a["request"]["capability_implementation_id"],"invocation_request_id":a["request"]["invocation_request_id"]}
 reg={"version":"7","continuity_status":"SATISFIED"}
 rev={"version":"9","status":"SATISFIED","stale":False,"token_revoked":False,"dependency_revoked":False}
 bud={"status":"SATISFIED","available_budget":{"cpu":1},"snapshot_hash":"BH"}
 return dict(token=tok,signing_key=KEY,issuance_event=ev,lifecycle=lc,registry_snapshot=reg,revocation_snapshot=rev,
 invocation_request=a["request"],invocation_binding_manifest=a["binding_manifest"],capability_binding_receipt=cb,
 current_dependency_vector=v,authority_snapshot={"status":"VALID"},approval_consent_quorum_snapshot={"status":"SATISFIED"},
 human_integrity_snapshot={"required":False,"status":"NOT_REQUIRED","snapshot_hash":"HI-CURRENT"},profile_snapshot={"status":"SATISFIED","profile_hash":"PROFILE-CURRENT"},target_state_snapshot={"status":"SATISFIED","snapshot_hash":"TARGET-CURRENT","target_binding":{"id":"T1"}},pending_composition_snapshot={"status":"SATISFIED","snapshot_hash":"PC-CURRENT","has_conflicting_pending_composition":False},
 budget_snapshot=bud,now="2026-10-01T10:00:00Z",revalidate_after="2026-10-01T10:05:00Z")

def test_positive_deterministic_read_only():
 x=fx(); before=deepcopy(x); a=verify_at_point_of_use(**x); b=verify_at_point_of_use(**x)
 assert a["status"]=="TOKEN_USABLE_FOR_GATE" and a["receipt"]["receipt_hash"]==b["receipt"]["receipt_hash"]
 assert x==before and a["lifecycle_input_unchanged"]
 for k in ("authorization_created","reservation_created","token_consumed","capability_accessed","execution_performed","p162d_opened"): assert a[k] is False

def test_signature_and_commit_required():
 x=fx(); x["signing_key"]=b"wrong"; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
 x=fx(); x["issuance_event"]["status"]="UNCOMMITTED"; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"

def test_terminal_and_temporal_uncertainty_block():
 x=fx(); x["lifecycle"]["state"]="REVOKED"; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
 x=fx(); x["clock_rollback"]=True; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"

def test_revocation_and_dependency_drift_block():
 x=fx(); x["revocation_snapshot"]["stale"]=True; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
 x=fx(); x["current_dependency_vector"]["authority_receipt_hash"]="NEW"; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"

def test_authority_and_evidence_currentness_block():
 x=fx(); x["authority_snapshot"]["status"]="UNKNOWN"; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
 x=fx(); x["approval_consent_quorum_snapshot"]["status"]="UNKNOWN"; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"

def test_exact_invocation_bindings_block_substitution():
 for field,value in (("capability_id","other"),("action_digest","other"),("target_binding",{"id":"X"}),("purpose_id","X"),("executor_id","X"),("environment","PRODUCTION")):
  x=fx(); x["invocation_request"][field]=value; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"

def test_argument_and_capability_receipt_block():
 x=fx(); x["invocation_request"]["arguments_digest"]="drift"; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
 x=fx(); x["capability_binding_receipt"]["verification_status"]="IMPLEMENTATION_MISMATCH"; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"

def test_budget_registry_and_unknown_block():
 x=fx(); x["budget_snapshot"]["available_budget"]["cpu"]=0; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
 x=fx(); x["registry_snapshot"]["continuity_status"]="UNKNOWN"; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
 x=fx(); x["revocation_snapshot"]["version"]="UNKNOWN"; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"

def test_receipt_versions_for_future_compare_and_reserve():
 r=verify_at_point_of_use(**fx())["receipt"]
 assert all(r.get(k) for k in ("token_state_version","registry_version","revocation_snapshot_version","dependency_snapshot_hash","budget_snapshot_hash","revalidate_after"))
 assert r["status"]=="TOKEN_USABLE_FOR_GATE"

def test_committed_issuance_issuer_matches_signed_body():
 x=fx()
 assert x["token"]["body"]["signer_id"]==x["issuance_event"]["issuer_id"]
 assert verify_at_point_of_use(**x)["status"]=="TOKEN_USABLE_FOR_GATE"
 x=fx(); x["issuance_event"]["issuer_id"]="OTHER"
 r=verify_at_point_of_use(**x)
 assert r["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
 assert "ISSUANCE_ISSUER_MISMATCH" in r["verification"]["failures"]

def test_contractual_current_state_queries_are_explicit():
 for mutate in (lambda x:x["human_integrity_snapshot"].update(required=True,status="UNKNOWN"),lambda x:x["profile_snapshot"].update(status="UNKNOWN"),lambda x:x["target_state_snapshot"].update(status="UNKNOWN"),lambda x:x["pending_composition_snapshot"].update(status="UNKNOWN")):
  x=fx(); mutate(x); assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
def test_human_integrity_when_required_must_be_current():
 x=fx(); x["human_integrity_snapshot"]={"required":True,"status":"SATISFIED","snapshot_hash":"HI2"}; assert verify_at_point_of_use(**x)["status"]=="TOKEN_USABLE_FOR_GATE"
 x["human_integrity_snapshot"]["status"]="REVOKED"; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
def test_target_current_state_must_match_invocation():
 x=fx(); x["target_state_snapshot"]["target_binding"]={"id":"OTHER"}; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
def test_pending_composition_conflict_blocks():
 x=fx(); x["pending_composition_snapshot"]["has_conflicting_pending_composition"]=True; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
def test_capability_receipt_exactly_binds_invocation():
 for field in ("capability_id","capability_version","implementation_identity","invocation_request_id"):
  x=fx(); x["capability_binding_receipt"][field]="OTHER"; assert verify_at_point_of_use(**x)["status"]=="TOKEN_NOT_USABLE_FOR_GATE"
def test_receipt_carries_contractual_current_state_hashes():
 r=verify_at_point_of_use(**fx())["receipt"]
 for k in ("human_integrity_snapshot_hash","profile_snapshot_hash","target_state_snapshot_hash","pending_composition_snapshot_hash"): assert r.get(k)
