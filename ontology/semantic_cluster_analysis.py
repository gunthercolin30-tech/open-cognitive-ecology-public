#!/usr/bin/env python3
"""
semantic_cluster_analysis.py

Analyse sémantique des clusters ontologiques et
inspection détaillée des dependency_overlap_pairs.
"""

from pathlib import Path
import json
import difflib
from collections import defaultdict

ROOT = Path.home() / "open-cognitive-ecology"

ONTOLOGY = ROOT / "ontology"

INPUT_REPORT = (
    ROOT / "redundancy_audit_report.json"
)

OUTPUT_REPORT = (
    ROOT / "semantic_cluster_report.json"
)


def tokenize(name):

    return set(
        name.lower().replace("-", "_").split("_")
    )


def similarity(a, b):

    return difflib.SequenceMatcher(
        None,
        a,
        b,
    ).ratio()


def load_modules():

    modules = []

    for path in sorted(
        ONTOLOGY.glob("*.py")
    ):

        if path.name == "__init__.py":
            continue

        modules.append(path.stem)

    return modules


def build_clusters(modules):

    clusters = defaultdict(list)

    for module in modules:

        tokens = tokenize(module)

        for token in tokens:

            if len(token) < 4:
                continue

            clusters[token].append(module)

    filtered = {
        k: sorted(set(v))
        for k, v in clusters.items()
        if len(v) >= 3
    }

    return dict(
        sorted(
            filtered.items(),
            key=lambda x: len(x[1]),
            reverse=True,
        )
    )


def analyze_similarity_density(modules):

    density = []

    for i in range(len(modules)):

        for j in range(i + 1, len(modules)):

            a = modules[i]
            b = modules[j]

            score = similarity(a, b)

            if score >= 0.80:

                density.append(
                    {
                        "module_a": a,
                        "module_b": b,
                        "similarity": round(
                            score,
                            4,
                        ),
                    }
                )

    return density


def load_overlap_pairs():

    if not INPUT_REPORT.exists():
        return []

    data = json.loads(
        INPUT_REPORT.read_text(
            encoding="utf-8"
        )
    )

    return data.get(
        "dependency_overlap",
        []
    )


def classify_overlap(pair):

    overlap = pair.get(
        "dependency_overlap",
        0.0,
    )

    if overlap >= 0.90:
        return "near_duplicate"

    if overlap >= 0.75:
        return "strong_overlap"

    return "moderate_overlap"


def analyze_dependency_overlap():

    overlaps = load_overlap_pairs()

    analysis = []

    for pair in overlaps:

        analysis.append(
            {
                "module_a":
                    pair["module_a"],
                "module_b":
                    pair["module_b"],
                "dependency_overlap":
                    pair[
                        "dependency_overlap"
                    ],
                "classification":
                    classify_overlap(pair),
            }
        )

    return analysis


def main():

    modules = load_modules()

    clusters = build_clusters(modules)

    similarity_density = (
        analyze_similarity_density(
            modules
        )
    )

    overlap_analysis = (
        analyze_dependency_overlap()
    )

    report = {
        "module_count":
            len(modules),
        "cluster_count":
            len(clusters),
        "top_clusters":
            dict(
                list(
                    clusters.items()
                )[:25]
            ),
        "high_similarity_pairs":
            similarity_density,
        "dependency_overlap_analysis":
            overlap_analysis,
    }

    OUTPUT_REPORT.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    summary = {
        "success": True,
        "module_count":
            len(modules),
        "cluster_count":
            len(clusters),
        "high_similarity_pairs":
            len(
                similarity_density
            ),
        "dependency_overlap_analysis":
            len(
                overlap_analysis
            ),
        "report_path":
            str(OUTPUT_REPORT),
    }

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
