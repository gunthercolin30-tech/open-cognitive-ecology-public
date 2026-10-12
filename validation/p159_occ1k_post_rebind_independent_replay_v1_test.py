from copy import deepcopy
from validation import p159_occ1k_post_rebind_independent_replay_v1 as a
def test_post_rebind_binding_is_exact():
    ok,e=a.source_binding(); assert ok and e["sha256"]==a.NEW and e["supersedes_sha256"]
def test_real_nir_and_compiler_replay():
    r=a.build()["replay"]; assert r["occ1b_nir_status"]=="PASS" and r["nir_principal_objects"]==48
    assert r["occ1c_compiler_status"]=="PASS" and r["compiled_rules"]==48
def test_static_replay_preserves_unresolved_if_not_materialized():
    r=a.build()["replay"]
    assert r["s7"]["result"]=="UNRESOLVED"
    assert r["s8"]["result"]=="UNRESOLVED"
    assert r["s10"]["result"]=="UNRESOLVED"
def test_no_empty_relation_or_missing_map_promoted():
    r=a.build(); assert r["conclusion"]["fl_b3"]=="BLOCKED"
    assert r["conclusion"]["candidate_binding_adoption_required"]
def test_boundaries_preserved():
    r=a.build(); b=r["boundaries"]; c=r["conclusion"]
    assert not b["authorization_created"] and not b["execution_performed"] and not b["runtime_binding_created"]
    assert not b["canonical_sources_modified"] and not c["p160b_opened"] and not c["lock_ready"] and not c["lock_granted"]
def test_deterministic():
    assert a.build()["semantic_hash"]==a.build()["semantic_hash"]
