from pathlib import Path
import importlib,sys
import pytest
from ontology.metrics_history_recorder import *

class E:
    def __init__(self):self.calls=[]
    def execute(self,*,request,handle,adapter_id,effector_id):
        self.calls.append((request,handle))
        return {"status":"EFFECT_CONFIRMED","operation_id":request.operation_id}

def ctx(mapping):
    return GovernedMetricsFilesystemEffectContext(E(),"R","A","F",mapping)

def test_constructor_no_mutation(tmp_path):
    root=tmp_path/"absent"; MetricsHistoryRecorder(root=root); assert not root.exists()

def test_import_engine_no_mutation(tmp_path,monkeypatch):
    monkeypatch.setattr(Path,"home",classmethod(lambda cls:tmp_path))
    sys.modules.pop("ontology.metrics_history_recorder",None)
    m=importlib.import_module("ontology.metrics_history_recorder")
    assert not (tmp_path/"open-cognitive-ecology"/"metrics").exists()
    assert m.ENGINE is not None

def test_no_context_fail_closed(tmp_path):
    root=tmp_path/"r";root.mkdir();r=MetricsHistoryRecorder(root=root)
    with pytest.raises(RuntimeError,match="context_required"):r.record({"metrics":{"x":1}})
    assert not (root/"metrics").exists()

def test_ticket_queue_supports_repeated_semantic_slot():
    c=ctx({SLOT_ROTATION_MOVE_REPLACE:[object(),object()]})
    from ontology.governed_filesystem_effector import FilesystemEffectRequest
    q1=FilesystemEffectRequest("FS_MOVE_OR_REPLACE","R","a.bak",None,"R","a")
    q2=FilesystemEffectRequest("FS_MOVE_OR_REPLACE","R","b.bak",None,"R","b")
    c.begin_recording()
    c.execute(SLOT_ROTATION_MOVE_REPLACE,q1);c.execute(SLOT_ROTATION_MOVE_REPLACE,q2)
    assert c.remaining(SLOT_ROTATION_MOVE_REPLACE)==0
    with pytest.raises(RuntimeError,match="missing_or_exhausted"):c.execute(SLOT_ROTATION_MOVE_REPLACE,q2)

def test_context_single_recording_use(tmp_path):
    root=tmp_path/"r";(root/"metrics").mkdir(parents=True)
    c=ctx({SLOT_HISTORY_APPEND:object(),SLOT_LEGACY_HISTORY_APPEND:object(),SLOT_STATE_WRITE_REPLACE:object()})
    r=MetricsHistoryRecorder(root=root)
    r.record({"timestamp":"2026-10-02T00:00:00Z","metrics":{"x":1}},effect_context=c)
    with pytest.raises(RuntimeError,match="context_replay_forbidden"):
        r.record({"timestamp":"2026-10-02T00:00:01Z","metrics":{"x":2}},effect_context=c)

def test_unused_conditional_rotation_grants_remain_unconsumed(tmp_path):
    root=tmp_path/"r";(root/"metrics").mkdir(parents=True)
    c=ctx({
        SLOT_HISTORY_APPEND:object(),SLOT_LEGACY_HISTORY_APPEND:object(),
        SLOT_STATE_WRITE_REPLACE:object(),
        SLOT_ROTATION_ARCHIVE_REMOVE:[object(),object()],
        SLOT_ROTATION_MOVE_REPLACE:[object(),object()],
    })
    MetricsHistoryRecorder(root=root).record(
        {"timestamp":"2026-10-02T00:00:00Z","metrics":{"x":1}},effect_context=c)
    assert c.remaining(SLOT_ROTATION_ARCHIVE_REMOVE)==2
    assert c.remaining(SLOT_ROTATION_MOVE_REPLACE)==2

def test_unknown_slot_rejected():
    with pytest.raises(ValueError,match="unknown_effect_slots"):ctx({"ambient":object()})

def test_nominal_existing_parent_dispatch(tmp_path):
    root=tmp_path/"r";(root/"metrics").mkdir(parents=True)
    c=ctx({SLOT_HISTORY_APPEND:object(),SLOT_LEGACY_HISTORY_APPEND:object(),SLOT_STATE_WRITE_REPLACE:object()})
    MetricsHistoryRecorder(root=root).record({"timestamp":"2026-10-02T00:00:00Z","metrics":{"x":1}},effect_context=c)
    assert [x[0].operation_id for x in c.effector.calls]==["FS_APPEND_BYTES","FS_APPEND_BYTES","FS_WRITE_REPLACE_BYTES"]

def test_record_metrics_without_context_is_non_recording(tmp_path,monkeypatch):
    monkeypatch.setattr(Path,"home",classmethod(lambda cls:tmp_path))
    out=record_metrics({"metrics":{"x":1}})
    assert out["recorded"] is False and out["error_count"]==1
    assert not (tmp_path/"open-cognitive-ecology"/"metrics").exists()
