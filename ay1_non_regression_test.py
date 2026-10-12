\
from pathlib import Path
import hashlib, tempfile
from ontology.theory_dependency_graph import TheoryDependencyGraph

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    root = Path(__file__).resolve().parent
    protected = [root / "ontology" / "theory_corpus_auditor.py", root / "ontology" / "theorem_dependency_mapper.py"]
    before = {str(p): digest(p) for p in protected if p.exists()}
    with tempfile.TemporaryDirectory(prefix="oce_ay1_nr_") as tmp:
        base=Path(tmp)
        graph={"schema_version":"1.0.0","nodes":[{"id":"A"},{"id":"B"}],"edges":[]}
        result=TheoryDependencyGraph(root=base).step({"theory_graph":graph,"relations":[{"source":"A","target":"B","relation":"supports","status":"validated","evidence":["manual"]}]}, persist=False)
        assert result["persisted"] is False
        assert not (base / "theory_evolution").exists()
    after = {str(p): digest(p) for p in protected if p.exists()}
    assert before == after
    print("AY1_NON_REGRESSION_OK")

if __name__ == "__main__": main()
