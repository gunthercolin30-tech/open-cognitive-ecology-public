from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

import acee5_hardening_test_support as support


required_exports = {"valid_context", "sha_file"}
missing = sorted(name for name in required_exports if not callable(getattr(support, name, None)))
assert not missing, f"missing public support exports: {missing}"

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    artifact = root / "artifact.bin"
    payload = (b"ACEE5-test-support-contract" * 4096) + b"tail"
    artifact.write_bytes(payload)

    expected = hashlib.sha256(payload).hexdigest()
    assert support.sha_file(artifact) == expected

    context = support.valid_context(root, proposal_id="support-contract", candidate_hash="e" * 64)
    assert context["proposal_id"] == "support-contract"
    assert context["candidate"]["content_sha256"] == "e" * 64
    assert context["validation_evidence"]["proposal_id"] == "support-contract"
    assert context["validation_evidence"]["candidate_content_sha256"] == "e" * 64
    assert context["timestamp_utc"].endswith("Z")
    assert context["validation_evidence"]["timestamp_utc"].endswith("Z")

print("ACEE5_TEST_SUPPORT_BACKWARD_COMPATIBILITY_OK")
