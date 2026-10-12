from pathlib import Path
from ontology.real_chatgpt_autonomous_api_adapter import RealChatGPTAutonomousAPIAdapter
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"ontology/real_chatgpt_autonomous_api_adapter.py"
class FakeEffector:
    def __init__(self,status="EFFECT_CONFIRMED"): self.status=status; self.calls=[]
    def execute(self,**kw):
        self.calls.append(kw)
        if self.status=="EFFECT_CONFIRMED":
            return {"status":"EFFECT_CONFIRMED","retry_allowed":False,"transport_result":{"status_code":200,"body":b'{"id":"resp_1","output_text":"governed ok","output":[]}'}}
        return {"status":self.status,"retry_allowed":False,"reason":"simulated"}
class H: pass
def source(): return P.read_text(encoding="utf-8")
def test_no_direct_secret_or_http_path():
    s=source()
    assert 'os.environ.get("OPENAI_API_KEY"' not in s and "urllib.request" not in s and "urllib.error" not in s
    assert not ('"Authorization"' in s and "Bearer" in s)
def test_missing_context_fails_closed(tmp_path,monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY","RAW_SHOULD_NOT_GRANT")
    o=RealChatGPTAutonomousAPIAdapter(tmp_path).step({"prompt":"x"})
    assert o["failure_reason"]=="governed_brokered_network_context_required" and o["raw_secret_observed"] is False
def test_governed_effector_path(tmp_path):
    a=RealChatGPTAutonomousAPIAdapter(tmp_path); f=FakeEffector()
    a.set_governed_network_context({"handle":H(),"brokered_use":object(),"adapter_id":"A","effector_id":"NET","now_iso":"2026-10-01T00:00:00Z","effector":f})
    o=a.step({"prompt":"x"})
    assert o["success"] is True and o["response_text"]=="governed ok"
    assert f.calls[0]["request"].method=="POST" and f.calls[0]["request"].idempotent is False
    assert "Authorization" not in f.calls[0]["request"].headers
def test_indeterminate_preserved(tmp_path):
    a=RealChatGPTAutonomousAPIAdapter(tmp_path); f=FakeEffector("EFFECT_STATE_INDETERMINATE")
    a.set_governed_network_context({"handle":H(),"brokered_use":object(),"adapter_id":"A","effector_id":"NET","now_iso":"2026-10-01T00:00:00Z","effector":f})
    o=a.step({"prompt":"x"})
    assert o["effect_state_indeterminate"] is True and o["retry_allowed"] is False
def test_empty_prompt_does_not_probe_secret(tmp_path,monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY","RAW")
    o=RealChatGPTAutonomousAPIAdapter(tmp_path).step({"prompt":""})
    assert o["brokered_credential_available"] is False and "api_key_present" not in o
def test_filesystem_dimension_not_claimed():
    s=source()
    assert "write_text(" in s or ".open(" in s
