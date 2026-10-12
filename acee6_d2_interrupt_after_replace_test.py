import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import (
    AceeGovernedCodeGenerationGate,
)
from ontology.acee_installation_executor import AceeInstallationExecutor


class InterruptAfterReplace(AceeInstallationExecutor):
    def _write_candidate_atomically(self, *args, **kwargs):
        result = super()._write_candidate_atomically(*args, **kwargs)
        raise RuntimeError("simulated_interruption_after_replace")


content = "new content\n"
content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
    target = root / "ontology" / "sample_candidate.py"
    target.write_text("old content\n", encoding="utf-8")

    decision = AceeGovernedCodeGenerationGate(root=root).step(
        inputs=valid_context(root, candidate_hash=content_hash),
        persist=False,
    )
    inputs = {
        "acee5_decision": decision,
        "admission_context": {
            "requested_stage": "ACEE6-D2",
            "candidate_content": content,
        },
    }

    try:
        InterruptAfterReplace(
            root=root,
            now_utc=fixed_now(),
        ).step(inputs=inputs, persist=True)
    except RuntimeError as exc:
        assert str(exc) == "simulated_interruption_after_replace"
    else:
        raise AssertionError("interruption_not_triggered")

    assert target.read_text(encoding="utf-8") == content

    recovered = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
    ).step(inputs=inputs, persist=True)

    assert recovered["transaction_state"] == "MUTATED"
    assert recovered["candidate_written"] is True
    assert target.read_text(encoding="utf-8") == content

print("ACEE6_D2_INTERRUPT_AFTER_REPLACE_OK")
