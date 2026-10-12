from pathlib import Path
import hashlib,json,tempfile,shutil
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/"evidence"/"p004"/"p004_final_lock.json").read_text(encoding="utf-8"))
rel=sorted(d["protected_hashes"])[0]; src=ROOT/rel
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/src.name; shutil.copy2(src,p); p.write_bytes(p.read_bytes()+b"\n#tamper\n")
 assert hashlib.sha256(p.read_bytes()).hexdigest()!=d["protected_hashes"][rel]
 assert hashlib.sha256(src.read_bytes()).hexdigest()==d["protected_hashes"][rel]
print("P004_FINAL_LOCK_TAMPER_OK")
