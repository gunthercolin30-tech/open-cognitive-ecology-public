from __future__ import annotations

import ast
import hashlib
import importlib
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
RUNTIME = ROOT / "ontology" / "acee_installation_executor.py"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def main():
    forbidden = {
        "subprocess.run", "subprocess.Popen", "os.replace",
        "shutil.copy", "shutil.copy2", "py_compile.compile",
    }
    for name in (
        "acee6_test_requirements_registry.py",
        "acee6_transaction_state_contract.py",
        "acee6_a_hardening_contract.py",
    ):
        tree = ast.parse((ROOT / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                try:
                    called = ast.unparse(node.func)
                except Exception:
                    called = ""
                assert called not in forbidden
    before = digest(RUNTIME)
    importlib.import_module("acee6_test_requirements_registry")
    importlib.import_module("acee6_transaction_state_contract")
    importlib.import_module("acee6_a_hardening_contract")
    after = digest(RUNTIME)
    assert before == after
    if RUNTIME.exists():
        source = RUNTIME.read_text(encoding="utf-8")
        for token in (
            "subprocess.run", "subprocess.Popen", "os.replace",
            "write_text(", "write_bytes(", "AceeRollbackEngine",
            "AceeValidationRunner",
        ):
            assert token not in source, token
        module = importlib.import_module("ontology.acee_installation_executor")
        assert module.STAGE == "ACEE6-B1"
    print("ACEE6_A_ACEE6B_BOUNDARY_OK")


if __name__ == "__main__":
    main()
