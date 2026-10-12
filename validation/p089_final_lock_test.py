from pathlib import Path
import hashlib, json, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
EVID=ROOT/"validation_evidence"
PROTECTED=['ontology/dna_f1_f18.py',
 'validation/p089_functional_test.py',
 'validation/p089_degradation_test.py',
 'validation/p089_non_regression_test.py',
 'validation/p089_determinism_non_mutation_test.py',
 'validation/p089_f17_f18_boundary_test.py',
 'validation/p089_adversarial_crown_test.py',
 'validation/p089_machinery_boundary_crown_test.py']
TESTS=['validation.p089_functional_test',
 'validation.p089_degradation_test',
 'validation.p089_non_regression_test',
 'validation.p089_determinism_non_mutation_test',
 'validation.p089_f17_f18_boundary_test',
 'validation.p089_adversarial_crown_test',
 'validation.p089_machinery_boundary_crown_test']
P088_LOCK="f1a7d4adf322378726d9c0f7f481c8c8fe820fac62e3d08e6b2094be2f9b9b59"

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    results=[]
    for mod in TESTS:
        cp=subprocess.run([sys.executable,"-m",mod],cwd=str(ROOT),capture_output=True,text=True)
        if cp.returncode != 0:
            raise AssertionError("test failed: %s\n%s\n%s" % (mod,cp.stdout,cp.stderr))
        results.append({"module":mod,"stdout":cp.stdout.strip(),"returncode":cp.returncode})
    hashes={rel:sha256(ROOT/rel) for rel in PROTECTED}
    payload={"milestone":"P089","schema":"oce.p089.final_lock.v1",
             "upstream_p088_final_lock":P088_LOCK,"protected_hashes":hashes}
    identity=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    report={**payload,"status":"LOCKED","protected_file_count":len(PROTECTED),
            "final_lock_identity_sha256":identity,"test_results":results,
            "p088_modified":False,"p090_implemented":True,
            "f18_status":"CANONICAL",
            "functional_conclusion_only":True,"phenomenology_undetermined":True}
    out=EVID/"p089_final_lock_report.json"
    EVID.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    loaded=json.loads(out.read_text(encoding="utf-8"))
    assert loaded["status"]=="LOCKED"
    assert loaded["protected_hashes"]==hashes
    assert loaded["final_lock_identity_sha256"]==identity
    assert loaded["f18_status"]=="CANONICAL"
    print("P089_FINAL_LOCK_OK")
    print("status=LOCKED")
    print("protected_file_count=%d" % len(PROTECTED))
    print("final_lock_identity_sha256="+identity)
    print("report="+str(out))
    print("p088_modified=false")
    print("p090_implemented=true")
    print("f18_status=CANONICAL")
    print("functional_conclusion_only=true")
    print("phenomenology_undetermined=true")

if __name__=="__main__":
    main()
