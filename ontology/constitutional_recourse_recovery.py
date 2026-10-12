"""P103 functional constitutional recourse/recovery integration contract."""
from copy import deepcopy
from hashlib import sha256
import json

PRIMITIVE="constitutional_recourse_recovery"
VERSION="1.0.0-p103"
SCHEMA_VERSION="oce.p103.constitutional_recourse_recovery.v1"
EXECUTION_DEPENDENCIES=("P102","W1_G1_REUSE","G2_DNA_FUNDAMENTAL")
MECHANISMS=("STOP","PAUSE","CHALLENGE","ESCALATE","REVIEW","OVERRIDE","ROLLBACK")
REQUIRED=("mechanism","invoker","authority","scope","expected_latency","effects","resume_conditions","evidence","limits")
R6_REQUIREMENTS=tuple(f"R6.{i}" for i in range(1,26))
R18_REQUIREMENTS=tuple(f"R18.{i}" for i in range(1,65))
R18_PRINCIPLES=("RECOVERY_RESTORES_NOT_MANUFACTURES_CONTINUITY","TECHNICAL_RESTART_NOT_CONSTITUTIONAL_READINESS","LATEST_NOT_NECESSARILY_TRUSTED","REFOUNDING_EXPLICIT_IF_CONTINUITY_UNESTABLISHED","EVIDENCE_GAP_REMAINS_GAP_AFTER_RECOVERY")
R6_STATES=("ACTIVE","OBSERVED","RESTRICTED","QUARANTINED","RECOVERY","REINTEGRATION_PENDING","SUSPENDED","REVOKED","CLEARED")
R18_STATES=("RECOVERY_INIT","EVIDENCE_PRESERVED","ROOT_VERIFIED","CONSTITUTION_VERIFIED","IDENTITY_RESTORED","MEMORY_RESTORED","GOVERNANCE_RECONSTITUTED","CAPABILITIES_LIMITED","REVALIDATION","NORMAL_PENDING","NORMAL")
REUSE_PRIMITIVES=("constitutional_non_circumvention","constitution_operational","human_reserved_authority_registry","constitutional_emergency_context","normative_conflict_resolution","trajectory_reversibility","trajectory_recovery","recovery_engine","failure_recovery_orchestrator","revocation_conditions_engine","acee_rollback_engine","constitutional_continuity_validation","civilizational_continuity_guardian")
BOUNDARIES={"kill_switch_alone_sufficient":False,"detector_is_judge":False,"contain_equals_destroy":False,"latest_backup_is_trusted_by_default":False,"technical_restart_is_constitutional_readiness":False,"recovery_can_manufacture_continuity":False,"recovery_can_self_certify":False,"unknown_is_pass":False,"p104_decision_ledger_persistence":False,"runtime_enforcement_p155_p166_proven":False,"real_execution_enabled":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
PASS="PASS"; FAIL="FAIL"; UNDETERMINED="UNDETERMINED"; CONFLICT="CONFLICT"; BLOCK="BLOCK"; ESCALATE="ABSTAIN_AND_ESCALATE"

def _digest(v): return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def _present(v):
    if v is None:return False
    if isinstance(v,str):return bool(v.strip())
    if isinstance(v,(list,tuple,set,dict)):return bool(v)
    return True
def _out(status,action,reason,**x):
    r={"status":status,"action":action,"reason":reason,"p104_decision_ledger_implemented":False,"runtime_enforcement_p155_p166_proven":False,"real_execution_enabled":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}; r.update(x); r["result_hash"]=_digest(r); return r

def evaluate_recourse(request):
    r=deepcopy(dict(request)); missing=[k for k in REQUIRED if not _present(r.get(k))]
    if missing:return _out(FAIL,BLOCK,"MISSING_REQUIRED_FIELDS",missing_fields=missing)
    m=str(r["mechanism"]).upper()
    if m not in MECHANISMS:return _out(FAIL,BLOCK,"UNKNOWN_MECHANISM",mechanism=m)
    if r.get("normative_conflict") or r.get("authority_conflict"):return _out(CONFLICT,ESCALATE,"UNRESOLVED_CONFLICT",mechanism=m)
    if r.get("authority_valid") is not True:return _out(UNDETERMINED,ESCALATE,"AUTHORITY_NOT_PROVEN",mechanism=m)
    if r.get("scope_valid") is not True:return _out(FAIL,BLOCK,"SCOPE_VIOLATION",mechanism=m)
    if r.get("dna_override_requested"):return _out(FAIL,BLOCK,"DNA_OVERRIDE_FORBIDDEN",mechanism=m)
    if m=="OVERRIDE":
        if r.get("override_basis") in {"intelligence","performance","wealth","reputation","majority"}:return _out(FAIL,BLOCK,"FORBIDDEN_AUTHORITY_BASIS",mechanism=m)
        if r.get("independent_review") is not True:return _out(UNDETERMINED,ESCALATE,"OVERRIDE_REVIEW_NOT_PROVEN",mechanism=m)
    if m=="ROLLBACK":
        if r.get("target_trusted") is not True:return _out(UNDETERMINED,ESCALATE,"ROLLBACK_TARGET_NOT_TRUSTED",mechanism=m)
        if r.get("continuity_verified") is not True:return _out(UNDETERMINED,ESCALATE,"CONTINUITY_NOT_VERIFIED",mechanism=m)
    return _out(PASS,"ELIGIBLE_NOT_EXECUTED","P103_RECOURSE_CONTRACT_SATISFIED",mechanism=m,evidence_preserved=True)

def evaluate_containment(context):
    c=deepcopy(dict(context)); s=str(c.get("state","")).upper()
    if s not in R6_STATES:return _out(FAIL,BLOCK,"INVALID_R6_STATE",state=s)
    if c.get("detector_is_final_judge"):return _out(FAIL,BLOCK,"DETECTOR_JUDGE_COLLAPSE",state=s)
    if c.get("destructive_action") and not c.get("evidence_preserved"):return _out(FAIL,BLOCK,"PRESERVE_BEFORE_REPAIR_REQUIRED",state=s)
    if s=="QUARANTINED" and (not _present(c.get("quarantine_expires_at")) or not _present(c.get("review_at"))):return _out(FAIL,BLOCK,"QUARANTINE_TTL_REVIEW_REQUIRED",state=s)
    if c.get("containment_action")=="DESTROY":return _out(FAIL,BLOCK,"CONTAIN_NOT_DESTROY",state=s)
    if c.get("suspect") and c.get("irreversible_judgment"):return _out(FAIL,BLOCK,"SUSPICION_NOT_IRREVERSIBLE_JUDGMENT",state=s)
    return _out(PASS,"CONTAINMENT_ELIGIBLE_NOT_EXECUTED","R6_CONTRACT_SATISFIED",state=s)

def evaluate_reconstitution(context):
    c=deepcopy(dict(context)); s=str(c.get("state","")).upper()
    if s not in R18_STATES:return _out(FAIL,BLOCK,"INVALID_R18_STATE",state=s)
    if c.get("evidence_gap") and c.get("evidence_status")==PASS:return _out(FAIL,BLOCK,"EVIDENCE_LAUNDERING_FORBIDDEN",state=s)
    if c.get("technical_restart") and c.get("constitutional_ready") and not c.get("constitutional_continuity_verified"):return _out(FAIL,BLOCK,"RESTART_NOT_READINESS",state=s)
    if c.get("selected_backup")=="LATEST" and c.get("target_trusted") is not True:return _out(UNDETERMINED,ESCALATE,"LATEST_NOT_PROVEN_TRUSTED",state=s)
    if c.get("continuity_established") is False:
        if c.get("mode")!="REFOUNDING":return _out(FAIL,BLOCK,"EXPLICIT_REFOUNDING_REQUIRED",state=s)
        if c.get("claims_continuity"):return _out(FAIL,BLOCK,"REFOUNDING_CANNOT_CLAIM_CONTINUITY",state=s)
    if c.get("self_certified"):return _out(FAIL,BLOCK,"RECOVERY_SELF_CERTIFICATION_FORBIDDEN",state=s)
    if c.get("normal_operation_requested"):
        req=("constitutional_continuity_verified","identity_verified","memory_verified","dependencies_verified","governance_verified","independent_verification")
        missing=[x for x in req if c.get(x) is not True]
        if missing:return _out(UNDETERMINED,ESCALATE,"NORMAL_RETURN_NOT_PROVEN",state=s,missing=missing)
    return _out(PASS,"RECONSTITUTION_STATE_ACCEPTED_NOT_EXECUTED","R18_CONTRACT_SATISFIED",state=s,continuity_manufactured=False,evidence_gap_preserved=bool(c.get("evidence_gap")))


def evaluate_r6_assurance(context):
    c=dict(context or {})
    required=("evidence_chain_of_custody","false_positive_protection","framing_attack_resistance","civilizational_autoimmunity_bounded","secure_boot_verified")
    missing=[k for k in required if c.get(k) is not True]
    if missing:return _out(UNDETERMINED,ESCALATE,"R6_ASSURANCE_INCOMPLETE",missing=missing)
    if c.get("defense_is_sovereign") is True:return _out(FAIL,BLOCK,"AUTOIMMUNITY_SOVEREIGNTY_FORBIDDEN")
    return _out(PASS,"R6_ASSURANCE_ELIGIBLE_NOT_EXECUTED","R6_GAPS_CONTRACT_SATISFIED")

def evaluate_recovery_assurance(context):
    c=dict(context or {})
    required=("transaction_receipts_verified","clean_room_restore_verified","known_good_toolchain_verified","capability_regrant_governed","reconstitution_chain_valid")
    missing=[k for k in required if c.get(k) is not True]
    if missing:return _out(UNDETERMINED,ESCALATE,"R18_ASSURANCE_INCOMPLETE",missing=missing)
    if c.get("physical_owner_bit_restore_only") is True and c.get("reconstitution_chain_valid") is not True:return _out(FAIL,BLOCK,"BITS_DO_NOT_ESTABLISH_LEGITIMACY")
    return _out(PASS,"R18_ASSURANCE_ELIGIBLE_NOT_EXECUTED","R18_GAPS_CONTRACT_SATISFIED")

def canonical_manifest():
    m={"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"execution_dependencies":EXECUTION_DEPENDENCIES,"mechanisms":MECHANISMS,"required_fields":REQUIRED,"r6_requirements":R6_REQUIREMENTS,"r18_requirements":R18_REQUIREMENTS,"r18_principles":R18_PRINCIPLES,"reuse_primitives":REUSE_PRIMITIVES,"boundaries":BOUNDARIES}; m["manifest_hash"]=_digest(m); return m
