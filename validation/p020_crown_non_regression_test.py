from pathlib import Path
from ontology import minimal_dna, dna_stack, dna_registry, dna_rule_contract, dna_severity_model
from ontology import dna_inheritance as d

ROOT = Path.home() / "open-cognitive-ecology"

assert getattr(minimal_dna, "PRIMITIVE", None) == "minimal_architectural_dna"
assert dna_stack.validate_stack()
assert dna_registry.validate_registry()
assert dna_severity_model.SEVERITY_LEVELS == (
    "ADVISORY", "STANDARD", "STRICT", "CONSTITUTIONAL",
)

p018 = {
    "rule_id": "P018:p020-crown",
    "layer": "DNA-0",
    "scope": "fixture",
    "severity": "UNSPECIFIED_PENDING_P019",
    "rationale": "P020 crown predecessor check",
    "enforcement": "UNKNOWN",
    "tests": (),
    "exceptions": (),
    "modification_authority": "UNKNOWN",
    "version": "1",
    "provenance": "P020-crown",
}
assert dna_rule_contract.validate_rule_contract(p018)

p019_lock = ROOT / "validation_evidence" / "p019_final_lock_report.json"
assert p019_lock.is_file() and p019_lock.stat().st_size > 0

m = d.inheritance_manifest()
assert m["scope"] == "P020_ONLY"
assert m["transversal_referentials"]["world_models_dependency"] is None
assert m["boundaries"]["does_not_define_p021_mutation_protocol"] is True
assert m["boundaries"]["functional_conclusion_only"] is True
assert m["boundaries"]["phenomenology_undetermined"] is True

print("P020_CROWN_NON_REGRESSION_TEST_OK")
