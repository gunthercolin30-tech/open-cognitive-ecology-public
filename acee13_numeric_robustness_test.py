from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager
with TemporaryDirectory() as tmp:
    m=AceeLineageManager(root=Path(tmp)); m.step({"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"},persist=True)
    for bad in (float("nan"),float("inf"),True,"bad"):
        r=m.step({"operation":"register_candidate","transaction_id":"T"+str(bad),"lineage_id":"L","generation_id":1,"architecture_id":"A1","parent_id":"A0","mutation_id":"M1","fitness_delta":bad},persist=False)
        assert "finite_fitness_delta_required" in r["blocking_reasons"]
print("ACEE13_NUMERIC_ROBUSTNESS_OK")
