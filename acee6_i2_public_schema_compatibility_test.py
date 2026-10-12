#!/usr/bin/env python3
from __future__ import annotations
import tempfile
from pathlib import Path
from ontology.acee_installation_executor import AceeInstallationExecutor
from acee6_i2_replay_functional_test import make_transaction

REQUIRED = {
    "primitive", "stage", "public_schema_version", "status",
    "functional_conclusion_only", "phenomenology_undetermined",
    "consciousness_proven", "subjectivity_proven",
    "qualia_proven", "phenomenology_proven", "result_hash",
}

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    make_transaction(root, "tx-a", "proposal-a", "a" * 64)
    engine = AceeInstallationExecutor(root=root)
    results = [
        engine.inspect_replay("tx-a", proposal_id="proposal-a", manifest_hash="a" * 64),
        engine.inspect_replay_registry(),
    ]
    for result in results:
        assert result["public_schema_version"] == "0.14.0", result
        assert REQUIRED.issubset(result), sorted(REQUIRED - set(result))
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
        for key in ("consciousness_proven", "subjectivity_proven", "qualia_proven", "phenomenology_proven"):
            assert result[key] is False, (key, result[key])
        assert isinstance(result["result_hash"], str)
        assert len(result["result_hash"]) == 64
print("ACEE6_I2_PUBLIC_SCHEMA_014_COMPATIBILITY_OK")
