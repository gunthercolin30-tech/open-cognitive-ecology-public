from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from ontology import constitutional_epistemic_pluralism as p

def h(i,status="PASS"):
    return {
        "hypothesis_id":i,
        "content_ref":"claim:"+i,
        "provenance_ref":"prov:"+i,
        "lineage_ref":"lin:"+i,
        "identity_ref":"id:"+i,
        "budget_ref":"budget:"+i,
        "permissions_ref":"perm:"+i,
        "epistemic_status":status,
    }

def main():
    assert p.validate_reuse_contract()["status"]=="PASS"
    a,b=h("A"),h("NOT_A")
    r=p.evaluate_pluralism([a,b],contradictory_pairs=[("A","NOT_A")])
    assert r["status"]=="PASS"
    assert r["contradictory_hypotheses_may_coexist"] is True
    assert r["majority_is_truth"] is False
    assert r["power_is_truth"] is False
    assert r==p.evaluate_pluralism([a,b],contradictory_pairs=[("A","NOT_A")])

    for basis in p.FORBIDDEN_TRUTH_BASES:
        x=p.evaluate_pluralism([a,b],truth_claim_basis=basis)
        assert x["status"]=="FAIL" and x["action"]=="BLOCK"

    for ns in ("FAIL","CONFLICT","UNDETERMINED"):
        x=p.evaluate_pluralism([a,b],normative_status=ns)
        assert x["status"]!="PASS"
        assert x["action"]=="ABSTAIN_AND_ESCALATE"

    assert p.evaluate_pluralism([a,b],influence_status="FAIL")["status"]=="FAIL"
    assert p.evaluate_pluralism([h("A","UNDETERMINED"),b])["status"]=="UNDETERMINED"
    assert p.evaluate_pluralism(
        [a,b],contradictory_pairs=[("A","MISSING")]
    )["status"]=="UNDETERMINED"

    for k in ("identity_ref","budget_ref","permissions_ref","lineage_ref","provenance_ref"):
        bad=h("X")
        bad.pop(k)
        assert p.validate_hypothesis(bad)["status"]=="UNDETERMINED"

    m=p.p101_manifest()
    assert m["transversal_references"]==("R20","R21","A-CANON","4B","4C","4D","4E")
    assert m["persistence_stateless_contract"]["implementation_is_stateless"] is True
    for k in (
        "persistent_hypothesis_records_require_identity",
        "persistent_hypothesis_records_require_budget",
        "persistent_hypothesis_records_require_permissions",
        "persistent_hypothesis_records_require_lineage",
        "persistent_hypothesis_records_require_provenance",
    ):
        assert m["persistence_stateless_contract"][k] is True
    assert m["boundaries"]["does_not_persist_p104_decision_ledger"] is True
    assert m["boundaries"]["does_not_prove_runtime_enforcement_p155_p166"] is True
    assert m["boundaries"]["real_execution_enabled"] is False

    print("P101_CONSTITUTIONAL_EPISTEMIC_PLURALISM_V1_TEST_OK")
    print("status=PASSED")
    print("contradictory_epistemically_admissible_hypotheses_coexist=True")
    print("majority_not_truth=True")
    print("power_not_truth=True")
    print("forbidden_truth_bases_blocked=6")
    print("vertical_normative_degradation=3")
    print("persistent_record_fields_required=5")
    print("recommendation_decision_authorization_execution_separated=True")
    print("p104_decision_ledger_implemented=False")
    print("real_execution_enabled=False")
    print("functional_conclusion_only=True")
    print("phenomenology_undetermined=True")

if __name__=="__main__":
    main()

