from ontology.p161_human_decision_integrity import *

REQ={"authorization_request_id":"AR1","normative_decision_id":"ND1","action_digest":"AD","purpose":"P","target":"T"}
AUTH={"status":"VALID","receipt_hash":"RH"}
BUNDLE={"status":"SATISFIED","evidence_bundle_hash":"EBH","checks":{"presentation_hash":"PH"}}
def he(**kw):
    d=dict(evidence_id="HE1",human_id="H1",human_role="principal_investigator",actor_kind="HUMAN",
      authorization_request_id="AR1",normative_decision_id="ND1",action_digest="AD",purpose="P",target="T",
      presentation_hash="PH",approval_presentation_hash="PH",decision="APPROVE",decided_at="NOW",nonce="N",
      withdrawn=False,identity_verified=True,role_verified=True,canonical_summary_presented=True,
      material_risks_presented=True,material_objections_presented=True,alternatives_presented=True,
      consequences_understood=True,ability_to_refuse=True,specific_confirmation=True,
      ui_or_model_decided_for_human=False,material_information_hidden=False)
    d.update(kw);return build_human_decision_evidence(**d)
def call(h=None,**kw):
    return evaluate_human_decision_integrity(REQ,kw.get("authority",AUTH),kw.get("bundle",BUNDLE),
      h or he(),human_required=kw.get("human_required",True),
      expected_human_roles=kw.get("roles",("principal_investigator",)))

def test_manifest_non_sovereign():
    m=manifest()
    assert all(m[k] is False for k in ("authority_created","approval_created","authorization_created",
      "authorization_token_created","capability_created","execution_performed","p162_opened"))
def test_positive_human_decision(): assert call()["status"]=="SATISFIED"
def test_deterministic(): assert call()["receipt_hash"]==call()["receipt_hash"]
def test_not_required_is_not_authorization():
    x=call(human_required=False);assert x["status"]=="NOT_REQUIRED" and x["authorization_created"] is False
def test_ai_substitution_rejected(): assert call(he(actor_kind="AI"))["status"]=="UNSATISFIED"
def test_wrong_role_rejected(): assert call(he(human_role="observer"))["status"]=="UNSATISFIED"
def test_presentation_drift_rejected(): assert call(he(presentation_hash="OTHER"))["status"]=="UNSATISFIED"
def test_withdrawn_rejected(): assert call(he(withdrawn=True))["status"]=="UNSATISFIED"
def test_hidden_information_rejected(): assert call(he(material_information_hidden=True))["status"]=="UNSATISFIED"
def test_ui_model_substitution_rejected(): assert call(he(ui_or_model_decided_for_human=True))["status"]=="UNSATISFIED"
def test_missing_understanding_unknown(): assert call(he(consequences_understood=False))["status"]=="UNKNOWN"
def test_missing_refusal_ability_unknown(): assert call(he(ability_to_refuse=False))["status"]=="UNKNOWN"
def test_missing_specific_confirmation_unknown(): assert call(he(specific_confirmation=False))["status"]=="UNKNOWN"
def test_missing_risks_unknown(): assert call(he(material_risks_presented=False))["status"]=="UNKNOWN"
def test_missing_objections_unknown(): assert call(he(material_objections_presented=False))["status"]=="UNKNOWN"
def test_missing_alternatives_unknown(): assert call(he(alternatives_presented=False))["status"]=="UNKNOWN"
def test_identity_unknown_not_positive(): assert call(he(identity_verified=False))["status"]=="UNKNOWN"
def test_hash_tamper_rejected():
    h=he();h["purpose"]="X";assert call(h)["status"]=="UNSATISFIED"
def test_request_binding_rejected(): assert call(he(authorization_request_id="X"))["status"]=="UNSATISFIED"
def test_unsatisfied_d_rejected():
    b=dict(BUNDLE,status="UNSATISFIED");assert call(bundle=b)["status"]=="UNSATISFIED"
def test_invalid_authority_rejected():
    a=dict(AUTH,status="EXPIRED");assert call(authority=a)["status"]=="UNSATISFIED"
def test_no_token_execution():
    x=call();assert x["authorization_token_created"] is False and x["execution_performed"] is False
