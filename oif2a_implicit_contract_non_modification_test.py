from pathlib import Path
import hashlib
from oif.audit.implicit_contract_consolidator import write_outputs

ROOT = Path.home() / "open-cognitive-ecology"
PROTECTED = ("ontology", "oif/application", "oif/adapters", "oif/ui")

def snapshot():
    result = {}
    for rel in PROTECTED:
        for path in sorted((ROOT / rel).rglob("*.py")):
            if "__pycache__" not in path.parts and not path.name.endswith(".bak"):
                result[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result

before = snapshot()
write_outputs(ROOT)
after = snapshot()
assert before == after
print("OIF2A_NON_MODIFICATION_OK", len(before))
