from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "open-cognitive-ecology.global_module_catalog.v1"

EXCLUDED_DIR_NAMES = {
    ".git", ".venv", "venv", "env", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "node_modules", ".DS_Store",
}

EXCLUDED_FILE_SUFFIXES = (".bak", ".corrupted", ".textClipping")

DOMAIN_DIRECTORIES = {
    "constraints", "cultural", "demography", "ecologies", "economy",
    "education", "environment", "health", "language", "law", "media",
    "memory", "narrative", "politics", "salience", "science",
    "technology", "world",
}

PRIMARY_DIRECTORIES = {
    "ontology", "validation", "runtime", "agents", "applications",
    "cognition", "cognitive_graph", "core", "processes", "visualization",
    "tests", "replication_packages", "archive",
}

CATEGORY_ORDER = [
    "ontology", "validation", "runtime", "agents", "applications",
    "cognition", "cognitive_graph", "core", "processes", "visualization",
    "tests", "replication_packages", "domain_modules", "root_scripts",
    "archive", "other_source",
]


def _is_excluded(rel: Path) -> bool:
    parts = set(rel.parts)
    if parts & EXCLUDED_DIR_NAMES:
        return True
    if rel.name.startswith("."):
        return True
    if any(rel.name.endswith(suffix) for suffix in EXCLUDED_FILE_SUFFIXES):
        return True
    if ".bak_" in rel.name or ".bak." in rel.name:
        return True
    if rel.name.endswith(".pyc"):
        return True
    return False


def _category_for(rel: Path) -> str:
    if len(rel.parts) == 1:
        return "root_scripts"
    top = rel.parts[0]
    if top in PRIMARY_DIRECTORIES:
        return top
    if top in DOMAIN_DIRECTORIES:
        return "domain_modules"
    return "other_source"


def _module_name_for(rel: Path) -> str:
    return ".".join(rel.with_suffix("").parts)


def _read_ontology_inventory_count(root: Path) -> int | None:
    p = root / "ontology_inventory.txt"
    if not p.exists():
        return None
    return len([line for line in p.read_text(encoding="utf-8").splitlines() if line.strip()])


def build_global_module_catalog(root: Path | None = None) -> dict[str, Any]:
    root = root or Path.home() / "open-cognitive-ecology"
    root = root.expanduser().resolve()

    python_files: list[dict[str, Any]] = []

    for path in sorted(root.rglob("*.py")):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue

        if _is_excluded(rel):
            continue

        category = _category_for(rel)
        top_level = rel.parts[0] if len(rel.parts) > 1 else "."

        python_files.append({
            "path": rel.as_posix(),
            "module_name": _module_name_for(rel),
            "category": category,
            "top_level": top_level,
            "is_ontology_module": category == "ontology",
            "is_validation_module": category == "validation",
            "is_test_module": category == "tests" or rel.name.startswith("test_"),
            "is_root_script": category == "root_scripts",
        })

    by_category: dict[str, int] = {category: 0 for category in CATEGORY_ORDER}
    by_top_level: dict[str, int] = {}

    for item in python_files:
        by_category[item["category"]] = by_category.get(item["category"], 0) + 1
        by_top_level[item["top_level"]] = by_top_level.get(item["top_level"], 0) + 1

    catalog = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "epistemic_status": "functional_architectural_inventory_only",
        "phenomenal_subjectivity_claimed": False,
        "does_not_modify_ontology_inventory": True,
        "does_not_move_files": True,
        "summary": {
            "total_python_files": len(python_files),
            "ontology_inventory_count": _read_ontology_inventory_count(root),
            "categories": by_category,
            "top_level": dict(sorted(by_top_level.items())),
        },
        "python_files": python_files,
    }
    return catalog


def write_global_module_catalog(root: Path | None = None) -> dict[str, Any]:
    root = root or Path.home() / "open-cognitive-ecology"
    root = root.expanduser().resolve()
    catalog = build_global_module_catalog(root)

    json_path = root / "global_module_catalog.json"
    txt_path = root / "global_module_catalog.txt"
    py_path = root / "global_module_catalog.py"

    json_path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )

    lines = [
        "Open Cognitive Ecology — Global Module Catalog",
        f"generated_at_utc: {catalog['generated_at_utc']}",
        f"total_python_files: {catalog['summary']['total_python_files']}",
        f"ontology_inventory_count: {catalog['summary']['ontology_inventory_count']}",
        "",
        "[categories]",
    ]

    for category in CATEGORY_ORDER:
        lines.append(f"{category}: {catalog['summary']['categories'].get(category, 0)}")

    lines.extend(["", "[modules]"])
    for item in catalog["python_files"]:
        lines.append(f"{item['category']}\t{item['module_name']}\t{item['path']}")

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    py_path.write_text(
        "# Auto-generated by validation.global_module_catalog.write_global_module_catalog\n"
        "from __future__ import annotations\n\n"
        "GLOBAL_MODULE_CATALOG = " + repr(catalog) + "\n",
        encoding="utf-8",
    )

    return {
        "success": True,
        "schema": catalog["schema"],
        "global_module_catalog_json": str(json_path),
        "global_module_catalog_txt": str(txt_path),
        "global_module_catalog_py": str(py_path),
        "total_python_files": catalog["summary"]["total_python_files"],
        "ontology_inventory_count": catalog["summary"]["ontology_inventory_count"],
        "epistemic_status": catalog["epistemic_status"],
        "phenomenal_subjectivity_claimed": False,
        "does_not_modify_ontology_inventory": True,
        "does_not_move_files": True,
    }


if __name__ == "__main__":
    print(json.dumps(write_global_module_catalog(), indent=2, ensure_ascii=False, sort_keys=True))
