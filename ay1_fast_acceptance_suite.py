\
from pathlib import Path
import tempfile
from ontology.theory_dependency_graph import TheoryDependencyGraph


def graph():
    return {"schema_version": "1.0.0", "nodes": [
        {"id": "A", "kind": "source_document", "title": "A"},
        {"id": "B", "kind": "source_document", "title": "B"},
        {"id": "C", "kind": "source_document", "title": "C"},
    ], "edges": []}


def main():
    relations = [
        {"source": "A", "target": "B", "relation": "requires", "status": "validated", "confidence": 1.0, "evidence": ["explicit_reference:p1"]},
        {"source": "B", "target": "C", "relation": "extends", "status": "candidate", "confidence": 0.7, "evidence": ["semantic_candidate"]},
    ]
    with tempfile.TemporaryDirectory(prefix="oce_ay1_fast_") as tmp:
        base = Path(tmp)
        a = TheoryDependencyGraph(root=base).step(inputs={"theory_graph": graph(), "relations": relations, "timestamp_utc": "2000-01-01T00:00:00Z"}, persist=False)
        b = TheoryDependencyGraph(root=base).step(inputs={"relations": list(reversed(relations)), "theory_graph": graph(), "timestamp_utc": "2000-01-01T00:00:00Z"}, persist=False)
        assert a["status"] == "THEORY_DEPENDENCY_GRAPH_READY"
        assert a["theory_dependency_graph_hash"] == b["theory_dependency_graph_hash"]
        assert a["validated_edge_count"] == 1 and a["candidate_edge_count"] == 1
        assert a["theory_dependency_graph"]["candidate_auto_promotion"] is False
        assert a["theory_dependency_graph"]["validated_edges"][0]["relation"] == "requires"
        for key in ("consciousness_proven", "subjectivity_proven", "qualia_proven", "phenomenology_proven"):
            assert a[key] is False
    print("AY1_FAST_ACCEPTANCE_ALL_OK")

if __name__ == "__main__": main()
