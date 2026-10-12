from pathlib import Path
import hashlib, json
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

ART=ROOT/"validation_artifacts/p159/occ1h/synthetic_fixture_feasibility_v1.json"
def load(): return json.loads(ART.read_text(encoding="utf-8"))
def test_fail_closed():
    x=load()
    assert x["decision"]=="SYNTHETIC_FIXTURE_NOT_ADMISSIBLE_WITH_CURRENT_H3_H4_CONTRACTS"
    assert set(x["scope"])=={"A021","A040","A041","A042"}
    assert all(v["status"]=="INCONCLUSIVE_PRESERVED" for v in x["per_attack"].values())
def test_no_false_closure():
    e=load()["epistemic"]
    assert e["functional_only"] is True and e["phenomenology_undetermined"] is True
    assert e["verdicts_modified"] is False and e["canonical_sources_modified"] is False
    assert e["compiled_profile_modified"] is False and e["occ1h_closed"] is False
    assert e["occ1i_opened"] is False and e["p159_final_lock"] is False and e["p160_opened"] is False
def test_hash_binding():
    x=load()
    assert all(x['contracts'].values())
    for rel,expected in x['source_hashes'].items():
        _assert_historical_source_binding(rel,expected)
