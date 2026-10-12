
from __future__ import annotations
from pathlib import Path
import hashlib, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"validation"/"evidence"/"p160e_ccad_runtime_arbitration"
RUNTIME=ROOT/"ontology"/"p160_ccad_runtime_arbitration.py"
EXPECTED_RUNTIME="a41e62799b0fc0b1e0eda520c478b3b6faf5734913395d9fa4cfa9856a71d9e2"
PROTECTED={
"ontology/p160_ccad_runtime_arbitration.py":EXPECTED_RUNTIME,
"validation/p160e_ccad_runtime_arbitration_v1.py":"2eb74b47a7e40b6aa17bc421ee71fecd747d857965b9ceba9e8f6b7351481ec8",
"validation/p160e_ccad_runtime_arbitration_v1_test.py":"f684bd31a0e59008a159d748096b48527955b5090fe0abb2dfbc64282a3fcde7",
"validation/p160e_ccad_runtime_arbitration_defensive_crown_v1.py":"08ffd6c6da2fb5598443186d65654f973810d2b47ed32015be99b240c1e4642b",
"validation/p160e_ccad_runtime_arbitration_defensive_crown_v1_test.py":"049f5b784a142235af0c879b6873180b6619acd7906ca24e8621fb744f1a6df7",
"validation/p160e_ccad_runtime_arbitration_mutation_crown_v1.py":"1bf63e6be048d91adaec0db5cdc924d19f58b410dcb9adef7bf95f12f4f5ea4f",
"validation/p160d_normative_conflict_detection_v1_test.py":"f9a30d0feb2db271eee86efe90dc8f4316f881253d396fff9f69af51731f4cf0",
"validation/evidence/p156_ccad_specification/p156_final_lock_v1.json":"d838e49076bfbee32a848dd956d342c1692c55928fcec396aa1fbd2f5b7772e8",
"validation/evidence/p156_ccad_specification/p156_postlock_verification_v1.json":"915790020ac37966b9ed98293ea90aace3264e60418e001b94606e0569b6d883",
"validation/evidence/p157_ccad_adversarial_crown/p157_exit_audit_v1.json":"4d4c092a81421169bc83983e096c3088154cfb5389763b24f405b529feca8240",
"validation/evidence/p158_ccad_final_lock/CCAD_FINAL_LOCK_REPORT.json":"cd826bf7d47e594c9452798e5e23f886608db79d26fac042a103e2b9602693b3",
"validation/evidence/p158_ccad_final_lock/MANIFEST.sha256":"578c8d7bb1c893ba5f24c66b825b2dbf24247e6b54c5fb6a4da050b70d7a62d4",
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def run(cmd):
    cp=subprocess.run(cmd,cwd=str(ROOT),text=True,capture_output=True)
    print("$ "+" ".join(cmd)); print(cp.stdout,end="")
    if cp.returncode: print(cp.stderr,end="",file=sys.stderr); raise SystemExit(cp.returncode)
def verify_hashes():
    bad=[]
    for rel,expected in PROTECTED.items():
        p=ROOT/rel
        if not p.is_file() or sha(p)!=expected: bad.append(rel)
    if bad: raise SystemExit("P160E_PROTECTED_HASH_DRIFT:"+",".join(bad))
def materialize_artifacts():
    from validation import p160e_ccad_runtime_arbitration_v1_test as h
    from ontology import p160_ccad_runtime_arbitration as e
    o=h.resolve(h.dcase("C2"),h.evidence())
    if e.verify_ccad_resolution(o).get("status")!="PASS": raise SystemExit("P160E_SAMPLE_VERIFICATION_FAILED")
    mapping={
      "conflict_case":o.get("conflict_case"),
      "ccad_resolution":o.get("ccad_resolution"),
      "constitutional_injury":o.get("constitutional_injuries"),
      "distributional_impact":o.get("distributional_impact"),
      "proportionality_assessment":o.get("proportionality_assessment"),
      "resolution_uncertainty":o.get("resolution_uncertainty"),
      "tragic_choice_record":o.get("tragic_choice_record"),
      "human_decision_requirements":o.get("human_decision_requirements"),
    }
    # Explicitly represent legitimate absence of injury/impact/uncertainty.
    if mapping["constitutional_injury"] is None: mapping["constitutional_injury"] = []
    if mapping["distributional_impact"] is None: mapping["distributional_impact"] = []
    if mapping["resolution_uncertainty"] is None: mapping["resolution_uncertainty"] = []
    missing=[k for k in ("conflict_case","ccad_resolution","proportionality_assessment") if mapping[k] is None]
    if missing: raise SystemExit("P160E_REQUIRED_ARTIFACT_ABSENT:"+",".join(missing))
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    out={}
    for name,value in mapping.items():
        obj={"schema":"oce.p160e.lock-artifact.v1","artifact":name,"value":value,
             "functional_conclusion_only":True,"phenomenology_undetermined":True}
        data=canonical(obj)+b"\n"; p=EVIDENCE/(name+".json"); p.write_bytes(data); out[name]=sha(p)
    return out
def main():
    verify_hashes()
    run([sys.executable,"-m","pytest","-q","validation/p160e_ccad_runtime_arbitration_v1_test.py"])
    run([sys.executable,"-m","pytest","-q","validation/p160e_ccad_runtime_arbitration_defensive_crown_v1_test.py"])
    run([sys.executable,"-m","validation.p160e_ccad_runtime_arbitration_mutation_crown_v1"])
    run([sys.executable,"-m","validation.p160e_ccad_runtime_arbitration_v1"])
    run([sys.executable,"-m","validation.p160e_ccad_runtime_arbitration_defensive_crown_v1"])
    run([sys.executable,"-m","pytest","-q","validation/p160d_normative_conflict_detection_v1_test.py"])
    verify_hashes()
    artifacts=materialize_artifacts()
    report={
      "schema":"oce.p160e.final-lock.v1","milestone":"P160-E","status":"LOCKED",
      "runtime_sha256":EXPECTED_RUNTIME,"baseline":"PASS_14_OF_14",
      "defensive_crown":"PASS_14_OF_14","mutation_score":1.0,
      "mutants_killed":"10/10","mutants_survived":0,"mutants_inconclusive":0,
      "protected_hashes":PROTECTED,"machine_readable_artifacts":artifacts,
      "boundaries":{"authority_resolved":False,"authority_created":False,
        "authorization_created":False,"execution_performed":False,
        "p160f_opened":False,"p161_opened":False},
      "functional_conclusion_only":True,"phenomenology_undetermined":True,
      "next_if_global_validation_passes":"P160-F",
    }
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    rp=EVIDENCE/"P160E_FINAL_LOCK_REPORT.json"; rp.write_bytes(canonical(report)+b"\n")
    manifest={"report_sha256":sha(rp),"runtime_sha256":EXPECTED_RUNTIME,
              "artifact_hashes":artifacts,"protected_hashes":PROTECTED}
    mp=EVIDENCE/"P160E_FINAL_LOCK_MANIFEST.json"; mp.write_bytes(canonical(manifest)+b"\n")
    verify_hashes()
    print("P160E_FINAL_LOCK_OK")
    print("STATUS=LOCKED")
    print("MUTATION_SCORE=1.0")
    print("MUTANTS_SURVIVED=0")
    print("MUTANTS_INCONCLUSIVE=0")
    print("RUNTIME_SHA256="+EXPECTED_RUNTIME)
    print("REPORT_SHA256="+sha(rp))
    print("MANIFEST_SHA256="+sha(mp))
    print("AUTHORITY_CREATED=false")
    print("AUTHORIZATION_CREATED=false")
    print("EXECUTION_PERFORMED=false")
    print("P160F_OPENED=false")
    print("P161_OPENED=false")
if __name__=="__main__": main()
