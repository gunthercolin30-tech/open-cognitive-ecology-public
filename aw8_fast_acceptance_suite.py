from pathlib import Path
import json, py_compile, tempfile
from aw8_context import build_context
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine

def main():
    with tempfile.TemporaryDirectory(prefix="oce_aw8_compile_") as tmp:
        py_compile.compile("ontology/civilizational_memory_engine.py", cfile=str(Path(tmp)/"civilizational_memory_engine.pyc"), doraise=True)
    with tempfile.TemporaryDirectory(prefix="oce_aw8_") as tmp:
        engine = CivilizationalMemoryEngine(root=Path(tmp))
        first = engine.step(inputs=build_context(), persist=True)
        second = engine.step(inputs=build_context(), persist=False)
        assert first["civilizational_memory_ready"] is True
        assert first["status"] == "CIVILIZATIONAL_MEMORY_READY"
        assert first["memory_record_count"] == 2
        assert first["result_hash"] == second["result_hash"]
        assert len(first["memory_hash"]) == 64
        path = Path(first["output_path"])
        assert path.exists() and json.loads(path.read_text())["status"] == "CIVILIZATIONAL_MEMORY_READY"
        assert first["collective_consciousness_proven"] is False
        assert first["functional_conclusion_only"] is True
    print("AW8_FAST_ACCEPTANCE_OK")
if __name__ == "__main__": main()
