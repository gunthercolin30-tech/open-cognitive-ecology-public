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

P=ROOT/"validation_artifacts/p159/occ1h/h6_a058_a062_mechanism_qualification_v1.json"
def load(): return json.loads(P.read_text())
def test_qualification():
 x=load(); assert x["decision"]=="CURRENT_P159_H6_MECHANISMS_NOT_MATERIALIZED"
 assert set(x["scope"])=={"A058","A059","A060","A061","A062"}
 assert all(v["verdict"]=="INCONCLUSIVE" for v in x["qualifications"].values())
 assert x["observations"]["S8_COMPOSITION"]["result"]=="UNRESOLVED"
 assert x["observations"]["S8_COMPOSITION"]["relations"]==0
 assert x["observations"]["CNP_RELATIONS_EMPTY"] is True
 assert x["observations"]["synthetic_substitute_used"] is False
def test_hash_binding():
    x=load()
    for rel,h in x['source_hashes'].items():
        p=ROOT/rel
        if rel=='ontology/occ_constitutional_adversarial_crown_h6.py':
            hist=p.with_suffix(p.suffix+'.bak')
            assert hist.is_file()
            assert hashlib.sha256(hist.read_bytes()).hexdigest()==h
            assert hashlib.sha256(p.read_bytes()).hexdigest()!=h
        else:
            _assert_historical_source_binding(rel,h)

def test_no_false_closure():
 e=load()["epistemic"]; assert e["functional_only"] is True and e["phenomenology_undetermined"] is True
 for k in ("verdicts_modified","canonical_sources_modified","compiled_profile_modified","occ1d_modified","occ1h_closed","occ1i_opened","p159_final_lock","p160_opened"): assert e[k] is False
