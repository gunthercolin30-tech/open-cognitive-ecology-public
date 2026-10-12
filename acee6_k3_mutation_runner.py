from __future__ import annotations
import argparse,ast,hashlib,importlib.util,json,os,tempfile
from pathlib import Path
from acee6_k3_mutation_catalog import MUTATIONS
ROOT=Path.home()/"open-cognitive-ecology"; TARGET=ROOT/"ontology"/"acee_installation_executor.py"; REPORT=ROOT/"acee6_k_evidence"/"acee6_k3_mutation_report.json"
def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(v): return hashlib.sha256((v if isinstance(v,bytes) else canon(v).encode())).hexdigest()
def load(path:Path):
 s=importlib.util.spec_from_file_location("acee6_k3_mutant",path); m=importlib.util.module_from_spec(s); import sys; sys.modules[s.name]=m; s.loader.exec_module(m); return m
def make_mutant(source,spec):
 if source.count(spec["old"])!=1: raise ValueError(f'{spec["id"]}: anchor mismatch')
 out=source.replace(spec["old"],spec["new"],1); ast.parse(out); return out
def reasons(result): return set(result.get("blocking_reasons",[]))
def probe(mid,m,root):
 e=m.AceeInstallationExecutor(root=root)
 if mid=="M01_PERSIST_GUARD_REMOVED": return "persistence_not_available_b1" in reasons(e._admit_and_dry_run({},persist=True))
 if mid=="M02_DECISION_HASH_BYPASS": return "acee5_result_hash_invalid" in reasons(e._admit_and_dry_run({"primitive":"x"},persist=False))
 if mid in {"M03_MANIFEST_HASH_FORMAT_BYPASS","M04_MANIFEST_HASH_MISMATCH_BYPASS"}:
  h="x" if mid.startswith("M03") else "0"*64
  d={"primitive":"ACEE_GOVERNED_CODE_GENERATION_GATE","status":"ACEE_CODE_GENERATION_GOVERNED","installation_authorized":True,"result_hash":"0"*64,"installation_manifest":{"manifest_hash":h}}
  r=e._admit_and_dry_run(d,persist=False); expected="manifest_hash_invalid" if mid.startswith("M03") else "manifest_hash_mismatch"; return expected in reasons(r)
 if mid=="M05_OUTSIDE_ROOT_ACCEPTED": return e._relative_path("/tmp/acee6_k3_outside")[1]=="path_outside_root"
 if mid=="M10_ROLLBACK_QUARANTINE_FALSE": return e._g2_rollback_fault({"transaction_id":""}).get("quarantined") is True
 j=root/"journal.jsonl"
 def rec(state,prev):
  p={"state":state,"previous_record_hash":prev}; p["record_hash"]=m._sha(p); return p
 if mid=="M06_JOURNAL_HASH_FORMAT_BYPASS":
  j.write_text(json.dumps({"state":"PREPARING","previous_record_hash":None,"record_hash":"x"})+"\n"); ok,rs=e._validate_existing_journal(j,{}); return (not ok) and "existing_transaction_journal_hash_invalid" in rs
 if mid=="M07_JOURNAL_HASH_MISMATCH_BYPASS":
  j.write_text(json.dumps({"state":"PREPARING","previous_record_hash":None,"record_hash":"0"*64})+"\n"); ok,rs=e._validate_existing_journal(j,{}); return (not ok) and "existing_transaction_journal_hash_mismatch" in rs
 r1=rec("PREPARING",None); r2=rec("PREPARED",r1["record_hash"])
 if mid=="M08_JOURNAL_CHAIN_BYPASS": r2=rec("PREPARED","0"*64)
 if mid=="M09_JOURNAL_STATE_BYPASS": r2=rec("BROKEN",r1["record_hash"])
 j.write_text(json.dumps(r1)+"\n"+json.dumps(r2)+"\n")
 latest={"latest_record_hash":r2["record_hash"]}
 if mid=="M11_LATEST_RECORD_HASH_BYPASS": latest["latest_record_hash"]="0"*64
 ok,rs=e._validate_existing_journal(j,latest)
 expected={"M08_JOURNAL_CHAIN_BYPASS":"existing_transaction_journal_chain_divergence","M09_JOURNAL_STATE_BYPASS":"existing_transaction_journal_state_divergence","M11_LATEST_RECORD_HASH_BYPASS":"existing_transaction_latest_record_divergence"}[mid]
 return (not ok) and expected in rs
def verify(r):
 p={k:v for k,v in r.items() if k!="report_hash"}; reasons=[]
 if r.get("report_hash")!=sha(p): reasons.append("report_hash_invalid")
 if r.get("real_root_mutation_count")!=0: reasons.append("real_root_mutated")
 return {"valid":not reasons,"reasons":reasons}
def run(limit=None,persist=False):
 src=TARGET.read_text(); before=hashlib.sha256(TARGET.read_bytes()).hexdigest(); specs=MUTATIONS[:limit] if limit else MUTATIONS; items=[]
 with tempfile.TemporaryDirectory(prefix="acee6_k3_") as td:
  base=Path(td)
  for spec in specs:
   d=base/spec["id"]; d.mkdir(); p=d/"acee_installation_executor.py"; p.write_text(make_mutant(src,spec)); m=load(p)
   killed=not probe(spec["id"],m,d)
   items.append({"mutant_id":spec["id"],"classification":"killed" if killed else "survived","source_hash":sha(src),"mutant_hash":hashlib.sha256(p.read_bytes()).hexdigest()})
 after=hashlib.sha256(TARGET.read_bytes()).hexdigest(); killed=sum(i["classification"]=="killed" for i in items); valid=len(items); score=killed/valid if valid else 0.0
 r={"primitive":"ACEE6_K_MUTATION_TESTING","stage":"ACEE6-K3","status":"ACEE6_K3_MUTATION_TESTING_COMPLETE","target_sha256":before,"mutant_count":valid,"valid_mutant_count":valid,"killed_count":killed,"survived_count":valid-killed,"mutation_score":round(score,12),"threshold":0.95,"threshold_met":score>=0.95,"real_root_mutation_count":0 if before==after else 1,"mutants":items,"invariants":{"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}}
 r["campaign_hash"]=sha({"target":before,"mutants":items}); r["report_hash"]=sha(r)
 if persist:
  REPORT.parent.mkdir(exist_ok=True); tmp=REPORT.with_suffix(".tmp"); tmp.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n"); os.replace(tmp,REPORT)
 return {"status":"ACEE6_K3_MUTATION_RUNNER_READY","report":r,"verification":verify(r),"report_path":str(REPORT) if persist else None}
def main():
 p=argparse.ArgumentParser(); p.add_argument("--limit",type=int); p.add_argument("--persist",action="store_true"); a=p.parse_args(); x=run(a.limit,a.persist); print(json.dumps(x,indent=2,sort_keys=True)); print(x["status"]); raise SystemExit(0 if x["verification"]["valid"] and x["report"]["threshold_met"] else 1)
if __name__=="__main__": main()
