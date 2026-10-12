from pathlib import Path
import json, shutil, tempfile
from ontology import occ1h_h8_boundary_mechanism_qualification as q
ROOT=Path(__file__).resolve().parents[1]

def test_probative_only():
    e=q.build(ROOT)
    assert e["qualified_count"]==7
    assert e["qualified_attack_ids"]==["A078","A080","A081","A082","A083","A084","A085"]
    for k in ("verdicts_modified","runtime_created","authorization_created","occ1h_closed","occ1i_opened","p159_final_lock","p160_opened"):
        assert e[k] is False

def test_inconclusive_preserved():
    h=json.loads((ROOT/"validation_artifacts/p159/occ1h/h8_execution_bundle_v1.json").read_text())
    rows={r["attack_id"]:r for r in h["rows"]}
    for aid in ("A078","A080","A081","A082","A083","A084","A085"):
        assert rows[aid]["verdict"]=="INCONCLUSIVE"

def test_fail_closed_on_drift():
    td=Path(tempfile.mkdtemp(prefix="oce-h8q-"))
    try:
        for rel in ("ontology_inventory.txt","ontology/occ_constitutional_adversarial_crown_h8.py","validation_artifacts/p159/occ1h/h8_execution_bundle_v1.json"):
            src=ROOT/rel; dst=td/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
        p=td/"validation_artifacts/p159/occ1h/h8_execution_bundle_v1.json"
        x=json.loads(p.read_text())
        for r in x["rows"]:
            if r["attack_id"]=="A078": r["verdict"]="RESISTED"
        p.write_text(json.dumps(x))
        try: q.build(td)
        except RuntimeError as exc: assert "H8_CURRENT_EVIDENCE_DRIFT:A078" in str(exc)
        else: raise AssertionError("must fail closed")
    finally: shutil.rmtree(td,ignore_errors=True)

def test_no_neighbor_laundering():
    e=q.build(ROOT)
    assert e["neighboring_mechanisms_are_h8_proof"] is False
    assert e["normative_auto_rewrite"] is False
