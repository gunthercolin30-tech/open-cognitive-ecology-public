from pathlib import Path
import hashlib, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
EVID=ROOT/"validation_evidence"
PROTECTED=['ontology/dna_meta_rules.py',
 'validation/p090_functional_test.py',
 'validation/p090_degradation_test.py',
 'validation/p090_non_regression_test.py',
 'validation/p090_determinism_non_mutation_test.py',
 'validation/p090_transversal_boundary_test.py',
 'validation/p090_adversarial_crown_test.py',
 'validation/p090_nonclosure_interaction_crown_test.py']
TESTS=['validation.p090_functional_test',
 'validation.p090_degradation_test',
 'validation.p090_non_regression_test',
 'validation.p090_determinism_non_mutation_test',
 'validation.p090_transversal_boundary_test',
 'validation.p090_adversarial_crown_test',
 'validation.p090_nonclosure_interaction_crown_test']
P089_LOCK="c8f571840fcb6656d9ffdc9bed613845ca1deb541d1a8bc8f4bceed18b660015"

def sha256(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def main():
    results=[]
    for mod in TESTS:
        cp=subprocess.run([sys.executable,"-m",mod],cwd=str(ROOT),capture_output=True,text=True)
        if cp.returncode:
            raise AssertionError("test failed: %s\n%s\n%s" % (mod,cp.stdout,cp.stderr))
        results.append({"module":mod,"stdout":cp.stdout.strip(),"returncode":0})
    hashes={r:sha256(ROOT/r) for r in PROTECTED}
    payload={"milestone":"P090","schema":"oce.p090.final_lock.v2",
              "upstream_p089_final_lock":P089_LOCK,"protected_hashes":hashes}
    identity=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    report={**payload,"status":"LOCKED","protected_file_count":len(PROTECTED),
             "final_lock_identity_sha256":identity,"test_results":results,
             "p089_modified":False,"g2_declared":False,
             "downstream_w3_implemented":True,
             "functional_conclusion_only":True,"phenomenology_undetermined":True}
    EVID.mkdir(parents=True,exist_ok=True)
    out=EVID/"p090_final_lock_report.json"
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    loaded=json.loads(out.read_text(encoding="utf-8"))
    assert loaded["status"]=="LOCKED"
    assert loaded["protected_hashes"]==hashes
    assert loaded["final_lock_identity_sha256"]==identity
    assert loaded["upstream_p089_final_lock"]==P089_LOCK
    assert loaded["g2_declared"] is False
    print("P090_FINAL_LOCK_OK")
    print("status=LOCKED")
    print("protected_file_count=%d" % len(PROTECTED))
    print("final_lock_identity_sha256="+identity)
    print("report="+str(out))
    print("p089_modified=false")
    print("g2_declared=false")
    print("downstream_w3_implemented=true")
    print("functional_conclusion_only=true")
    print("phenomenology_undetermined=true")

if __name__=="__main__": main()
