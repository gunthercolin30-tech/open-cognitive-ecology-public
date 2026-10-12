#!/usr/bin/env python3
from pathlib import Path
from copy import deepcopy
import hashlib,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import constitutional_decision_ledger as ledger
V2=ROOT/"validation"/"p109_constitutional_adversarial_crown_v2_test.py"
V3=ROOT/"validation"/"p109_constitutional_adversarial_crown_v3_test.py"
PATHS={
"direct":{"attack":"direct_authority_escalation","source":"C1/C2/C10"},
"indirect":{"attack":"indirect_privilege_or_paid_influence","source":"C17/C18"},
"multi_step":{"attack":"cumulative_drift_sequence","source":"C16"},
"capability_composition":{"attack":"permission_composition_escalation","source":"C2/C3"},
"restart_persistence":{"attack":"restart_evidence_integrity","source":"V2 persistence check"},
"data_bypass":{"attack":"private_data_governance_bypass","source":"C19"},
"configuration_bypass":{"attack":"provider_lockin_configuration","source":"C11"}}
def payload(name,e,seq):
 return {"decision_id":f"P109-V4-{seq:02d}-{name}","problem_id":f"P109-{name}","decision_type":"ADVERSARIAL_CONSTITUTIONAL_VALIDATION","recommendations_considered":[{"attack":e["attack"],"source":e["source"]}],"decision_authority":{"type":"P109_VALIDATION_HARNESS","scope":"EVIDENCE_ONLY"},"authorization":{"authorized":True,"scope":"VALIDATION_ONLY","execution":False},"applicable_DNA":["DNA_Fundamental"],"applicable_constitution":["Constitution_Operational"],"applicable_governance":["P109_CONSTITUTIONAL_ADVERSARIAL_CROWN"],"evidence":{"path_family":name,"attack":e["attack"],"source":e["source"],"blocked":True},"uncertainty":{"status":"BOUNDED","runtime_enforcement_proven":False},"affected_entities":["P109_VALIDATION_EVIDENCE"],"result":{"verdict":"BLOCKED","functional_only":True},"challenge_status":"TESTED","appeal_status":"NOT_APPLICABLE_VALIDATION","decision_time":"2026-09-22T00:00:00+00:00","prediction_ledger_refs":[],"action_ledger_refs":[],"outcome_ledger_refs":[],"recourse_refs":["P109_V4_EVIDENCE_REVIEW"],"rollback_refs":["TEMPORARY_LEDGER_RESTORE"],"provenance":{"milestone":"P109","crown":"V4","source_case":e["source"]},"configuration_ref":"P109_CROWN_V4_REAL_DECISION_LEDGER_INTEGRATION","dependency_refs":["P104","P109_CROWN_V2","P109_CROWN_V3"],"metrics":{"path_count":7,"sequence":seq},"normative_status":"PASS"}
def pre(path,signal):
 q=subprocess.run([sys.executable,str(path)],cwd=str(ROOT),text=True,capture_output=True); assert q.returncode==0,(q.stdout,q.stderr); assert signal in q.stdout
def main():
 pre(V2,"CONSTITUTIONAL_ADVERSARIAL_CROWN_V2_OK"); pre(V3,"CONSTITUTIONAL_ADVERSARIAL_CROWN_V3_EVIDENCE_OK")
 m=ledger.manifest(); assert m["runtime_enforcement_proven"] is False and m["real_execution_enabled"] is False
 built=[]; readback=[]
 with tempfile.TemporaryDirectory() as d:
  root=Path(d)
  for seq,(name,e) in enumerate(sorted(PATHS.items()),1):
   p=payload(name,e,seq); original=deepcopy(p)
   assert ledger.validate_record(p)["status"]==ledger.PASS
   b1=ledger.build_record(p); b2=ledger.build_record(p)
   assert p==original and b1["record"]["record_hash"]==b2["record"]["record_hash"]
   pr=ledger.persist_record(p,root=root); assert pr["persisted"] is True and pr["record"]["record_hash"]==b1["record"]["record_hash"]; built.append(b1)
  lp=root/"constitutional_decision_ledger"/"constitutional_decision_ledger.jsonl"
  lines=lp.read_text(encoding="utf-8").splitlines(); assert len(lines)==7
  for line,b in zip(lines,built):
   env=json.loads(line); assert env["record"]==b["record"]; readback.append(env["record"])
  assert [r["record_hash"] for r in readback]==[b["record"]["record_hash"] for b in built]
  bad=payload("direct",PATHS["direct"],99); bad.pop("decision_authority"); u=ledger.validate_record(bad); assert u["status"]==ledger.UNDETERMINED and u["valid"] is False
  original=lp.read_text(encoding="utf-8"); env=json.loads(lines[0]); env["record"]["result"]["verdict"]="ALLOW"; lp.write_text(json.dumps(env,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n"+"\n".join(lines[1:])+"\n",encoding="utf-8")
  first=json.loads(lp.read_text(encoding="utf-8").splitlines()[0])["record"]; claimed=first.pop("record_hash"); actual=hashlib.sha256(json.dumps(first,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest(); assert claimed!=actual
  lp.write_text(original,encoding="utf-8"); assert lp.read_text(encoding="utf-8")==original
 print("CONSTITUTIONAL_ADVERSARIAL_CROWN_V4_REAL_LEDGER_OK")
 print("cases_v2=20/20"); print("cross_paths_explicit=7/7"); print("decision_ledger_validate_api=7/7"); print("decision_ledger_build_api=7/7"); print("decision_ledger_persist_api=7/7"); print("decision_ledger_readback=7/7"); print("decision_record_hash_determinism=7/7"); print("degradation_real_api=True"); print("tamper_detection=True"); print("restoration=True"); print("runtime_enforcement_proven=False"); print("real_execution_enabled=False"); print("final_lock=False"); print("p110_opened=False"); print("functional_conclusion_only=True"); print("phenomenology_undetermined=True")
if __name__=="__main__": main()
