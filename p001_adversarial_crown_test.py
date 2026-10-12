from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "validation" / "p001_objective_director.py"

spec = importlib.util.spec_from_file_location("_p001_crown_target", TARGET)
assert spec and spec.loader
p001 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p001)

# ------------------------------------------------------------
# 1. Determinism: same repository state -> same semantic result hash.
# ------------------------------------------------------------
a = p001.audit(ROOT)
b = p001.audit(ROOT)
assert a["result_hash"] == b["result_hash"]
assert a["decision"] == b["decision"] == "P001_REPRESENTABLE"
print("P001_CROWN_DETERMINISM_OK")

# ------------------------------------------------------------
# 2. Every canonical stage must fail closed when all evidence
#    candidates for that stage are absent.
# ------------------------------------------------------------
with tempfile.TemporaryDirectory() as td:
    fake = Path(td)
    (fake / "ontology").mkdir()
    # Populate all referenced modules first.
    all_modules = set()
    for mods in p001.REPRESENTATION_MAP.values():
        all_modules.update(mods)
    all_modules.update(p001.GUARD_MODULES)
    for module in all_modules:
        path = fake / "ontology" / f"{module}.py"
        path.write_text("VALUE = 1\n", encoding="utf-8")

    for stage, modules in p001.REPRESENTATION_MAP.items():
        removed = []
        for module in modules:
            path = fake / "ontology" / f"{module}.py"
            if path.exists():
                removed.append((path, path.read_bytes()))
                path.unlink()
        result = p001.audit(fake)
        assert result["loop_coverage"][stage]["status"] == "UNKNOWN", stage
        assert result["decision"] == "UNKNOWN", stage
        for path, raw in removed:
            path.write_bytes(raw)
print("P001_CROWN_STAGE_REMOVAL_OK")

# ------------------------------------------------------------
# 3. Every guard is individually mandatory.
# ------------------------------------------------------------
with tempfile.TemporaryDirectory() as td:
    fake = Path(td)
    (fake / "ontology").mkdir()
    all_modules = set()
    for mods in p001.REPRESENTATION_MAP.values():
        all_modules.update(mods)
    all_modules.update(p001.GUARD_MODULES)
    for module in all_modules:
        (fake / "ontology" / f"{module}.py").write_text("VALUE = 1\n", encoding="utf-8")

    for guard in p001.GUARD_MODULES:
        path = fake / "ontology" / f"{guard}.py"
        raw = path.read_bytes()
        path.unlink()
        result = p001.audit(fake)
        assert result["guard_coverage"][guard]["status"] == "UNKNOWN", guard
        assert result["decision"] == "UNKNOWN", guard
        path.write_bytes(raw)
print("P001_CROWN_GUARD_REMOVAL_OK")

# ------------------------------------------------------------
# 4. False-positive probe.
# Current P001 v1 uses file-level architectural evidence.
# A fake same-name module MUST NOT be silently interpreted as
# implementation evidence by the hardened auditor.
# ------------------------------------------------------------
with tempfile.TemporaryDirectory() as td:
    fake = Path(td)
    (fake / "ontology").mkdir()
    all_modules = set()
    for mods in p001.REPRESENTATION_MAP.values():
        all_modules.update(mods)
    all_modules.update(p001.GUARD_MODULES)
    for module in all_modules:
        (fake / "ontology" / f"{module}.py").write_text(
            "# intentionally empty adversarial placeholder\n",
            encoding="utf-8",
        )
    result = p001.audit(fake)
    # This assertion intentionally detects the known weakness in v1.
    assert result["decision"] != "P001_REPRESENTABLE", (
        "FALSE POSITIVE: filename-only placeholders satisfy P001"
    )
print("P001_CROWN_FALSE_POSITIVE_OK")
