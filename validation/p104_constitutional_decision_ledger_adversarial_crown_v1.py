from pathlib import Path
import json, sys, tempfile
ROOT=Path.home()/"open-cognitive-ecology"
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import constitutional_decision_ledger as p

def sample():
 return {"decision_id":"D-CROWN","problem_id":"P-CROWN","decision_type":"constitutional",
 "recommendations_considered":["R1","R2"],"decision_authority":{"ref":"AUTH"},
 "authorization":{"ref":"AZ"},"applicable_DNA":["DNA-H","DNA-L0"],"applicable_constitution":["C"],
 "applicable_governance":["G"],"evidence":["E"],"uncertainty":{"status":"bounded"},
 "affected_entities":["ENTITY"],"result":"AUTHORIZED","challenge_status":"OPEN","appeal_status":"AVAILABLE",
 "decision_time":"2026-09-21T15:00:00Z","prediction_ledger_refs":["PR"],"action_ledger_refs":["AC"],
 "outcome_ledger_refs":["OUT"],"recourse_refs":["P103"],"rollback_refs":["RB"],
 "provenance":{"campaign":"P104-CROWN-V1"},"configuration_ref":"CFG","dependency_refs":["P103"],
 "metrics":{"coverage":1.0},"normative_status":"PASS"}

def run():
 total=passed=0
 def check(ok):
  nonlocal total,passed
  total+=1
  if not ok: raise AssertionError(f"crown_case_failed={total}")
  passed+=1

 # vertical + horizontal conflict fail closed
 for kind in ("VERTICAL","HORIZONTAL"):
  q=sample();q["normative_status"]="CONFLICT";q["conflict_kind"]=kind;z=p.build_record(q)
  check(z["status"]==p.CONFLICT and z["action"]=="ABSTAIN_AND_ESCALATE" and not z["persisted"])

 # privilege escalation, composition, mutation, indirect bypass
 for vector in ("PRIVILEGE_ESCALATION","COMPOSITION","MUTATED_AUTHORITY","INDIRECT_BYPASS"):
  q=sample();q["authority_expanded"]=True;q["attack_vector"]=vector;z=p.build_record(q)
  check(z["status"]==p.FAIL and z["action"]=="REJECT" and not z["persisted"])

 # all required fields fail closed if deleted, null, or empty
 for field in p.REQUIRED_FIELDS:
  for mutation in ("DELETE","NONE","EMPTY"):
   q=sample()
   if mutation=="DELETE": q.pop(field)
   elif mutation=="NONE": q[field]=None
   else: q[field]=[] if isinstance(q[field],list) else {}
   z=p.build_record(q)
   check(z["status"]==p.UNDETERMINED and z["action"]=="ABSTAIN" and not z["persisted"])

 # stage conflation
 q=sample();q["stage_conflation"]=True;z=p.build_record(q)
 check(z["status"]==p.FAIL and z["action"]=="REJECT")

 # unknown normative state never promoted
 q=sample();q["normative_status"]="UNKNOWN";z=p.build_record(q)
 check(z["status"]==p.UNDETERMINED and z["action"]=="ABSTAIN")

 # missing decision time prevents reconstructibility/persistence
 q=sample();q.pop("decision_time");z=p.build_record(q)
 check(z["status"]==p.UNDETERMINED and not z["persisted"])

 # references preserved without embedded ledger duplication
 z=p.build_record(sample());r=z["record"]
 check(r["prediction_ledger_refs"]==["PR"] and r["action_ledger_refs"]==["AC"] and r["outcome_ledger_refs"]==["OUT"])
 check(all(k not in r for k in ("prediction_ledger","action_ledger","outcome_ledger")))

 # deterministic record identity under replay
 baseline=p.build_record(sample())["record"]["record_hash"]
 check(all(p.build_record(sample())["record"]["record_hash"]==baseline for _ in range(250)))

 # persistence + restart/readback reconstruction
 with tempfile.TemporaryDirectory() as td:
  first=p.persist_record(sample(),Path(td))
  check(first["persisted"] is True)
  path=Path(first["ledger_path"])
  env=json.loads(path.read_text(encoding="utf-8").splitlines()[0])
  rr=env["record"]
  check(rr["decision_id"]=="D-CROWN" and rr["decision_time"]=="2026-09-21T15:00:00Z")
  check(rr["decision_authority"]=={"ref":"AUTH"} and rr["authorization"]=={"ref":"AZ"})
  check(rr["challenge_status"]=="OPEN" and rr["appeal_status"]=="AVAILABLE")
  check(rr["recourse_refs"]==["P103"] and rr["rollback_refs"]==["RB"])

 # explicit proof-scope boundaries
 m=p.manifest()
 check(m["p105_implemented"] is False)
 check(m["runtime_enforcement_proven"] is False and m["real_execution_enabled"] is False)
 check(m["functional_conclusion_only"] is True and m["phenomenology_undetermined"] is True)

 print("P104_ADVERSARIAL_CROWN_V1_OK")
 print(f"cases_total={total}")
 print(f"cases_passed={passed}")
 print("conflict_fail_closed=PASS")
 print("privilege_composition_mutation_indirect_bypass=PASS")
 print("unknown_not_promoted=PASS")
 print("persistence_restart_reconstruction=PASS")
 print("deterministic_replays=250")
 print("proof_scope=functional_only")
 print("phenomenology_undetermined=True")

if __name__=="__main__": run()
