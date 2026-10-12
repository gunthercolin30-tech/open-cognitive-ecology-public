from pathlib import Path
import hashlib, json, shutil
import pytest
from ontology import occ_independent_constitutional_verification_report as r
ROOT=Path.home()/"open-cognitive-ecology"
HIST=ROOT/"validation_artifacts/p159/occ1h/a075_defensive_assurance_gap_historization_v1.json"
HIST_SHA="78a24798383f314c952f0ef66de7befa8c8628be4c6df1becf4a341efd0ef762"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def test_known_legacy_preclose_drift_is_separated_from_valid_anchor():
    d=r.diagnose_preclose_binding(ROOT)
    assert d["identity_anchor_valid"] is True
    assert d["legacy_builder_epoch_drift"] is True
    assert d["correction_installation_status"]=="ANCHOR_VALID_LEGACY_PRECLOSE_DRIFT_SEPARATED"
def test_controlled_identity_drift_fails_closed_before_legacy_recalculation(tmp_path):
    root=tmp_path/"repo"
    req=["ontology/occ_independent_constitutional_verifier.py","ontology/occ_independent_constitutional_verification_report.py","ontology/occ_normative_ir.py","ontology/occ_normative_ir_real_builder.py","validation_artifacts/p159/occ1f/verifier_identity_authorization_anchor_v1.json","validation_artifacts/p159/occ1f/common_tcb_manifest_v1.json","validation_artifacts/p159/occ1f/verifier_check_registry_v1.json","oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json"]
    from ontology import occ_independent_constitutional_verifier as v
    for src in v.paths(ROOT).values():
        if src.exists():
            try: req.append(str(src.relative_to(ROOT)))
            except ValueError: pass
    for rel in sorted(set(req)):
        src=ROOT/rel
        if not src.exists(): continue
        dst=root/rel
        if src.is_dir(): shutil.copytree(src,dst,dirs_exist_ok=True)
        else: dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    vp=root/"ontology/occ_independent_constitutional_verifier.py"; s=vp.read_text(); m='lm.get("self_activation") is False'; assert m in s; vp.write_text(s.replace(m,"True",1))
    got=r.verify_preclose_evidence(root)
    assert got["status"]=="REJECTED" and got["reason"]=="VERIFIER_IDENTITY_NOT_INDEPENDENTLY_AUTHORIZED"
    with pytest.raises(RuntimeError,match="OCC1F_VERIFIER_IDENTITY_NOT_AUTHORIZED"): r.materialize_preclose_evidence(root)
def test_historical_a075_finding_remains_immutable():
    assert sha(HIST)==HIST_SHA
    x=json.loads(HIST.read_text()); assert x["finding"]=="ASSURANCE_GAP"; assert x["root_verdict"]=="INCONCLUSIVE"; assert x["root_verdict_changed"] is False
