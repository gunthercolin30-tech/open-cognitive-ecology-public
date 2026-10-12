from pathlib import Path
from ontology.scoped_handle_broker import ScopedEffectHandle
from ontology.governed_network_effector import GovernedTcpProbeEffector
from ontology.real_community_node_certification import RealCommunityNodeCertification
ROOT=Path(__file__).resolve().parents[1]
def handle(target="example.org:22",operation="TCP_CONNECT_PROBE",adapter="A",effector="TCP"):
    return ScopedEffectHandle("h","l","r","c",adapter,effector,operation,target,"s",adapter,"2999-01-01T00:00:00Z")
class FakeTcp:
    def __init__(self,mode="ok"): self.mode=mode; self.calls=[]
    def __call__(self,**kw):
        self.calls.append(kw)
        if self.mode=="timeout": raise TimeoutError()
        if self.mode=="oserror": raise ConnectionRefusedError()
        if self.mode=="unknown": raise RuntimeError("unknown")
        return {"connected":True}
def test_node_no_direct_socket():
    s=(ROOT/"ontology/real_community_node_certification.py").read_text()
    assert "socket.create_connection" not in s and "\nimport socket\n" not in s
def test_missing_context_fails_closed(tmp_path):
    a=RealCommunityNodeCertification(tmp_path)
    assert a._probe_reachability("example.org",22,1) is False
    assert a._last_reachability_diagnostic=="governed_tcp_probe_context_required"
def test_exact_target_and_operation():
    f=FakeTcp(); e=GovernedTcpProbeEffector(transport=f)
    assert e.execute(host="example.org",port=22,timeout_seconds=1,handle=handle("other:22"),adapter_id="A",effector_id="TCP")["status"]=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
    assert e.execute(host="example.org",port=22,timeout_seconds=1,handle=handle(operation="GET"),adapter_id="A",effector_id="TCP")["status"]=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
    assert f.calls==[]
def test_governed_probe(tmp_path):
    f=FakeTcp(); e=GovernedTcpProbeEffector(transport=f); a=RealCommunityNodeCertification(tmp_path)
    a.set_governed_tcp_probe_context({"handle":handle(),"adapter_id":"A","effector_id":"TCP","effector":e})
    assert a._probe_reachability("example.org",22,1) is True
    assert f.calls==[{"host":"example.org","port":22,"timeout_seconds":1.0}]
def test_timeout_refusal_and_unknown():
    for mode in ("timeout","oserror"):
        o=GovernedTcpProbeEffector(transport=FakeTcp(mode)).execute(host="example.org",port=22,timeout_seconds=1,handle=handle(),adapter_id="A",effector_id="TCP")
        assert o["status"]=="EFFECT_FAILED_CONFIRMED" and o["reachable"] is False
    o=GovernedTcpProbeEffector(transport=FakeTcp("unknown")).execute(host="example.org",port=22,timeout_seconds=1,handle=handle(),adapter_id="A",effector_id="TCP")
    assert o["status"]=="EFFECT_STATE_INDETERMINATE" and o["retry_allowed"] is False
def test_no_credentials_or_payload():
    s=(ROOT/"ontology/governed_network_effector.py").read_text().split("class GovernedTcpProbeEffector:",1)[1]
    assert "credential_resolver" not in s and "Authorization" not in s and "body=" not in s
def test_step_reports_governance_block(tmp_path):
    a=RealCommunityNodeCertification(tmp_path)
    o=a.step({"community_node_id":"n","host":"example.org","operator":"o","operator_consent":True,"governance_acknowledged":True,"external_operator_confirmed":True,"external_site_confirmed":True,"non_founder_device_confirmed":True,"require_reachability":True})
    assert o["community_node_reachable"] is False
    assert o["diagnostics"]["reachability_probe_governance"]=="governed_tcp_probe_context_required"
