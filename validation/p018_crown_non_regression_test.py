import hashlib
from pathlib import Path
from ontology import dna_registry, dna_rule_contract, dna_stack, minimal_dna

ROOT = Path.home() / "open-cognitive-ecology"

def main():
    assert minimal_dna.PRIMITIVE == "minimal_architectural_dna"
    assert dna_stack.validate_stack()["valid"] is True
    assert dna_registry.validate_registry()["valid"] is True
    assert dna_rule_contract.P018_SCOPE == "P018_ONLY"
    assert dna_rule_contract.contract_manifest()["p017_registry_schema"] == dna_registry.P017_SCHEMA_VERSION
    lock = ROOT / "validation_evidence" / "p017_final_lock_report.json"
    assert lock.is_file() and lock.stat().st_size > 0
    assert len(hashlib.sha256(lock.read_bytes()).hexdigest()) == 64
    print("P018_CROWN_NON_REGRESSION_TEST_OK")

if __name__ == "__main__":
    main()
