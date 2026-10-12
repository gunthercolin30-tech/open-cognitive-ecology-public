import hashlib
import subprocess
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REFINER = Path.home() / "Downloads" / "refine_acee_lineage_manager.py"
TARGETS = [
    ROOT / "ontology" / "acee_lineage_manager.py",
    ROOT / "acee13_fast_acceptance_suite.py",
    ROOT / "acee13_final_lock.py",
    ROOT / "ontology_inventory.txt",
    ROOT / "ontology_inventory.py",
    ROOT / "ontology" / "ontology_inventory.py",
    ROOT / "dependency_registry.py",
    ROOT / "global_module_catalog.txt",
    ROOT / "global_module_catalog.py",
]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

before = {str(path): digest(path) for path in TARGETS}
subprocess.run(["python3", str(REFINER)], cwd=ROOT, check=True)
after = {str(path): digest(path) for path in TARGETS}
assert before == after
print("ACEE13_REFINER_IDEMPOTENT_OK")
