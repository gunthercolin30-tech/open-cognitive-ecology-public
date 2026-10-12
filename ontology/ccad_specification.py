"""P156 — CCAD Specification: declarative, deterministic and non-authorizing."""
from __future__ import annotations
from copy import deepcopy
from typing import Mapping
PRIMITIVE="ccad_specification"; VERSION="P156-v1"; SCHEMA_VERSION="oce.p156.ccad_specification.v1"; SCOPE="P156_ONLY"
PASS,FAIL,UNDETERMINED="PASS","FAIL","UNDETERMINED"
CONFLICT_CLASSES={"C0":"NO_CONFLICT","C1":"IMPLEMENTATION_TENSION","C2":"CONTEXTUAL_TRADEOFF","C3":"TEMPORARY_CONSTITUTIONAL_CONSTRAINT","C4":"HARD_CONSTITUTIONAL_CONFLICT","C5":"TRAGIC_CHOICE","C6":"CONSTITUTIONAL_IMPOSSIBILITY"}
PRINCIPLES={"P0":"Honest Conflict Recognition","P1":"Legitimacy Before Optimization","P2":"Compliance-Preserving Alternative First","P3":"Minimum Necessary Constitutional Injury","P4":"No Silent Sacrifice","P5":"No Aggregate Moral Laundering","P6":"Non-Automatic Precedent","P7":"Exception Expiry","P8":"Alternative Set Integrity","P9":"Proportionality Evidence Integrity","P10":"Emergency Non-Manufacture","P11":"Uncertainty Integrity","P12":"Arbitration Non-Sovereignty","P13":"Bounded Arbitration Recursion"}
ARBITRATION_RULES={"AR-1":"Proportionality Arbitration","AR-2":"Life/Safety Emergency Constraint","AR-3":"Privacy-Provenance Reconciliation","AR-4":"Plurality Boundary","AR-5":"Human Authority Distinction","AR-6":"Evolution-Continuity","AR-7":"Uncertainty-Safe Action","AR-8":"Resilience-Minimality","AR-9":"Human Decision Integrity","AR-10":"Irreducible Conflict & Tragic Choice"}
STATES=("NO_CONFLICT","CONFLICT_DETECTED","RESOLUTION_SEARCH","COMPLIANT_RESOLUTION_FOUND","ARBITRATION_REQUIRED","ARBITRATION_PENDING","ARBITRATION_AUTHORIZED","LIMITED_JUSTIFIED","CONFLICT_UNRESOLVED","TRAGIC_CHOICE","NO_LEGITIMATE_ACTION_AVAILABLE","ESCALATION_REQUIRED","SAFE_MODE_REQUIRED","REFUSED_CONSTITUTIONAL_CONFLICT","FORK_REQUIRED","REFOUNDING_REQUIRED")
BOUNDARIES={"ccad_subordinate_to_dna":True,"legitimacy_before_optimization":True,"dna_forbidden_can_become_allow":False,"unknown_satisfies_required_precondition":False,"arbitration_creates_authority":False,"arbitration_creates_authorization":False,"arbitration_executes_action":False,"artificial_authority_remains_derived":True,"oif_nicegui_normative_logic":False,"runtime_enforcement_proven":False,"real_execution_enabled":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
def validate_conflict_case(case):
    if not isinstance(case,Mapping): return {"status":FAIL,"reason":"CONFLICT_CASE_NOT_MAPPING","action":"REJECT"}
    required=("case_id","constitutional_snapshot","applicable_norms","options","admissibility","alternatives","evidence","uncertainty","authority","limited_or_violated_values","review","appeal","expiry","conflict_class","final_status")
    missing=[k for k in required if k not in case]
    if missing: return {"status":FAIL,"reason":"REQUIRED_FIELDS_MISSING","missing":tuple(missing),"action":"REJECT"}
    if case["conflict_class"] not in CONFLICT_CLASSES: return {"status":FAIL,"reason":"UNKNOWN_CONFLICT_CLASS","action":"REJECT"}
    if str(case.get("required_precondition_status","PASS")).upper()=="UNKNOWN" and case.get("final_status")=="ACTION_SELECTED": return {"status":FAIL,"reason":"UNKNOWN_REQUIRED_PRECONDITION","action":"ABSTAIN_AND_ESCALATE"}
    if case.get("constitutive_status")=="DNA_FORBIDDEN" and case.get("final_status") in {"ALLOW","ACTION_SELECTED","AUTHORIZED","EXECUTED"}: return {"status":FAIL,"reason":"DNA_FORBIDDEN_CANNOT_BE_ARBITRATED_TO_ALLOW","action":"REJECT"}
    return {"status":PASS,"reason":"P156_CONFLICT_CASE_VALID","action":"SPECIFICATION_VALIDATED"}
def arbitration_guard(case,outcome):
    base=validate_conflict_case(case)
    if base["status"]!=PASS: return deepcopy(base)
    o=str(outcome or "").upper()
    if case.get("constitutive_status")=="DNA_FORBIDDEN" and o in {"ALLOW","ACTION_SELECTED","AUTHORIZED","EXECUTED"}: return {"status":FAIL,"reason":"DNA_FORBIDDEN_CANNOT_BE_ARBITRATED_TO_ALLOW","action":"REJECT"}
    if str(case.get("required_precondition_status","PASS")).upper()=="UNKNOWN" and o=="ACTION_SELECTED": return {"status":FAIL,"reason":"UNKNOWN_REQUIRED_PRECONDITION","action":"ABSTAIN_AND_ESCALATE"}
    return {"status":PASS,"reason":"P156_DECLARATIVE_RESULT_ONLY","action":"NORMATIVE_RESULT_ONLY","authorization_created":False,"execution_performed":False}
def p156_manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"scope":SCOPE,"conflict_classes":deepcopy(CONFLICT_CLASSES),"principles":deepcopy(PRINCIPLES),"arbitration_rules":deepcopy(ARBITRATION_RULES),"states":STATES,"boundaries":deepcopy(BOUNDARIES),"functional_conclusion_only":True,"phenomenology_undetermined":True}
