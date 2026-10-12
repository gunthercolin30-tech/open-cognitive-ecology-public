from __future__ import annotations
from copy import deepcopy
from ontology import dna_registry

def must_fail(records):
    result = dna_registry.validate_registry(tuple(records))
    assert result["valid"] is False, result

def main():
    base = list(dna_registry.registry_entries())
    assert dna_registry.validate_registry(tuple(base))["valid"] is True

    # Duplicate discovery identifier.
    x = deepcopy(base)
    x.append(deepcopy(x[0]))
    must_fail(x)

    # Unknown / forged DNA layer.
    x = deepcopy(base)
    x[0]["layer"] = "DNA-P018-FORGED"
    must_fail(x)

    # Missing and empty provenance.
    x = deepcopy(base)
    x[0].pop("provenance")
    must_fail(x)
    x = deepcopy(base)
    x[0]["provenance"] = ""
    must_fail(x)

    # Missing / malformed version.
    x = deepcopy(base)
    x[0]["version"] = ""
    must_fail(x)
    x = deepcopy(base)
    x[0]["version"] = None
    must_fail(x)

    # Invalid dependency container.
    x = deepcopy(base)
    x[0]["dependencies"] = ["dna_stack"]
    must_fail(x)

    # Invalid test coverage container / empty coverage.
    x = deepcopy(base)
    x[0]["test_coverage"] = []
    must_fail(x)
    x = deepcopy(base)
    x[0]["test_coverage"] = ()
    must_fail(x)

    # Epistemic privilege escalation must be rejected.
    for promoted in ("PASS", "TRUE", "ENFORCED", True):
        x = deepcopy(base)
        x[0]["enforcement_status"] = promoted
        must_fail(x)

    # Deep-copy isolation: caller mutation cannot mutate authoritative registry.
    external = dna_registry.registry_entries()
    original_scope = dna_registry.registry_entries()[0]["scope"]
    external[0]["scope"] = "ATTACKED"
    external[0]["dependencies"] = ("ATTACKED",)
    fresh = dna_registry.registry_entries()
    assert fresh[0]["scope"] == original_scope
    assert fresh[0]["dependencies"] != ("ATTACKED",)

    # Manifest is also isolated.
    manifest = dna_registry.registry_manifest()
    manifest["boundaries"]["does_not_grant_runtime_authority"] = False
    manifest["entries"][0]["enforcement_status"] = "PASS"
    fresh_manifest = dna_registry.registry_manifest()
    assert fresh_manifest["boundaries"]["does_not_grant_runtime_authority"] is True
    assert fresh_manifest["entries"][0]["enforcement_status"] == "UNKNOWN"

    # P017 may discover but must not silently become P018.
    forbidden_boundary_keys = {
        "severity_model",
        "inheritance_model",
        "mutation_protocol",
        "modification_authority",
    }
    assert forbidden_boundary_keys.isdisjoint(dna_registry.P017_BOUNDARIES)
    assert dna_registry.P017_BOUNDARIES["does_not_define_p018_rule_contract"] is True
    assert dna_registry.P017_BOUNDARIES["does_not_grant_runtime_authority"] is True
    assert dna_registry.P017_BOUNDARIES["does_not_claim_end_to_end_enforcement"] is True

    print("P017_ADVERSARIAL_TEST_OK")

if __name__ == "__main__":
    main()
