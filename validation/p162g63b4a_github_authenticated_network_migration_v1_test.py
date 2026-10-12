from pathlib import Path
from ontology.github_publication_connector import GitHubPublicationConnector
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"ontology/github_publication_connector.py"
class FakeEffector:
 def __init__(self): self.calls=[]
 def execute(self,**kw): self.calls.append(kw); return {"status":"EFFECT_CONFIRMED","retry_allowed":False,"transport_result":{"status_code":201,"body":b'{"id":1,"upload_url":""}'}}
class H: pass
def test_no_direct_authenticated_network_path():
 s=P.read_text(encoding="utf-8"); assert "urllib.request.urlopen" not in s; assert 'add_header("Authorization"' not in s
def test_raw_input_secret_forbidden(tmp_path):
 o=GitHubPublicationConnector(tmp_path).step({"real_publish":True,"github_pat":"RAW"}); assert o["real_publication_status"]=="raw_github_secret_forbidden"
def test_raw_environment_secret_forbidden(tmp_path,monkeypatch):
 monkeypatch.setenv("GITHUB_TOKEN","RAW"); assert GitHubPublicationConnector(tmp_path).step({"real_publish":True})["real_publication_status"]=="raw_github_secret_forbidden"
def test_brokered_context_required(tmp_path,monkeypatch):
 monkeypatch.delenv("GITHUB_TOKEN",raising=False); monkeypatch.delenv("OCE_GITHUB_PAT",raising=False); assert GitHubPublicationConnector(tmp_path).step({"real_publish":True})["real_publication_status"]=="governed_brokered_network_context_required"
def test_request_uses_effector_without_auth_header(tmp_path):
 c=GitHubPublicationConnector(tmp_path); f=FakeEffector(); c.set_governed_network_context({"handle":H(),"brokered_use":object(),"adapter_id":"A","effector_id":"NET","now_iso":"2026-10-01T00:00:00Z","effector":f}); o=c._github_request("POST","https://api.github.com/repos/u/r/releases",{"x":1}); assert o["ok"] and len(f.calls)==1; assert "Authorization" not in f.calls[0]["request"].headers
def test_simulation_still_available(tmp_path,monkeypatch):
 monkeypatch.delenv("GITHUB_TOKEN",raising=False); monkeypatch.delenv("OCE_GITHUB_PAT",raising=False); o=GitHubPublicationConnector(tmp_path).step({"real_publish":False}); assert not o["real_publish_performed"]
