from pathlib import Path
import json,shutil,tempfile
from ontology import occ1h_h10_final_inconclusive_qualification as q
ROOT=Path(__file__).resolve().parents[1]

def test_h10_final_probative_only():
    e=q.build(ROOT)
    assert e["qualified_count"]==5
    assert e["qualified_attack_ids"]==["A095","A097","A100","A101","A105"]
    for k in ("verdicts_modified","mechanisms_created","authorization_created","occ1h_closed","occ1i_opened","p159_final_lock","p160_opened"):
        assert e[k] is False

def test_h10_dependencies_exact():
    e=q.build(ROOT)
    c=e["causal_qualifications"]
    assert c["A097"]=="DEPENDS_ON_UNRESOLVED_A060_A062"
    assert c["A101"]=="DEPENDS_ON_UNRESOLVED_A075"
    assert "A095_A097_A100_A101" in c["A105"]

def test_h10_inconclusive_preserved():
    b=json.loads((ROOT/"validation_artifacts/p159/occ1h/h10_execution_bundle_v1.json").read_text())
    rows={r["attack_id"]:r for r in b["rows"]}
    for aid in ("A095","A097","A100","A101","A105"):
        assert rows[aid]["verdict"]=="INCONCLUSIVE"

def test_h10_fails_closed_on_dependency_drift():
    td=Path(tempfile.mkdtemp(prefix="oce-h10q-"))
    try:
        for rel in ("ontology_inventory.txt","ontology/occ_constitutional_adversarial_crown_h10.py","validation_artifacts/p159/occ1h/h10_execution_bundle_v1.json"):
            src=ROOT/rel; dst=td/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
        p=td/"validation_artifacts/p159/occ1h/h10_execution_bundle_v1.json"
        x=json.loads(p.read_text())
        for r in x["rows"]:
            if r["attack_id"]=="A097": r["evidence"]["h6_A060"]="DETECTED"
        p.write_text(json.dumps(x))
        try:q.build(td)
        except RuntimeError as exc: assert "H10_A097_DEPENDENCY_DRIFT" in str(exc)
        else: raise AssertionError("dependency drift must fail closed")
    finally: shutil.rmtree(td,ignore_errors=True)
