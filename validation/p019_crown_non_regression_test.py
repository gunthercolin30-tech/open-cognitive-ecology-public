import hashlib
from pathlib import Path

from ontology import (
    dna_registry,
    dna_rule_contract,
    dna_severity_model,
    dna_stack,
    minimal_dna,
)

ROOT = Path.home() / "open-cognitive-ecology"

def main():
    assert minimal_dna.PRIMITIVE == "minimal_architectural_dna"
    assert dna_stack.validate_stack()["valid"] is True
    assert dna_registry.validate_registry()["valid"] is True
    assert dna_rule_contract.P018_SCOPE == "P018_ONLY"
    assert dna_severity_model.P019_SCOPE == "P019_ONLY"

    p018_lock = ROOT / "validation_evidence/p018_final_lock_report.json"
    assert p018_lock.is_file() and p018_lock.stat().st_size > 0
    assert len(hashlib.sha256(p018_lock.read_bytes()).hexdigest()) == 64

    m = dna_severity_model.severity_manifest()
    assert m["p018_contract_schema"] == dna_rule_contract.P018_SCHEMA_VERSION
    assert m["levels"] == ("ADVISORY", "STANDARD", "STRICT", "CONSTITUTIONAL")
    assert m["boundaries"]["does_not_define_p020_inheritance"] is True
    assert m["transversal_referentials"]["world_models_dependency"] is None

    print("P019_CROWN_NON_REGRESSION_TEST_OK")

if __name__ == "__main__":
    main()
