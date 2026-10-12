from pathlib import Path
import json
import pytest
from ontology.civilizational_memory_archive import CivilizationalMemoryArchive
from ontology.embodied_environmental_memory_integration import EmbodiedEnvironmentalMemoryIntegration

class FakeContext:
    def __init__(self): self.calls=[]
    def execute_path(self, slot, operation_id, path, payload=None):
        path=Path(path); self.calls.append((slot,operation_id,str(path)))
        if operation_id=='FS_CREATE_DIR': path.mkdir(parents=True,exist_ok=True)
        elif operation_id=='FS_WRITE_REPLACE_BYTES':
            path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(payload or b'')
        elif operation_id=='FS_APPEND_BYTES':
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('ab') as f: f.write(payload or b'')
        else: raise AssertionError(operation_id)
        return {'status':'EFFECT_CONFIRMED'}

def test_archive_fail_closed_and_counter_transactional(tmp_path):
    a=CivilizationalMemoryArchive(output_dir=tmp_path/'archive')
    with pytest.raises(RuntimeError,match='governed_filesystem_context_required'): a.archive(payload={'x':1})
    assert a.record_counter==0 and not (tmp_path/'archive').exists()

def test_archive_governed_effects(tmp_path):
    c=FakeContext(); a=CivilizationalMemoryArchive(output_dir=tmp_path/'archive')
    r=a.archive(payload={'x':1},filesystem_context=c)
    assert a.record_counter==1 and r['archive_success'] is True
    assert [x[1] for x in c.calls]==['FS_CREATE_DIR','FS_WRITE_REPLACE_BYTES']

def test_g11_persist_false_needs_no_authority(tmp_path):
    e=EmbodiedEnvironmentalMemoryIntegration(root=tmp_path)
    r=e.step({'events':[]},persist=False)
    assert r['persisted'] is False and not (tmp_path/'embodied_environmental_memory').exists()

def test_g11_persist_true_fail_closed(tmp_path):
    e=EmbodiedEnvironmentalMemoryIntegration(root=tmp_path)
    with pytest.raises(RuntimeError,match='governed_filesystem_context_required'): e.step({'events':[]},persist=True)
    assert not (tmp_path/'embodied_environmental_memory').exists()

def test_g11_governed_local_and_archive_effects(tmp_path):
    c=FakeContext(); e=EmbodiedEnvironmentalMemoryIntegration(root=tmp_path)
    event={'events':[{'event_type':'temperature','channel':'sensor','severity':0.7}]}
    r=e.step(event,persist=True,filesystem_context=c)
    assert r['persisted'] is True
    ops=[x[1] for x in c.calls]
    assert ops.count('FS_APPEND_BYTES')==1
    assert ops.count('FS_WRITE_REPLACE_BYTES')==4
    assert any(x[0]=='civilizational_archive_write' for x in c.calls)
