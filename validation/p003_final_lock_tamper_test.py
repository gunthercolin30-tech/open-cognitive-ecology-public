from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]; d=json.loads((ROOT/"evidence"/"p003"/"p003_final_lock.json").read_text()); rel=sorted(d["protected_hashes"])[0]; b=(ROOT/rel).read_bytes()
assert hashlib.sha256(b+b"tamper").hexdigest()!=d["protected_hashes"][rel]; assert hashlib.sha256(b).hexdigest()==d["protected_hashes"][rel]
print("P003_FINAL_LOCK_TAMPER_OK")
