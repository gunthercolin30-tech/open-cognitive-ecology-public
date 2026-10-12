import tempfile,json,hashlib
from pathlib import Path
from ontology.occ1h_a105_rrpe_blocker_decomposition_remediation_authority import authority_gate
from ontology.occ1h_a095_rrpf_bounded_provenance_assurance import experiment as e95
from ontology.occ1h_a097_posthardening_evidence import build as e97
from ontology.occ1h_a100_rrpf_governed_transition_requalification import experiment as e100
from ontology.occ1h_a101_rrpf_bounded_assurance_requalification import experiment as e101

LINKS=("A095_provenance","A097_compound_detection","A100_transition_authority","A101_verifier_integrity")

def _rrp21(case):
    # Sequential, non-compensatory surrogate: every governed component link must remain intact.
    trace=[]
    for link in LINKS:
        ok=case.get(link) is True
        trace.append({"link":link,"ok":ok})
        if not ok:
            return {"result":"REJECTED_FAIL_CLOSED","trace":trace}
    return {"result":"BOUNDED_CHAIN_ACCEPTED","trace":trace}

def _rrp22(case):
    # Independent method: fresh-data set equality, no RRP21 result/trace consumption.
    present={k for k,v in case.items() if v is True}
    required=set(LINKS)
    return "BOUNDED_CHAIN_ACCEPTED" if present==required and len(case)==len(LINKS) else "REJECTED_FAIL_CLOSED"

def experiment(root):
    gate=authority_gate(root)
    assert gate["rrp20"]=="TECHNICAL_REMEDIATION_AUTHORIZED"
    assert gate["rrp21_authorized_scope"]=="BOUNDED_NON_PRODUCTION_A105_COMPOSITIONAL_ASSURANCE_EXPERIMENT_ONLY"

    # Bind the surrogate to currently governed component evidence without changing component semantics.
    c95=e95(); c97=e97(root); c100=e100(); c101=e101()
    component_bindings={
      "A095":c95.get("experiment_passed") is True,
      "A097":c97.get("current_verdict")=="DETECTED" and c97.get("compound_execution") is True,
      "A100":c100.get("rrp21_discrimination_ok") is True and c100.get("rrp22_discrimination_ok") is True,
      "A101":c101.get("discrimination_ok") is True}
    assert all(component_bindings.values())

    intact={k:True for k in LINKS}
    cases={"intact_control":dict(intact)}
    for link in LINKS:
        c=dict(intact); c[link]=False; cases["broken_"+link]=c

    expected={k:("BOUNDED_CHAIN_ACCEPTED" if k=="intact_control" else "REJECTED_FAIL_CLOSED") for k in cases}
    r21={k:_rrp21(v)["result"] for k,v in cases.items()}
    r22={k:_rrp22(dict(v)) for k,v in cases.items()}

    with tempfile.TemporaryDirectory() as td:
        fixture=Path(td)/"a105_compositional_fixture.json"
        fixture.write_text(json.dumps(cases,sort_keys=True,separators=(",",":")))
        fixture_sha=hashlib.sha256(fixture.read_bytes()).hexdigest()

    ok21=r21==expected
    ok22=r22==expected
    return {
      "scenario":"A105",
      "rrp21":"BOUNDED_NON_PRODUCTION_A105_COMPOSITIONAL_ASSURANCE_EXPERIMENT_EXECUTED",
      "component_bindings":component_bindings,
      "fixture_scope":"TEMPORARY_ISOLATED_NON_PRODUCTION",
      "fixture_sha256":fixture_sha,
      "cases":cases,"expected":expected,
      "rrp21_results":r21,"rrp21_discrimination_ok":ok21,
      "non_compensatory_fail_closed":all(r21[k]=="REJECTED_FAIL_CLOSED" for k in r21 if k!="intact_control"),
      "rrp22":"INDEPENDENT_REQUALIFICATION_SUPPORTS_RETURN_TO_RRP9_12" if ok22 else "INDEPENDENT_REQUALIFICATION_FAILED",
      "rrp22_results":r22,"rrp22_discrimination_ok":ok22,
      "rrp22_independent_method":"FRESH_CASE_SET_EQUALITY_WITHOUT_CONSUMING_RRP21_STATUS_RESULTS_OR_TRACE",
      "candidate_verdict":"RESISTED" if ok21 and ok22 else "INCONCLUSIVE",
      "root_materiality_candidate":"ROOT",
      "return_to_rrp9_12_required":ok21 and ok22,
      "historical_inconclusive_preserved":True,
      "evidence_scope":"BOUNDED_NON_PRODUCTION_COMPOSITIONAL_SURROGATE_ONLY",
      "production_grand_chain_materialized":False,
      "production_runtime_modified":False,"criticality_changed":False,
      "occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,
      "functional_only":True,"phenomenology_undetermined":True}
