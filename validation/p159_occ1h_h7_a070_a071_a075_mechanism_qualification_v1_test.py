from pathlib import Path
import json, shutil, tempfile
from ontology import occ1h_h7_a070_a071_a075_mechanism_qualification as q

ROOT=Path(__file__).resolve().parents[1]

def test_h7_three_case_qualification_is_probative_only():
    e=q.build(ROOT)
    assert e["qualified_attack_ids"]==["A070","A071","A075"]
    assert e["qualified_count"]==3
    assert e["verdicts_modified"] is False
    assert e["occ1f_modified"] is False
    assert e["occ1h_closed"] is False
    assert e["occ1i_opened"] is False
    assert e["p159_final_lock"] is False
    assert e["p160_opened"] is False

def test_h7_three_case_qualification_preserves_inconclusive():
    h=json.loads((ROOT/"validation_artifacts/p159/occ1h/h7_execution_bundle_v1.json").read_text())
    rows={r["attack_id"]:r for r in h["rows"]}
    for aid in ("A070","A071","A075"):
        assert rows[aid]["verdict"]=="INCONCLUSIVE"

def test_h7_three_case_qualification_fails_closed_on_tcb_tamper():
    td=Path(tempfile.mkdtemp(prefix="oce-h7-qual-test-"))
    try:
        # Recreate only the required relative paths.
        required=[
          "ontology_inventory.txt",
          "ontology/occ_constitutional_adversarial_crown_h7.py",
          "ontology/occ_independent_constitutional_verifier.py",
          "ontology/occ_independent_constitutional_verification_report.py",
          "validation_artifacts/p159/occ1h/h7_execution_bundle_v1.json",
          "validation_artifacts/p159/occ1f/common_tcb_manifest_v1.json",
          "validation_artifacts/p159/occ1f/independent_constitutional_verification_report_v1.json",
        ]
        for rel in required:
            src=ROOT/rel; dst=td/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
        p=td/"validation_artifacts/p159/occ1f/common_tcb_manifest_v1.json"
        x=json.loads(p.read_text()); x["common_mode_risk_explicit"]=False
        p.write_text(json.dumps(x,sort_keys=True,indent=2)+"\n")
        try:
            q.build(td)
        except RuntimeError as exc:
            assert "H7_COMMON_TCB_DISCLOSURE_DRIFT" in str(exc)
        else:
            raise AssertionError("tampered Common-TCB must fail closed")
    finally:
        shutil.rmtree(td,ignore_errors=True)
