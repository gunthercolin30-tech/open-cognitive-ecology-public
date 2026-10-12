from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_architecture_genealogy import AceeArchitectureGenealogy


def base(
    architecture_id="ARCH-A",
    parent_architecture_id=None,
    generation_id=0,
    rollback_status="not_rolled_back",
):
    return {
        "architecture_id": architecture_id,
        "architecture": {
            "architecture_id": architecture_id,
            "modules": ["m1", "m2"],
            "parameters": {"x": 1},
        },
        "parent_architecture_id": parent_architecture_id,
        "generation_id": generation_id,
        "mutation_id": (
            f"MUT-{architecture_id}"
            if parent_architecture_id
            else None
        ),
        "selection_decision": {
            "selection_id": f"SEL-{architecture_id}",
            "decision": "accept",
        },
        "causal_analysis": {
            "analysis_id": f"CAUSAL-{architecture_id}",
        },
        "impact_evaluation": {
            "evaluation_id": f"IMPACT-{architecture_id}",
        },
        "rollback_status": rollback_status,
        "continuity_evidence": {"lineage_integrity": 0.91},
        "diversity_evidence": {"lineage_diversity_score": 0.82},
        "inheritance_evidence": {"inheritance_fidelity": 0.93},
        "timestamp_utc": "2026-07-13T20:00:00Z",
    }


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        first = AceeArchitectureGenealogy(root=root)
        root_record = first.step(inputs=base(), persist=True)
        assert root_record["persisted"] is True
        assert root_record["previous_genealogy_hash"] is None

        second = AceeArchitectureGenealogy(root=root)
        child_record = second.step(
            inputs=base("ARCH-B", "ARCH-A", 1),
            persist=True,
        )
        assert child_record["persisted"] is True
        assert (
            child_record["previous_genealogy_hash"]
            == root_record["genealogy_hash"]
        )
        assert child_record["ancestry_path"] == ["ARCH-A"]
        assert child_record["lineage_depth"] == 1

        third = AceeArchitectureGenealogy(root=root)
        grandchild = third.step(
            inputs=base("ARCH-C", "ARCH-B", 2),
            persist=True,
        )
        assert grandchild["persisted"] is True
        assert (
            grandchild["previous_genealogy_hash"]
            == child_record["genealogy_hash"]
        )
        assert grandchild["ancestry_path"] == ["ARCH-A", "ARCH-B"]
        assert grandchild["lineage_depth"] == 2

        directory = (
            root
            / "acee_runtime"
            / "ACEE12_acee_architecture_genealogy"
        )
        history_path = directory / "genealogy_history.jsonl"
        latest_path = directory / "latest_genealogy_record.json"
        graph_path = directory / "architecture_genealogy_graph.json"

        history = [
            json.loads(line)
            for line in history_path.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]
        assert len(history) == 3
        assert [item["architecture_id"] for item in history] == [
            "ARCH-A",
            "ARCH-B",
            "ARCH-C",
        ]

        latest = json.loads(latest_path.read_text(encoding="utf-8"))
        assert latest == history[-1]
        assert latest["architecture_id"] == "ARCH-C"

        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        assert graph["node_count"] == 3
        assert graph["edge_count"] == 2
        assert graph["children"] == {
            "ARCH-A": ["ARCH-B"],
            "ARCH-B": ["ARCH-C"],
        }

        fourth = AceeArchitectureGenealogy(root=root)
        branch = fourth.step(
            inputs=base("ARCH-D", "ARCH-A", 1),
            persist=True,
        )
        assert branch["persisted"] is True
        assert branch["ancestry_path"] == ["ARCH-A"]
        assert branch["lineage_depth"] == 1

    print("ACEE12_RESTART_CONTINUITY_OK")


if __name__ == "__main__":
    main()
