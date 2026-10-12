from validation import p159_occ1k_governed_semantic_binding_adoption_dossier_v1 as a
def test_all_eight_source_anchors_verified():
 r=a.build();assert r["candidate_count"]==8 and all(r["anchor_checks"].values())
def test_sources_are_hash_bound():
 r=a.build();assert all(len(x["source_sha256"])==64 for x in r["proposals"])
def test_no_candidate_is_runtime_authority():
 assert all(not x["runtime_authority_granted"] and not x["execution_performed"] for x in a.build()["proposals"])
def test_human_confirmation_required():
 r=a.build();assert r["decision"]["adopt"] is None and r["decision"]["explicit_confirmation_required"]
def test_no_adoption_side_effect():
 r=a.build();m=r["mutation"];assert not any(m.values())
def test_flb3_remains_blocked():
 r=a.build()["epistemic_boundaries"];assert r["fl_b3"]=="BLOCKED" and not r["lock_ready"] and not r["lock_granted"] and not r["p160b_opened"]
def test_deterministic():
 assert a.build()["semantic_hash"]==a.build()["semantic_hash"]

def test_mapping_key_anchor_is_resolved_structurally():
 p=a.ROOT/a.SOURCES["NORMATIVE_HIERARCHY"]
 assert "lower_may_not_contradict_higher" in a.names(p)

def test_executable_return_status_anchor_is_resolved_structurally():
 p=a.ROOT/a.SOURCES["GOVERNANCE_CONTEXTUAL"]
 assert "CONFLICT" in a.names(p)
