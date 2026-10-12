from pathlib import Path
from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from ontology.acee_installation_executor import AceeInstallationExecutor
import hashlib

def seed(root):
 (root/"ontology").mkdir(parents=True,exist_ok=True)
 names=["alpha"]
 (root/"ontology_inventory.txt").write_text("alpha\n",encoding="utf-8")
 for rel in ["ontology_inventory.py","ontology/ontology_inventory.py"]:
  p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text("# Auto-generated ontology inventory\n\nONTOLOGY_INVENTORY = ['alpha']\n",encoding="utf-8")
 (root/"dependency_registry.py").write_text("# Auto-generated dependency registry\n\nDEPENDENCY_REGISTRY = {'alpha': []}\n",encoding="utf-8")
 (root/"global_module_catalog.txt").write_text("Open Cognitive Ecology — Global Module Catalog\n[modules]\n",encoding="utf-8")

def payload(root,content='VALUE = 1\n',deps=None):
 digest=hashlib.sha256(content.encode()).hexdigest(); decision=AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root,candidate_hash=digest),persist=False)
 return {'acee5_decision':decision,'admission_context':{'requested_stage':'ACEE6-E','candidate_content':content,'inventory_dependencies':deps or []}}
