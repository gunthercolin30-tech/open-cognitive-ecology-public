#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FAST_SUITE_GLOB = "*_fast_acceptance_suite.py"


class FastSuiteGuard(ast.NodeVisitor):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.issues: list[tuple[int, str, str]] = []

    def issue(self, node: ast.AST, code: str, message: str) -> None:
        self.issues.append((getattr(node, "lineno", 0), code, message))

    def visit_Call(self, node: ast.Call) -> None:
        self._check_step_call(node)
        self._check_py_compile_call(node)
        self._check_repository_scan(node)
        self._check_forbidden_subprocess(node)
        self.generic_visit(node)

    def _check_step_call(self, node: ast.Call) -> None:
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "step":
            return
        if any(keyword.arg == "inputs" for keyword in node.keywords):
            return
        self.issue(
            node,
            "step_without_inputs",
            "Fast suites must call .step(inputs=ready_or_synthetic_context, ...).",
        )

    def _check_py_compile_call(self, node: ast.Call) -> None:
        if not (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "compile"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "py_compile"
        ):
            return
        if any(keyword.arg == "cfile" for keyword in node.keywords):
            return
        self.issue(
            node,
            "py_compile_without_tmp_cfile",
            "Fast suites must write py_compile bytecode with cfile under /private/tmp.",
        )

    def _check_repository_scan(self, node: ast.Call) -> None:
        if not isinstance(node.func, ast.Attribute) or node.func.attr not in {
            "glob",
            "rglob",
        }:
            return
        pattern = _literal_string(node.args[0]) if node.args else ""
        if "**" in pattern or "latest_" in pattern:
            self.issue(
                node,
                "recursive_repository_scan",
                "Fast suites must not scan the whole repository; inject explicit fixtures.",
            )

    def _check_forbidden_subprocess(self, node: ast.Call) -> None:
        if not _is_subprocess_or_system(node):
            return
        command_text = " ".join(_flatten_literal_strings(node.args[0])) if node.args else ""
        forbidden = (
            "validation.main",
            "validation/standard.py",
            "pytest",
            "-m pytest",
        )
        if any(marker in command_text for marker in forbidden):
            self.issue(
                node,
                "slow_subprocess_in_fast_suite",
                "Fast suites must not launch full validation or pytest subprocesses.",
            )


def _literal_string(node: ast.AST) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return ""


def _flatten_literal_strings(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Constant):
        return [str(node.value)]
    if isinstance(node, (ast.List, ast.Tuple)):
        values: list[str] = []
        for element in node.elts:
            values.extend(_flatten_literal_strings(element))
        return values
    return []


def _is_subprocess_or_system(node: ast.Call) -> bool:
    func = node.func
    if not isinstance(func, ast.Attribute):
        return False
    if func.attr == "system" and isinstance(func.value, ast.Name):
        return func.value.id == "os"
    if func.attr in {"run", "call", "check_call", "check_output", "Popen"}:
        return isinstance(func.value, ast.Name) and func.value.id == "subprocess"
    return False


def guard_file(path: Path) -> list[tuple[int, str, str]]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    guard = FastSuiteGuard(path)
    guard.visit(tree)
    return sorted(guard.issues)


def discover_fast_suites() -> list[Path]:
    return sorted(ROOT.glob(FAST_SUITE_GLOB), key=lambda path: path.name)


def print_issues(path: Path, issues: list[tuple[int, str, str]]) -> None:
    for line, code, message in issues:
        print(f"{path.name}:{line}: {code}: {message}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate the fast-suite contract before running generated suites."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="specific fast suite files; default with --all: every *_fast_acceptance_suite.py",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="check every root-level *_fast_acceptance_suite.py",
    )
    args = parser.parse_args()

    paths = [ROOT / name for name in args.files]
    if args.all or not paths:
        paths = discover_fast_suites()

    failures = 0
    for path in paths:
        issues = guard_file(path)
        if issues:
            failures += 1
            print_issues(path, issues)
    if failures:
        raise SystemExit(1)
    print(f"FAST_SUITE_GUARD_OK files={len(paths)}")


if __name__ == "__main__":
    main()
