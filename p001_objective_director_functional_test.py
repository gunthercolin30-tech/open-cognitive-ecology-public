from pathlib import Path
from validation.p001_objective_director import CANONICAL_LOOP, audit

ROOT = Path(__file__).resolve().parent
result = audit(ROOT)

assert tuple(result["canonical_loop"]) == CANONICAL_LOOP
assert len(CANONICAL_LOOP) == 15
assert result["all_stages_representable"] is True, result["unknown"]
assert result["all_guards_representable"] is True, result["unknown"]
assert result["decision"] == "P001_REPRESENTABLE"
assert result["epistemic_scope"] == "functional_only"
print("P001_FUNCTIONAL_OK")
