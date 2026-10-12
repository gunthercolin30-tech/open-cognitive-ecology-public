from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from ontology import occ_candidate_materialization as m
x=m.build_dossiers(ROOT);assert m.validate(x)
assert len(x["dossiers"])==23
print("P159_OCC1A_CM_23_DOSSIERS_OK")
assert all(d["numbered_semantic_binding_status"]=="UNRESOLVED" for d in x["dossiers"])
assert all(d["machine_selected_historical_id"] is None and d["machine_candidate_definition"] is None for d in x["dossiers"])
print("P159_OCC1A_CM_NO_NUMBERED_BINDING_OK")
assert all(d["machine_ranking_performed"] is False for d in x["dossiers"])
print("P159_OCC1A_CM_NO_RANKING_OK")
by={d["canonical_id"]:d for d in x["dossiers"]}
assert {a["historical_id"] for a in by["DNA.H1"]["layer_compatible_historical_sources"]}=={"F2","F3","F4","F5","F6","F7","F8","F10","F12","F17"}
assert {a["historical_id"] for a in by["DNA.L0.1"]["layer_compatible_historical_sources"]}=={"F1","F9","F11","F13","F15"}
assert {a["historical_id"] for a in by["DNA.L1.1"]["layer_compatible_historical_sources"]}=={"F10","F11","F12","F14","F15","F16"}
print("P159_OCC1A_CM_LAYER_COMPATIBILITY_EXACT_OK")
f17=[a for a in by["DNA.H1"]["layer_compatible_historical_sources"] if a["historical_id"]=="F17"][0]
assert f17["distinct_normative_object_preserved"] is True
assert all(a["historical_id"]!="F18" for d in x["dossiers"] for a in d["layer_compatible_historical_sources"])
print("P159_OCC1A_CM_F17_F18_DISTINCTION_OK")
assert x["automatic_numbered_binding"] is False and x["automatic_ranking"] is False and x["automatic_merging"] is False and x["automatic_adoption"] is False
assert x["occ1a_closed"] is False and x["occ1b_opened"] is False and x["p160_opened"] is False
print("P159_OCC1A_CM_SCOPE_BOUNDARY_OK")
assert x["functional_conclusion_only"] is True and x["phenomenology_undetermined"] is True
print("P159_OCC1A_CANDIDATE_MATERIALIZATION_OK")
