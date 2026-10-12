import hashlib
from pathlib import Path
from acee4_fast_acceptance_suite import context
from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager
paths=[Path("ontology/acee_meta_orchestrator.py"),Path("ontology/acee_rollback_engine.py"),Path("ontology/evolution_sandbox.py"),Path("dependency_registry.py"),Path("ontology_inventory.txt")]
def d(p): return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
b={str(p):d(p) for p in paths}; r=AceeAutonomousCycleManager().step(inputs=context(),persist=False); a={str(p):d(p) for p in paths}
assert b==a and r["persisted"] is False and r["execution_dispatched"] is False
print("ACEE4_NON_REGRESSION_OK")
