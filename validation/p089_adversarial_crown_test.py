from copy import deepcopy

import ontology.dna_f1_f18 as p089


def main():
    # 1. Exact namespace: no missing/duplicate/extra F-rule.
    table = p089.canonical_table()
    ids = tuple(row["id"] for row in table)
    assert ids == tuple("F%d" % i for i in range(1, 19))
    assert len(ids) == len(set(ids)) == 18

    # 2. Exact partition: values and machinery cannot overlap or leak.
    assert set(p089.DNA_VALUES).isdisjoint(set(p089.DNA_MACHINERY))
    assert set(p089.DNA_VALUES + p089.DNA_MACHINERY) == set(ids)
    assert set(p089.DNA_MACHINERY) == {"F13", "F14", "F15", "F16"}

    # 3. Canonical F18 cannot be weakened/demoted by mutating returned structures.
    f18 = p089.get_rule("F18")
    f18["status"] = "PROPOSED_PENDING_CANONICAL_REVIEW"
    f18["definition"] = "tampered"
    assert p089.get_rule("F18")["status"] == "CANONICAL"
    assert p089.get_rule("F18")["definition"] != "tampered"

    # 4. F17/F18 semantic and reuse boundaries remain distinct.
    f17 = p089.get_rule("F17")
    f18 = p089.get_rule("F18")
    assert f17["id"] != f18["id"]
    assert f17["definition"] != f18["definition"]
    assert set(f17["reuse_interfaces"]) != set(f18["reuse_interfaces"])
    assert "humaine" in f17["definition"]
    assert "biodiversité" in f18["definition"]

    # 5. Unknown identifiers fail closed, including malformed aliases.
    for bad in ("F0", "F19", "f1", "F01", "", None, "M1"):
        try:
            p089.get_rule(bad)
        except KeyError:
            pass
        else:
            raise AssertionError("unknown/malformed identifier accepted: %r" % (bad,))

    # 6. P090 leakage prohibited.
    manifest = p089.manifest()
    assert manifest["scope"] == "P089_ONLY"
    assert not any(key.lower().startswith("metarule") for key in manifest)
    assert any("does not implement P090" in x for x in manifest["boundaries"])

    # 7. Downstream P061-P086 cannot become execution prerequisites.
    assert any("P061-P086" in x and "not execution prerequisites" in x
               for x in manifest["boundaries"])

    # 8. P088 cryptographic anchoring remains exact.
    assert manifest["upstream_p088_final_lock"] == (
        "f1a7d4adf322378726d9c0f7f481c8c8fe820fac62e3d08e6b2094be2f9b9b59"
    )

    # 9. Manifest/table outputs are non-mutating and deterministic.
    m1 = p089.manifest()
    m2 = p089.manifest()
    assert m1 == m2
    tampered = deepcopy(m1)
    tampered["rules"][0]["definition"] = "tampered"
    tampered["dna_values"] = ()
    assert p089.manifest() == m2

    # 10. No implicit runtime authority / epistemic leakage.
    assert any("No runtime authority" in x for x in manifest["boundaries"])
    assert manifest["functional_conclusion_only"] is True
    assert manifest["phenomenology_undetermined"] is True

    # 11. Every rule exposes a reuse interface without claiming proof.
    for row in table:
        assert isinstance(row["reuse_interfaces"], tuple)
        assert len(row["reuse_interfaces"]) >= 1
        assert row["modification_authority"] == "governed_DNA_amendment"
    assert any("not automatic proof" in x for x in manifest["boundaries"])

    print("P089_ADVERSARIAL_CROWN_OK")
    print("namespace_integrity=PASS")
    print("partition_integrity=PASS")
    print("f18_canonical_anti_weakening=PASS")
    print("f17_f18_separation=PASS")
    print("malformed_identifier_fail_closed=PASS")
    print("p090_non_leakage=PASS")
    print("downstream_dependency_boundary=PASS")
    print("p088_anchor=PASS")
    print("manifest_non_mutation=PASS")
    print("runtime_epistemic_boundary=PASS")
    print("reuse_interface_contract=PASS")


if __name__ == "__main__":
    main()
