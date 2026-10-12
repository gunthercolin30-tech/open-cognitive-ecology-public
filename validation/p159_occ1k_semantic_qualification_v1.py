from pathlib import Path
import json, hashlib

ROOT=Path.home()/"open-cognitive-ecology"
R1=ROOT/"validation_artifacts/p159/occ1k_r1"
R2=ROOT/"validation_artifacts/p159/occ1k_r2"
OUT=ROOT/"validation_artifacts/p159/occ1k_r3"

GATE_RULES={
"FL-B1":("Source Integrity",("occ1a","occ1b")),
"FL-B2":("Compilation Integrity",("occ1c",)),
"FL-B3":("Static Checks",("occ1d",)),
"FL-B4":("Independent Verification",("occ1f",)),
"FL-B5":("Golden Crown",("occ1g",)),
"FL-B6":("Defensive Crown",("occ1h",)),
"FL-B7":("Mutation Crown",("occ1i",)),
"FL-B8":("Reproducibility",("occ1j",)),
"FL-B9":("Persistence",("occ1j",)),
"FL-B10":("Evidence Integrity",("occ1k_r1","occ1k_r2")),
"FL-B11":("Residual Critical Findings",("occ1k_r1",)),
"FL-B12":("Non-Regression",("occ1k",)),
}

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def _load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def _r2():
    return _load(R2/"fl_b1_b12_blocker_gate_registry_v1.json")

def _r1():
    return _load(R1/"occ1k_r1_evidence_foundation_v1.json")

def _qualify_gate(g,r1):
    # R3 is deliberately conservative: R2 evidence presence alone is insufficient.
    if g["state"]=="EVIDENCE_MISSING":
        return "FAIL","Required evidence missing"
    if g["gate_id"]=="FL-B11":
        if r1["residual_risk_register"] or r1["assurance_debt_registry"]:
            return "BLOCKED","Open residual risk / assurance debt remains"
    return "INCONCLUSIVE","Evidence exists but canonical semantic criterion has not yet been independently established by R3"

def build():
    r1=_r1(); r2=_r2()
    q=[]
    for g in r2["gates"]:
        verdict,reason=_qualify_gate(g,r1)
        q.append({"gate_id":g["gate_id"],"title":g["title"],"verdict":verdict,
                  "reason":reason,"evidence_anchors":g["anchors"],
                  "lock_credit":"NOT_GRANTED"})
    counts={v:sum(x["verdict"]==v for x in q) for v in ("PASS","FAIL","BLOCKED","INCONCLUSIVE")}
    result={"schema":"oce.p159.occ1k.semantic_evidence_qualification.v1",
            "milestone":"P159/OCC-1K-R3","status":"SEMANTIC_QUALIFICATION_READY",
            "qualifications":q,"counts":counts,
            "all_gates_pass":counts["PASS"]==12,
            "lock_ready":False,"lock_granted":False,
            "historical_lock_preserved":True,"p160b_opened":False,
            "authorization_created":False,"execution_performed":False,
            "functional_conclusion_only":True,"phenomenology_undetermined":True}
    result["semantic_hash"]=hashlib.sha256(canonical(result)).hexdigest()
    return result

def write():
    OUT.mkdir(parents=True,exist_ok=True)
    r=build()
    p=OUT/"fl_b1_b12_semantic_qualification_v1.json"
    p.write_bytes(canonical(r)+b"\n")
    m={"schema":"oce.p159.occ1k.r3.manifest.v1","artifact":p.relative_to(ROOT).as_posix(),"sha256":sha(p)}
    mp=OUT/"occ1k_r3_sha256_manifest_v1.json"; mp.write_bytes(canonical(m)+b"\n")
    return r,p,mp

def main():
    r,p,mp=write()
    print("P159_OCC1K_R3_SEMANTIC_QUALIFICATION_READY")
    for k in ("PASS","FAIL","BLOCKED","INCONCLUSIVE"): print(k+"="+str(r["counts"][k]))
    print("ALL_GATES_PASS="+str(r["all_gates_pass"]).lower())
    print("LOCK_READY=false")
    print("LOCK_GRANTED=false")
    print("HISTORICAL_LOCK_MODIFIED=false")
    print("P160B_OPENED=false")
    print("ARTIFACT_SHA256="+sha(p)+" "+p.relative_to(ROOT).as_posix())
    print("MANIFEST_SHA256="+sha(mp)+" "+mp.relative_to(ROOT).as_posix())
if __name__=="__main__": main()
