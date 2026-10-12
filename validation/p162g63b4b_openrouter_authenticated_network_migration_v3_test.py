from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"ontology/openrouter_autonomous_provider_adapter.py"
def source(): return P.read_text(encoding="utf-8")

def test_source_compiles_and_marker():
    compile(source(),str(P),"exec")
    assert "P162_G63B4B_AUTH_NETWORK_MEDIATED = True" in source()

def test_direct_urllib_removed():
    s=source()
    assert "urllib.request.urlopen" not in s
    assert "urllib.request.Request" not in s

def test_direct_bearer_removed():
    s=source()
    assert not ('"Authorization"' in s and '"Bearer "' in s)

def test_brokered_context_fail_closed_present():
    s=source()
    assert "governed_brokered_network_context_required" in s
    assert "context.get('brokered_use')" in s

def test_governed_effector_is_http_boundary():
    s=source()
    assert "GovernedNetworkEffector" in s
    assert "brokered_use=context.get('brokered_use')" in s

def test_response_semantics_preserved():
    s=source()
    assert "json.loads(raw)" in s
    assert "status_code = transport_result.get('status_code', 200)" in s

def test_post_is_non_idempotent():
    s=source()
    assert "'POST'" in s and "idempotent=False" in s
