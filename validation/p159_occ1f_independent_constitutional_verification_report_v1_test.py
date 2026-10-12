from __future__ import annotations

from copy import deepcopy
import json
import shutil
from pathlib import Path
from types import SimpleNamespace
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector

from ontology import occ_independent_constitutional_verification_report as r
from ontology import occ_independent_constitutional_verifier as v

ROOT = Path(__file__).resolve().parents[1]
class _P162Broker:
    def __init__(self, ids): self.ids=set(ids); self.used=set()
    def consume_once(self, handle_id):
        if handle_id not in self.ids or handle_id in self.used: return False
        self.used.add(handle_id); return True
def _p162_handle(i,op,b): return SimpleNamespace(handle_id=i,adapter_id="p159-occ1f-test-adapter",effector_id="p159-occ1f-test-effector",operation_id=op,target_binding=b,ambient_authority=False,transferable=False,child_inheritance=False,single_use=True)
def _p162_binding(root,path): return "filesystem://p159-occ1f-test/"+path.resolve().relative_to(root.resolve()).as_posix()
def _p162_materialize_context(root):
    target=root/r.REPORT_REL;ids={"write"};slots={"occ1f_report_write_replace":[_p162_handle("write","FS_WRITE_REPLACE_BYTES",_p162_binding(root,target))]}
    if not target.parent.exists(): ids.add("mkdir");slots["occ1f_report_create_dirs"]=[_p162_handle("mkdir","FS_CREATE_DIRS",_p162_binding(root,target.parent))]
    broker=_P162Broker(ids);effector=GovernedFilesystemEffector(root_registry={"p159-occ1f-test":str(root)},handle_broker=broker)
    return GovernedFilesystemEffectContext(slots=slots,effector=effector,root_id="p159-occ1f-test",root_path=root,adapter_id="p159-occ1f-test-adapter",effector_id="p159-occ1f-test-effector")

def _sandbox(tmp_path):
    dst = tmp_path / "repo"
    for src in v.paths(ROOT).values():
        if not src.exists():
            continue
        target = dst / src.relative_to(ROOT)
        if src.is_dir():
            shutil.copytree(src, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
    return dst

def test_real_report_is_verified_and_boundaries_remain_closed():
    x = r.build_report(ROOT)
    assert x["verdict"] == v.VERIFIED
    assert x["check_counts"] == {"PASS":12,"FAIL":0,"INCONCLUSIVE":0,"SKIPPED":0}
    assert x["failed_check_ids"] == []
    assert x["inconclusive_check_ids"] == []
    assert all(value is False for value in x["downstream_state"].values())
    assert x["epistemic_limits"]["functional_conclusion_only"] is True
    assert x["epistemic_limits"]["phenomenology_undetermined"] is True
    assert r.validate_report(x)

def test_report_is_deterministic():
    assert r.build_report(ROOT) == r.build_report(ROOT)

def test_materialization_is_idempotent_and_bound(tmp_path):
    root = _sandbox(tmp_path)
    first = r.materialize(root, _p162_materialize_context(root))
    target = root / r.REPORT_REL
    b1 = target.read_bytes()
    second = r.materialize(root, _p162_materialize_context(root))
    assert first == second
    assert b1 == target.read_bytes()
    assert r.verify_materialized(root)["status"] == "VERIFIED_REPORT_BINDING"

def test_materialization_does_not_mutate_upstream(tmp_path):
    root = _sandbox(tmp_path)
    protected = [p for p in v.paths(root).values() if p.exists() and p.is_file()]
    before = {str(p): p.read_bytes() for p in protected}
    r.materialize(root, _p162_materialize_context(root))
    after = {str(p): p.read_bytes() for p in protected}
    assert before == after

def test_report_tamper_is_rejected(tmp_path):
    root = _sandbox(tmp_path)
    r.materialize(root, _p162_materialize_context(root))
    target = root / r.REPORT_REL
    x = json.loads(target.read_text())
    x["verdict"] = v.REJECTED
    target.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")
    assert r.verify_materialized(root)["status"] == "REJECTED"

def test_profile_tamper_breaks_binding(tmp_path):
    root = _sandbox(tmp_path)
    r.materialize(root, _p162_materialize_context(root))
    p = v.paths(root)["profile"]
    x = json.loads(p.read_text())
    x["rules"] = x["rules"][:-1]
    p.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")
    assert r.verify_materialized(root)["status"] == "REJECTED"

def test_missing_evidence_stays_indeterminate(tmp_path):
    root = _sandbox(tmp_path)
    v.paths(root)["occ1d_enforcement"].unlink()
    x = r.build_report(root)
    assert x["verdict"] == v.INDETERMINATE
    assert x["epistemic_limits"]["indeterminate_is_not_verified"] is True

def test_forged_closure_flag_invalidates_report():
    x = r.build_report(ROOT)
    y = deepcopy(x)
    y["downstream_state"]["occ1f_closed"] = True
    y.pop("report_sha256")
    y["report_sha256"] = r._canonical_hash(y)
    assert not r.validate_report(y)
