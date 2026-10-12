import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import (
    AceeGovernedCodeGenerationGate,
)
from ontology.acee_installation_executor import AceeInstallationExecutor


content = "candidate\n"
content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
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

    executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    first = executor.step(inputs=inputs, persist=True)
    manifest = Path(first["mutation_manifest_path"])
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["written_sha256"] = "f" * 64
    manifest.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    second = executor.step(inputs=inputs, persist=True)
    assert second["transaction_state"] == "STATE_CORRUPTED"
    assert "existing_mutation_manifest_hash_invalid" in (
        second["blocking_reasons"]
    )

print("ACEE6_D2_MUTATION_MANIFEST_TAMPER_OK")
