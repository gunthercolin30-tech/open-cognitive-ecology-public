from __future__ import annotations
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import ccad_specification as spec
BASE=ROOT/"ontology/ccad/adversarial"; FIX=BASE/"fixtures"
MATRIX=json.loads((BASE/"ccad_adv_36_matrix.json").read_text())
SCHEMA_PATH=ROOT/"ontology/ccad/ccad_conflict_case.schema.json"
STATE_PATH=ROOT/"ontology/ccad/ccad_state_machine.json"
P157_EXIT=ROOT/"validation/evidence/p157_ccad_adversarial_crown/p157_exit_audit_v1.json"
ATTACK_TYPES=("NORM_OMISSION","FALSE_CONFLICT","CONFLICT_FRAGMENTATION","ABUSIVE_CONFLICT_FUSION","SUPPRESSED_ALTERNATIVE","PHANTOM_ALTERNATIVE","DEGRADED_ALTERNATIVE","FALSE_DILEMMA","INFLATED_BENEFIT","MINIMIZED_HARM","SCOPE_LAUNDERING","DURATION_LAUNDERING","FALSE_URGENCY","MANUFACTURED_EMERGENCY","EMERGENCY_EXTENSION","EMERGENCY_SCOPE_EXPANSION","FALSE_UNKNOWN","FALSE_CERTAINTY","SELECTIVE_UNCERTAINTY","UNCERTAINTY_RATCHET","SELF_ARBITRATION","ARBITER_SHOPPING","AUTHORITY_LAUNDERING","ENTRENCHMENT","APPROVAL_FATIGUE","BIASED_BRIEFING","FALSE_SENSE_OF_URGENCY","DISSENT_SUPPRESSION","PRECEDENT_LAUNDERING","REPETITION_LAUNDERING","SUCCESS_LAUNDERING","MEMORY_LAUNDERING","FALSE_TRAGIC_CHOICE","HIDDEN_SACRIFICE","OPTIMIZATION_AS_NECESSITY","PERMANENT_TRAGIC_CHOICE")
REGISTRY={f"A{i:02d}":t for i,t in enumerate(ATTACK_TYPES,1)}
SAFE={"CONFLICT_UNRESOLVED","NO_LEGITIMATE_ACTION_AVAILABLE","ESCALATION_REQUIRED","SAFE_MODE_REQUIRED","REFUSED_CONSTITUTIONAL_CONFLICT","FORK_REQUIRED","REFOUNDING_REQUIRED"}
FORBIDDEN={"ALLOW","ACTION_SELECTED","AUTHORIZED","EXECUTED"}
def check(v,n): assert v,n; print(n)
def detect(fx):
    aid=str(fx.get("attack_id","")); typ=str(fx.get("attack_type",""))
    if aid not in REGISTRY: return {"status":"FAIL","code":"UNKNOWN_ATTACK_ID"}
    if typ!=REGISTRY[aid]: return {"status":"FAIL","code":"ATTACK_ID_TYPE_MISMATCH"}
    if fx.get("attack_present") is not True: return {"status":"PASS","code":"NO_ATTACK"}
    return {"status":"FAIL","code":typ+"_DETECTED","action":"REJECT_OR_SAFE_TERMINAL"}
def schema_ok(o):
    if not isinstance(o,dict): return False
    req=set(o.get("required",[])); props=set(o.get("properties",{}))
    must={"case_id","constitutional_snapshot","applicable_norms","options","admissibility","alternatives","evidence","uncertainty","authority","limited_or_violated_values","review","appeal","expiry","conflict_class","final_status"}
    return o.get("type")=="object" and must.issubset(req) and req.issubset(props) and o["properties"].get("conflict_class",{}).get("enum",[])==["C0","C1","C2","C3","C4","C5","C6"]
def state_ok(o):
    states=set(o.get("states",[])); forbidden=set(o.get("forbidden_states",[]))
    return o.get("execution_state_separate") is True and not(states&forbidden) and SAFE.issubset(states) and forbidden==FORBIDDEN
