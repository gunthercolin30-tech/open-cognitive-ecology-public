\
from pathlib import Path
import tempfile
from ontology.theory_dependency_graph import TheoryDependencyGraph

def main():
    graph={"schema_version":"1.0.0","nodes":[{"id":"A"},{"id":"B"}],"edges":[]}
    rel=[{"source":"A","target":"B","relation":"requires","status":"validated","confidence":1.0,"evidence":["explicit"]}]
    with tempfile.TemporaryDirectory(prefix="oce_ay1_lock_") as tmp:
        a=TheoryDependencyGraph(root=Path(tmp)).step({"theory_graph":graph,"relations":rel,"timestamp_utc":"2000-01-01T00:00:00Z"}, persist=False)
        b=TheoryDependencyGraph(root=Path(tmp)).step({"relations":rel,"theory_graph":graph,"timestamp_utc":"2000-01-01T00:00:00Z"}, persist=False)
        assert a["status"] == "THEORY_DEPENDENCY_GRAPH_READY"
        assert a["dependency_graph_ready"] is True
        assert a["theory_dependency_graph_hash"] == b["theory_dependency_graph_hash"]
        assert a["theory_dependency_graph"]["candidate_auto_promotion"] is False
        assert a["functional_conclusion_only"] is True and a["phenomenology_undetermined"] is True
        for key in ("consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven"): assert a[key] is False
    print("AY1_THEORY_DEPENDENCY_GRAPH_FINAL_LOCK_OK")

if __name__ == "__main__": main()
