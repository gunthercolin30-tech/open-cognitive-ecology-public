from pathlib import Path
import hashlib, json
ROOT = Path(__file__).resolve().parent
baseline = json.loads((ROOT / "oif2g_crown_protected_hashes.json").read_text(encoding="utf-8"))
for rel, expected in baseline.items():
    actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    assert actual == expected, rel
print("OIF2G_CROWN_NON_MODIFICATION_OK")
