from validation import p159_occ1k_governed_rule_consumer_binding_decision_dossier_v1 as a
def test_exact_48_rules(): assert a.build()["rule_count"]==48
def test_partition_complete(): r=a.build(); assert sum(r["counts"].values())==48
def test_allowed_consumers_only():
 r=a.build()
 assert all(c in a.ALLOWED for d in r["decisions"] for c in d["consumer_candidates"])
def test_no_guessing():
 r=a.build()
 for d in r["decisions"]:
  if not d["evidence"]["existing_consumers"]: assert d["classification"]=="UNRESOLVED" and d["consumer_candidates"]==[]
def test_proposal_not_adoption(): r=a.build(); assert not r["decision_policy"]["automatic_adoption"] and r["decision_policy"]["proposal_is_not_adoption"]
def test_boundaries():
 r=a.build()["boundaries"]
 assert not any(r[k] for k in ("cnp_modified","canonical_source_modified","runtime_binding_created","runtime_enforcement_proven","authorization_created","execution_performed","lock_ready","lock_granted","p160b_opened"))
 assert r["fl_b3"]=="BLOCKED"
def test_deterministic(): assert a.build()==a.build()
