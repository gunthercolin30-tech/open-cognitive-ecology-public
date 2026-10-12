from pathlib import Path
import json
from oif.audit.implicit_contract_consolidator import build_inventory, write_outputs, CLASSIFICATIONS

ROOT = Path.home() / "open-cognitive-ecology"
result = write_outputs(ROOT)
inv = json.loads(Path(result["inventory"]).read_text(encoding="utf-8"))
assert inv["status"] == "OIF2A_IMPLICIT_CONTRACT_CONSOLIDATION_READY"
assert set(inv["classifications"]) == set(CLASSIFICATIONS)
assert len(inv["contracts"]) >= 20
assert len(inv["required_sources"]) == 10
assert inv["non_redundancy"]["new_ontology_primitive_required"] is False
assert inv["dsl_readiness"]["oif2b_started"] is False
print("OIF2A_FUNCTIONAL_OK")
