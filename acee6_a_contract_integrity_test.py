from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
CONTRACTS = (
    "acee6_test_requirements_registry.py",
    "acee6_transaction_state_contract.py",
    "acee6_a_hardening_contract.py",
    "acee6_non_redundancy_report.json",
    "acee6_a_hardening_report.json",
    "acee6_a_contract_snapshot.py",
)


def semantic_digest(path):
    if path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    else:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        canonical = ast.dump(tree, annotate_fields=True, include_attributes=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main():
    digests = {}
    for relative in CONTRACTS:
        path = ROOT / relative
        assert path.is_file(), relative
        digest = semantic_digest(path)
        assert len(digest) == 64
        digests[relative] = digest
    assert len(set(digests.values())) == len(digests)
    assert semantic_digest(ROOT / "acee6_non_redundancy_report.json") == semantic_digest(ROOT / "acee6_non_redundancy_report.json")
    print("ACEE6_A_CONTRACT_INTEGRITY_OK")


if __name__ == "__main__":
    main()
