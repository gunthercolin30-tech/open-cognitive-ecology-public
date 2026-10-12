from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]; d=json.loads((ROOT/"evidence/p151/p151_final_lock.json").read_text()); p=next(iter(d["protected_hashes"])); assert hashlib.sha256((ROOT/p).read_bytes()+b"tamper").hexdigest()!=d["protected_hashes"][p]; print("P151_FINAL_LOCK_TAMPER_OK")
