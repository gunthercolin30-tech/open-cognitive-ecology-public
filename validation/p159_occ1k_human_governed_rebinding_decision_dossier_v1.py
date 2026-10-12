from pathlib import Path
import ast,json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
SRC=ROOT/"ontology/human_reserved_authority_registry.py"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9c"
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def constants():
    tree=ast.parse(SRC.read_text(encoding="utf-8"))
    wanted={"VERSION","SCHEMA_VERSION","SCOPE","FUNCTIONAL_ONLY","PHENOMENOLOGY_UNDETERMINED",
    "REAL_EXECUTION_ENABLED","RESERVED_CLASSES","INITIAL_DEVELOPMENT_AUTHORITY_V1",
    "INITIAL_DEVELOPMENT_REGIME","INITIAL_DEVELOPMENT_HOLDER","INITIAL_DEVELOPMENT_ROLE",
    "INITIAL_DEVELOPMENT_SCOPE","INITIAL_DEVELOPMENT_CONTINUITY","ROOT_OVERRIDE_ALL"}
    vals={}
    for n in tree.body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            name=n.targets[0].id
            if name in wanted:
                try: vals[name]=ast.literal_eval(n.value)
                except Exception:
                    if isinstance(n.value,ast.Name): vals[name]={"reference":n.value.id}
    return vals
def build():
    c=constants()
    required=("VERSION","SCHEMA_VERSION","SCOPE","FUNCTIONAL_ONLY","PHENOMENOLOGY_UNDETERMINED",
              "REAL_EXECUTION_ENABLED","RESERVED_CLASSES","INITIAL_DEVELOPMENT_AUTHORITY_V1",
              "INITIAL_DEVELOPMENT_REGIME","INITIAL_DEVELOPMENT_HOLDER","INITIAL_DEVELOPMENT_ROLE",
              "INITIAL_DEVELOPMENT_SCOPE","INITIAL_DEVELOPMENT_CONTINUITY","ROOT_OVERRIDE_ALL")
    missing=[x for x in required if x not in c]
    if missing: raise RuntimeError("R9C_REQUIRED_SEMANTICS_MISSING:"+",".join(missing))
    r={
      "schema":"oce.p159.occ1k.r9c.human_governed_rebinding_decision_dossier.v1",
      "milestone":"P159/OCC-1K-R9C",
      "status":"HUMAN_DECISION_DOSSIER_READY",
      "current_source":{"path":"ontology/human_reserved_authority_registry.py","sha256":sha(SRC),"extracted_constants":c},
      "semantic_observations":{
        "functional_only":c["FUNCTIONAL_ONLY"] is True,
        "real_execution_disabled":c["REAL_EXECUTION_ENABLED"] is False,
        "root_override_all_disabled":c["ROOT_OVERRIDE_ALL"] is False,
        "initial_development_authority_enabled":c["INITIAL_DEVELOPMENT_AUTHORITY_V1"] is True,
        "authority_regime":c["INITIAL_DEVELOPMENT_REGIME"],
        "authority_holder":c["INITIAL_DEVELOPMENT_HOLDER"],
        "authority_role":c["INITIAL_DEVELOPMENT_ROLE"],
        "authority_continuity":c["INITIAL_DEVELOPMENT_CONTINUITY"],
        "reserved_classes":list(c["RESERVED_CLASSES"]),
      },
      "epistemic_limit":{
        "historical_bytes_available":False,
        "historical_semantic_diff_possible":False,
        "claim_current_semantics_equal_historical":False,
        "reason":"Historical manifest-bound bytes are unavailable; hash alone cannot establish semantic equivalence."
      },
      "decision_options":{
        "REBIND_CURRENT":{
          "effect":"Governedly accept the exact current bytes as a superseding canonical HUMAN_RESERVED_AUTHORITY source for subsequent OCC-1A replay.",
          "does_not_mean":["historical bytes recovered","historical irregularity erased","ROOT_OVERRIDE_ALL","runtime authorization","P160-B opened","FL-B3 passed"],
          "requires_explicit_human_confirmation":True},
        "KEEP_UNRESOLVED":{
          "effect":"Preserve the provenance debt; do not adopt current bytes as canonical; downstream authority preflight remains blocked.",
          "requires_explicit_human_confirmation":False}
      },
      "default_without_confirmation":"KEEP_UNRESOLVED",
      "boundaries":{"canonical_occ1a_modified":False,"manifest_modified":False,"authority_registry_modified":False,
                    "runtime_binding_created":False,"p160b_opened":False,"fl_b3":"BLOCKED",
                    "lock_ready":False,"lock_granted":False},
      "next_if_rebind_confirmed":"R9D_GOVERNED_SUPERSEDING_SOURCE_REBIND_TRANSACTION",
      "next_if_not_confirmed":"STOP_WITH_PROVENANCE_DEBT_OPEN",
      "functional_conclusion_only":True,"phenomenology_undetermined":True
    }
    r["semantic_hash"]=hashlib.sha256(canon(r)).hexdigest()
    return r
def write():
    OUT.mkdir(parents=True,exist_ok=True); r=build()
    p=OUT/"human_governed_rebinding_decision_dossier_v1.json"; p.write_bytes(canon(r)+b"\n")
    return r,p
def main():
    r,p=write(); o=r["semantic_observations"]
    print("P159_OCC1K_R9C_HUMAN_GOVERNED_REBINDING_DECISION_DOSSIER_COMPLETE")
    print("STATUS="+r["status"])
    print("CURRENT_SOURCE_SHA256="+r["current_source"]["sha256"])
    print("FUNCTIONAL_ONLY="+str(o["functional_only"]).lower())
    print("REAL_EXECUTION_DISABLED="+str(o["real_execution_disabled"]).lower())
    print("ROOT_OVERRIDE_ALL_DISABLED="+str(o["root_override_all_disabled"]).lower())
    print("INITIAL_DEVELOPMENT_AUTHORITY_ENABLED="+str(o["initial_development_authority_enabled"]).lower())
    print("AUTHORITY_REGIME="+o["authority_regime"])
    print("AUTHORITY_ROLE="+o["authority_role"])
    print("AUTHORITY_CONTINUITY="+o["authority_continuity"])
    print("HISTORICAL_SEMANTIC_DIFF_POSSIBLE=false")
    print("DEFAULT_WITHOUT_CONFIRMATION=KEEP_UNRESOLVED")
    print("CANONICAL_OCC1A_MODIFIED=false"); print("P160B_OPENED=false")
    print("FL_B3=BLOCKED"); print("LOCK_READY=false"); print("LOCK_GRANTED=false")
    print("ARTIFACT_SHA256="+sha(p))
if __name__=="__main__": main()
