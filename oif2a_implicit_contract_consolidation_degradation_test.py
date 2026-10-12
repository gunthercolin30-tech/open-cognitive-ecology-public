from pathlib import Path
import shutil, tempfile
from oif.audit.implicit_contract_consolidator import build_inventory, REQUIRED_SOURCES

ROOT = Path.home() / "open-cognitive-ecology"
with tempfile.TemporaryDirectory() as tmp:
    test_root = Path(tmp)
    for rel in REQUIRED_SOURCES:
        src = ROOT / rel
        dst = test_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    (test_root / REQUIRED_SOURCES[0]).unlink()
    try:
        build_inventory(test_root)
    except FileNotFoundError as exc:
        assert REQUIRED_SOURCES[0] in str(exc)
    else:
        raise AssertionError("missing source must fail closed")
assert not list(ROOT.rglob("*.oif2a_tmp"))
print("OIF2A_DEGRADATION_OK")
