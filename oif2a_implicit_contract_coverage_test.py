from pathlib import Path
from oif.audit.implicit_contract_consolidator import build_inventory, CLASSIFICATIONS, REQUIRED_SOURCES

ROOT = Path.home() / "open-cognitive-ecology"
inv = build_inventory(ROOT)
ids = {row["id"] for row in inv["contracts"]}
for required in {"provider-id", "provider-zone", "provider-payload", "provider-status", "zone-order", "query", "expanded-cards", "nicegui-widgets", "historical-sequence", "degraded-providers"}:
    assert required in ids, required
for classification in CLASSIFICATIONS:
    assert inv["classification_counts"][classification] > 0, classification
assert len(inv["security_constraints"]) >= 8
assert all((ROOT / rel).is_file() for rel in REQUIRED_SOURCES)
print("OIF2A_COVERAGE_OK")
