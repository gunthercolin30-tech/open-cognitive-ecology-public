import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = (ROOT / "ontology" / "civilization_theorem_checker.py").read_text(encoding="utf-8")

mutations = {
    "validated_threshold": ('"validated": 0.80', '"validated": 0.20'),
    "contradiction_ignored": ("if contradictory:", "if False and contradictory:"),
    "counterexample_ignored": ("(0.5 if counterexamples else 1.0)", "(1.0 if counterexamples else 1.0)"),
    "applicability_ignored": ("if not applicable:", "if False and not applicable:"),
}

probe = r'''from civilization_theorem_checker import CivilizationTheoremChecker
c = CivilizationTheoremChecker()
base = {"tested_at_utc": "2026-07-13T12:00:00Z", "property_scores": {name: 0.90 for name in c.PROPERTY_ORDER}}
low = dict(base); low["property_scores"] = dict(base["property_scores"]); low["property_scores"]["coordination"] = 0.50
assert c.step(low, False)["property_statuses"]["coordination"] == "NOT_VALIDATED"
contra = dict(base); contra["contradictions"] = {"resilience": [{"id": "C"}]}
assert c.step(contra, False)["property_statuses"]["resilience"] == "NOT_VALIDATED"
ce = dict(base); ce["counterexamples"] = {"diversity": [{"id": "CE"}]}
r = c.step(ce, False); item = next(x for x in r["property_tests"] if x["property"] == "diversity")
assert item["confidence"] < 0.90
na = dict(base); na["property_applicability"] = {"local_autonomy": False}
assert c.step(na, False)["property_statuses"]["local_autonomy"] == "NOT_APPLICABLE"
'''

for name, (old, new) in mutations.items():
    assert old in SOURCE, f"mutation anchor missing: {name}"
    mutant = SOURCE.replace(old, new, 1)
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        (temp / "civilization_theorem_checker.py").write_text(mutant, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=str(temp),
            env={"PYTHONPATH": str(temp)},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert completed.returncode != 0, f"surviving mutation: {name}"

print("AW13_MUTATION_TEST_OK")
