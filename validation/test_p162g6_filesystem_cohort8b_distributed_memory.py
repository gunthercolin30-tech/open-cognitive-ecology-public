from pathlib import Path
import pytest
from ontology.distributed_civilizational_memory import DistributedCivilizationalMemory
class RecordingContext:
    def __init__(self): self.calls=[]
    def execute_path(self,slot,operation_id,path,payload=None):
        self.calls.append((slot,operation_id,Path(path),payload)); return {"status":"EFFECT_CONFIRMED"}
def test_constructor_is_pure(tmp_path):
    DistributedCivilizationalMemory(root=tmp_path); assert list(tmp_path.iterdir())==[]
def test_default_step_is_read_only(tmp_path):
    e=DistributedCivilizationalMemory(root=tmp_path); r=e.step({"replica_count":2})
    assert r["replica_write_count"]==0 and r["registry_written"] is False and r["history_written"] is False
    assert list(tmp_path.iterdir())==[]
def test_persist_without_context_rejected_before_effect(tmp_path):
    e=DistributedCivilizationalMemory(root=tmp_path)
    with pytest.raises(PermissionError,match="filesystem_effect_context_required"): e.step({"replica_count":2},persist=True)
    assert list(tmp_path.iterdir())==[]
def test_persist_routes_all_effects_through_context(tmp_path):
    e=DistributedCivilizationalMemory(root=tmp_path); c=RecordingContext()
    r=e.step({"replica_count":2},persist=True,filesystem_effect_context=c); ops=[x[1] for x in c.calls]
    assert ops.count("FS_APPEND_BYTES")==1 and "FS_CREATE_DIR" in ops
    assert r["replica_count"]==3
    assert r["replica_write_count"]==r["replica_count"]
    assert ops.count("FS_WRITE_REPLACE_BYTES")==r["replica_count"]+1
    assert r["registry_written"] is True and r["history_written"] is True
    assert list(tmp_path.iterdir())==[]
def test_read_helpers_need_no_authority(tmp_path):
    e=DistributedCivilizationalMemory(root=tmp_path); assert isinstance(e.evaluate({"memory_nodes":[]}),dict)
