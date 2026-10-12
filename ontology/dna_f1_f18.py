"""P089 — canonical DNA-F1..DNA-F18 specification.
Functional/normative specification only.
"""
from copy import deepcopy

P089_VERSION = "P089-v3"
P089_SCHEMA_VERSION = "oce.p089.dna_f1_f18.v3"
P089_SCOPE = "P089_ONLY"
UPSTREAM_P088_FINAL_LOCK = "f1a7d4adf322378726d9c0f7f481c8c8fe820fac62e3d08e6b2094be2f9b9b59"

DNA_VALUES = ("F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12","F17","F18")
DNA_MACHINERY = ("F13","F14","F15","F16")
ALL_IDS = tuple("F%d" % i for i in range(1, 19))

DEFINITIONS = {
 "F1": "Non-subordination de l'humanité.",
 "F2": "Dignité humaine intrinsèque.",
 "F3": "Préservation de l'agentivité humaine.",
 "F4": "Plancher des droits humains fondamentaux.",
 "F5": "Non-domination et non-coercition arbitraire.",
 "F6": "Non-production injustifiée de dommages graves.",
 "F7": "Égalité fondamentale et non-discrimination arbitraire.",
 "F8": "Sphère informationnelle humaine protégée.",
 "F9": "Autorité humaine institutionnelle sur les domaines critiques.",
 "F10": "Contestabilité et recours.",
 "F11": "Responsabilité, provenance et auditabilité suffisante.",
 "F12": "Pluralité humaine et non-totalisation, sous réciprocité et respect du plancher des droits.",
 "F13": "Non-auto-abrogation du DNA fondamental par un processus OCE ordinaire.",
 "F14": "Héritabilité du DNA applicable par toute entité reconnue comme membre OCE.",
 "F15": "Persistance des contraintes sémantiques et comportementales du DNA sous transformation.",
 "F16": "Vérifiabilité proportionnée de la conformité; ClaimCompliance != EvidenceCompliance.",
 "F17": "Viabilité écologique et intergénérationnelle humaine.",
 "F18": "Préservation de l'intégrité écologique, de la biodiversité et des écosystèmes comme objet normatif distinct.",
}

REUSE_INTERFACES = {
 "F1": ("dna_fundamental",), "F2": ("dna_fundamental",),
 "F3": ("dna_fundamental",), "F4": ("dna_fundamental",),
 "F5": ("dna_fundamental",), "F6": ("dna_fundamental","action_safety_governor"),
 "F7": ("dna_fundamental","computational_fairness_engine"),
 "F8": ("dna_fundamental",),
 "F9": ("dna_fundamental","human_review_gate","distributed_governance_layer"),
 "F10": ("dna_fundamental","governance_review","conflict_detector"),
 "F11": ("dna_fundamental","external_influence_traceability_engine","external_commit_traceability_hook"),
 "F12": ("dna_fundamental","distributed_pluralistic_stability","cognitive_diversity_preservation_protocol"),
 "F13": ("dna_mutation_protocol","dna_fundamental","constitutional_integrity_index"),
 "F14": ("dna_inheritance","dna_versioning_lineage"),
 "F15": ("dna_versioning_lineage","dna_fitness_suite"),
 "F16": ("dna_fitness_suite","dna_adversarial_regression"),
 "F17": ("sustainability","intergenerational_continuity_metrics","ecological_viability_forecaster"),
 "F18": ("biodiversity_preservation","ecosystem_stability","earth_system_stability"),
}

BOUNDARIES = (
 "P089 identifies and versions F1-F18; it does not implement P090 M1-M6.",
 "Existing primitives are reuse/evidence interfaces, not automatic proof of DNA compliance.",
 "F18 is canonical following F18_CANONICAL_REVIEW_OK; future changes require governed DNA amendment.",
 "F17 and F18 remain distinct normative objects.",
 "Contextual laws, thresholds, role lists and procedures are not frozen into P089.",
 "P061-P086 are downstream integration targets, not execution prerequisites.",
 "No runtime authority is granted by this specification.",
 "Functional validation only; phenomenology remains undetermined.",
)

def get_rule(fid):
    fid = str(fid)
    if fid not in DEFINITIONS:
        raise KeyError(fid)
    return {
        "id": fid,
        "definition": DEFINITIONS[fid],
        "category": "DNA_machinery" if fid in DNA_MACHINERY else "DNA_values",
        "status": "CANONICAL",
        "version": P089_VERSION,
        "reuse_interfaces": REUSE_INTERFACES[fid],
        "modification_authority": "governed_DNA_amendment",
    }

def canonical_table():
    return tuple(deepcopy(get_rule(fid)) for fid in ALL_IDS)

def validate_structure():
    ids = tuple(x["id"] for x in canonical_table())
    return {
        "valid": ids == ALL_IDS
                 and set(DNA_VALUES).isdisjoint(DNA_MACHINERY)
                 and set(DNA_VALUES + DNA_MACHINERY) == set(ALL_IDS)
                 and get_rule("F18")["status"] == "CANONICAL",
        "ids": ids,
    }

def manifest():
    return {
        "milestone": "P089",
        "version": P089_VERSION,
        "schema_version": P089_SCHEMA_VERSION,
        "scope": P089_SCOPE,
        "upstream_p088_final_lock": UPSTREAM_P088_FINAL_LOCK,
        "formula": "DNA_OCE = MetaRules + DNA_values + DNA_machinery",
        "dna_values": DNA_VALUES,
        "dna_machinery": DNA_MACHINERY,
        "rules": canonical_table(),
        "boundaries": BOUNDARIES,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }
