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


def expected_graph(records):
    nodes = {}
    children = {}

    for record in records:
        architecture_id = str(record.get("architecture_id") or "")
        assert architecture_id

        nodes[architecture_id] = {
            "architecture_id": architecture_id,
            "parent_architecture_id": record.get(
                "parent_architecture_id"
            ),
            "generation_id": record.get("generation_id"),
            "architecture_fingerprint": record.get(
                "architecture_fingerprint"
            ),
            "rollback_status": record.get("rollback_status"),
            "active": record.get("active"),
        }

        parent = record.get("parent_architecture_id")
        if parent:
            children.setdefault(str(parent), []).append(
                architecture_id
            )

    return {
        "primitive": "ACEE_ARCHITECTURE_GENEALOGY",
        "node_count": len(nodes),
        "edge_count": sum(
            len(values)
            for values in children.values()
        ),
        "nodes": nodes,
        "children": {
            key: sorted(set(values))
            for key, values in sorted(children.items())
        },
    }


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        records_to_write = [
            base("ARCH-A", None, 0),
            base("ARCH-B", "ARCH-A", 1),
            base("ARCH-C", "ARCH-A", 1),
            base("ARCH-D", "ARCH-B", 2),
            base(
                "ARCH-E",
                "ARCH-C",
                2,
                rollback_status="rolled_back",
            ),
        ]

        for payload in records_to_write:
            result = AceeArchitectureGenealogy(root=root).step(
                inputs=payload,
                persist=True,
            )
            assert result["persisted"] is True

        directory = (
            root
            / "acee_runtime"
            / "ACEE12_acee_architecture_genealogy"
        )
        history_path = directory / "genealogy_history.jsonl"
        graph_path = directory / "architecture_genealogy_graph.json"
        latest_path = directory / "latest_genealogy_record.json"

        history = [
            json.loads(line)
            for line in history_path.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]
        persisted_graph = json.loads(
            graph_path.read_text(encoding="utf-8")
        )
        latest = json.loads(
            latest_path.read_text(encoding="utf-8")
        )

        rebuilt_graph = expected_graph(history)
        assert persisted_graph == rebuilt_graph

        assert persisted_graph["node_count"] == len(history)
        assert persisted_graph["edge_count"] == 4
        assert set(persisted_graph["nodes"]) == {
            item["architecture_id"]
            for item in history
        }
        assert persisted_graph["children"] == {
            "ARCH-A": ["ARCH-B", "ARCH-C"],
            "ARCH-B": ["ARCH-D"],
            "ARCH-C": ["ARCH-E"],
        }

        assert persisted_graph["nodes"]["ARCH-E"]["active"] is False
        assert (
            persisted_graph["nodes"]["ARCH-E"]["rollback_status"]
            == "rolled_back"
        )

        assert latest == history[-1]
        assert (
            latest["genealogy_hash"]
            == history[-1]["genealogy_hash"]
        )

        probe = AceeArchitectureGenealogy(root=root).step(
            inputs=base("ARCH-F", "ARCH-D", 3),
            persist=False,
        )
        assert probe["genealogy_ready"] is True
        assert probe["ancestry_path"] == [
            "ARCH-A",
            "ARCH-B",
            "ARCH-D",
        ]

    print("ACEE12_GRAPH_HISTORY_CONSISTENCY_OK")


if __name__ == "__main__":
    main()
