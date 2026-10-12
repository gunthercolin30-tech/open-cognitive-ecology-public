from pathlib import Path
import pytest
from ontology.acee_prediction_engine import ACEEPredictionEngine
class RecordingContext:
    def __init__(self): self.calls=[]
    def execute_path(self,slot,operation_id,path,payload=None):
        self.calls.append((slot,operation_id,Path(path),payload)); return {"status":"EFFECT_CONFIRMED"}
def test_default_step_is_read_only(tmp_path):
    e=ACEEPredictionEngine(root=tmp_path); r=e.step()
    assert r["persist_requested"] is False
    assert not (tmp_path/"acee_runtime").exists()
def test_persist_without_context_is_rejected(tmp_path):
    e=ACEEPredictionEngine(root=tmp_path)
    with pytest.raises(PermissionError,match="filesystem_effect_context_required"): e.step(persist=True)
    assert not (tmp_path/"acee_runtime").exists()
def test_persist_uses_exact_governed_operations(tmp_path):
    e=ACEEPredictionEngine(root=tmp_path); c=RecordingContext()
    r=e.step(persist=True,filesystem_effect_context=c)
    assert r["persist_requested"] is True
    assert [x[0] for x in c.calls]==["prediction_parent_create","prediction_write_replace"]
    assert [x[1] for x in c.calls]==["FS_CREATE_DIR","FS_WRITE_REPLACE_BYTES"]
    assert c.calls[1][2].name=="latest_prediction.json"
    assert isinstance(c.calls[1][3],bytes)
    assert not (tmp_path/"acee_runtime").exists()
def test_constructor_has_no_filesystem_effect(tmp_path):
    ACEEPredictionEngine(root=tmp_path); assert list(tmp_path.iterdir())==[]
