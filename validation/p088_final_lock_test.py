from __future__ import annotations
from pathlib import Path
import hashlib, json, subprocess, sys
from ontology import dna_fundamental as d

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"validation_evidence"
EVIDENCE.mkdir(exist_ok=True)

PROTECTED_REL=(
 "ontology/dna_fundamental.py",
 "validation/p088_functional_test.py",
 "validation/p088_conflict_degradation_test.py",
 "validation/p088_authority_separation_test.py",
 "validation/p088_non_regression_test.py",
 "validation/p088_determinism_non_mutation_test.py",
 "validation/p088_adversarial_crown_test.py",
 "validation/p088_boundary_crown_test.py",
)

TEST_MODULES=(
 "validation.p088_functional_test",
 "validation.p088_conflict_degradation_test",
 "validation.p088_authority_separation_test",
 "validation.p088_non_regression_test",
 "validation.p088_determinism_non_mutation_test",
 "validation.p088_adversarial_crown_test",
 "validation.p088_boundary_crown_test",
)

def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()

def main():
 missing=[r for r in PROTECTED_REL if not (ROOT/r).is_file()]
 if missing: raise AssertionError("missing protected files: "+",".join(missing))

 results=[]
 for mod in TEST_MODULES:
  p=subprocess.run([sys.executable,"-m",mod],cwd=ROOT,text=True,capture_output=True)
  if p.returncode!=0:
   raise AssertionError(f"{mod} failed\\nSTDOUT:\\n{p.stdout}\\nSTDERR:\\n{p.stderr}")
  results.append({"module":mod,"status":"PASS","stdout":p.stdout.strip()})

 manifest={r:sha256(ROOT/r) for r in PROTECTED_REL}
 identity_payload=json.dumps(manifest,sort_keys=True,separators=(",",":")).encode()
 identity=hashlib.sha256(identity_payload).hexdigest()

 m=d.fundamental_manifest()
 assert m["version"]=="P088-v1"
 assert m["functional_conclusion_only"] is True
 assert m["phenomenology_undetermined"] is True
 assert m["p015_p024_reused_without_mutation"] is True

 report={
  "milestone":"P088",
  "status":"LOCKED",
  "schema":"oce.p088.final_lock.v1",
  "primitive":"dna_fundamental",
  "primitive_version":m["version"],
  "protected_file_count":len(PROTECTED_REL),
  "protected_hashes":manifest,
  "final_lock_identity_sha256":identity,
  "local_and_adversarial_tests":results,
  "p015_p024_reused_without_mutation":True,
  "p089_started":False,
  "p090_started":False,
  "p061_p086_execution_prerequisite":False,
  "functional_conclusion_only":True,
  "phenomenology_undetermined":True,
 }
 out=EVIDENCE/"p088_final_lock_report.json"
 out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")

 # Read-back consistency.
 loaded=json.loads(out.read_text(encoding="utf-8"))
 assert loaded["final_lock_identity_sha256"]==identity
 assert loaded["protected_hashes"]==manifest
 assert loaded["status"]=="LOCKED"

 print("P088_FINAL_LOCK_OK")
 print("status=LOCKED")
 print("protected_file_count="+str(len(PROTECTED_REL)))
 print("final_lock_identity_sha256="+identity)
 print("report="+str(out))
 print("p015_p024_reused_without_mutation=true")
 print("functional_conclusion_only=true")
 print("phenomenology_undetermined=true")

if __name__=="__main__":
 main()
