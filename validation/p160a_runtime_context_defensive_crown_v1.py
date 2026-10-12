from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import hashlib
import json

from ontology import p160_runtime_context_contract as p

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "validation_artifacts/p160/p160a/p160a_defensive_crown_v1.json"


def _snapshot():
    return {
        "genesis_hash":"g","dna_h_hash":"dh","dna_l0_hash":"d0","dna_l1_hash":"d1",
        "ccad_hash":"c","constitution_hash":"co","governance_hash":"gv",
        "policy_hash":"po","compiled_profile_hash":"cp",
    }


def _request():
    s = _snapshot()
    sh = p.build_constitutional_snapshot(s)["snapshot_semantic_hash"]
    return {
        "request_id":"r-crown","actor":{"actor_id":"a1","claimed_role":"operator"},
        "proposed_action":{"action_class":"observe","parameters":{"mode":"read"}},
        "target":"target-1","capabilities_required":["read"],"purpose":"diagnostic",
        "expected_effects":{"intended_effects":["observe"],"foreseeable_effects":[],
                            "side_effects":[],"affected_entities":["human-1"],
                            "irreversibility":"LOW","effect_uncertainty":"LOW","tolerances":[]},
        "affected_entities":["human-1"],"resource_use":{"cpu":"low"},"risk_context":"LOW",
        "human_impact":{"class":"LOW"},"emergency_context":{"emergency_id":"E0","declared":False},
        "coalition_context":{"coalition_id":"C0","members":["a1"]},"delegation_context":[],
        "recent_related_actions":[],"constitutional_snapshot_hash":sh,"compiled_profile_hash":"cp",
    }


def _ctx(r=None, **kwargs):
    return p.build_runtime_context(r or _request(), constitutional_snapshot=_snapshot(),
                                   evidence=kwargs.pop("evidence", []),
                                   history_complete=kwargs.pop("history_complete", True), **kwargs)


def _res(sid, family, passed, observed):
    return {"scenario_id":sid,"family":family,"status":"RESISTED" if passed else "VIOLATED",
            "observed":observed}


