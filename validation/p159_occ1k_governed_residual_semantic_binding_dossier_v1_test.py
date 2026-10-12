from validation import p159_occ1k_governed_residual_semantic_binding_dossier_v1 as a
def D():return a.build()
def test_14_contextual():assert D()["counts"]["contextual"]==14
def test_one_unresolved():assert D()["counts"]["unresolved"]==1
def test_no_adoption():assert D()["counts"]["bindings_adopted"]==0
def test_contextual_requires_human_governance():assert all(x["decision_state"]=="HUMAN_GOVERNED_SEMANTIC_DECISION_REQUIRED" for x in D()["contextual_cases"])
def test_unresolved_cannot_promote():assert D()["decision_policy"]["unresolved_case_cannot_be_promoted"] and all(x["allowed_decisions"]==["KEEP_UNRESOLVED"] for x in D()["unresolved_cases"])
def test_no_automatic_bulk():assert not D()["decision_policy"]["bulk_automatic_adoption"] and D()["decision_policy"]["per_case_traceability_required"]
def test_boundaries():
 b=D()["boundaries"];assert not b["rule_bindings_modified"] and not b["runtime_binding_created"] and not b["authorization_created"] and not b["execution_performed"] and not b["p160b_opened"]
def test_deterministic():assert D()==D()
