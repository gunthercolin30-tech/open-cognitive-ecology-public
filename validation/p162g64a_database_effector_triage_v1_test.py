import ast,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g64a/database_effector_triage.json"
def dotted(n):
    if isinstance(n,ast.Name): return n.id
    if isinstance(n,ast.Attribute):
        a=dotted(n.value); return (a+"."+n.attr) if a else n.attr
    return ""
def test_exact_active_database_scope():
    d=json.loads(R.read_text())
    assert d["active_database_modules"]==3
    assert d["direct_bypass_confirmed"]==3
    assert d["review_required"]==0
    assert {x["path"] for x in d["database_effectors"]}=={
      "ontology/advanced_causal_reasoning_engine.py",
      "ontology/autonomous_web_navigation_engine.py",
      "ontology/persistent_external_memory_fabric.py"}
def test_current_sources_retain_expected_sqlite_bypasses():
    d=json.loads(R.read_text())
    for item in d["database_effectors"]:
        t=ast.parse((ROOT/item["path"]).read_text())
        calls=[n for n in ast.walk(t) if isinstance(n,ast.Call) and dotted(n.func)=="sqlite3.connect"]
        assert len(calls)==len(item["connect_lines"])
def test_persistent_memory_has_mutating_sql():
    s=(ROOT/"ontology/persistent_external_memory_fabric.py").read_text()
    for token in ["INSERT INTO memory","ON CONFLICT","DELETE FROM memory","VACUUM"]:
        assert token in s
def test_history_databases_have_persistent_insert_paths():
    a=(ROOT/"ontology/advanced_causal_reasoning_engine.py").read_text()
    w=(ROOT/"ontology/autonomous_web_navigation_engine.py").read_text()
    assert "INSERT INTO causal_history" in a
    assert "INSERT INTO navigation_history" in w
def test_local_sqlite_is_not_treated_as_noncausal():
    d=json.loads(R.read_text())
    assert d["database_effects_are_persistent"] is True
    assert d["local_database_does_not_exempt_governance"] is True
    assert all(x["persistent_effect"] and x["migration_required"] for x in d["database_effectors"])
def test_no_authority_or_closure_claim():
    d=json.loads(R.read_text())
    assert d["database_availability_creates_authorization"] is False
    assert d["database_migration_complete"] is False
    assert d["database_bypass_zero_claimed"] is False
    assert d["authorization_created"] is False and d["execution_right_created"] is False
    assert d["p162g_closure_claimed"] is False and d["p162h_opened"] is False
