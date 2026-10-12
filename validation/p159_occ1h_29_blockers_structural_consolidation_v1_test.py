from pathlib import Path
import json,shutil,tempfile
from ontology import occ1h_29_blockers_structural_consolidation as q
ROOT=Path(__file__).resolve().parents[1]
def test_exact_29_partition():
    e=q.build(ROOT); flat=[a for v in e["groups"].values() for a in v]
    assert e["root_inconclusive_count"]==29 and len(flat)==29 and len(set(flat))==29 and set(flat)==set(e["blockers"])
    assert e["independent_structural_gap_count"]==7
def test_compound_dependencies_are_nonindependent():
    e=q.build(ROOT)
    assert e["dependency_edges"]["A097"]==["A060","A062"]
    assert e["dependency_edges"]["A101"]==["A075"]
    assert e["dependency_edges"]["A105"]==["A095","A097","A100","A101"]
def test_probative_only_and_boundaries_preserved():
    e=q.build(ROOT)
    for k in ("verdicts_modified","mechanisms_created","authorization_created","runtime_created","occ1h_closed","occ1i_opened","p159_final_lock","p160_opened"): assert e[k] is False
def test_fails_closed_on_h10_causal_drift():
    td=Path(tempfile.mkdtemp(prefix="oce-29struct-"))
    try:
        rels=["ontology_inventory.txt","validation_artifacts/p159/occ1h/h1_h3_execution_bundle_v1.json","validation_artifacts/p159/occ1h/h4_execution_bundle_v1.json","validation_artifacts/p159/occ1h/h5_mechanism_qualification_v1.json","validation_artifacts/p159/occ1h/h6_a058_a062_mechanism_qualification_v1.json","validation_artifacts/p159/occ1h/h7_a070_a071_a075_mechanism_qualification_v1.json","validation_artifacts/p159/occ1h/h8_boundary_mechanism_qualification_v1.json","validation_artifacts/p159/occ1h/h10_final_inconclusive_qualification_v1.json"]
        for rel in rels:
            src=ROOT/rel; dst=td/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
        p=td/rels[-1]; d=json.loads(p.read_text()); d["causal_qualifications"]["A101"]="ALTERED"; p.write_text(json.dumps(d))
        try:q.build(td)
        except RuntimeError as exc: assert "A101_CAUSAL_DRIFT" in str(exc)
        else: raise AssertionError("causal drift must fail closed")
    finally: shutil.rmtree(td,ignore_errors=True)
