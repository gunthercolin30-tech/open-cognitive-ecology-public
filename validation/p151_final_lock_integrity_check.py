from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]; d=json.loads((ROOT/"evidence/p151/p151_final_lock.json").read_text()); expected=d.pop("lock_sha256"); assert hashlib.sha256(json.dumps(d,sort_keys=True,separators=(",",":")).encode()).hexdigest()==expected; [(_ for _ in ()).throw(AssertionError(p)) for p,h in d["protected_hashes"].items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]; print("P151_FINAL_LOCK_INTEGRITY_OK")
