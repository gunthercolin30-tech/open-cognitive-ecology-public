import ast
from pathlib import Path
from ontology.knowledge_acquisition_engine import KnowledgeAcquisitionEngine
from ontology.multi_source_encyclopedic_integration_engine import MultiSourceEncyclopedicIntegrationEngine
ROOT=Path(__file__).resolve().parents[1]
MIGRATED=[ROOT/"ontology/knowledge_acquisition_engine.py",ROOT/"ontology/multi_source_encyclopedic_integration_engine.py"]
class FakeEffector:
 def __init__(self,payload): self.payload=payload; self.calls=[]
 def execute(self,**kw): self.calls.append(kw); return {"status":"EFFECT_CONFIRMED","transport_result":{"body":self.payload}}
class H: pass
def ctx(fake): return {"handle":H(),"brokered_use":None,"adapter_id":"A","effector_id":"NET","now_iso":"2026-10-01T00:00:00Z","effector":fake}
def test_no_direct_urlopen_or_urllib_request_import():
 for p in MIGRATED:
  src=p.read_text(encoding="utf-8"); assert "urlopen(" not in src
  tree=ast.parse(src)
  for n in ast.walk(tree):
   if isinstance(n,ast.Import): assert all(a.name!="urllib.request" for a in n.names)
   if isinstance(n,ast.ImportFrom): assert n.module!="urllib.request"
def test_knowledge_fails_closed_without_context(): assert KnowledgeAcquisitionEngine().search_web("Open Cognitive Ecology") is None
def test_knowledge_uses_governed_effector():
 f=FakeEffector(b'{"AbstractText":"A governed result"}'); e=KnowledgeAcquisitionEngine(ctx(f)); assert e.search_web("Open Cognitive Ecology"); assert len(f.calls)==1
def test_multisource_fails_closed_without_context():
 try: MultiSourceEncyclopedicIntegrationEngine()._get_json("https://fr.wikipedia.org/w/api.php")
 except PermissionError: pass
 else: raise AssertionError("network effect did not fail closed")
def test_multisource_uses_governed_effector():
 f=FakeEffector(b'{"query":{"search":[]}}'); e=MultiSourceEncyclopedicIntegrationEngine(ctx(f)); assert e._get_json("https://fr.wikipedia.org/w/api.php")=={"query":{"search":[]}}; assert len(f.calls)==1
def test_trusted_transport_is_only_urlopen_location_in_three_files():
 net=(ROOT/"ontology/governed_network_effector.py").read_text(encoding="utf-8"); assert "class UrllibTrustedTransport:" in net and "urllib.request.urlopen" in net
 for p in MIGRATED: assert "urllib.request.urlopen" not in p.read_text(encoding="utf-8")
