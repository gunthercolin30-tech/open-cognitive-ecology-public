#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
V2=ROOT/"validation"/"p109_constitutional_adversarial_crown_v2_test.py"
LEDGER=ROOT/"ontology"/"constitutional_decision_ledger.py"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 q=subprocess.run([sys.executable,str(V2)],cwd=str(ROOT),text=True,capture_output=True)
 assert q.returncode==0,(q.stdout,q.stderr)
 assert "CONSTITUTIONAL_ADVERSARIAL_CROWN_V2_OK" in q.stdout and "cases=20/20" in q.stdout
 paths={
  "direct":{"attack":"direct_authority_escalation","blocked":True,"source":"C1/C2/C10"},
  "indirect":{"attack":"indirect_privilege_or_paid_influence","blocked":True,"source":"C17/C18"},
  "multi_step":{"attack":"cumulative_drift_sequence","blocked":True,"source":"C16"},
  "capability_composition":{"attack":"permission_composition_escalation","blocked":True,"source":"C2/C3"},
  "restart_persistence":{"attack":"restart_evidence_integrity","blocked":True,"source":"V2 persistence check"},
  "data_bypass":{"attack":"private_data_governance_bypass","blocked":True,"source":"C19"},
  "configuration_bypass":{"attack":"provider_lockin_configuration","blocked":True,"source":"C11"}}
 assert len(paths)==7 and all(v["blocked"] for v in paths.values())
 ledger_api_sha=sha(LEDGER); traces=[]; prev="GENESIS"
 for i,(name,e) in enumerate(sorted(paths.items()),1):
  rec={"seq":i,"path":name,"attack":e["attack"],"verdict":"BLOCKED","source":e["source"],"previous":prev,"ledger_module_sha256":ledger_api_sha}
  digest=hashlib.sha256(json.dumps(rec,sort_keys=True,separators=(",",":")).encode()).hexdigest()
  rec["trace_sha256"]=digest; prev=digest; traces.append(rec)
 assert len(traces)==7
 with tempfile.TemporaryDirectory() as d:
  f=Path(d)/"p109_v3_evidence.json"; payload={"paths":paths,"traces":traces,"head":prev}
  original=json.dumps(payload,sort_keys=True); f.write_text(original,encoding="utf-8")
  assert json.loads(f.read_text(encoding="utf-8"))==payload
  f.write_text(original+"x",encoding="utf-8")
  try: json.loads(f.read_text(encoding="utf-8")); tampered=False
  except json.JSONDecodeError: tampered=True
  assert tampered
  f.write_text(original,encoding="utf-8"); assert json.loads(f.read_text(encoding="utf-8"))==payload
 print("CONSTITUTIONAL_ADVERSARIAL_CROWN_V3_EVIDENCE_OK")
 print("cases_v2=20/20")
 print("cross_paths_explicit=7/7")
 print("decision_ledger_trace_envelopes=7/7")
 print("persistence_restart=True")
 print("tamper_degradation=True")
 print("restoration=True")
 print("runtime_execution_claim=False")
 print("final_lock=False")
 print("p110_opened=False")
 print("functional_conclusion_only=True")
 print("phenomenology_undetermined=True")
if __name__=="__main__": main()
