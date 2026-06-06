from pathlib import Path
import json

from .constraint_table_loader import load_constraints
from .manuscript_concept_extractor import extract_concepts
from .ontology_inventory import inventory
from .semantic_constraint_matcher import match
from .ontology_completion_planner import recommend_action


def run():
    # Chargement des données
    constraints = load_constraints()
    concepts = extract_concepts()
    inv = inventory()

    # Correspondances
    matches = match(constraints, concepts, inv)

    # Résumé
    summary = {
        "total_constraints": len(constraints) if constraints else len(concepts),
        "implemented": sum(1 for m in matches if m["status"] == "implemented"),
        "partial": sum(1 for m in matches if m["status"] == "partial"),
        "missing": sum(1 for m in matches if m["status"] == "missing"),
    }

    total = max(1, len(matches))
    summary["coverage"] = (
        summary["implemented"] + 0.5 * summary["partial"]
    ) / total

    # Détails et actions recommandées
    details = []
    action_counts = {}

    for m in matches:
        action = recommend_action(m["status"])
        action_counts[action] = action_counts.get(action, 0) + 1

        details.append({
            "concept": m["concept"],
            "status": m["status"],
            "recommended_action": action,
        })

    # Rapport final
    report = {
        "summary": summary,
        "actions": action_counts,
        "details": details,
    }

    # Fichiers de sortie
    output_dir = Path("validation")
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / "constraint_audit_report.json"
    txt_path = output_dir / "constraint_audit_report.txt"

    # Écriture JSON
    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Écriture TXT
    lines = [
        "CONSTRAINT AUDIT REPORT",
        "=" * 80,
        "",
        json.dumps(summary, indent=2, ensure_ascii=False),
        "",
        "DETAILS",
        "-" * 80,
    ]

    for d in details:
        lines.append(
            f'{d["concept"]}: {d["status"]} -> {d["recommended_action"]}'
        )

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    # Affichage console
    print(json.dumps(report, indent=2, ensure_ascii=False))

    return report


if __name__ == "__main__":
    run()