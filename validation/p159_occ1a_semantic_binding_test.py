from __future__ import annotations
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_semantic_binding as b
def ck(v,n): assert v,n; print(n)
def main():
 m=b.manifest(); rows=list(m["bindings"])
 ck(m["target_count"]==48 and len(rows)==48 and len({x["canonical_id"] for x in rows})==48,"P159_OCC1A_BINDING_48_TARGETS_AUDITED_OK")
 ck(m["direct_explicit_bindings"]==24 and m["exact_unresolved_bindings"]==24,"P159_OCC1A_BINDING_24_DIRECT_24_UNRESOLVED_OK")
 ck(m["invented_bindings"]==0,"P159_OCC1A_BINDING_NO_INVENTED_MAPPING_OK")
 direct=[x for x in rows if x["binding_status"]==b.DIRECT]; unresolved=[x for x in rows if x["binding_status"]==b.UNRESOLVED]
 ck(all(x["canonical_id"].startswith("CCAD.") for x in direct),"P159_OCC1A_BINDING_DIRECT_ONLY_CCAd_OK")
 ck(all(not x["canonical_id"].startswith("CCAD.") for x in unresolved),"P159_OCC1A_BINDING_GENESIS_DNA_FAIL_CLOSED_OK")
 ck(m["historical_layer_evidence"]["one_to_one_canonical_id_binding_proven"] is False,"P159_OCC1A_BINDING_LAYER_EVIDENCE_NOT_PROMOTED_OK")
 ck(all(x["source_object_id"] is None and x["text"] is None for x in unresolved),"P159_OCC1A_BINDING_NO_SYNTHETIC_TEXT_OK")
 h=json.loads((ROOT/"validation/evidence/p155_constitutional_architecture_v2/p155_historical_dna_semantic_binding_v2.json").read_text(encoding="utf-8"))
 ck(h["bindings"]["F17"].get("distinct_normative_object_preserved") is True,"P159_OCC1A_BINDING_F17_DISTINCT_OK")
 ck(h["bindings"]["F18"].get("distinct_normative_object_preserved") is True and h["bindings"]["F18"].get("not_reduced_to_human_welfare") is True,"P159_OCC1A_BINDING_F18_NONREDUCTION_OK")
 from ontology import ccad_specification as c
 ck(c.BOUNDARIES["ccad_subordinate_to_dna"] and not c.BOUNDARIES["arbitration_creates_authority"] and not c.BOUNDARIES["arbitration_creates_authorization"],"P159_OCC1A_BINDING_CCAd_NON_SOVEREIGN_OK")
 code="import json; from ontology.occ_semantic_binding import manifest; print(json.dumps(manifest(),sort_keys=True,separators=(',',':')))"
 env=dict(os.environ); env["PYTHONPATH"]=str(ROOT)
 a=subprocess.check_output([sys.executable,"-c",code],cwd=str(ROOT),env=env,text=True); z=subprocess.check_output([sys.executable,"-c",code],cwd="/tmp",env=env,text=True)
 ck(a==z,"P159_OCC1A_BINDING_CWD_DETERMINISM_OK")
 ck(not m["occ1a_closed"] and not m["occ1b_opened"] and not m["p160_opened"],"P159_OCC1A_BINDING_SCOPE_BOUNDARY_OK")
 ck(m["functional_conclusion_only"] and m["phenomenology_undetermined"],"P159_OCC1A_BINDING_EPISTEMIC_INVARIANTS_OK")
 print("P159_OCC1A_SEMANTIC_BINDING_AUDIT_OK")
if __name__=="__main__": main()
