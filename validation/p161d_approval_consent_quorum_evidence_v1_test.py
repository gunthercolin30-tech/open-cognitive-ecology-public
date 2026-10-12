from ontology.p161_approval_consent_quorum_evidence import *

REQ={"authorization_request_id":"AR1","normative_decision_id":"ND1","action_digest":"AD",
     "purpose":"P","target":"T"}
AUTH={"status":"VALID","receipt_hash":"RH"}
R=[{"requirement_id":"approval","state":"SATISFIED"}]
C={"state":"INFORMED"}
Q={"type":"N_OF_M","required":2,"veto_defined":True}
EL=["H1","H2","H3"]

def ev(i,**kw):
    d=dict(evidence_id="E"+i,participant_id=i,authorization_request_id="AR1",
      normative_decision_id="ND1",action_digest="AD",purpose="P",target="T",
      scope={"x":1},presentation_hash="PH",expression="APPROVE",expressed_at="NOW",
      nonce="N"+i,revoked=False,expired=False,separation_of_duties_ok=True,veto=False)
    d.update(kw); return build_approval_evidence(**d)
def call(es=None,**kw):
    return validate_evidence(REQ,AUTH,es or [ev("H1"),ev("H2")],
      requirements=kw.get("requirements",R),eligible_participants=EL,
      quorum_rule=kw.get("quorum_rule",Q),consent_requirement=kw.get("consent_requirement",C))

def test_manifest_non_sovereign():
    m=manifest()
    assert all(m[k] is False for k in ("authorization_created","authorization_token_created","capability_created","execution_performed","p162_opened"))
def test_valid_2_of_3(): assert call()["status"]=="SATISFIED"
def test_deterministic(): assert call()["evidence_bundle_hash"]==call()["evidence_bundle_hash"]
def test_authority_not_approval():
    a=dict(AUTH,status="EXPIRED")
    assert validate_evidence(REQ,a,[ev("H1"),ev("H2")],requirements=R,eligible_participants=EL,quorum_rule=Q,consent_requirement=C)["status"]=="UNSATISFIED"
def test_request_binding(): assert call([ev("H1",authorization_request_id="X"),ev("H2")])["status"]=="UNSATISFIED"
def test_revoked(): assert call([ev("H1",revoked=True),ev("H2")])["status"]=="UNSATISFIED"
def test_expired(): assert call([ev("H1",expired=True),ev("H2")])["status"]=="UNSATISFIED"
def test_hash_tamper():
    e=ev("H1"); e["purpose"]="X"
    assert call([e,ev("H2")])["status"]=="UNSATISFIED"
def test_duplicate_alias_not_double_counted():
    assert call([ev("H1",participant_alias="SAME"),ev("H2",participant_alias="SAME")])["status"]=="UNSATISFIED"
def test_ineligible_not_counted(): assert call([ev("H1"),ev("X")])["status"]=="UNSATISFIED"
def test_presentation_same(): assert call([ev("H1"),ev("H2",presentation_hash="OTHER")])["status"]=="UNSATISFIED"
def test_separation(): assert call([ev("H1"),ev("H2",separation_of_duties_ok=False)])["status"]=="UNSATISFIED"
def test_defined_veto(): assert call([ev("H1"),ev("H2",veto=True)])["status"]=="UNSATISFIED"
def test_unknown_requirement_not_positive():
    assert call(requirements=[{"requirement_id":"approval","state":"UNKNOWN"}])["status"]=="UNKNOWN"
def test_unsatisfied_requirement():
    assert call(requirements=[{"requirement_id":"approval","state":"UNSATISFIED"}])["status"]=="UNSATISFIED"
def test_withdrawn_consent():
    assert call(consent_requirement={"state":"WITHDRAWN"})["status"]=="UNSATISFIED"
def test_invalid_delegated_consent():
    assert call(consent_requirement={"state":"DELEGATED","delegation_valid":False})["status"]=="UNSATISFIED"
def test_missing_consent_requirement_unknown():
    assert call(consent_requirement={})["status"]=="UNKNOWN"
def test_missing_quorum_unknown():
    assert call(quorum_rule={})["status"]=="UNKNOWN"
def test_no_token_execution():
    x=call()
    assert x["authorization_created"] is False and x["authorization_token_created"] is False and x["execution_performed"] is False
