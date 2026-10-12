from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List, Set

FORBIDDEN_EXACT_CALLS: Set[str] = {
    "builtins.eval", "builtins.exec", "builtins.compile",
    "eval", "exec", "compile",
    "os.system", "os.popen", "os.remove", "os.unlink", "os.replace",
    "os.rename", "os.mkdir", "os.makedirs", "os.rmdir",
    "subprocess.run", "subprocess.call", "subprocess.check_call",
    "subprocess.check_output", "subprocess.Popen",
    "asyncio.create_subprocess_exec", "asyncio.create_subprocess_shell",
    "shutil.copy", "shutil.copy2", "shutil.copyfile", "shutil.copytree",
    "shutil.move", "shutil.rmtree",
    "sqlite3.connect", "shelve.open", "dbm.open",
    "runpy.run_path", "runpy.run_module",
}

FORBIDDEN_PATH_METHODS: Set[str] = {
    "write_text", "write_bytes", "unlink", "rename", "replace", "touch",
    "mkdir", "rmdir", "chmod", "symlink_to", "hardlink_to",
}

ALLOWED_EXACT_CALLS: Set[str] = {"nicegui.ui.run", "ui.run"}
WRITE_MODE_FLAGS = frozenset("wax+")


def _attribute_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _attribute_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _import_aliases(tree: ast.AST) -> Dict[str, str]:
    aliases: Dict[str, str] = {
        "eval": "eval", "exec": "exec", "compile": "compile", "open": "open"
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                local = item.asname or item.name.split(".", 1)[0]
                aliases[local] = item.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for item in node.names:
                if item.name == "*":
                    continue
                local = item.asname or item.name
                aliases[local] = f"{node.module}.{item.name}"
    return aliases


def _local_aliases(tree: ast.AST, aliases: Dict[str, str]) -> Dict[str, str]:
    result = dict(aliases)
    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name):
                continue
            if isinstance(node.value, ast.Call):
                raw = _attribute_name(node.value.func)
            else:
                raw = _attribute_name(node.value)
            if not raw:
                continue
            resolved = _resolve_name(raw, result)
            if target.id not in result and resolved:
                result[target.id] = resolved
                changed = True
    return result


def _resolve_name(raw: str, aliases: Dict[str, str]) -> str:
    if not raw:
        return raw
    first, dot, rest = raw.partition(".")
    base = aliases.get(first, first)
    return f"{base}.{rest}" if dot else base


def _call_target_name(node: ast.AST, aliases: Dict[str, str]) -> str:
    if isinstance(node, ast.Call):
        raw = _attribute_name(node.func)
        return _resolve_name(raw, aliases)
    return _resolve_name(_attribute_name(node), aliases)


def _is_path_receiver(node: ast.AST, aliases: Dict[str, str]) -> bool:
    target = _call_target_name(node, aliases)
    return target in {"pathlib.Path", "Path"}


def _open_mode(node: ast.Call) -> str | None:
    mode_node = None
    if len(node.args) >= 2:
        mode_node = node.args[1]
    else:
        for kw in node.keywords:
            if kw.arg == "mode":
                mode_node = kw.value
                break
    if isinstance(mode_node, ast.Constant) and isinstance(mode_node.value, str):
        return mode_node.value
    return None


def renderer_policy_findings_from_source(source: str, filename: str = "<renderer>") -> List[str]:
    tree = ast.parse(source, filename=filename)
    aliases = _local_aliases(tree, _import_aliases(tree))
    findings: List[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        raw = _attribute_name(node.func)
        resolved = _resolve_name(raw, aliases)
        line = getattr(node, "lineno", 0)

        if resolved in ALLOWED_EXACT_CALLS or raw in ALLOWED_EXACT_CALLS:
            continue
        if resolved in FORBIDDEN_EXACT_CALLS or raw in FORBIDDEN_EXACT_CALLS:
            findings.append(f"forbidden-call:{resolved or raw}:{line}")
            continue

        if isinstance(node.func, ast.Attribute):
            method = node.func.attr
            if method in FORBIDDEN_PATH_METHODS and _is_path_receiver(node.func.value, aliases):
                findings.append(f"direct-pathlib-write:pathlib.Path.{method}:{line}")
                continue

        if resolved in {"open", "builtins.open", "io.open"}:
            mode = _open_mode(node)
            if mode is None:
                # Default open mode is read-only and therefore not a direct write.
                continue
            if WRITE_MODE_FLAGS.intersection(mode):
                findings.append(f"direct-open-write:{mode}:{line}")

    return sorted(set(findings))


def renderer_policy_findings(path: Path) -> List[str]:
    return renderer_policy_findings_from_source(
        path.read_text(encoding="utf-8"), filename=str(path)
    )
