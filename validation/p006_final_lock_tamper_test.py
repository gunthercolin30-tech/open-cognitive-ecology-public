from pathlib import Path
import hashlib,json,tempfile,shutil
ROOT=Path(__file__).resolve().parents[1]
lock=json.loads((ROOT/"evidence"/"p006"/"p006_final_lock.json").read_text())
rel="validation/p006_go_rethink_stop.py"; expected=lock["protected_hashes"][rel]
with tempfile.TemporaryDirectory() as d:
    q=Path(d)/"x.py"; shutil.copy2(ROOT/rel,q); q.write_text(q.read_text()+"\n# tamper\n")
    assert hashlib.sha256(q.read_bytes()).hexdigest()!=expected
print("P006_FINAL_LOCK_TAMPER_OK")
