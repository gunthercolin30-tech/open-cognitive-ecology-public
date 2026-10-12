import tempfile
from pathlib import Path
from acee11_fast_acceptance_suite import context
from ontology.acee_rollback_engine import AceeRollbackEngine
with tempfile.TemporaryDirectory() as td:
    root=Path(td)/"root"; inputs=context(root); inputs["dry_run"]=False; inputs["execute"]=True
    destination=root/"ontology"/"sample.py"; destination.write_text("broken = True\n",encoding="utf-8")
    r=AceeRollbackEngine(root=root).step(inputs=inputs,persist=False)
    assert r["rollback_status"]=="ACEE_ROLLBACK_ENGINE_READY"
    assert r["rollback_performed"] is True and r["restored_count"]==1
    assert destination.read_text(encoding="utf-8")=="restored = True\n"
    assert (root/"ontology"/"sample.py.bak").read_text(encoding="utf-8")=="restored = True\n"
    assert r["consciousness_proven"] is False and r["functional_conclusion_only"] is True
print("ACEE_ROLLBACK_ENGINE_FINAL_LOCK_OK")
