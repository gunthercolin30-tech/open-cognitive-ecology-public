from pathlib import Path
import ast


def inventory(ontology_dir="ontology"):
    path = Path(ontology_dir)
    if not path.exists():
        return []

    results = []

    for py in path.rglob("*.py"):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8", errors="ignore"))

            classes = [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            ]

            functions = [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
            ]

            results.append({
                "file": str(py),
                "classes": classes,
                "functions": functions,
            })

        except Exception:
            # Ignore modules that cannot be parsed.
            pass

    return results


def build_inventory(ontology_dir="ontology"):
    """
    Backward-compatible alias expected by other validation modules.
    """
    return inventory(ontology_dir)


if __name__ == "__main__":
    import json
    print(json.dumps(build_inventory(), indent=2))