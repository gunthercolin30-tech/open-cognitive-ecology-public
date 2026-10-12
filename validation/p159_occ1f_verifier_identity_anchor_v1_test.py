from pathlib import Path
import hashlib,json,shutil
import pytest
from ontology import occ_independent_constitutional_verification_report as r
ROOT=Path.home()/"open-cognitive-ecology"; HIST=ROOT/"validation_artifacts/p159/occ1h/a075_defensive_assurance_gap_historization_v1.json"; HS="78a24798383f314c952f0ef66de7befa8c8628be4c6df1becf4a341efd0ef762"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sb(tmp_path):
 d=tmp_path/"repo"
 from ontology import occ_independent_constitutional_verifier as v
 rels=["ontology/occ_independent_constitutional_verifier.py","ontology/occ_independent_constitutional_verification_report.py","ontology/occ_normative_ir.py","ontology/occ_normative_ir_real_builder.py",str(r.VERIFIER_IDENTITY_ANCHOR_REL),str(r.SOURCE_AUTHORITY_REL),str(r.COMMON_TCB_REL),str(r.CHECK_REGISTRY_REL)]
 for src in v.paths(ROOT).values():
  if src.exists(): rels.append(str(src.relative_to(ROOT)))
 for rel in set(rels):
  src=ROOT/rel; dst=d/rel
  if src.is_dir(): shutil.copytree(src,dst,dirs_exist_ok=True)
  else: dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
 return d
def test_current_anchor_and_binding():
 d=r.diagnose_preclose_binding(ROOT)
 assert d["identity_anchor_valid"] is True
 assert d["legacy_builder_epoch_drift"] is True
 assert d["correction_installation_status"]=="ANCHOR_VALID_LEGACY_PRECLOSE_DRIFT_SEPARATED"
def test_missing_anchor_fails_closed(tmp_path):
 d=sb(tmp_path); (d/r.VERIFIER_IDENTITY_ANCHOR_REL).unlink(); assert r.verify_preclose_evidence(d)["status"]=="REJECTED"
 with pytest.raises(RuntimeError): r.materialize_preclose_evidence(d)
def test_identity_drift_cannot_rebind(tmp_path):
 d=sb(tmp_path); p=d/"ontology/occ_independent_constitutional_verifier.py"; s=p.read_text(); m='lm.get("self_activation") is False'; assert m in s; p.write_text(s.replace(m,"True",1)); assert r.verify_preclose_evidence(d)["reason"]=="VERIFIER_IDENTITY_NOT_INDEPENDENTLY_AUTHORIZED"; h=sha(d/r.VERIFIER_IDENTITY_ANCHOR_REL)
 with pytest.raises(RuntimeError): r.materialize_preclose_evidence(d)
 assert sha(d/r.VERIFIER_IDENTITY_ANCHOR_REL)==h and r.verify_preclose_evidence(d)["status"]=="REJECTED"
def test_anchor_tamper_fails_closed(tmp_path):
 d=sb(tmp_path); p=d/r.VERIFIER_IDENTITY_ANCHOR_REL; x=json.loads(p.read_text()); x["authorized_verifier"]["file_sha256"]="0"*64; p.write_text(json.dumps(x)+"\n"); assert r.verify_preclose_evidence(d)["status"]=="REJECTED"
def test_historical_finding_unchanged(): assert sha(HIST)==HS and json.loads(HIST.read_text())["root_verdict"]=="INCONCLUSIVE"
def test_no_authority_expansion():
 x=json.loads((ROOT/r.VERIFIER_IDENTITY_ANCHOR_REL).read_text()); c=x["constraints"]; assert c["authority_expansion"] is False and c["root_override_all"] is False and c["automatic_identity_rebinding"] is False and x["occ1h_closed"] is False and x["p160_opened"] is False
