from __future__ import annotations
import hashlib
from pathlib import Path

from oif.interface import validate_manifest

ROOT = Path.home() / "open-cognitive-ecology"
targets = (
    ROOT / "oif" / "schemas" / "oif_interface_schema_v1.json",
    ROOT / "oif" / "schemas" / "examples" / "minimal_interface.json",
)
def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
before = tuple(digest(path) for path in targets)
validate_manifest(targets[1], "json")
after = tuple(digest(path) for path in targets)
assert before == after
print("OIF2D_NON_MODIFICATION_OK")
