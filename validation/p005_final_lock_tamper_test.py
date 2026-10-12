from pathlib import Path
import hashlib,json,tempfile,shutil
ROOT=Path(__file__).resolve().parents[1]
lock=json.loads((ROOT/"evidence"/"p005"/"p005_final_lock.json").read_text())
rel="validation/p005_product_market_evidence_ladder.py"; expected=lock["protected_hashes"][rel]
with tempfile.TemporaryDirectory() as d:
    q=Path(d)/"x.py"; shutil.copy2(ROOT/rel,q); q.write_text(q.read_text()+"\n# tamper\n")
    assert hashlib.sha256(q.read_bytes()).hexdigest()!=expected
print("P005_FINAL_LOCK_TAMPER_OK")
