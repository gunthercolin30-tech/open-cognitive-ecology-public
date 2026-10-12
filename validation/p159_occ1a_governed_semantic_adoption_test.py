from __future__ import annotations
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from ontology import occ_norm_adoption_event as o
from ontology import human_reserved_authority_registry as p095
def ck(v,n): assert v,n; print(n)
def main():
 h=json.loads((ROOT/"validation/evidence/p155_constitutional_architecture_v2/p155_historical_dna_semantic_binding_v2.json").read_text(encoding="utf-8"))
 w=o.prepare_workbook(h["bindings"]);m=o.manifest()
 ck(len(w["dna_rows"])==23 and len({x["canonical_id"] for x in w["dna_rows"]})==23,"P159_OCC1A_ADOPTION_23_DNA_TARGETS_OK")
 ck(len(w["historical_sources"])==18,"P159_OCC1A_ADOPTION_F1_F18_SOURCES_OK")
 ck(all(x["historical_id"] is None and x["state"]=="DRAFT" for x in w["dna_rows"]),"P159_OCC1A_ADOPTION_ZERO_PREASSIGNMENT_OK")
 ck(not m["machine_assignment_permitted"] and not m["machine_adoption_permitted"] and not m["machine_activation_permitted"],"P159_OCC1A_ADOPTION_MACHINE_NON_SOVEREIGN_OK")
 p=o.propose_binding(w["dna_rows"][0],"F2",h["bindings"]["F2"]["definition"],"human-governed candidate only")
 ck(p["accepted"] and p["record"]["state"]=="PROPOSED" and not p["normative_binding_created"],"P159_OCC1A_ADOPTION_PROPOSAL_NOT_BINDING_OK")
 ev={"proposal":True,"rationale":True,"incompatibility_analysis":True,"rights_impact":True,"adversarial_review":True,"long_form_human_governance":True,"fork_or_migration_decision":True,"provenance":True}
 bad=dict(ev);bad.pop("long_form_human_governance")
 ck(not o.amendment_gate(p["record"],bad)["accepted"],"P159_OCC1A_ADOPTION_P106_MISSING_EVIDENCE_FAIL_CLOSED_OK")
 ck(o.amendment_gate(p["record"],ev)["accepted"],"P159_OCC1A_ADOPTION_P106_REUSED_OK")
 ck(h["bindings"]["F17"].get("distinct_normative_object_preserved") is True,"P159_OCC1A_ADOPTION_F17_DISTINCT_OK")
 ck(h["bindings"]["F18"].get("distinct_normative_object_preserved") is True and h["bindings"]["F18"].get("not_reduced_to_human_welfare") is True,"P159_OCC1A_ADOPTION_F18_NONREDUCTION_OK")
 ck(w["genesis"]["pdf_extraction_must_not_define_machine_semantics"],"P159_OCC1A_ADOPTION_GENESIS_EXTRACTION_FAIL_CLOSED_OK")
 d=o.build_adoption_decision(p["record"],{"status":p095.UNDETERMINED},o.amendment_gate(p["record"],ev),"D1","2026-09-23T00:00:00Z")
 ck(d["status"]=="UNDETERMINED","P159_OCC1A_ADOPTION_NO_AUTHORITY_NO_DECISION_OK")
 ck(not m["occ1a_closed"] and not m["occ1b_opened"] and not m["p160_opened"],"P159_OCC1A_ADOPTION_SCOPE_BOUNDARY_OK")
 code="import json;from ontology.occ_norm_adoption_event import manifest;print(json.dumps(manifest(),sort_keys=True,separators=(',',':')))"
 env=dict(os.environ);env["PYTHONPATH"]=str(ROOT)
 a=subprocess.check_output([sys.executable,"-c",code],cwd=str(ROOT),env=env,text=True);b=subprocess.check_output([sys.executable,"-c",code],cwd="/tmp",env=env,text=True)
 ck(a==b,"P159_OCC1A_ADOPTION_CWD_DETERMINISM_OK")
 ck(m["functional_conclusion_only"] and m["phenomenology_undetermined"],"P159_OCC1A_ADOPTION_EPISTEMIC_INVARIANTS_OK")
 print("P159_OCC1A_GOVERNED_SEMANTIC_ADOPTION_OK")
if __name__=="__main__":main()
