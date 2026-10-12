import hashlib, tempfile
from pathlib import Path
from acee11_fast_acceptance_suite import context
from ontology.acee_rollback_engine import AceeRollbackEngine

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    root=Path(td)/"root"; inputs=context(root); destination=root/"ontology"/"sample.py"; destination.write_text("unchanged=True\n",encoding="utf-8")
    before=digest(destination); r=AceeRollbackEngine(root=root).step(inputs=inputs,persist=False); after=digest(destination)
    assert before==after and r["rollback_performed"] is False and r["persisted"] is False
print("ACEE11_NON_REGRESSION_OK")
