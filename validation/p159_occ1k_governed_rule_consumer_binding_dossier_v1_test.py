from validation import p159_occ1k_governed_rule_consumer_binding_dossier_v1 as a
def D():return a.build()
def test_48_rules():assert D()["counts"]["rules"]==48
def test_partition_complete():
 c=D()["counts"];assert c["ready_for_governed_adoption"]+c["partial_keep_unresolved"]+c["unresolved_no_binding_proposed"]==48
def test_ready_only_has_proven_consumers():
 assert all(x["proposed_consumers"] for x in D()["rules"] if x["binding_state"]=="READY_FOR_GOVERNED_ADOPTION")
def test_partial_stays_unresolved():
 assert all(x["unresolved_reasons"] for x in D()["rules"] if x["binding_state"]=="PARTIAL_KEEP_UNRESOLVED")
def test_unresolved_has_no_proposed_binding():
 assert all(not x["proposed_consumers"] for x in D()["rules"] if x["binding_state"]=="UNRESOLVED_NO_BINDING_PROPOSED")
def test_no_automatic_adoption():assert not D()["decision"]["automatic_adoption"]
def test_boundaries():
 b=D()["boundaries"];assert not b["rule_bindings_modified"] and not b["cnp_modified"] and not b["runtime_binding_created"] and not b["p160b_opened"]
def test_deterministic():assert D()==D()
