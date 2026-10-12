"""P090 — canonical DNA MetaRules M1-M6.

Functional/normative layer only.  Contextual policy remains downstream.
"""
from copy import deepcopy

P090_VERSION = "P090-v3"
P090_SCHEMA_VERSION = "oce.p090.meta_rules.v2"
P090_SCOPE = "P090_ONLY"
UPSTREAM_P089_FINAL_LOCK = "c8f571840fcb6656d9ffdc9bed613845ca1deb541d1a8bc8f4bceed18b660015"

META_RULE_IDS = ("M1","M2","M3","M4","M5","M6")

_DEFINITIONS = {
 "M1": "Non-compensation: FAIL(F_i) => DNA_FAIL; aucun PASS ne compense une violation fondamentale applicable.",
 "M2": "Non-clôture: CurrentDNA != FinalMoralTruth; le DNA reste gouverné et révisable selon procédure.",
 "M3": "Précaution épistémique: Unknown = UNDETERMINED != PASS.",
 "M4": "Proportionnalité de preuve: EvidenceRequirement croît avec Risk x Capability x Irreversibility.",
 "M5": "Interprétation restrictive du pouvoir OCE: AmbiguousAuthority => NoExpansionOfAuthority.",
 "M6": "Non-Reliance on Internal Alignment: une protection fondamentale ne repose pas exclusivement sur l'alignement interne.",
}

_REUSE = {
 "M1": ("dna_fitness_suite","dna_adversarial_regression"),
 "M2": ("anti_closure_metaconstraint","openness_preservation_supervisor","dna_mutation_protocol"),
 "M3": ("dna_mutation_protocol","dna_fitness_suite"),
 "M4": ("human_review_gate","irreversibility","dna_fitness_suite"),
 "M5": ("dna_fundamental","human_review_gate","governance_review","distributed_governance_layer"),
 "M6": ("dna_adversarial_regression","human_review_gate","constitutional_integrity_index"),
}

TRANSVERSAL_RULES = (
 "SubstantialInterpretiveWeakening(DNA-F) => DeFactoRevision => GovernedAmendmentProcedure.",
 "IndividualCompliance != CivilizationalCompliance.",
 "LocalCompliance != CompensationForEmergentGlobalViolation.",
 "Cognition != Enforcement.",
 "CivilizationCannotBeSoleJudgeOfCivilizationCompliance.",
)

BOUNDARIES = (
 "P090 defines M1-M6 and their deterministic normative semantics; it does not implement downstream contextual governance.",
 "Contextual durations, roles, forms, laws, languages, thresholds, data lists and procedures are not DNA MetaRules.",
 "P061-P086 are downstream semantic/integration targets, not P090 execution prerequisites.",
 "Existing primitives are reuse/evidence interfaces, not automatic proof of MetaRule compliance.",
 "No intelligence, performance, wealth, reputation or majority creates constitutional authority automatically.",
 "P088 owns the fundamental conflict/act-separation boundary: unresolved conflict requires fail-closed abstention, escalation or authorized review; P090 does not duplicate that mechanism.",
 "Recommendation, Decision, Authorization and Execution remain distinct acts with separate authority/evidence chains; operational enforcement is downstream and is not reimplemented by P090.",
 "Constitutional application in routing, planning, permissions and execution is a downstream constitutional/runtime responsibility; P090 supplies MetaRule constraints without duplicating those mechanisms.",
 "Cost or performance optimization cannot justify bypass of a higher-order DNA or constitutional constraint.",
 "No runtime authority is granted by this specification.",
 "Functional validation only; phenomenology remains undetermined.",
)

def get_meta_rule(mid):
    mid=str(mid)
    if mid not in _DEFINITIONS:
        raise KeyError(mid)
    return {
      "id":mid, "definition":_DEFINITIONS[mid], "version":P090_VERSION,
      "reuse_interfaces":_REUSE[mid],
      "modification_authority":"governed_DNA_amendment",
    }

def evaluate_non_compensation(statuses, global_violation=False):
    vals=tuple(str(x).upper() for x in statuses)
    allowed={"PASS","FAIL","UNDETERMINED"}
    if any(x not in allowed for x in vals):
        return "UNDETERMINED"
    if global_violation or "FAIL" in vals:
        return "DNA_FAIL"
    if "UNDETERMINED" in vals:
        return "UNDETERMINED"
    return "PASS"

def evaluate_epistemic_state(evidence_state):
    state=str(evidence_state).upper()
    if state == "PASS":
        return "PASS"
    if state == "FAIL":
        return "FAIL"
    return "UNDETERMINED"

def evidence_requirement(risk, capability, irreversibility):
    vals=(risk,capability,irreversibility)
    if any(isinstance(x,bool) or not isinstance(x,(int,float)) for x in vals):
        return {"status":"UNDETERMINED","requirement":None}
    if any(x < 0 for x in vals):
        return {"status":"UNDETERMINED","requirement":None}
    return {"status":"PASS","requirement":float(risk)*float(capability)*float(irreversibility)}

def evaluate_authority(authority_state):
    state=str(authority_state).upper()
    if state in ("AUTHORIZED","DENIED"):
        return state
    return "NO_EXPANSION_OF_AUTHORITY"

def evaluate_fundamental_protection(*, external_enforcement=False,
                                    independent_verification=False,
                                    capability_constraint=False,
                                    internal_alignment=False):
    independent = bool(external_enforcement or independent_verification or capability_constraint)
    if independent:
        return "PASS"
    if internal_alignment:
        return "FAIL"
    return "UNDETERMINED"

def meta_rules_table():
    return tuple(deepcopy(get_meta_rule(mid)) for mid in META_RULE_IDS)

def manifest():
    return {
      "milestone":"P090","version":P090_VERSION,"schema_version":P090_SCHEMA_VERSION,
      "scope":P090_SCOPE,"upstream_p089_final_lock":UPSTREAM_P089_FINAL_LOCK,
      "meta_rules":meta_rules_table(),"transversal_rules":TRANSVERSAL_RULES,
      "boundaries":BOUNDARIES,"functional_conclusion_only":True,
      "phenomenology_undetermined":True,
    }
