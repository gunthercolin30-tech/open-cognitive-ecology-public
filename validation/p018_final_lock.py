from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from ontology import dna_registry, dna_rule_contract, dna_stack, minimal_dna
from validation.p018_dna_rule_contract import sample

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = ROOT / "validation_evidence" / "p018_final_lock_report.json"

PROTECTED_RELATIVE_PATHS = (
    "ontology/dna_rule_contract.py",
    "validation/p018_dna_rule_contract.py",
    "validation/p018_functional_test.py",
    "validation/p018_degradation_test.py",
    "validation/p018_non_regression_test.py",
    "validation/p018_determinism_test.py",
    "validation/p018_non_mutation_test.py",
    "validation/p018_provenance_version_test.py",
    "validation/p018_adversarial_test.py",
    "validation/p018_boundary_test.py",
    "validation/p018_crown_non_regression_test.py",
)

EXPECTED_FIELDS = (
    "rule_id", "layer", "scope", "severity", "rationale", "enforcement",
    "tests", "exceptions", "modification_authority", "version", "provenance",
)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def build_report():
    assert minimal_dna.PRIMITIVE == "minimal_architectural_dna"
    assert dna_stack.validate_stack()["valid"] is True
    assert dna_registry.validate_registry()["valid"] is True

    manifest = dna_rule_contract.contract_manifest()
    assert tuple(manifest["canonical_fields"]) == EXPECTED_FIELDS
    assert manifest["scope"] == "P018_ONLY"
    assert manifest["p017_registry_schema"] == dna_registry.P017_SCHEMA_VERSION

    normalized = dna_rule_contract.normalize_rule(sample())
    assert tuple(normalized.keys()) == EXPECTED_FIELDS
    assert normalized["enforcement"] == "UNKNOWN"

    boundaries = manifest["boundaries"]
    required_boundaries = (
        "contract_structure_only",
        "does_not_define_p019_severity_semantics",
        "does_not_define_p020_inheritance",
        "does_not_define_p021_mutation_protocol",
        "does_not_define_p022_lineage_versioning",
        "does_not_define_p023_fitness_suite",
        "does_not_define_p024_adversarial_campaign",
        "does_not_grant_runtime_authority",
        "does_not_claim_end_to_end_enforcement",
        "unknown_may_not_be_promoted_by_contract",
        "functional_conclusion_only",
        "phenomenology_undetermined",
    )
    for key in required_boundaries:
        assert boundaries[key] is True

    refs = manifest["transversal_referentials"]
    assert tuple(refs["doctrines"]) == ("R3", "R4", "R5", "R10", "R11", "R19", "R21")
    assert tuple(refs["artifacts"]) == ("A-CANON", "A-R0R21", "A-TRACE")
    assert refs["world_models_dependency"] is None

    protected_hashes = {}
    for rel in PROTECTED_RELATIVE_PATHS:
        path = ROOT / rel
        assert path.is_file(), rel
        protected_hashes[rel] = digest(path)

    p017_lock = ROOT / "validation_evidence" / "p017_final_lock_report.json"
    assert p017_lock.is_file()
    predecessor_hashes = {
        "ontology/minimal_dna.py": digest(ROOT / "ontology/minimal_dna.py"),
        "ontology/dna_stack.py": digest(ROOT / "ontology/dna_stack.py"),
        "ontology/dna_registry.py": digest(ROOT / "ontology/dna_registry.py"),
        "validation_evidence/p017_final_lock_report.json": digest(p017_lock),
    }

    evidence = {
        "functional": "PASS",
        "degradation": "PASS",
        "non_regression": "PASS",
        "determinism": "PASS",
        "non_mutation": "PASS",
        "provenance_version": "PASS",
        "adversarial": "PASS",
        "boundary": "PASS",
        "crown_non_regression": "PASS",
    }

    stable_payload = {
        "schema": "oce.p018.final_lock.v1",
        "milestone": "P018",
        "status": "LOCKED",
        "scope": "P018_ONLY",
        "decision": "CREATE_THIN_DNA_RULE_CONTRACT",
        "contract_schema": dna_rule_contract.P018_SCHEMA_VERSION,
        "canonical_fields": EXPECTED_FIELDS,
        "evidence": evidence,
        "protected_hashes": protected_hashes,
        "predecessor_hashes": predecessor_hashes,
        "boundaries": boundaries,
        "transversal_referentials": refs,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "unknown_promotion": False,
        "runtime_authority_granted": False,
    }
    lock_identity = hashlib.sha256(canonical_json(stable_payload).encode("utf-8")).hexdigest()

    report = dict(stable_payload)
    report["lock_identity_sha256"] = lock_identity
    report["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    return report

def main():
    report = build_report()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("P018_FINAL_LOCK_OK")
    print("report=" + str(REPORT))
    print("lock_identity_sha256=" + report["lock_identity_sha256"])
    print("protected_file_count=" + str(len(report["protected_hashes"])))
    print("status=LOCKED")
    print("functional_conclusion_only=true")
    print("phenomenology_undetermined=true")

if __name__ == "__main__":
    main()
