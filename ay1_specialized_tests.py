\
from pathlib import Path
import json, tempfile
from ontology.theory_dependency_graph import TheoryDependencyGraph

def expect(exc, fn):
    try: fn()
    except exc: return
    raise AssertionError(f"expected {exc.__name__}")

def main():
    graph={"schema_version":"1.0.0","nodes":[{"id":"A"},{"id":"B"},{"id":"C"}],"edges":[]}
    with tempfile.TemporaryDirectory(prefix="oce_ay1_spec_") as tmp:
        base=Path(tmp); engine=TheoryDependencyGraph(root=base)
        expect(ValueError, lambda: engine.step({"theory_graph":graph,"relations":[{"source":"A","target":"A","relation":"supports","status":"validated","evidence":["x"]}]}))
        expect(ValueError, lambda: engine.step({"theory_graph":graph,"relations":[{"source":"A","target":"Z","relation":"supports","status":"validated","evidence":["x"]}]}))
        expect(ValueError, lambda: engine.step({"theory_graph":graph,"relations":[{"source":"A","target":"B","relation":"causes","status":"validated","evidence":["x"]}]}))
        expect(ValueError, lambda: engine.step({"theory_graph":graph,"relations":[{"source":"A","target":"B","relation":"supports","status":"validated","evidence":[]}]}))
        relations=[
          {"source":"A","target":"B","relation":"requires","status":"validated","evidence":["r1"]},
          {"source":"B","target":"C","relation":"requires","status":"validated","evidence":["r2"]},
          {"source":"C","target":"A","relation":"requires","status":"validated","evidence":["r3"]},
        ]
        cycle=engine.step({"theory_graph":graph,"relations":relations}, persist=True)
        assert cycle["theory_dependency_graph"]["validated_cycle_detected"] is True
        output=Path(cycle["output_path"]); assert output.exists(); json.loads(output.read_text())
        candidate=engine.step({"theory_graph":graph,"relations":[{"source":"A","target":"B","relation":"supports","status":"candidate","confidence":0.9}]})
        assert candidate["validated_edge_count"] == 0 and candidate["candidate_edge_count"] == 1
        assert candidate["status"] == "THEORY_DEPENDENCY_GRAPH_DEGRADED"
    print("AY1_SPECIALIZED_TESTS_OK")

if __name__ == "__main__": main()
