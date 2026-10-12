import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g63b7/final_network_rescan.json"
def test_b5_preserved_historically():
    b=json.loads((ROOT/"validation_artifacts/p162/p162g/g63b5/post_migration_network_audit.json").read_text())
    assert b["direct_runtime_bypass_remaining"]==1 and b["network_migration_complete"] is False
def test_b6_removed_old_runtime_socket():
    s=(ROOT/"ontology/real_community_node_certification.py").read_text()
    assert "socket.create_connection" not in s and "P162_G63B6_TCP_PROBE_MEDIATED = True" in s
def test_current_network_zero():
    d=json.loads(R.read_text())
    assert d["known_migrated_modules_direct_transport"]==[]
    assert d["direct_runtime_network_bypass_remaining"]==0
    assert d["review_required"]==0
    assert d["network_bypass_zero_verified"] is True
    assert d["network_migration_complete"] is True
def test_tcb_owns_http_and_tcp():
    s=(ROOT/"ontology/governed_network_effector.py").read_text()
    assert "urllib.request.urlopen" in s and "socket.create_connection" in s
    assert "class GovernedNetworkEffector:" in s and "class GovernedTcpProbeEffector:" in s
def test_current_zero_not_retroactive():
    d=json.loads(R.read_text())
    assert d["historical_b5_preserved"] is True and d["b5_historical_residual_count"]==1 and d["b6_old_residual_removed"] is True
def test_no_authority_or_g_closure():
    d=json.loads(R.read_text())
    assert d["authorization_created"] is False and d["execution_right_created"] is False
    assert d["p162g_closure_claimed"] is False and d["p162h_opened"] is False
    assert set(d["remaining_dimensions"])=={"PROCESS","DATABASE","FILESYSTEM"}
