\
from pathlib import Path
import tempfile
from ontology.theory_dependency_graph import TheoryDependencyGraph

def main():
    with tempfile.TemporaryDirectory(prefix="oce_ay1_deg_") as tmp:
        result = TheoryDependencyGraph(root=Path(tmp)).step({"theory_graph": {"schema_version": "1.0.0", "nodes": [], "edges": []}, "relations": []}, persist=False)
        assert result["status"] == "THEORY_DEPENDENCY_GRAPH_DEGRADED"
        assert "empty_input_theory_graph" in result["degraded_reasons"]
        assert "no_validated_dependencies" in result["degraded_reasons"]
    print("AY1_DEGRADATION_OK")

if __name__ == "__main__": main()
