from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

class MutatingExecutor(AceeInstallationExecutor):
    def _backup_transaction(self, prepared):
        target = self.root / prepared["normalized_plan"]["target_path"]
        if target.exists(): target.write_text("changed\n", encoding="utf-8")
        return super()._backup_transaction(prepared)

with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    decision = valid_acee5_decision(root)
    target = root / "ontology" / "sample_candidate.py"; target.write_text("original\n", encoding="utf-8")
    Path(str(target)+".bak").write_bytes(target.read_bytes())
    import hashlib
    from ontology.acee_installation_executor import _sha
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    decision["installation_manifest"]["backup_sha256"] = actual
    decision["installation_manifest"]["manifest_hash"] = _sha({k:v for k,v in decision["installation_manifest"].items() if k != "manifest_hash"})
    decision["result_hash"] = _sha({k:v for k,v in decision.items() if k != "result_hash"})
    inputs = {"acee5_decision": decision, "admission_context": {"requested_stage": "ACEE6-D1"}}
    from validation.acee6_d1_preissued_fixture import ExpectedEffect, PreissuedD1Fixture
    dry = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    admitted = dry.step(inputs=inputs, persist=False)
    assert admitted.get("admissible") is True, "d1_guarded_admission_precondition"
    txdir = root / "acee6_transactions" / dry._transaction_id(admitted)
    effects = (
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "snapshot.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
        ExpectedEffect("FS_CREATE_DIR", root / "acee6_transactions"),
    )
    fixture = PreissuedD1Fixture(root, effects)
    result = MutatingExecutor(
        root=root, now_utc=fixed_now(), filesystem_effect_context_provider=fixture,
    ).step(inputs=inputs, persist=True)
    fixture.assert_exhausted()
    assert result["transaction_state"] == "STATE_CORRUPTED"
    assert "backup_source_snapshot_divergence" in result["blocking_reasons"]
print("ACEE6_D1_SOURCE_DIVERGENCE_OK")
