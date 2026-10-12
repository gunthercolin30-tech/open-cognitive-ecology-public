from pathlib import Path
import hashlib, json
ROOT=Path.home()/"open-cognitive-ecology"
ART=ROOT/"evidence/p159_occ1h/a075_builder_identity_epoch_binding_v1.json"
CUR=ROOT/"ontology/occ_normative_ir_real_builder.py"
OLD=ROOT/"ontology/occ_normative_ir_real_builder.py.bak"
HIST="0ae2b0e5728f1db3b9a07cdef16fd553a5a9e45efaf68fe6dee82e797a1d35b4"
CURRENT="b1e0ad044f6c2f59c37e71e6b03519c4d707e2b50d9b7e8ba187437b5d964828"
def _sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def test_a075_identity_epochs_are_exact_and_distinct():
    d=json.loads(ART.read_text())
    assert _sha(OLD)==HIST and _sha(CUR)==CURRENT and HIST!=CURRENT
    assert d["historical_hash_rebound_to_current"] is False
    assert d["historical_builder_restored"] is False
    assert d["a075_current_verdict"]=="INCONCLUSIVE"
    assert d["root_inconclusive_count"]==23
def test_a075_identity_epoch_degradation_detected(tmp_path):
    x=tmp_path/"builder.py"
    x.write_bytes(CUR.read_bytes()+b"\n# identity-drift-fixture\n")
    assert _sha(x)!=CURRENT and _sha(x)!=HIST
def test_a075_closure_boundaries_remain_closed():
    d=json.loads(ART.read_text())
    assert d["occ1h_closed"] is False and d["occ1i_opened"] is False
    assert d["p159_final_lock"] is False and d["p160_opened"] is False
