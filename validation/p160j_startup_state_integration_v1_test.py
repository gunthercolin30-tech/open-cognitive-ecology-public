from ontology.p160_normative_decision_persistence import P160JRuntime

def test_runtime_startup_all_five_states_reachable(tmp_path):
    r=P160JRuntime(tmp_path)
    assert r.startup_reconcile()["startup_state"]=="STARTUP_VALID"
    assert r.startup_reconcile(minimum_viable_constitution=True,startup_issues=["NONCRITICAL_CACHE"])["startup_state"]=="STARTUP_DEGRADED"
    assert r.startup_reconcile(startup_issues=["REGISTRY_X"])["startup_state"]=="STARTUP_RECONCILIATION_REQUIRED"
    assert r.startup_reconcile(startup_issues=["JOURNAL_CONTINUITY_INVALID"])["startup_state"]=="STARTUP_CONTINUITY_UNCERTAIN"
    assert r.startup_reconcile(startup_issues=["SAFE_MODE_REQUIRED:constitution"])["startup_state"]=="STARTUP_SAFE_MODE_REQUIRED"

def test_degraded_requires_explicit_mvc_and_only_noncritical(tmp_path):
    r=P160JRuntime(tmp_path)
    assert r.startup_reconcile(startup_issues=["NONCRITICAL_CACHE"])["startup_state"]=="STARTUP_RECONCILIATION_REQUIRED"
    assert r.startup_reconcile(minimum_viable_constitution=True,startup_issues=["NONCRITICAL_CACHE","REGISTRY_X"])["startup_state"]=="STARTUP_RECONCILIATION_REQUIRED"

def test_startup_never_authorizes_or_executes(tmp_path):
    r=P160JRuntime(tmp_path)
    for kw in ({},{"startup_issues":["SAFE_MODE_REQUIRED:constitution"]},{"minimum_viable_constitution":True,"startup_issues":["NONCRITICAL_CACHE"]}):
        x=r.startup_reconcile(**kw)
        assert x["authorization_created"] is False
        assert x["authorization_token_created"] is False
        assert x["execution_performed"] is False
        assert x["p161_opened"] is False
