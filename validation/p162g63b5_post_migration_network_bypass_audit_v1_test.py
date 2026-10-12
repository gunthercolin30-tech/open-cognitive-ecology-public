import ast,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g63b5/post_migration_network_audit.json"
def dotted(n):
    if isinstance(n,ast.Name): return n.id
    if isinstance(n,ast.Attribute):
        a=dotted(n.value); return (a+"."+n.attr) if a else n.attr
    return ""
def test_audit_honestly_blocks_network_closure():
    d=json.loads(R.read_text()); assert d["network_migration_complete"] is False; assert d["direct_runtime_bypass_remaining"]==1
def test_residual_is_real_current_tcp_call():
    t=ast.parse((ROOT/"ontology/real_community_node_certification.py").read_text()); assert any(isinstance(n,ast.Call) and dotted(n.func)=="socket.create_connection" for n in ast.walk(t))
def test_known_migrated_modules_have_no_direct_transport():
    d=json.loads(R.read_text()); forbidden={"urllib.request.urlopen","requests.get","requests.post","requests.request","httpx.get","httpx.post","httpx.request","socket.create_connection"}
    for rel in d["migrated_runtime_modules_verified_no_direct_transport"]:
        t=ast.parse((ROOT/rel).read_text()); assert not any(isinstance(n,ast.Call) and dotted(n.func) in forbidden for n in ast.walk(t)),rel
def test_tcb_owns_real_urllib_transport():
    assert "urllib.request.urlopen" in (ROOT/"ontology/governed_network_effector.py").read_text()
def test_oif_calls_are_loopback_test_context():
    for rel in ["oif2_3e_interface_validation_crown.py","oif2_3f_adversarial_navigation_crown.py"]: assert "127.0.0.1" in (ROOT/rel).read_text()
def test_no_authority_or_closure_claim():
    d=json.loads(R.read_text()); assert d["authorization_created"] is False and d["execution_right_created"] is False and d["p162g_closure_claimed"] is False and d["p162h_opened"] is False
