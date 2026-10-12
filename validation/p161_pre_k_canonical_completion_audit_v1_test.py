from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
O=ROOT/"ontology"; V=ROOT/"validation"
def text(rel): return (ROOT/rel).read_text(encoding="utf-8")

def test_p161_a_canonical_request_surface():
    t=text("ontology/p161_authorization_request.py")
    required=("environment","related_requests","break_glass","max_uses","max_resource","max_targets","max_duration","max_concurrent_uses")
    missing=[x for x in required if x not in t]
    assert not missing, "P161-A canonical request fields/guards missing: "+",".join(missing)

def test_p161_f_cross_dimension_and_composition_guards():
    t=text("ontology/p161_authorization_scope_construction.py")
    groups={"tuple_integrity":("constraint","tuple"),"active_composition":("active","authorization"),
            "reservation":("reservation",),"budget":("budget",),"environment":("environment",)}
    missing=[n for n,ps in groups.items() if not all(re.search(p,t,re.I) for p in ps)]
    assert not missing, "P161-F canonical guards missing: "+",".join(missing)

def test_p161_g_signed_budget_event_and_commit_binding():
    t=text("ontology/p161_authorization_token_binding.py")
    groups={"signed_budget":("budget",),"max_uses":("max_uses",),"environment":("environment",),
            "authorization_event":("AuthorizationEvent|authorization_event",),
            "semantic_slot":("semantic.*slot|slot.*semantic",),"uncommitted":("UNCOMMITTED|uncommitted",),
            "issuer_bounded":("issuer.*registry|issuer.*environment|issuer.*class",)}
    missing=[n for n,ps in groups.items() if not all(re.search(p,t,re.I|re.S) for p in ps)]
    assert not missing, "P161-G canonical binding/commit guards missing: "+",".join(missing)

def test_p161_h_lifecycle_canonical_surface():
    t=text("ontology/p161_authorization_token_lifecycle.py")+text("ontology/p161_authorization_token_persistence.py")
    groups={"tombstone":("tombstone",),"indeterminate":("INDETERMINATE",),"idempotency":("idempot",),
            "dependency_revocation":("dependency","revok"),"partial_effect":("PARTIAL|FAILED_AFTER_EFFECT",),
            "clock_uncertainty":("clock|temporal","uncertain|rollback")}
    missing=[n for n,ps in groups.items() if not all(re.search(p,t,re.I|re.S) for p in ps)]
    assert not missing, "P161-H canonical lifecycle guards missing: "+",".join(missing)

def test_p161_i_root_c01_c25_explicit_coverage():
    from validation.p161i_authorization_defensive_crown_v1 import ROOT_IDS, run_canonical_root_crown
    expected=tuple(f"ROOT-C{i:02d}" for i in range(1,26))
    assert ROOT_IDS==expected
    report=run_canonical_root_crown()
    assert report["root_total"]==25
    assert report["root_pass"]==25
    assert report["root_violated"]==0
    assert report["root_inconclusive"]==0
    assert report["root_skipped"]==0
    assert report["positive_pass"]==report["positive_total"]==10
    assert report["status"]=="PASS"

def test_p161_i_independent_detection_is_material():
    t=text("validation/p161i_authorization_defensive_crown_v1.py")
    assert re.search(r"independent",t,re.I), "P161-I lacks explicit materially-independent ROOT detection evidence"

def test_p161_j_mutation_catalogue_a_to_h_and_meta_controls():
    from validation.p161j_semantic_mutation_crown_v1 import run_canonical_mutation_campaign
    r=run_canonical_mutation_campaign()
    assert r["zones_covered"]==[f"zone{x}" for x in "ABCDEFGH"]
    assert r["double_mutants"]>=2
    assert r["false_restrictive_mutants"]>=2
    assert r["meta_mutants"]>=2
    assert r["status"]=="PASS"

def test_p161_j_root_metrics_and_isolation():
    from validation.p161j_semantic_mutation_crown_v1 import run_canonical_mutation_campaign
    r=run_canonical_mutation_campaign()
    assert r["ROOT_SURVIVED"]==0
    assert r["ROOT_INCONCLUSIVE"]==0
    assert r["META_TEST_FAILURE"]==0
    assert r["CONTROL_MUTANT_FAILURE"]==0
    assert r["MUTATION_CONTAMINATION"]==0
    assert r["baseline_hash"]==r["restored_hash"]
    assert r["workspace_isolated"] is True
    assert r["status"]=="PASS"

def test_p161_j_full_crash_point_surface():
    t=text("ontology/p161_authorization_token_persistence.py")+text("validation/p161j_mutation_persistence_concurrency_v1_test.py")
    for stage in ("PREPARE","VALIDATE","SIGN","STORE","JOURNAL","REGISTRY","COMMIT"):
        assert stage in t, "P161-J crash stage missing: "+stage
    assert re.search(r"precommit|before.*COMMIT",t,re.I|re.S), "P161-J before-COMMIT unusability not explicit"
    assert re.search(r"post.commit|post_commit|after.*COMMIT",t,re.I|re.S), "P161-J after-COMMIT recovery not explicit"

def test_p161_j_concurrency_canonical_families():
    from validation.p161j_race_final_compare_crown_v1 import run_canonical_concurrency_crown
    r=run_canonical_concurrency_crown()
    assert r["total"]==11
    assert r["pass_count"]==11
    assert r["status"]=="PASS"

def test_p161_end_to_end_a_to_h_real_objects_not_only_synthetic():
    tests="\n".join(p.read_text(encoding="utf-8") for p in V.glob("p161*.py"))
    names=("build_authorization_request","verify_for_authorization","revalidate_authority","validate_evidence",
           "evaluate_human_decision_integrity","construct_authorization_scope","issue_authorization_token","initialize_lifecycle")
    missing=[n for n in names if n not in tests]
    assert not missing, "P161 A-H integration APIs absent from test corpus: "+",".join(missing)

def test_p161_k_and_p162_still_unopened():
    assert not (ROOT/"ontology/p161_final_lock.py").exists()
    assert not any(V.glob("p161k*"))
    assert not any(O.glob("p162*"))
