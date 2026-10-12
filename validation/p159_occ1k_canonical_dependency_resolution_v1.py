from pathlib import Path
import json, hashlib

ROOT=Path.home()/"open-cognitive-ecology"
OUT=ROOT/"validation_artifacts/p159/occ1k_r6"

STATIC="validation_artifacts/p159/occ1d/static_constitutional_check_report_v1_2.json"
COVERAGE="validation_artifacts/p159/occ1d/s7_s8_s10_executable_coverage_v1.json"
R5="validation_artifacts/p159/occ1k_r5/fl_b3_boundary_reconciliation_audit_v1.json"

def load(rel): return json.loads((ROOT/rel).read_text(encoding="utf-8"))
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def build():
    s=load(STATIC); c=load(COVERAGE); r5=load(R5)
    fs={x["finding_id"]:x for x in s["findings"]}
    ids=("S7.CCAD","S8.COMPOSITION","S10.ENFORCEMENT")
    findings={i:{"severity":fs[i]["severity"],"historical_result":fs[i]["result"],
                 "historical_disposition":fs[i]["disposition"]} for i in ids}
    facts={
      "historical_findings_preserved":all(fs[i]["result"]=="UNRESOLVED" for i in ids),
      "runtime_consumers_not_created":c.get("runtime_consumers_created") is False,
      "p160_not_opened":c.get("p160_opened") is False and r5["conclusion"]["p160b_opened"] is False,
      "r5_requires_reconciliation":r5["status"]=="CANONICAL_BOUNDARY_RECONCILIATION_REQUIRED",
    }
    # Canonical source resolution recorded as data, never as an invented runtime fact:
    canonical={
      "p159_order":"OCC-1 implementation and Final Lock precede P160",
      "p159_runtime_rule":"P159 implementation criteria explicitly say not to start with runtime",
      "p160_input_contract":"P160 consumes a verified CompiledNormativeProfile issued by P159/OCC-1",
      "p160_scope":"P160-A..K owns runtime context, norm resolution, constitutive filter, conflict detection, CCAD runtime arbitration, authority resolution, decision sealing and its own Final Lock",
      "resolution":"PRE_RUNTIME_CONTRACT_OBLIGATION",
      "meaning":"P159 may prove static contract completeness/fail-closed behavior and bind deferred runtime obligations; it must not require or fabricate P160 runtime materialization as a precondition to entering P160.",
    }
    result={
      "schema":"oce.p159.occ1k.canonical_dependency_resolution.v1",
      "milestone":"P159/OCC-1K-R6",
      "status":"CANONICAL_DEPENDENCY_RESOLVED",
      "resolution_class":"PRE_RUNTIME_CONTRACT_OBLIGATION",
      "canonical_resolution":canonical,
      "historical_static_findings":findings,
      "facts":facts,
      "effects":{
        "historical_occ1d_rewritten":False,
        "static_pass_manufactured":False,
        "runtime_graph_invented":False,
        "runtime_binding_created":False,
        "p160b_opened":False,
        "fl_b3_promoted_to_pass":False,
        "lock_ready":False,
        "lock_granted":False,
        "next_required_step":"R7_SUPERSEDING_PRE_RUNTIME_STATIC_CONTRACT_ASSESSMENT"
      },
      "r7_acceptance_rule":[
        "S7/S8/S10 may only be resolved for P159 if their P159-side contract is explicit, deterministic, fail-closed and provenance-bound.",
        "Any property requiring actual P160 runtime state remains a deferred obligation bound to P160 and cannot be represented as an observed runtime fact in P159.",
        "R7 must preserve the historical UNRESOLVED OCC-1D report and produce a distinct superseding assessment.",
        "No deferred obligation may be converted to PASS merely because P160 is planned.",
        "P160 remains unopened until the P159-side contract assessment and remaining Final-Lock criteria permit the governed transition."
      ],
      "functional_conclusion_only":True,"phenomenology_undetermined":True
    }
    assert all(facts.values())
    result["semantic_hash"]=hashlib.sha256(canon(result)).hexdigest()
    return result

def write():
    OUT.mkdir(parents=True,exist_ok=True)
    r=build(); p=OUT/"canonical_dependency_resolution_v1.json"
    p.write_bytes(canon(r)+b"\n")
    m={"schema":"oce.p159.occ1k.r6.manifest.v1","artifact":p.relative_to(ROOT).as_posix(),"sha256":sha(p)}
    mp=OUT/"occ1k_r6_sha256_manifest_v1.json"; mp.write_bytes(canon(m)+b"\n")
    return r,p,mp

def main():
    r,p,mp=write()
    print("P159_OCC1K_R6_CANONICAL_DEPENDENCY_RESOLUTION_COMPLETE")
    print("STATUS="+r["status"])
    print("RESOLUTION_CLASS="+r["resolution_class"])
    print("HISTORICAL_OCC1D_REWRITTEN=false")
    print("STATIC_PASS_MANUFACTURED=false")
    print("RUNTIME_BINDING_CREATED=false")
    print("P160B_OPENED=false")
    print("FL_B3_PROMOTED_TO_PASS=false")
    print("LOCK_READY=false")
    print("LOCK_GRANTED=false")
    print("NEXT="+r["effects"]["next_required_step"])
    print("ARTIFACT_SHA256="+sha(p))
    print("MANIFEST_SHA256="+sha(mp))
if __name__=="__main__": main()
