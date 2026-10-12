import json, tempfile
from pathlib import Path
from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker
with tempfile.TemporaryDirectory() as directory:
    checker = CivilizationTheoremChecker(Path(directory)); result = checker.step(build_context(), persist=True); path = Path(result["history_path"])
    path.write_text(path.read_text(encoding="utf-8")[:-5] + "xxxxx", encoding="utf-8")
    try: json.loads(path.read_text(encoding="utf-8").splitlines()[0]); corrupted = False
    except json.JSONDecodeError: corrupted = True
    assert corrupted
print("AW13_CORRUPTION_OK")
