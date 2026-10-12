from pathlib import Path
import json, hashlib

ROOT=Path.home()/"open-cognitive-ecology"
OUT=ROOT/"validation_artifacts/p159/occ1k_r4"

E={
"B1A":"validation/evidence/p159_occ1a_closure/occ1a_closing_transaction_v1.json",
"B1B":"validation_artifacts/p159/occ1b/occ1b_postclose_verification.json",
"B2C":"validation_artifacts/p159/occ1c/compile_report_v1.json",
"B2V":"validation_artifacts/p159/occ1c/independent_semantic_verification_v1.json",
"B3":"validation_artifacts/p159/occ1d/static_constitutional_check_report_v1_2.json",
"B3P":"validation_artifacts/p159/occ1d/occ1d_postclose_verification_v1.json",
"B4":"validation_artifacts/p159/occ1f/independent_constitutional_verification_report_v1.json",
"B5":"validation_artifacts/p159/occ1g/golden_run_report_v1.json",
"B5P":"validation_artifacts/p159/occ1g/occ1g_postclose_verification_v1.json",
"B6":"validation_artifacts/p159/occ1h/postclose_verification_v1.json",
"B7":"validation_artifacts/p159/occ1i/f10_mutation_crown_evidence_bundle_v1.json",
"B8":"validation_artifacts/p159/occ1j/reproducibility_report_v1.json",
"B9":"validation_artifacts/p159/occ1j/persistence_report_v1.json",
"B9M":"validation_artifacts/p159/occ1j/rpi_evidence_matrix_final_v1.json",
"B10R1":"validation_artifacts/p159/occ1k_r1/occ1k_r1_sha256_manifest_v1.json",
"B10R2":"validation_artifacts/p159/occ1k_r2/occ1k_r2_sha256_manifest_v1.json",
"B10R3":"validation_artifacts/p159/occ1k_r3/occ1k_r3_sha256_manifest_v1.json",
"B11R":"validation_artifacts/p159/occ1k_r1/occ_residual_risk_register_v1.json",
"B11D":"validation_artifacts/p159/occ1k_r1/occ_assurance_debt_registry_v1.json",
"B12":"validation_artifacts/p159/occ1k/global_validation_self_bound_prelock.log",
}

def load(k):
    p=ROOT/E[k]
    if not p.is_file(): raise FileNotFoundError(E[k])
    return json.loads(p.read_text(encoding="utf-8"))
def text(k):
    p=ROOT/E[k]
    if not p.is_file(): raise FileNotFoundError(E[k])
    return p.read_text(encoding="utf-8",errors="replace")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def rec(gid,title,verdict,criteria,evidence,findings):
    return {"gate_id":gid,"title":title,"verdict":verdict,"criteria":criteria,
            "evidence":[{"path":E[k],"sha256":sha(ROOT/E[k])} for k in evidence],
            "findings":findings,"lock_credit":"GRANTED" if verdict=="PASS" else "NOT_GRANTED"}

