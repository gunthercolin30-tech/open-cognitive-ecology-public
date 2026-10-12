from pathlib import Path
import hashlib, json

ROOT=Path.home()/"open-cognitive-ecology"
R1=ROOT/"validation_artifacts/p159/occ1k_r1"
OUT=ROOT/"validation_artifacts/p159/occ1k_r2"

GATES={
"FL-B1":{"title":"Source Integrity","anchors":["validation/evidence/p159_occ1a_closure/occ1a_closing_transaction_v1.json","validation_artifacts/p159/occ1b/occ1b_closure_transaction.json"]},
"FL-B2":{"title":"Compilation Integrity","anchors":["validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json","validation_artifacts/p159/occ1c/compile_report_v1.json"]},
"FL-B3":{"title":"Static Checks","anchors":["validation_artifacts/p159/occ1d/enforcement_coverage_map_v1.json"]},
"FL-B4":{"title":"Independent Verification","anchors":["validation_artifacts/p159/occ1f/independent_constitutional_verification_report_v1.json"]},
"FL-B5":{"title":"Golden Crown","anchors":["validation_artifacts/p159/occ1g/golden_run_report_v1.json","validation_artifacts/p159/occ1g/occ1g_closure_transaction_v1.json"]},
"FL-B6":{"title":"Defensive Crown","anchors":["validation_artifacts/p159/occ1h"]},
"FL-B7":{"title":"Mutation Crown","anchors":["validation_artifacts/p159/occ1i"]},
"FL-B8":{"title":"Reproducibility","anchors":["validation_artifacts/p159/occ1j/reproducibility_report_v1.json"]},
"FL-B9":{"title":"Persistence","anchors":["validation_artifacts/p159/occ1j/persistence_report_v1.json"]},
"FL-B10":{"title":"Evidence Integrity","anchors":["validation_artifacts/p159/occ1k_r1/occ1k_r1_sha256_manifest_v1.json"]},
"FL-B11":{"title":"Residual Critical Findings","anchors":["validation_artifacts/p159/occ1k_r1/occ_residual_risk_register_v1.json","validation_artifacts/p159/occ1k_r1/occ_assurance_debt_registry_v1.json"]},
"FL-B12":{"title":"Non-Regression","anchors":["validation_artifacts/p159/occ1k/p159_postlock_verification_v1.json"]},
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def inspect_anchor(rel):
    p=ROOT/rel
    if p.is_dir():
        files=sorted(x for x in p.rglob("*") if x.is_file() and not x.name.endswith(".bak"))
        return {"path":rel,"kind":"directory","present":bool(files),"file_count":len(files),
                "aggregate":hashlib.sha256("".join(sha(x) for x in files).encode()).hexdigest() if files else None}
    return {"path":rel,"kind":"file","present":p.is_file(),"sha256":sha(p) if p.is_file() else None}

def build():
    gates=[]
    for gid,spec in GATES.items():
        anchors=[inspect_anchor(x) for x in spec["anchors"]]
        state="EVIDENCE_PRESENT" if all(a["present"] for a in anchors) else "EVIDENCE_MISSING"
        # Presence is never semantic qualification.
        gates.append({"gate_id":gid,"title":spec["title"],"state":state,"anchors":anchors,
                      "semantic_verdict":"TO_BE_QUALIFIED","lock_credit":"NOT_GRANTED"})

    risk_path=R1/"occ_residual_risk_register_v1.json"
    debt_path=R1/"occ_assurance_debt_registry_v1.json"
    open_risks=[]; open_debts=[]
    if risk_path.is_file():
        open_risks=[x for x in json.loads(risk_path.read_text())["items"] if x.get("status")=="OPEN"]
    if debt_path.is_file():
        open_debts=[x for x in json.loads(debt_path.read_text())["items"] if x.get("status")=="OPEN"]

    for g in gates:
        if g["gate_id"]=="FL-B11":
            g["state"]="BLOCKED" if open_risks or open_debts else g["state"]
            g["semantic_verdict"]="BLOCKED_BY_OPEN_RISK_OR_DEBT" if open_risks or open_debts else "TO_BE_QUALIFIED"

    r={"schema":"oce.p159.occ1k.blocker_gates.v1","milestone":"P159/OCC-1K-R2",
       "status":"BLOCKER_GATES_READY","gates":gates,
       "open_risk_count":len(open_risks),"open_debt_count":len(open_debts),
       "all_gates_pass":False,"lock_ready":False,"lock_granted":False,
       "historical_lock_preserved":True,"p160b_opened":False,
       "authorization_created":False,"execution_performed":False,
       "functional_conclusion_only":True,"phenomenology_undetermined":True}
    r["semantic_hash"]=hashlib.sha256(canonical(r)).hexdigest()
    return r

def write():
    OUT.mkdir(parents=True,exist_ok=True)
    r=build()
    p=OUT/"fl_b1_b12_blocker_gate_registry_v1.json"
    p.write_bytes(canonical(r)+b"\n")
    m={"schema":"oce.p159.occ1k.r2.manifest.v1","artifact":p.relative_to(ROOT).as_posix(),"sha256":sha(p)}
    mp=OUT/"occ1k_r2_sha256_manifest_v1.json"; mp.write_bytes(canonical(m)+b"\n")
    return r,p,mp

def main():
    r,p,mp=write()
    print("P159_OCC1K_R2_BLOCKER_GATES_READY")
    print("GATES="+str(len(r["gates"])))
    print("EVIDENCE_PRESENT="+str(sum(g["state"]=="EVIDENCE_PRESENT" for g in r["gates"])))
    print("EVIDENCE_MISSING="+str(sum(g["state"]=="EVIDENCE_MISSING" for g in r["gates"])))
    print("BLOCKED="+str(sum(g["state"]=="BLOCKED" for g in r["gates"])))
    print("OPEN_RISKS="+str(r["open_risk_count"]))
    print("OPEN_DEBTS="+str(r["open_debt_count"]))
    print("ALL_GATES_PASS=false")
    print("LOCK_READY=false")
    print("LOCK_GRANTED=false")
    print("HISTORICAL_LOCK_MODIFIED=false")
    print("P160B_OPENED=false")
    print("ARTIFACT_SHA256="+sha(p)+" "+p.relative_to(ROOT).as_posix())
    print("MANIFEST_SHA256="+sha(mp)+" "+mp.relative_to(ROOT).as_posix())
if __name__=="__main__": main()
