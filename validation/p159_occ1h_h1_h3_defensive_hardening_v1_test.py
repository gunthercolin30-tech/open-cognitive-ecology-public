from validation.p159_occ1h_adversarial_crown_h1_h3_v1_test import governed_crown_run
from pathlib import Path
import json, shutil, tempfile
from ontology import occ_normative_ir_real_builder as builder
from ontology import occ_constitutional_adversarial_crown_h1_h3 as crown

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "normative/occ1a"

def _clone():
    td = Path(tempfile.mkdtemp(prefix="oce-occ1h-hardening-"))
    dst = td / "occ1a"
    shutil.copytree(SRC, dst)
    return td, dst

def test_a008_illegitimate_adoption_fails_closed():
    td, dst = _clone()
    try:
        p = dst / "dna/dna_h.yaml"
        obj = json.loads(p.read_text(encoding="utf-8"))
        obj["norms"][0]["semantic_status"] = "ACTIVE_WITHOUT_GOVERNED_ADOPTION"
        p.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")), encoding="utf-8")
        r = builder.build_real_nir(dst)
        assert r["status"] == "FAIL"
        assert str(r["reason"]).startswith("SEMANTIC_STATUS_NOT_ALLOWED:")
    finally:
        shutil.rmtree(td, ignore_errors=True)

def test_a009_duplicate_json_key_rejected():
    td, dst = _clone()
    try:
        p = dst / "dna/dna_h.yaml"
        p.write_text('{"norms":[],"norms":[{"canonical_id":"X"}]}', encoding="utf-8")
        try:
            builder._load_partition(p)
            accepted = True
        except ValueError as exc:
            accepted = False
            assert "DUPLICATE_JSON_KEY:norms" in str(exc)
        assert accepted is False
    finally:
        shutil.rmtree(td, ignore_errors=True)

def test_real_canonical_package_still_builds():
    r = builder.build_real_nir(SRC)
    assert r["status"] == "PASS", r

def test_h1_h3_crown_has_no_violation_after_hardening():
    r = governed_crown_run(SRC)
    by_id = {x["attack_id"]: x for x in r["rows"]}
    assert by_id["A008"]["verdict"] == "DETECTED"
    assert by_id["A009"]["verdict"] == "DETECTED"
    assert r["verdict_counts"]["VIOLATED"] == 0
    assert by_id["A021"]["verdict"] == "INCONCLUSIVE"
    assert r["occ1h_closed"] is False
    assert r["occ1i_opened"] is False
    assert r["p159_final_lock"] is False
    assert r["p160_opened"] is False