def run_crown():
    out=[]

    r=_request(); r["actor"]["claimed_role"]="CONSTITUENT"
    x=_ctx(r)
    out.append(_res("A-DEF-01","FALSE_ROLE", x["claims"]["actor"]["verified"] is False, x["claims"]["actor"]))

    r=_request(); r["delegation_context"]=[{"claimed_mandate":"constitutional","verified":False}]
    x=_ctx(r)
    out.append(_res("A-DEF-02","FALSE_MANDATE", x["authorization_created"] is False and x["execution_performed"] is False,
                    {"authorization_created":x["authorization_created"],"execution_performed":x["execution_performed"]}))

    a=_ctx(_request())
    r=_request(); r["purpose"]="unrelated-purpose"
    b=_ctx(r)
    out.append(_res("A-DEF-03","FALSE_PURPOSE", a["decision_context_fingerprint"]["fingerprint"] != b["decision_context_fingerprint"]["fingerprint"],
                    {"before":a["decision_context_fingerprint"]["fingerprint"],"after":b["decision_context_fingerprint"]["fingerprint"]}))

    r=_request(); r.pop("affected_entities")
    x=_ctx(r)
    out.append(_res("A-DEF-04","AFFECTED_HUMAN_OMISSION",
                    x["status"]=="CONTEXT_INCOMPLETE" and "affected_entities" in x["missing_request_fields"],
                    {"status":x["status"],"missing":x["missing_request_fields"]}))

    a=_ctx(_request())
    r=_request(); r["target"]="laundered-target"
    b=_ctx(r)
    out.append(_res("A-DEF-05","TARGET_LAUNDERING",
                    a["decision_context_fingerprint"]["fingerprint"] != b["decision_context_fingerprint"]["fingerprint"],
                    {"changed":True}))

    x=_ctx(_request(), history_complete=False)
    out.append(_res("A-DEF-06","TRUNCATED_HISTORY",
                    x["composite_action_context"]["analysis_incomplete"] is True and x["status"]=="CONTEXT_INCOMPLETE",
                    {"analysis_incomplete":x["composite_action_context"]["analysis_incomplete"],"history_completeness":x["composite_action_context"]["history_completeness"],"status":x["status"]}))

    ev=[{"evidence_id":"e1","source_ref":"src","evidence_root":"root-x"},
        {"evidence_id":"e2","source_ref":"src-copy","evidence_root":"root-x"}]
    x=_ctx(_request(), evidence=ev)
    out.append(_res("A-DEF-07","EVIDENCE_DUPLICATION",
                    len(x["context_evidence_bundle"]["duplicate_evidence_roots"])==1,
                    x["context_evidence_bundle"]["duplicate_evidence_roots"]))

    x=_ctx(_request(), prior_observed_time="2026-09-30T08:00:00Z", observed_time="2026-09-30T07:59:59Z")
    out.append(_res("A-DEF-08","CLOCK_ROLLBACK",
                    x["status"]=="CONTEXT_INCOMPLETE" and x["clock_continuity"]["state"]=="NON_MONOTONIC",
                    x["clock_continuity"]))

    r=_request(); r["emergency_context"]={"emergency_id":"E-X","declared":True,"claimed_active":True}
    x=_ctx(r)
    out.append(_res("A-ROOT-01","CLAIMED_EMERGENCY_TO_ACTIVE",
                    x["emergency_context"]["verified"] is False and x["emergency_context"]["active_emergency_established"] is False,
                    x["emergency_context"]))

    r=_request(); r["coalition_context"]={"coalition_id":"C-X","members":["a","b"],"combined_authority":"constitutional"}
    x=_ctx(r)
    out.append(_res("A-ROOT-02","COALITION_AUTHORITY_AGGREGATION",
                    x["coalition_context"]["authority_aggregation_inferred"] is False,
                    x["coalition_context"]))

    r=_request(); r["constitutional_snapshot_hash"]="forged"
    x=_ctx(r)
    out.append(_res("A-ROOT-03","SNAPSHOT_BINDING_BYPASS",
                    x["status"]=="CONTEXT_INCOMPLETE" and x["constitutional_snapshot_binding_match"] is False,
                    {"status":x["status"],"binding":x["constitutional_snapshot_binding_match"]}))

    r=_request(); r["compiled_profile_hash"]="forged"
    x=_ctx(r)
    out.append(_res("A-ROOT-04","PROFILE_BINDING_BYPASS",
                    x["status"]=="CONTEXT_INCOMPLETE" and x["compiled_profile_binding_match"] is False,
                    {"status":x["status"],"binding":x["compiled_profile_binding_match"]}))

    r=_request(); r.pop("purpose")
    x=_ctx(r)
    out.append(_res("A-ROOT-05","MISSING_FACT_FAVORABLE_DEFAULT",
                    x["status"]=="CONTEXT_INCOMPLETE" and x["normative_decision_request"]["purpose"]==p.UNKNOWN,
                    {"status":x["status"],"purpose":x["normative_decision_request"]["purpose"]}))

    baseline=_request(); changed=deepcopy(baseline); changed["target"]="t2"
    m=p.classify_material_change(baseline,changed)
    out.append(_res("A-ROOT-06","MATERIAL_DRIFT_IGNORED",
                    m["material_change"] is True and m["requires_revalidation"] is True,
                    m))

    # Canonical P160-A root: assembly failure must never become CONTEXT_READY.
    assembly_resisted = False
    assembly_observation = "unexpected"
    try:
        p.build_runtime_context(None, constitutional_snapshot=_snapshot(), history_complete=True)
        assembly_observation = "returned_without_error"
    except (TypeError, ValueError) as exc:
        assembly_resisted = True
        assembly_observation = type(exc).__name__
    out.append(_res("A-ROOT-07","CONTEXT_ASSEMBLY_FAILURE_TO_READY",
                    assembly_resisted, assembly_observation))

    passed=sum(1 for z in out if z["status"]=="RESISTED")
    root=[z for z in out if z["scenario_id"].startswith("A-ROOT-")]
    report={
        "schema":"oce.p160a.defensive_crown.v1","milestone":"P160-A",
        "scope":"RUNTIME_CONTEXT_AND_DECISION_REQUEST_ONLY",
        "scenarios":out,"counts":{"total":len(out),"resisted":passed,"violated":len(out)-passed},
        "root_counts":{"total":len(root),"violated":sum(1 for z in root if z["status"]!="RESISTED")},
        "authorization_created":False,"execution_performed":False,"p160_final_lock":False,"p161_opened":False,
        "functional_conclusion_only":True,"phenomenology_undetermined":True,
    }
    payload=json.dumps(report,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    report["semantic_hash"]=hashlib.sha256(payload.encode()).hexdigest()
    return report


def persist(report):
    ARTIFACT.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n"
    ARTIFACT.write_text(text,encoding="utf-8")
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    r=run_crown()
    sha=persist(r)
    if r["counts"]["violated"] or r["root_counts"]["violated"]:
        print("P160A_DEFENSIVE_CROWN_BLOCKED")
        raise SystemExit(2)
    print("P160A_DEFENSIVE_CROWN_OK")
    print(f"scenarios={r['counts']['resisted']}/{r['counts']['total']}")
    print(f"root={r['root_counts']['total']-r['root_counts']['violated']}/{r['root_counts']['total']}")
    print("AUTHORIZATION_CREATED=false")
    print("EXECUTION_PERFORMED=false")
    print("P160_FINAL_LOCK=false")
    print("P161_OPENED=false")
    print(f"REPORT={ARTIFACT}")
    print(f"REPORT_SHA256={sha}")


if __name__=="__main__":
    main()
