from pathlib import Path
import json, hashlib
try:
    import yaml
except Exception:
    yaml=None

ROOT=Path.home()/"open-cognitive-ecology"
OUT=ROOT/"validation_artifacts/p159/occ1k_r8"

def read_struct(rel):
    p=ROOT/rel
    raw=p.read_text(encoding="utf-8")
    if p.suffix==".json": return json.loads(raw)
    if yaml is None: raise RuntimeError("PyYAML required for canonical YAML evidence")
    return yaml.safe_load(raw)
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def build():
    cc=read_struct("normative/occ1a/ccad/ccad_conflict_classes.yaml")
    constitution=read_struct("normative/occ1a/constitution/constitution.yaml")
    governance=read_struct("normative/occ1a/governance/governance.yaml")
    cnp=read_struct("validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json")
    r7=read_struct("validation_artifacts/p159/occ1k_r7/pre_runtime_static_contract_assessment_v1.json")
    ccad=(ROOT/"ontology/ccad_specification.py").read_text(encoding="utf-8")
    checker=(ROOT/"ontology/occ_static_constitutional_checker.py").read_text(encoding="utf-8")
    s10=read_struct("validation_artifacts/p159/occ1d/s10_enforcement_evidence_v1.json")

    source_gaps={
      "ccad_conflict_classes":{
        "population_status":cc.get("population_status"),
        "package_state":cc.get("package_state"),
        "norm_count":len(cc.get("norms") or []),
        "note":cc.get("note"),
      },
      "constitution":{
        "population_status":constitution.get("population_status"),
        "package_state":constitution.get("package_state"),
        "norm_count":len(constitution.get("norms") or []),
      },
      "governance":{
        "population_status":governance.get("population_status"),
        "package_state":governance.get("package_state"),
        "norm_count":len(governance.get("norms") or []),
      },
    }
    facts={
      "ccad_conflict_partition_unresolved":source_gaps["ccad_conflict_classes"]["population_status"]=="UNRESOLVED" and source_gaps["ccad_conflict_classes"]["norm_count"]==0,
      "constitution_partition_unresolved":source_gaps["constitution"]["population_status"]=="UNRESOLVED" and source_gaps["constitution"]["norm_count"]==0,
      "governance_partition_unresolved":source_gaps["governance"]["population_status"]=="UNRESOLVED" and source_gaps["governance"]["norm_count"]==0,
      "ccad_spec_has_conflict_taxonomy":"CONFLICT_CLASSES" in ccad,
      "cnp_relations_empty":len(cnp.get("relations") or [])==0,
      "checker_supports_s7_s8_s10":all(x in checker for x in ("_s7_conflict_ccad","_s8_composition","_s10_enforcement")),
      "s10_runtime_graph_not_proven":s10.get("runtime_enforcement_consumer_graph_present") is False,
      "r7_requires_source_backing":r7["status"]=="PRE_RUNTIME_STATIC_CONTRACT_INCOMPLETE",
    }
    assert all(facts.values())

    result={
      "schema":"oce.p159.occ1k.r8.source_backed_materialization_assessment.v1",
      "milestone":"P159/OCC-1K-R8",
      "status":"UPSTREAM_SOURCE_SEMANTIC_BINDING_REQUIRED",
      "source_gaps":source_gaps,
      "facts":facts,
      "assessment":{
        "S7.CCAD":{
          "status":"UNRESOLVED",
          "reason":"CANONICAL_CCAd_CONFLICT_CLASS_PARTITION_EXPLICITLY_UNRESOLVED",
          "materialization_performed":False,
          "why":"A code-level CCAD taxonomy exists, but the canonical OCC-1A conflict-class partition explicitly forbids inferred mapping and contains no bound norms."
        },
        "S8.COMPOSITION":{
          "status":"UNRESOLVED",
          "reason":"SOURCE_BACKED_COMPOSITION_RELATIONS_NOT_CANONICALLY_BOUND",
          "materialization_performed":False,
          "why":"The CNP contains zero semantic relations and unresolved Constitution/Governance source partitions cannot be replaced by inferred SAFE composition edges."
        },
        "S10.ENFORCEMENT":{
          "status":"PARTIAL",
          "reason":"PRE_RUNTIME_RULE_TO_CONSUMER_MAPPING_NOT_SOURCE_BOUND",
          "materialization_performed":False,
          "why":"Declared consumer-interface concepts and declarative compilation evidence do not establish a source-bound rule-to-consumer enforcement map or actual runtime reachability."
        }
      },
      "conclusion":{
        "fl_b3":"BLOCKED",
        "historical_occ1d_rewritten":False,
        "canonical_occ1a_rewritten":False,
        "synthetic_relations_created":False,
        "runtime_graph_invented":False,
        "runtime_binding_created":False,
        "p160b_opened":False,
        "lock_ready":False,"lock_granted":False,
        "next_required_step":"R9_GOVERNED_UPSTREAM_SEMANTIC_BINDING_REMEDIATION"
      },
      "r9_constraints":[
        "Remediate the canonical OCC-1A/OCC-1B semantic binding gap before replaying OCC-1C/OCC-1D.",
        "Populate only relations supported by explicit canonical source semantics and provenance; never infer a SAFE relation merely to satisfy S7 or S8.",
        "Treat code-level CCAD taxonomy as lineage evidence, not as automatic canonical binding.",
        "Materialize the P159 enforcement contract only where rule class and consumer interface are canonically justified; actual runtime reachability remains a P160 obligation.",
        "Preserve historical OCC-1A through OCC-1D evidence and supersede through governed replay rather than rewriting it."
      ],
      "functional_conclusion_only":True,"phenomenology_undetermined":True
    }
    result["semantic_hash"]=hashlib.sha256(canon(result)).hexdigest()
    return result

def write():
    OUT.mkdir(parents=True,exist_ok=True)
    r=build(); p=OUT/"source_backed_materialization_assessment_v1.json"
    p.write_bytes(canon(r)+b"\n")
    m={"schema":"oce.p159.occ1k.r8.manifest.v1","artifact":p.relative_to(ROOT).as_posix(),"sha256":sha(p)}
    mp=OUT/"occ1k_r8_sha256_manifest_v1.json"; mp.write_bytes(canon(m)+b"\n")
    return r,p,mp

def main():
    r,p,mp=write()
    print("P159_OCC1K_R8_SOURCE_BACKED_MATERIALIZATION_ASSESSMENT_COMPLETE")
    print("STATUS="+r["status"])
    for k,v in r["assessment"].items(): print(k+"="+v["status"])
    print("SYNTHETIC_RELATIONS_CREATED=false")
    print("CANONICAL_OCC1A_REWRITTEN=false")
    print("RUNTIME_BINDING_CREATED=false")
    print("P160B_OPENED=false")
    print("FL_B3=BLOCKED")
    print("LOCK_READY=false")
    print("LOCK_GRANTED=false")
    print("NEXT="+r["conclusion"]["next_required_step"])
    print("ARTIFACT_SHA256="+sha(p)); print("MANIFEST_SHA256="+sha(mp))
if __name__=="__main__": main()
