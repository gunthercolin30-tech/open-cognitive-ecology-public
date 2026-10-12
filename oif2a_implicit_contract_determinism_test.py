from pathlib import Path
import hashlib
from oif.audit.implicit_contract_consolidator import build_inventory, _canonical_json, build_markdown

ROOT = Path.home() / "open-cognitive-ecology"
a = build_inventory(ROOT)
b = build_inventory(ROOT)
assert _canonical_json(a) == _canonical_json(b)
assert build_markdown(a) == build_markdown(b)
assert a["inventory_sha256"] == b["inventory_sha256"]
print("OIF2A_DETERMINISM_OK", hashlib.sha256(_canonical_json(a)).hexdigest())
