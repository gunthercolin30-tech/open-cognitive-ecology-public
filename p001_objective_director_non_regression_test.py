from pathlib import Path
from validation.p001_objective_director import FUNCTIONAL_INVARIANTS, audit

ROOT = Path(__file__).resolve().parent
before = dict(FUNCTIONAL_INVARIANTS)
result = audit(ROOT)

assert result["functional_invariants"] == before
assert result["functional_invariants"] == {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}
assert result["modifies_production_code"] is False
print("P001_NON_REGRESSION_OK")
