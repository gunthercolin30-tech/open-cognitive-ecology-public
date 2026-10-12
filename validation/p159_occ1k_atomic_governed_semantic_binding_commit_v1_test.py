from validation import p159_occ1k_atomic_governed_semantic_binding_commit_v1 as a
def test_preflight(): assert a.preflight()["binding_count"]==8
def test_sources_current(): assert a.layer()["binding_count"]==8
def test_boundaries():
 r=a.layer(); assert not r["runtime_binding_created"] and not r["runtime_enforcement_proven"] and not r["authorization_created"] and not r["execution_performed"] and not r["lock_ready"] and not r["lock_granted"] and not r["p160b_opened"]
def test_history(): r=a.layer(); assert r["historical_evidence_preserved"] and not r["retroactive_repair"]
def test_confirmation():
 try:a.commit("WRONG")
 except RuntimeError as e: assert str(e)=="EXPLICIT_CONFIRMATION_REQUIRED"
 else: assert False
def test_deterministic(): assert a.layer()==a.layer()
