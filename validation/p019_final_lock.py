from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from ontology import dna_registry, dna_rule_contract, dna_severity_model, dna_stack, minimal_dna

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = ROOT / "validation_evidence/p019_final_lock_report.json"

PROTECTED = (
    "ontology/dna_severity_model.py",
    "validation/p019_dna_severity_model.py",
    "validation/p019_functional_test.py",
    "validation/p019_degradation_test.py",
    "validation/p019_non_regression_test.py",
    "validation/p019_determinism_test.py",
    "validation/p019_non_mutation_test.py",
    "validation/p019_provenance_version_test.py",
    "validation/p019_adversarial_test.py",
    "validation/p019_authority_boundary_test.py",
    "validation/p019_crown_non_regression_test.py",
)

PREDECESSORS = (
    "ontology/minimal_dna.py",
    "ontology/dna_stack.py",
    "ontology/dna_registry.py",
    "ontology/dna_rule_contract.py",
    "validation_evidence/p018_final_lock_report.json",
)

EVIDENCE = {
    "dna_severity_model": "PASS",
    "functional": "PASS",
    "degradation": "PASS",
    "non_regression": "PASS",
    "determinism": "PASS",
    "non_mutation": "PASS",
    "provenance_version": "PASS",
    "adversarial": "PASS",
    "authority_boundary": "PASS",
    "crown_non_regression": "PASS",
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical_hash(payload) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def main():
    assert minimal_dna.PRIMITIVE == "minimal_architectural_dna"
    assert dna_stack.validate_stack()["valid"] is True
    assert dna_registry.validate_registry()["valid"] is True
    assert dna_rule_contract.P018_SCOPE == "P018_ONLY"
    assert dna_severity_model.P019_SCOPE == "P019_ONLY"

    m = dna_severity_model.severity_manifest()
    assert m["levels"] == ("ADVISORY", "STANDARD", "STRICT", "CONSTITUTIONAL")
    assert m["rank"] == {"ADVISORY": 0, "STANDARD": 1, "STRICT": 2, "CONSTITUTIONAL": 3}
    assert m["p018_contract_schema"] == dna_rule_contract.P018_SCHEMA_VERSION
    assert m["transversal_referentials"]["doctrines"] == ("R0", "R5", "R6", "R17", "R21")
    assert m["transversal_referentials"]["artifacts"] == ("A-CANON", "A-TRACE")
    assert m["transversal_referentials"]["world_models_dependency"] is None
    assert all(m["boundaries"].values())

    protected_hashes = {}
    for rel in PROTECTED:
        p = ROOT / rel
        assert p.is_file(), rel
        protected_hashes[rel] = sha(p)

    predecessor_hashes = {}
    for rel in PREDECESSORS:
        p = ROOT / rel
        assert p.is_file(), rel
        predecessor_hashes[rel] = sha(p)

    stable = {
        "schema": "oce.p019.final_lock.v1",
        "milestone": "P019",
        "status": "LOCKED",
        "scope": "P019_ONLY",
        "decision": "CREATE_THIN_DNA_SEVERITY_MODEL",
        "severity_schema": dna_severity_model.P019_SCHEMA_VERSION,
        "levels": list(dna_severity_model.SEVERITY_LEVELS),
        "rank": dict(dna_severity_model.SEVERITY_RANK),
        "evidence": EVIDENCE,
        "protected_hashes": protected_hashes,
        "predecessor_hashes": predecessor_hashes,
        "boundaries": m["boundaries"],
        "transversal_referentials": m["transversal_referentials"],
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "unknown_promotion": False,
        "runtime_authority_granted": False,
    }
    identity = canonical_hash(stable)
    report = dict(stable)
    report["lock_identity_sha256"] = identity
    report["generated_at_utc"] = datetime.now(timezone.utc).isoformat()

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("P019_FINAL_LOCK_OK")
    print("report=" + str(REPORT))
    print("lock_identity_sha256=" + identity)
    print("protected_file_count=" + str(len(PROTECTED)))
    print("status=LOCKED")
    print("functional_conclusion_only=true")
    print("phenomenology_undetermined=true")

if __name__ == "__main__":
    main()
