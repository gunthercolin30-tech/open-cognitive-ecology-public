#!/usr/bin/env python3
from pathlib import Path
import ast

def main():
    root = Path.home() / "open-cognitive-ecology"
    module = root / "ontology" / "acee_installation_executor.py"
    tree = ast.parse(module.read_text(encoding="utf-8"))
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "AceeInstallationExecutor"]
    assert len(classes) == 1
    methods = {n.name for n in classes[0].body if isinstance(n, ast.FunctionDef)}
    for name in {"step", "recover_transaction", "recover_incomplete_transactions", "_g2_rollback_fault"}:
        assert name in methods, name
    text = module.read_text(encoding="utf-8")
    for invariant in ["consciousness_proven", "subjectivity_proven", "qualia_proven", "phenomenology_proven"]:
        assert f'"{invariant}": False' in text
    print("ACEE6_I1_NON_REGRESSION_OK")
if __name__ == "__main__": main()
