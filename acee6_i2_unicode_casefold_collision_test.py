#!/usr/bin/env python3
from __future__ import annotations
import tempfile
import unicodedata
from pathlib import Path
from ontology.acee_installation_executor import AceeInstallationExecutor
from acee6_i2_replay_functional_test import make_transaction

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    composed = "Proposition-ÉCOLE"
    decomposed = unicodedata.normalize("NFD", "proposition-école")
    canonical = unicodedata.normalize("NFC", composed).casefold()
    assert canonical == unicodedata.normalize("NFC", decomposed).casefold()
    make_transaction(root, "tx-a", composed, "a" * 64)
    make_transaction(root, "tx-b", decomposed, "b" * 64)
    engine = AceeInstallationExecutor(root=root)
    registry = engine.inspect_replay_registry()
    assert registry["status"] == "ACEE6_REPLAY_REGISTRY_DIVERGED", registry
    assert canonical in registry["proposal_collisions"], registry
    identities = registry["proposal_collisions"][canonical]
    assert [item["transaction_id"] for item in identities] == ["tx-a", "tx-b"], identities
    replay = engine.inspect_replay("tx-a", proposal_id=decomposed, manifest_hash="a" * 64)
    assert replay["status"] == "ACEE6_REPLAY_REJECTED", replay
    assert "duplicate_proposal_collision" in replay["blocking_reasons"], replay
print("ACEE6_I2_UNICODE_CASEFOLD_COLLISION_OK")