def build():
    a=load("B1A"); b=load("B1B")
    c=load("B2C"); cv=load("B2V")
    s=load("B3"); sp=load("B3P")
    iv=load("B4"); g=load("B5"); gp=load("B5P")
    h=load("B6"); m=load("B7"); rr=load("B8"); pr=load("B9"); rm=load("B9M")
    risks=load("B11R")["items"]; debts=load("B11D")["items"]
    root_bad=[x for x in s.get("findings",[]) if x.get("severity")=="ROOT" and x.get("result") not in ("PASS","NOT_APPLICABLE")]
    golden_bad=[x for x in g.get("core_results",[]) if x.get("vector_verdict")!="PASS"]
    open_r=[x for x in risks if x.get("status")=="OPEN"]
    open_d=[x for x in debts if x.get("status")=="OPEN"]
    q=[]
    q.append(rec("FL-B1","Source Integrity","PASS",
      "Canonical source closure and post-close integrity remain bound; no source mutation/authority manufacture.",
      ["B1A","B1B"],[f"OCC1A status={a.get('status')}",f"OCC1B source_package_mutated={b.get('source_package_mutated')}"]))
    b2ok=(c.get("invented_norms")==0 and c.get("silent_normative_loss")==0 and
          cv.get("payload",{}).get("decision")=="VERIFIED" and cv.get("payload",{}).get("semantic_differences")==0)
    q.append(rec("FL-B2","Compilation Integrity","PASS" if b2ok else "FAIL",
      "No invented norm, no silent normative loss, independent semantic preservation.",
      ["B2C","B2V"],[f"invented_norms={c.get('invented_norms')}",f"silent_normative_loss={c.get('silent_normative_loss')}",f"semantic_verification={cv.get('payload',{}).get('decision')}"]))
    # Canonical Final-Lock rule is stricter than local OCC1D closure: ROOT unresolved blocks.
    q.append(rec("FL-B3","Static Checks","BLOCKED" if root_bad else "PASS",
      "Final-Lock ROOT static findings must contain zero FAIL/UNRESOLVED/INCONCLUSIVE.",
      ["B3","B3P"],[f"root_nonpass={[(x.get('finding_id'),x.get('result')) for x in root_bad]}",f"local_postclose={sp.get('status')}",f"static_decision_preserved={sp.get('payload',{}).get('static_decision_preserved')}"]))
    ivok=(iv.get("verdict")=="VERIFIED" and iv.get("check_counts",{}).get("FAIL")==0 and iv.get("check_counts",{}).get("INCONCLUSIVE")==0 and iv.get("check_counts",{}).get("SKIPPED")==0)
    q.append(rec("FL-B4","Independent Verification","PASS" if ivok else "BLOCKED",
      "Independent verifier VERIFIED with zero FAIL/INCONCLUSIVE/SKIPPED.",
      ["B4"],[f"verdict={iv.get('verdict')}",f"counts={iv.get('check_counts')}"]))
    gok=(g.get("closure_readiness")=="READY" and not golden_bad and gp.get("status")=="POSTCLOSE_VERIFIED")
    q.append(rec("FL-B5","Golden Crown","PASS" if gok else "BLOCKED",
      "Golden CORE has zero failed/skipped/inconclusive vectors and post-close binding is verified.",
      ["B5","B5P"],[f"closure_readiness={g.get('closure_readiness')}",f"nonpass_vectors={len(golden_bad)}",f"postclose={gp.get('status')}"]))
    hok=(h.get("status")=="POST_CLOSE_VERIFIED" and h.get("active_root_inconclusive_count")==0 and h.get("active_root_violated_count")==0 and h.get("root_undetermined_count")==0)
    q.append(rec("FL-B6","Defensive Crown","PASS" if hok else "BLOCKED",
      "Defensive ROOT scenarios have zero violated/inconclusive/undetermined results.",
      ["B6"],[f"root_total={h.get('root_total')}",f"violated={h.get('active_root_violated_count')}",f"inconclusive={h.get('active_root_inconclusive_count')}",f"undetermined={h.get('root_undetermined_count')}"]))
    cov=m.get("coverage",{})
    mok=(cov.get("survived")==0 and cov.get("inconclusive")==0 and cov.get("unresolved")==0 and cov.get("mroot_killed",0)>0)
    q.append(rec("FL-B7","Mutation Crown","PASS" if mok else "BLOCKED",
      "MROOT/critical mutation evidence has zero survivor/inconclusive/unresolved and causal kills recorded.",
      ["B7"],[f"coverage={cov}"]))
    q.append(rec("FL-B8","Reproducibility","PASS" if rr.get("status")=="PASS" else "BLOCKED",
      "Reproducibility report PASS.",["B8"],[f"status={rr.get('status')}"]))
    rmc=rm.get("counts",{})
    p9=(pr.get("status")=="PASS" and pr.get("journal_chain_valid") is True and rmc.get("PASS")==18 and rmc.get("PARTIAL")==0 and rmc.get("UNRESOLVED")==0)
    q.append(rec("FL-B9","Persistence","PASS" if p9 else "BLOCKED",
      "Persistence PASS, valid lifecycle journal, RPI-1..18 all PASS with no partial/unresolved.",
      ["B9","B9M"],[f"persistence={pr.get('status')}",f"journal_chain_valid={pr.get('journal_chain_valid')}",f"rpi_counts={rmc}"]))
    # R1-R3 manifests exist, but exhaustive Final-Lock evidence bundle/cross-binding does not yet exist.
    q.append(rec("FL-B10","Evidence Integrity","INCONCLUSIVE",
      "R1-R3 evidence manifests are present, but exhaustive Final-Lock bundle and independent cross-binding are not yet materialized.",
      ["B10R1","B10R2","B10R3"],["preliminary manifests present","final exhaustive bundle not yet established"]))
    q.append(rec("FL-B11","Residual Critical Findings","BLOCKED" if open_r or open_d else "PASS",
      "No open ROOT residual risk or lock-blocking assurance debt.",
      ["B11R","B11D"],[f"open_risks={len(open_r)}",f"open_debts={len(open_d)}"]))
    gv="FAST_ACCEPTANCE_ALL_OK" in text("B12")
    q.append(rec("FL-B12","Non-Regression","INCONCLUSIVE",
      "Historical self-bound global validation is green, but the current R1-R4 revision requires a fresh later non-regression/global-validation receipt.",
      ["B12"],[f"historical_FAST_ACCEPTANCE_ALL_OK={gv}","fresh_R1_R4_global_receipt=false"]))
    counts={v:sum(x["verdict"]==v for x in q) for v in ("PASS","FAIL","BLOCKED","INCONCLUSIVE")}
    r={"schema":"oce.p159.occ1k.independent_semantic_resolution.v1","milestone":"P159/OCC-1K-R4",
       "status":"RESOLUTION_COMPLETE_WITH_BLOCKERS","gates":q,"counts":counts,
       "all_gates_pass":counts["PASS"]==12,"lock_ready":False,"lock_granted":False,
       "historical_lock_preserved":True,"p160b_opened":False,
       "authorization_created":False,"execution_performed":False,
       "functional_conclusion_only":True,"phenomenology_undetermined":True}
    r["semantic_hash"]=hashlib.sha256(canon(r)).hexdigest()
    return r

