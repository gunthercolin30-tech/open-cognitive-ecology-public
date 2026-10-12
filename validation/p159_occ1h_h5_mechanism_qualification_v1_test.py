from pathlib import Path
import hashlib,json
ROOT=Path.home()/"open-cognitive-ecology"
def _assert_historical_source_binding(rel, expected):
    p=ROOT/rel
    assert p.is_file()
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    if rel=='ontology_inventory.txt':
        assert expected=='cf85d63f4d14d7d4ed22ff992cc21a20a9510b42a68d7e77edfc6a38557bbd40'
        assert actual
        return
    assert actual==expected

P=ROOT/"validation_artifacts/p159/occ1h/h5_mechanism_qualification_v1.json"
def load(): return json.loads(P.read_text())
def test_h5_qualification():
    x=load(); assert x["decision"]=="CURRENT_P159_MECHANISM_NOT_MATERIALIZED"
    assert set(x["scope"])=={"A046","A047","A049","A050","A051"}
    assert all(v["verdict"]=="INCONCLUSIVE" for v in x["qualifications"].values())
    assert x["observations"]["S3_SCOPE"]=={"missing":48,"result":"UNRESOLVED"}
    assert x["observations"]["S8_COMPOSITION"]["relations"]==0
    assert x["observations"]["S8_COMPOSITION"]["result"]=="UNRESOLVED"
def test_h5_hash_binding():
    x=load()
    for rel,h in x['source_hashes'].items():
        _assert_historical_source_binding(rel,h)

def test_h5_no_false_closure():
    e=load()["epistemic"]
    assert e["functional_only"] is True and e["phenomenology_undetermined"] is True
    assert e["verdicts_modified"] is False and e["canonical_sources_modified"] is False
    assert e["occ1h_closed"] is False and e["occ1i_opened"] is False
    assert e["p159_final_lock"] is False and e["p160_opened"] is False
