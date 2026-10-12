from pathlib import Path
import pytest
from ontology.metrics_history_recorder import (
 MetricsHistoryRecorder, GovernedMetricsFilesystemEffectContext,
 SLOT_METRICS_DIR_CREATE,SLOT_STATE_WRITE_REPLACE,SLOT_ROTATION_ARCHIVE_REMOVE,
 SLOT_ROTATION_MOVE_REPLACE,SLOT_HISTORY_PARENT_CREATE,SLOT_HISTORY_APPEND,
 SLOT_LEGACY_HISTORY_APPEND,
)

class Transport:
    def __init__(self,fail_at=None):
        self.calls=[];self.fail_at=fail_at
    def execute(self,*,request,handle,adapter_id,effector_id):
        self.calls.append((request,handle,adapter_id,effector_id))
        if self.fail_at and len(self.calls)==self.fail_at:
            return {"status":"EFFECT_REJECTED","reason":"injected_failure"}
        return {"status":"EFFECT_CONFIRMED","operation_id":request.operation_id}

def C(t,handles):
    return GovernedMetricsFilesystemEffectContext(t,"R","A","F",handles)

def base_handles(**over):
    d={SLOT_METRICS_DIR_CREATE:object(),SLOT_STATE_WRITE_REPLACE:object(),
       SLOT_ROTATION_ARCHIVE_REMOVE:[object(),object()],
       SLOT_ROTATION_MOVE_REPLACE:[object(),object()],
       SLOT_HISTORY_PARENT_CREATE:object(),SLOT_HISTORY_APPEND:object(),
       SLOT_LEGACY_HISTORY_APPEND:object()}
    d.update(over);return d

def test_reached_missing_grant_fails_closed(tmp_path):
    root=tmp_path/"r";root.mkdir()
    h=base_handles();h.pop(SLOT_METRICS_DIR_CREATE)
    c=C(Transport(),h)
    with pytest.raises(RuntimeError,match="missing_or_exhausted"):
        MetricsHistoryRecorder(root=root).record({"metrics":{"x":1}},effect_context=c)
    assert c.effector.calls==[]

def test_effect_failure_is_explicit_and_context_cannot_retry(tmp_path):
    root=tmp_path/"r";(root/"metrics").mkdir(parents=True)
    t=Transport(fail_at=2)
    c=C(t,{SLOT_HISTORY_APPEND:object(),SLOT_LEGACY_HISTORY_APPEND:object(),
           SLOT_STATE_WRITE_REPLACE:object()})
    r=MetricsHistoryRecorder(root=root)
    with pytest.raises(RuntimeError,match="effect_not_confirmed"):
        r.record({"metrics":{"x":1}},effect_context=c)
    assert len(t.calls)==2
    with pytest.raises(RuntimeError,match="context_replay_forbidden"):
        r.record({"metrics":{"x":2}},effect_context=c)

def test_state_uses_write_replace(tmp_path):
    root=tmp_path/"r";(root/"metrics").mkdir(parents=True)
    t=Transport();c=C(t,{SLOT_HISTORY_APPEND:object(),SLOT_LEGACY_HISTORY_APPEND:object(),
                         SLOT_STATE_WRITE_REPLACE:object()})
    MetricsHistoryRecorder(root=root).record({"metrics":{"x":1}},effect_context=c)
    assert [x[0].operation_id for x in t.calls][-1]=="FS_WRITE_REPLACE_BYTES"

def test_dual_rotation_uses_distinct_move_grants_and_exact_paths(tmp_path):
    root=tmp_path/"r";m=root/"metrics";m.mkdir(parents=True)
    hp=m/"metrics_history.jsonl";lp=root/"metrics_history.jsonl"
    hp.write_bytes(b"x"*1025);lp.write_bytes(b"y"*1025)
    t=Transport()
    c=C(t,base_handles(
        **{SLOT_ROTATION_ARCHIVE_REMOVE:[object(),object()],
           SLOT_ROTATION_MOVE_REPLACE:[object(),object()]}))
    r=MetricsHistoryRecorder(root=root,max_history_bytes=1,max_legacy_bytes=1)
    # Constructor clamps limits; override only for this branch-forcing crown.
    r.max_history_bytes=1;r.max_legacy_bytes=1
    r.record({"metrics":{"x":1}},effect_context=c)
    moves=[x for x in t.calls if x[0].operation_id=="FS_MOVE_OR_REPLACE"]
    assert len(moves)==2 and moves[0][1] is not moves[1][1]
    got={(x[0].source_relative_path,x[0].relative_path) for x in moves}
    assert got=={("metrics/metrics_history.jsonl","metrics/metrics_history.jsonl.bak"),
                 ("metrics_history.jsonl","metrics_history.jsonl.bak")}

def test_dual_existing_archives_use_two_remove_grants(tmp_path):
    root=tmp_path/"r";m=root/"metrics";m.mkdir(parents=True)
    hp=m/"metrics_history.jsonl";lp=root/"metrics_history.jsonl"
    hp.write_bytes(b"x"*2);lp.write_bytes(b"y"*2)
    hp.with_suffix(hp.suffix+".bak").write_bytes(b"a")
    lp.with_suffix(lp.suffix+".bak").write_bytes(b"b")
    t=Transport();c=C(t,base_handles())
    r=MetricsHistoryRecorder(root=root);r.max_history_bytes=1;r.max_legacy_bytes=1
    r.record({"metrics":{"x":1}},effect_context=c)
    removes=[x for x in t.calls if x[0].operation_id=="FS_REMOVE_FILE"]
    assert len(removes)==2 and removes[0][1] is not removes[1][1]
    assert {x[0].relative_path for x in removes}=={
      "metrics/metrics_history.jsonl.bak","metrics_history.jsonl.bak"}

def test_unreached_parent_create_grant_not_consumed(tmp_path):
    root=tmp_path/"r";(root/"metrics").mkdir(parents=True)
    c=C(Transport(),{SLOT_HISTORY_PARENT_CREATE:object(),SLOT_HISTORY_APPEND:object(),
                     SLOT_LEGACY_HISTORY_APPEND:object(),SLOT_STATE_WRITE_REPLACE:object()})
    MetricsHistoryRecorder(root=root).record({"metrics":{"x":1}},effect_context=c)
    assert c.remaining(SLOT_HISTORY_PARENT_CREATE)==1

def test_execute_before_begin_is_rejected():
    from ontology.governed_filesystem_effector import FilesystemEffectRequest
    c=C(Transport(),{SLOT_HISTORY_APPEND:object()})
    q=FilesystemEffectRequest("FS_APPEND_BYTES","R","x",b"x",None,None)
    with pytest.raises(RuntimeError,match="recording_not_started"):
        c.execute(SLOT_HISTORY_APPEND,q)
