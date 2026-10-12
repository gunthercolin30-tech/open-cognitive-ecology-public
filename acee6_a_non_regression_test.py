from __future__ import annotations

import hashlib
import importlib
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
RUNTIME = ROOT / "ontology" / "acee_installation_executor.py"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def main():
    before = digest(RUNTIME)
    importlib.import_module("acee6_test_requirements_registry")
    importlib.import_module("acee6_transaction_state_contract")
    after = digest(RUNTIME)
    assert before == after
    if RUNTIME.exists():
        module = importlib.import_module("ontology.acee_installation_executor")
        assert module.STAGE == "ACEE6-B1"
        assert module.PUBLIC_SCHEMA_VERSION == "0.1.0"
    print("ACEE6_A_NON_REGRESSION_OK")


if __name__ == "__main__":
    main()
