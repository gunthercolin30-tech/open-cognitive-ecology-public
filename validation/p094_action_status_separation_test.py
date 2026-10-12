from copy import deepcopy
from ontology.action_status_separation import *
def chain():
 a=make_authorization("AUT-1",authority_ref="AUTH-A",evidence_ref="EA",conditions=("c",),permissions=("p",))
 return {"recommendation":make_recommendation("REC-1",evidence_ref="ER"),"decision":make_decision("DEC-1",authority_ref="AUTH-D",evidence_ref="ED"),"authorization":a,"execution":make_execution("EXE-1",authorization_ref="AUT-1",executor_ref="EXEC-1",evidence_ref="EX")}
def main():
 c=validate_p094_contract(); assert c["status"]==PASS and c["stage_count"]==4 and c["real_execution_enabled"] is False
 assert evaluate_chain(chain())["status"]==PASS and evaluate_chain(chain())["execution_permitted"] is False
 for field in ("conditions","permissions"):
  x=chain(); x["authorization"][field]=(); assert evaluate_chain(x)["status"]==FAIL
 x=chain(); x["execution"]["executor_ref"]=""; assert evaluate_chain(x)["status"]==FAIL
 x=chain(); x["execution"]["authorization_ref"]="WRONG"; assert evaluate_chain(x)["status"]==FAIL
 x=chain(); x["decision"]["ref"]="REC-1"; assert evaluate_chain(x)["status"]==FAIL
 assert evaluate_transition("Recommendation","Decision",evidence_status=PASS)["permitted"] is True
 assert evaluate_transition("Decision","Authorization",evidence_status=PASS)["permitted"] is True
 assert evaluate_transition("Authorization","Execution",evidence_status=PASS)["permitted"] is True
 assert evaluate_transition("Recommendation","Execution",evidence_status=PASS)["status"]==FAIL
 assert evaluate_transition("Decision","Execution",evidence_status=PASS)["status"]==FAIL
 assert evaluate_transition("Recommendation","Decision",evidence_status="UNKNOWN")["status"]==UNDETERMINED
 assert evaluate_transition("Decision","Authorization",evidence_status=CONFLICT)["action"]=="ESCALATE"
 m=p094_manifest(); m["boundaries"]["stage_skipping_forbidden"]=False; assert p094_manifest()["boundaries"]["stage_skipping_forbidden"] is True
 x=chain(); before=deepcopy(x); evaluate_chain(x); assert x==before
 print("P094_ACTION_STATUS_SEPARATION_TEST_OK")
 print("status=PASSED"); print("stages=4"); print("stage_order=Recommendation>Decision>Authorization>Execution")
 print("stage_skipping=REJECTED"); print("implicit_promotion=REJECTED")
 print("authorization_conditions_required=True"); print("authorization_permissions_required=True"); print("identified_executor_required=True")
 print("unknown_promoted_to_pass=False"); print("conflict_action=ESCALATE"); print("defensive_manifest_copy=PASS"); print("input_non_mutation=PASS")
 print("execution_permitted_by_p094=False"); print("runtime_enforcement_proven=False"); print("execution_authority_proven=False"); print("real_execution_enabled=False")
 print("functional_conclusion_only=True"); print("phenomenology_undetermined=True")
if __name__=="__main__": main()