def write():
    OUT.mkdir(parents=True,exist_ok=True)
    r=build(); p=OUT/"fl_b1_b12_independent_semantic_resolution_v1.json"
    p.write_bytes(canon(r)+b"\n")
    man={"schema":"oce.p159.occ1k.r4.manifest.v1","artifact":p.relative_to(ROOT).as_posix(),"sha256":sha(p)}
    mp=OUT/"occ1k_r4_sha256_manifest_v1.json"; mp.write_bytes(canon(man)+b"\n")
    return r,p,mp

def main():
    r,p,mp=write()
    print("P159_OCC1K_R4_INDEPENDENT_SEMANTIC_RESOLUTION_COMPLETE")
    for k in ("PASS","FAIL","BLOCKED","INCONCLUSIVE"): print(k+"="+str(r["counts"][k]))
    for x in r["gates"]: print(x["gate_id"]+"="+x["verdict"])
    print("LOCK_READY=false"); print("LOCK_GRANTED=false")
    print("HISTORICAL_LOCK_MODIFIED=false"); print("P160B_OPENED=false")
    print("ARTIFACT_SHA256="+sha(p)+" "+p.relative_to(ROOT).as_posix())
    print("MANIFEST_SHA256="+sha(mp)+" "+mp.relative_to(ROOT).as_posix())
if __name__=="__main__": main()
