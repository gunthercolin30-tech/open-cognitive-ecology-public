#!/usr/bin/env python3
"""
ontology_redundancy_audit.py

Analyse globale des redondances potentielles dans l'ontologie
Open Cognitive Ecology.

Fonctions :
- scan complet des modules ontology/*.py
- extraction des PRIMITIVE
- extraction des DEPENDENCIES
- similarité lexicale des noms
- similarité structurelle simple
- détection des doublons potentiels
- génération d'un rapport JSON
"""

from pathlib import Path
import ast
import json
import difflib
from collections import defaultdict

ROOT = Path.home() / "open-cognitive-ecology"
ONTOLOGY = ROOT / "ontology"

REPORT_PATH = ROOT / "redundancy_audit_report.json"


def safe_read(path):

    try:
        return path.read_text(
            encoding="utf-8"
        )

    except Exception:
        return ""


def extract_metadata(path):

    source = safe_read(path)

    primitive = None
    dependencies = []
    classes = []
    functions = []

    try:

        tree = ast.parse(source)

        for node in tree.body:

            if isinstance(node, ast.Assign):

                for target in node.targets:

                    if (
                        isinstance(target, ast.Name)
                        and target.id == "PRIMITIVE"
                    ):

                        try:
                            primitive = ast.literal_eval(
                                node.value
                            )
                        except Exception:
                            pass

                    if (
                        isinstance(target, ast.Name)
                        and target.id == "DEPENDENCIES"
                    ):

                        try:
                            dependencies = ast.literal_eval(
                                node.value
                            )
                        except Exception:
                            pass

            elif isinstance(node, ast.ClassDef):

                classes.append(node.name)

            elif isinstance(node, ast.FunctionDef):

                functions.append(node.name)

    except Exception:
        pass

    return {
        "module": path.stem,
        "primitive": primitive,
        "dependencies": dependencies,
        "classes": classes,
        "functions": functions,
        "line_count": len(source.splitlines()),
        "source": source,
    }


def similarity(a, b):

    return difflib.SequenceMatcher(
        None,
        a,
        b,
    ).ratio()


def main():

    modules = []

    for path in sorted(
        ONTOLOGY.glob("*.py")
    ):

        if path.name == "__init__.py":
            continue

        modules.append(
            extract_metadata(path)
        )

    primitive_duplicates = defaultdict(list)

    for module in modules:

        primitive = module["primitive"]

        if primitive:
            primitive_duplicates[
                primitive
            ].append(module["module"])

    primitive_collisions = {
        k: v
        for k, v in primitive_duplicates.items()
        if len(v) > 1
    }

    lexical_similarities = []

    for i in range(len(modules)):

        for j in range(i + 1, len(modules)):

            a = modules[i]
            b = modules[j]

            score = similarity(
                a["module"],
                b["module"],
            )

            if score >= 0.72:

                lexical_similarities.append(
                    {
                        "module_a": a["module"],
                        "module_b": b["module"],
                        "similarity": round(
                            score,
                            4,
                        ),
                    }
                )

    dependency_overlap = []

    for i in range(len(modules)):

        for j in range(i + 1, len(modules)):

            a = modules[i]
            b = modules[j]

            deps_a = set(a["dependencies"])
            deps_b = set(b["dependencies"])

            if not deps_a or not deps_b:
                continue

            overlap = (
                len(deps_a & deps_b)
                / len(deps_a | deps_b)
            )

            if overlap >= 0.60:

                dependency_overlap.append(
                    {
                        "module_a": a["module"],
                        "module_b": b["module"],
                        "dependency_overlap":
                            round(
                                overlap,
                                4,
                            ),
                    }
                )

    report = {
        "module_count": len(modules),
        "primitive_collisions":
            primitive_collisions,
        "lexical_similarities":
            lexical_similarities,
        "dependency_overlap":
            dependency_overlap,
    }

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "success": True,
                "report_path":
                    str(REPORT_PATH),
                "module_count":
                    len(modules),
                "primitive_collisions":
                    len(
                        primitive_collisions
                    ),
                "lexical_similarity_pairs":
                    len(
                        lexical_similarities
                    ),
                "dependency_overlap_pairs":
                    len(
                        dependency_overlap
                    ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
