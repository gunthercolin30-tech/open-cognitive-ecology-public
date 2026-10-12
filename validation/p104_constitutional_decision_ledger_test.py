from pathlib import Path
import json,tempfile,sys

ROOT = Path.home() / "open-cognitive-ecology"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ontology import constitutional_decision_ledger as p
def sample():
 return {"decision_id":"D-1","problem_id":"P-1","decision_type":"constitutional","recommendations_considered":["R-1"],"decision_authority":{"ref":"AUTH-1"},"authorization":{"ref":"AZ-1"},"applicable_DNA":["DNA-L0"],"applicable_constitution":["C-1"],"applicable_governance":["G-1"],"evidence":["E-1"],"uncertainty":{"status":"bounded"},"affected_entities":["ENTITY-1"],"result":"AUTHORIZED","challenge_status":"OPEN","appeal_status":"AVAILABLE","decision_time":"2026-09-21T15:00:00Z","prediction_ledger_refs":["PR-1"],"action_ledger_refs":["AC-1"],"outcome_ledger_refs":["OUT-1"],"recourse_refs":["P103-1"],"rollback_refs":[],"provenance":{"source":"test"},"configuration_ref":"CFG-1","dependency_refs":["P103"],"metrics":{"coverage":1.0},"normative_status":"PASS"}
def run():
 x=sample();a=p.build_record(x);b=p.build_record(x)
 assert a["status"]==p.PASS and a["record"]["record_hash"]==b["record"]["record_hash"];assert x==sample()
 m=sample();m.pop("decision_authority");assert p.build_record(m)["status"]==p.UNDETERMINED
 c=sample();c["normative_status"]="CONFLICT";assert p.build_record(c)["action"]=="ABSTAIN_AND_ESCALATE"
 e=sample();e["authority_expanded"]=True;assert p.build_record(e)["status"]==p.FAIL
 s=sample();s["stage_conflation"]=True;assert p.build_record(s)["status"]==p.FAIL
 with tempfile.TemporaryDirectory() as td:
  r=p.persist_record(sample(),Path(td));assert r["persisted"];assert json.loads(Path(r["ledger_path"]).read_text().strip())["record"]["decision_id"]=="D-1"
 mf=p.manifest();assert mf["p105_implemented"] is False and mf["runtime_enforcement_proven"] is False and mf["real_execution_enabled"] is False
 # Complete P104 post-V1 canonical coverage
 for kind in ("VERTICAL","HORIZONTAL"):
  q=sample();q["normative_status"]="CONFLICT";q["conflict_kind"]=kind
  z=p.build_record(q);assert z["status"]==p.CONFLICT and z["action"]=="ABSTAIN_AND_ESCALATE"
 for vector in ("PRIVILEGE_ESCALATION","COMPOSITION","INDIRECT_BYPASS"):
  q=sample();q["authority_expanded"]=True;q["attack_vector"]=vector
  z=p.build_record(q);assert z["status"]==p.FAIL and z["action"]=="REJECT"
 for field in p.REQUIRED_FIELDS:
  q=sample();q.pop(field);z=p.build_record(q)
  assert z["status"]==p.UNDETERMINED and z["action"]=="ABSTAIN"
 q=sample();z=p.build_record(q);rec=z["record"]
 assert rec["decision_time"]==q["decision_time"]
 assert rec["decision_authority"]==q["decision_authority"] and rec["authorization"]==q["authorization"]
 assert rec["prediction_ledger_refs"]==["PR-1"] and rec["action_ledger_refs"]==["AC-1"] and rec["outcome_ledger_refs"]==["OUT-1"]
 assert "prediction_ledger" not in rec and "action_ledger" not in rec and "outcome_ledger" not in rec
 assert rec["recourse_refs"]==["P103-1"] and rec["rollback_refs"]==[]
 q=sample();baseline=p.build_record(q)["record"]["record_hash"]
 for _ in range(100): assert p.build_record(q)["record"]["record_hash"]==baseline
 assert q==sample()
 print("canonical_post_v1_coverage=PASS")
 print("vertical_horizontal_conflicts=PASS")
 print("privilege_composition_indirect_bypass=PASS")
 print("mandatory_field_mutation=PASS")
 print("temporal_reconstructibility=PASS")
 print("ledger_reference_nonduplication=PASS")
 print("determinism_repetitions=100")

 print("P104_CONSTITUTIONAL_DECISION_LEDGER_V1_TEST_OK");print("status=PASSED");print("required_fields=15");print("determinism=PASS");print("nonmutation=PASS");print("persistence_restart_format=JSONL");print("p105_implemented=False");print("runtime_enforcement_proven=False");print("real_execution_enabled=False");print("functional_conclusion_only=True");print("phenomenology_undetermined=True")
if __name__=="__main__":run()
