from validation import p159_occ1k_governed_consumer_semantic_contract_dossier_v1 as a
def test_six_consumers(): assert a.build()["consumer_count"]==6
def test_exact_consumer_set(): assert tuple(x["consumer"] for x in a.build()["responsibilities"])==a.CONSUMERS
def test_proposal_only(): assert all(x["status"]=="PROPOSED_NOT_ADOPTED" for x in a.build()["responsibilities"])
def test_no_execution(): assert all(not x["may_execute"] for x in a.build()["responsibilities"])
def test_unknown_preserved(): assert a.build()["derivation_policy"]["unknown_remains_unresolved"]
def test_human_decision_required(): r=a.build(); assert r["decision"]["default"]=="KEEP_UNRESOLVED" and not r["decision"]["automatic_adoption"]
def test_boundaries():
 b=a.build()["boundaries"]; assert b["fl_b3"]=="BLOCKED" and not any(b[k] for k in ("rule_bindings_modified","cnp_modified","canonical_source_modified","runtime_binding_created","runtime_enforcement_proven","authorization_created","execution_performed","lock_ready","lock_granted","p160b_opened"))
def test_deterministic(): assert a.build()==a.build()
