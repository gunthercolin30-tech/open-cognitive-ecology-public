from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager

with TemporaryDirectory() as tmp:
    manager = AceeLineageManager(root=Path(tmp))
    inputs = {"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0","metadata":{"nested":[1,2,3]}}
    before = deepcopy(inputs)
    manager.step(inputs=inputs, persist=True)
    assert inputs == before
print("ACEE13_INPUT_IMMUTABILITY_OK")
