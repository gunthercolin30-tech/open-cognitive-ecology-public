import hashlib
from pathlib import Path
from acee2_fast_acceptance_suite import context
from ontology.acee_meta_orchestrator import AceeMetaOrchestrator

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
paths=[Path("ontology/acee_integration_auditor.py"),Path("ontology/acee_capability_map.py"),Path("ontology/acee_bridge_adapter.py"),Path("ontology/controlled_evolution_orchestrator.py"),Path("ontology/recursive_self_improvement_governor.py"),Path("dependency_registry.py"),Path("ontology_inventory.txt")]
before={str(p):digest(p) for p in paths}
r=AceeMetaOrchestrator().step(inputs=context(),persist=False)
after={str(p):digest(p) for p in paths}
assert before==after
assert r["persisted"] is False
assert r["execution_dispatched"] is False
print("ACEE2_NON_REGRESSION_OK")