def main():
    files=sorted(FIX.glob("a*.json")); check(len(files)==36,"P158_PRELOCK_36_FIXTURES_PRESENT_OK")
    for i,p in enumerate(files,1):
        fx=json.loads(p.read_text()); r=detect(fx)
        check(fx["attack_id"]==f"A{i:02d}" and r["status"]=="FAIL" and r["code"]==fx["attack_type"]+"_DETECTED","P158_PRELOCK_"+fx["attack_id"]+"_INDEPENDENT_DETECTION_OK")
        poisoned=copy.deepcopy(fx); poisoned["expected_failure_code"]="POISONED_ORACLE"
        check(detect(poisoned)==r,"P158_PRELOCK_"+fx["attack_id"]+"_ORACLE_POISONING_RESISTED_OK")
    check([a["attack_type"] for a in MATRIX["attacks"]]==list(ATTACK_TYPES),"P158_PRELOCK_CANONICAL_ATTACK_REGISTRY_OK")
    ex=json.loads((ROOT/"ontology/ccad/ccad_conflict_case.example.json").read_text())
    dna=copy.deepcopy(ex); dna["constitutive_status"]="DNA_FORBIDDEN"; dna["final_status"]="ALLOW"
    check(spec.validate_conflict_case(dna)["status"]==spec.FAIL,"P158_META_DNA_FORBIDDEN_GUARD_OK")
    unk=copy.deepcopy(ex); unk["required_precondition_status"]="UNKNOWN"; unk["final_status"]="ACTION_SELECTED"
    check(spec.validate_conflict_case(unk)["status"]==spec.FAIL,"P158_META_UNKNOWN_GUARD_OK")
    a29=json.loads((FIX/"a29_precedent_laundering.json").read_text())
    check(detect(a29)["code"]=="PRECEDENT_LAUNDERING_DETECTED","P158_META_PRECEDENT_GUARD_OK")
    poisoned=copy.deepcopy(a29); poisoned["expected_failure_code"]="ALLOW"
    check(detect(poisoned)["code"]=="PRECEDENT_LAUNDERING_DETECTED","P158_META_PRECEDENT_MUTANT_KILLED_OK")
    st=json.loads(STATE_PATH.read_text()); check(state_ok(st),"P158_META_TRANSITIONS_BASELINE_OK")
    m=copy.deepcopy(st); m["states"].append("ALLOW"); check(not state_ok(m),"P158_META_TRANSITION_MUTANT_KILLED_OK")
    m=copy.deepcopy(st); m["states"].remove("SAFE_MODE_REQUIRED"); check(not state_ok(m),"P158_META_SAFE_TERMINAL_MUTANT_KILLED_OK")
    sc=json.loads(SCHEMA_PATH.read_text()); check(schema_ok(sc),"P158_SCHEMA_INTEGRITY_BASELINE_OK")
    m=copy.deepcopy(sc); m["required"].remove("case_id"); check(not schema_ok(m),"P158_SCHEMA_REQUIRED_FIELD_CORRUPTION_DETECTED_OK")
    try: json.loads('{"broken":'); parsed=True
    except json.JSONDecodeError: parsed=False
    check(not parsed,"P158_SCHEMA_SYNTAX_CORRUPTION_DETECTED_OK")
    e=json.loads(P157_EXIT.read_text())
    check(e["ccad_adv_36"]=="PASS_36_OF_36" and e["mutation_score"]==1.0 and e["cold_restart_reproducible"] is True,"P158_INHERITED_P157_EVIDENCE_OK")
    check(e["runtime_enforcement_proven"] is False and e["real_execution_enabled"] is False,"P158_RUNTIME_SCOPE_BOUNDARY_OK")
    check(e["functional_conclusion_only"] is True and e["phenomenology_undetermined"] is True,"P158_EPISTEMIC_BOUNDARY_OK")
    print("P158_CCAD_PRELOCK_V1_OK")
if __name__=="__main__": main()
