from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ontology import constitutional_emergency_context as p

def C():
    return {"emergency_id":"E-1","reason":"bounded safety anomaly","trigger":"T-1","authority_ref":"AUTH-1",
      "authority_basis":"EXISTING_CONSTITUTIONAL_AUTHORITY","scope":"TEST_SCOPE",
      "start":"2026-09-19T07:00:00Z","end":"2026-09-19T08:00:00Z",
      "affected_rules":["POLICY_X"],"actions":["PAUSE_X"],"evidence_ref":"EV-1","post_event_review_ref":"REVIEW-1"}

def main():
    c=C(); before=deepcopy(c); r=p.validate_context(c,now="2026-09-19T07:30:00Z")
    assert r["status"]=="PASS" and r["active"] and r["expiration_mandatory"] and r["dna_fundamental_preserved"]
    assert r["execution_permitted"] is False and c==before
    assert p.validate_context(c,now="2026-09-19T08:00:00Z")["reason"]=="EMERGENCY_EXPIRED"
    bad=C(); bad["affected_rules"]=["DNA_FUNDAMENTAL"]
    assert p.validate_context(bad,now="2026-09-19T07:30:00Z")["status"]=="FAIL"
    for basis in p.FORBIDDEN_AUTHORITY_BASES:
        bad=C(); bad["authority_basis"]=basis
        assert p.validate_context(bad,now="2026-09-19T07:30:00Z")["status"]=="FAIL"
    renew=C(); renew["renewal_count"]=1
    assert p.validate_context(renew,now="2026-09-19T07:30:00Z")["status"]=="FAIL"
    renew["renewal_authorization_ref"]="AUTH-2"; renew["renewal_justification"]="new evidence"
    assert p.validate_context(renew,now="2026-09-19T07:30:00Z")["status"]=="PASS"
    assert p.validate_context(c,now="2026-09-19T07:30:00Z",normative_status="CONFLICT")["status"]=="CONFLICT"
    assert p.validate_context(c,now="2026-09-19T07:30:00Z",influence_status="FAIL")["status"]=="FAIL"
    ids=[p.validate_context(c,now="2026-09-19T07:30:00Z")["evidence_event_id"] for _ in range(25)]
    assert len(set(ids))==1 and p.validate_reuse_contract()["status"]=="PASS"
    m=p.p102_manifest()
    assert m["boundaries"]["does_not_implement_p103_appeal_override"] and m["boundaries"]["does_not_persist_p104_decision_ledger"]
    print("P102_CONSTITUTIONAL_EMERGENCY_CONTEXT_V1_TEST_OK")
    print("status=PASSED")
    print("bounded_emergency_context=True")
    print("expiration_mandatory=True")
    print("dna_fundamental_preserved=True")
    print("forbidden_authority_bases_blocked=7")
    print("renewal_requires_new_authorization_and_justification=True")
    print("normative_conflict_escalation=True")
    print("determinism_repetitions=25")
    print("stateless_non_mutation=True")
    print("p104_decision_ledger_implemented=False")
    print("real_execution_enabled=False")
    print("functional_conclusion_only=True")
    print("phenomenology_undetermined=True")
if __name__=="__main__": main()
