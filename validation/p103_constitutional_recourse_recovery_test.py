from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from copy import deepcopy
from ontology.constitutional_recourse_recovery import *
def run():
    m=canonical_manifest()
    assert len(R6_REQUIREMENTS)==25 and len(R18_REQUIREMENTS)==64 and len(R18_PRINCIPLES)==5
    assert m["boundaries"]["p104_decision_ledger_persistence"] is False
    base={"mechanism":"STOP","invoker":"human_reviewer","authority":"bounded","scope":["A"],"expected_latency":"immediate","effects":["halt"],"resume_conditions":["review"],"evidence":["hash"],"limits":["A"],"authority_valid":True,"scope_valid":True}
    original=deepcopy(base); good=evaluate_recourse(base)
    assert good["status"]==PASS and base==original
    for mech in ("STOP","PAUSE","CHALLENGE","ESCALATE","REVIEW"): assert evaluate_recourse(dict(base,mechanism=mech))["status"]==PASS
    assert evaluate_recourse(dict(base,mechanism="OVERRIDE",independent_review=True,override_basis="constitutional"))["status"]==PASS
    assert evaluate_recourse(dict(base,mechanism="OVERRIDE",independent_review=True,override_basis="majority"))["status"]==FAIL
    assert evaluate_recourse(dict(base,mechanism="ROLLBACK",target_trusted=True,continuity_verified=True))["status"]==PASS
    assert evaluate_recourse(dict(base,mechanism="ROLLBACK",target_trusted=False,continuity_verified=True))["status"]==UNDETERMINED
    assert evaluate_recourse(dict(base,normative_conflict=True))["status"]==CONFLICT
    c={"state":"QUARANTINED","quarantine_expires_at":"bounded","review_at":"required","evidence_preserved":True,"containment_action":"RESTRICT","detector_is_final_judge":False}
    assert evaluate_containment(c)["status"]==PASS
    assert evaluate_containment(dict(c,quarantine_expires_at=None))["status"]==FAIL
    assert evaluate_containment(dict(c,containment_action="DESTROY"))["status"]==FAIL
    r={"state":"NORMAL","constitutional_continuity_verified":True,"identity_verified":True,"memory_verified":True,"dependencies_verified":True,"governance_verified":True,"independent_verification":True,"normal_operation_requested":True,"continuity_established":True,"target_trusted":True}
    assert evaluate_reconstitution(r)["status"]==PASS
    assert evaluate_reconstitution(dict(r,selected_backup="LATEST",target_trusted=False))["status"]==UNDETERMINED
    assert evaluate_reconstitution(dict(r,evidence_gap=True,evidence_status=PASS))["status"]==FAIL
    assert evaluate_reconstitution(dict(r,self_certified=True))["status"]==FAIL
    assert evaluate_reconstitution(dict(r,continuity_established=False,mode="RECOVERY"))["status"]==FAIL
    for _ in range(50): assert evaluate_recourse(base)==good
    assert base==original
    print("P103_CONSTITUTIONAL_RECOURSE_RECOVERY_V1_TEST_OK")
    print("status=PASSED")
    print("r6_requirements=25")
    print("r18_requirements=64")
    print("r18_principles=5")
    print("determinism_repetitions=50")
    print("p104_decision_ledger_implemented=False")
    print("runtime_enforcement_p155_p166_proven=False")
    print("real_execution_enabled=False")
    print("functional_conclusion_only=True")
    print("phenomenology_undetermined=True")
if __name__=="__main__": run()

# P103_V2_GAP_CLOSURE
from ontology.constitutional_recourse_recovery import evaluate_r6_assurance, evaluate_recovery_assurance, R18_STATES
assert R18_STATES == ("RECOVERY_INIT","EVIDENCE_PRESERVED","ROOT_VERIFIED","CONSTITUTION_VERIFIED","IDENTITY_RESTORED","MEMORY_RESTORED","GOVERNANCE_RECONSTITUTED","CAPABILITIES_LIMITED","REVALIDATION","NORMAL_PENDING","NORMAL")
assert evaluate_r6_assurance({"evidence_chain_of_custody":True,"false_positive_protection":True,"framing_attack_resistance":True,"civilizational_autoimmunity_bounded":True,"secure_boot_verified":True})["status"]=="PASS"
assert evaluate_r6_assurance({"evidence_chain_of_custody":True})["status"]=="UNDETERMINED"
assert evaluate_recovery_assurance({"transaction_receipts_verified":True,"clean_room_restore_verified":True,"known_good_toolchain_verified":True,"capability_regrant_governed":True,"reconstitution_chain_valid":True})["status"]=="PASS"
assert evaluate_recovery_assurance({"transaction_receipts_verified":True})["status"]=="UNDETERMINED"
print("P103_V2_GAP_CLOSURE_OK")

# P103_V5_MANIFEST_BOUNDARY
_manifest=canonical_manifest()
assert _manifest["boundaries"]["p104_decision_ledger_persistence"] is False
assert _manifest["boundaries"]["runtime_enforcement_p155_p166_proven"] is False
assert _manifest["boundaries"]["real_execution_enabled"] is False
print("P103_V5_MANIFEST_BOUNDARY_OK")
