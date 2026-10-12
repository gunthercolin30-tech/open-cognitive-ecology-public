from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import tempfile
from pathlib import Path
from typing import Dict

import acee5_hardening_test_support as support

ROOT = Path(__file__).resolve().parent
SUPPORT_PATH = ROOT / "acee5_hardening_test_support.py"
EXPECTED_CALLABLE_EXPORTS = {"sha_file", "valid_context"}
EXPECTED_SIGNATURES = {
    "sha_file": {
        "parameters": ("path",),
        "defaults": {},
    },
    "valid_context": {
        "parameters": ("root", "proposal_id", "candidate_hash"),
        "defaults": {
            "proposal_id": "proposal-001",
            "candidate_hash": "a" * 64,
        },
    },
}
REFINERS = (
    Path.home() / "Downloads" / "refine_acee5_additional_hardening_tests.py",
    Path.home() / "Downloads" / "refine_acee5_optional_validation_tests.py",
)


def declared_public_callables(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and not node.name.startswith("_")
    }


def consumer_imports() -> set[str]:
    required: set[str] = set()
    for path in sorted(ROOT.glob("acee5_*.py")):
        if path.name in {SUPPORT_PATH.name, Path(__file__).name}:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "acee5_hardening_test_support":
                required.update(alias.name for alias in node.names if alias.name != "*")
    return required


def embedded_files(path: Path) -> Dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "FILES" for target in node.targets):
            continue
        value = ast.literal_eval(node.value)
        assert isinstance(value, dict), f"FILES must be a dict in {path}"
        return value
    raise AssertionError(f"FILES assignment missing in {path}")


def check_signatures() -> None:
    for name, contract in EXPECTED_SIGNATURES.items():
        value = getattr(support, name, None)
        assert callable(value), f"missing callable export: {name}"
        signature = inspect.signature(value)
        assert tuple(signature.parameters) == contract["parameters"], (
            name,
            tuple(signature.parameters),
        )
        actual_defaults = {
            parameter_name: parameter.default
            for parameter_name, parameter in signature.parameters.items()
            if parameter.default is not inspect.Parameter.empty
        }
        assert actual_defaults == contract["defaults"], (
            name,
            actual_defaults,
        )


def check_behavior() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first = root / "first.bin"
        second = root / "second.bin"
        first.write_bytes(b"ACEE5-public-api-snapshot")
        second.write_bytes(b"ACEE5-public-api-snapshot-modified")

        first_expected = hashlib.sha256(first.read_bytes()).hexdigest()
        assert support.sha_file(first) == first_expected
        assert support.sha_file(first) == support.sha_file(first)
        assert support.sha_file(first) != support.sha_file(second)
        assert len(support.sha_file(first)) == 64
        assert set(support.sha_file(first)) <= set("0123456789abcdef")

        context = support.valid_context(
            root,
            proposal_id="snapshot-proposal",
            candidate_hash="e" * 64,
        )
        assert isinstance(context, dict)
        assert context["proposal_id"] == "snapshot-proposal"
        assert context["candidate"]["content_sha256"] == "e" * 64
        assert context["validation_evidence"]["proposal_id"] == "snapshot-proposal"
        assert context["validation_evidence"]["candidate_content_sha256"] == "e" * 64
        assert context["timestamp_utc"].endswith("Z")
        assert context["validation_evidence"]["timestamp_utc"].endswith("Z")
        guards = context["constitutional_evidence"]
        assert guards["functional_conclusion_only"] is True
        assert guards["phenomenology_undetermined"] is True


def check_refiners() -> None:
    for path in REFINERS:
        assert path.is_file(), f"missing refiner: {path}"
        files = embedded_files(path)
        embedded = files.get(SUPPORT_PATH.name)
        assert isinstance(embedded, str), f"support payload missing in {path}"
        embedded_tree = ast.parse(embedded, filename=f"{path}:{SUPPORT_PATH.name}")
        functions = {
            node.name
            for node in embedded_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert EXPECTED_CALLABLE_EXPORTS <= functions, (
            path,
            sorted(EXPECTED_CALLABLE_EXPORTS - functions),
        )


def main() -> None:
    importlib.invalidate_caches()
    declared = declared_public_callables(SUPPORT_PATH)
    assert declared == EXPECTED_CALLABLE_EXPORTS, (
        "public callable snapshot changed",
        sorted(declared),
    )

    runtime_callables = {
        name
        for name in EXPECTED_CALLABLE_EXPORTS
        if callable(getattr(support, name, None))
    }
    assert runtime_callables == EXPECTED_CALLABLE_EXPORTS

    required_by_consumers = consumer_imports()
    assert required_by_consumers <= EXPECTED_CALLABLE_EXPORTS, (
        "consumer expanded support API without snapshot update",
        sorted(required_by_consumers - EXPECTED_CALLABLE_EXPORTS),
    )
    assert required_by_consumers == EXPECTED_CALLABLE_EXPORTS, (
        "snapshot contains unused callable exports",
        sorted(EXPECTED_CALLABLE_EXPORTS - required_by_consumers),
    )

    check_signatures()
    check_behavior()
    check_refiners()
    print("ACEE5_PUBLIC_API_SNAPSHOT_OK")


if __name__ == "__main__":
    main()
