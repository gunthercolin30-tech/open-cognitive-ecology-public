from pathlib import Path
import tempfile
from aw8_context import build_context
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine

def main():
    with tempfile.TemporaryDirectory(prefix="oce_aw8_corrupt_") as tmp:
        engine = CivilizationalMemoryEngine(root=Path(tmp))
        path = engine.output_dir / "latest_civilizational_memory_engine.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{broken", encoding="utf-8")
        result = engine.step(inputs={**build_context(), "load_existing": True}, persist=False)
        assert result["previous_result_loaded"] is False
        assert result["civilizational_memory_ready"] is True
    print("AW8_CORRUPTION_FALLBACK_OK")
if __name__ == "__main__": main()
