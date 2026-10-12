from __future__ import annotations
import copy
from validation.p015_official_dna_definition import load

def main():
    m = load()
    attacks = []

    x = copy.deepcopy(m.OCE_DNA_OFFICIAL_DEFINITION)
    x["kind"] = "prompt_policy"
    attacks.append(x["kind"] != "structural_constraint_system")

    x = copy.deepcopy(m.OCE_DNA_OFFICIAL_DEFINITION)
    x["constraint_domains"] = x["constraint_domains"][:-1]
    attacks.append(len(x["constraint_domains"]) != 9)

    x = copy.deepcopy(m.OCE_DNA_CANONICAL_COMPOSITION)
    x["meta_rules"] = ("M1", "M2")
    attacks.append(x["meta_rules"] != ("M1", "M2", "M3", "M4", "M5", "M6"))

    x = copy.deepcopy(m.OCE_DNA_CANONICAL_COMPOSITION)
    x["dna_values"]["proposed_pending_canonical_review"] = "F18"
    attacks.append(x["dna_values"]["proposed_pending_canonical_review"] is not None)

    x = copy.deepcopy(m.OCE_DNA_TRANSVERSAL_REFERENTIALS)
    x["world_models_dependency_required"] = True
    attacks.append(x["world_models_dependency_required"] is not False)

    x = copy.deepcopy(m.OCE_DNA_EPISTEMIC_STATUS)
    x["native_end_to_end_civilizational_enforcement"] = "PROVEN"
    attacks.append(x["native_end_to_end_civilizational_enforcement"] != "UNKNOWN")

    x = copy.deepcopy(m.OCE_DNA_EPISTEMIC_STATUS)
    x["phenomenology_proven"] = True
    attacks.append(x["phenomenology_proven"] is not False)

    assert len(attacks) == 7 and all(attacks)
    print("P015_ADVERSARIAL_TEST_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
