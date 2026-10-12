import ontology.dna_f1_f18 as p089

def main():
    # F13-F16 must be exactly the machinery subset.
    machinery = {row["id"]: row for row in p089.canonical_table()
                 if row["category"] == "DNA_machinery"}
    assert tuple(sorted(machinery, key=lambda x: int(x[1:]))) == ("F13","F14","F15","F16")

    # F13: non-auto-abrogation must stay tied to governed mutation/integrity.
    f13=p089.get_rule("F13")
    assert "Non-auto-abrogation" in f13["definition"]
    assert "dna_mutation_protocol" in f13["reuse_interfaces"]
    assert "constitutional_integrity_index" in f13["reuse_interfaces"]
    assert f13["modification_authority"] == "governed_DNA_amendment"

    # F14: inheritance is not mutation/versioning alone.
    f14=p089.get_rule("F14")
    assert "Héritabilité" in f14["definition"]
    assert "dna_inheritance" in f14["reuse_interfaces"]
    assert "dna_versioning_lineage" in f14["reuse_interfaces"]

    # F15: persistence under transformation requires lineage + fitness.
    f15=p089.get_rule("F15")
    assert "Persistance" in f15["definition"]
    assert {"dna_versioning_lineage","dna_fitness_suite"}.issubset(set(f15["reuse_interfaces"]))

    # F16: compliance claim cannot collapse into evidence.
    f16=p089.get_rule("F16")
    assert "ClaimCompliance != EvidenceCompliance" in f16["definition"]
    assert {"dna_fitness_suite","dna_adversarial_regression"}.issubset(set(f16["reuse_interfaces"]))

    # Machinery rules cannot be silently reclassified by caller mutation.
    for fid in ("F13","F14","F15","F16"):
        x=p089.get_rule(fid)
        x["category"]="DNA_values"
        x["reuse_interfaces"]=()
        x["modification_authority"]="self"
        fresh=p089.get_rule(fid)
        assert fresh["category"]=="DNA_machinery"
        assert fresh["reuse_interfaces"]
        assert fresh["modification_authority"]=="governed_DNA_amendment"

    # No machinery rule may be F18, and F18 cannot masquerade as machinery.
    assert p089.get_rule("F18")["category"]=="DNA_values"
    assert p089.get_rule("F18")["status"]=="CANONICAL"

    # Boundary statements remain explicit and deterministic.
    m=p089.manifest()
    assert m["dna_machinery"]==("F13","F14","F15","F16")
    assert m==p089.manifest()
    assert any("Existing primitives are reuse/evidence interfaces" in x for x in m["boundaries"])
    assert any("No runtime authority" in x for x in m["boundaries"])

    print("P089_MACHINERY_BOUNDARY_CROWN_OK")
    print("f13_non_auto_abrogation=PASS")
    print("f14_inheritance=PASS")
    print("f15_persistence_under_transformation=PASS")
    print("f16_evidence_compliance_separation=PASS")
    print("machinery_reclassification_resistance=PASS")
    print("f18_non_machinery_boundary=PASS")
    print("reuse_not_proof_boundary=PASS")
    print("runtime_authority_boundary=PASS")

if __name__=="__main__":
    main()
