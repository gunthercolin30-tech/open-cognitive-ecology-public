from pathlib import Path
import json,hashlib,copy
ROOT=Path(__file__).resolve().parents[1]
lock=json.loads((ROOT/"evidence/p154/p154_final_lock.json").read_text()); bad=copy.deepcopy(lock); bad["status"]="UNLOCKED"; expected=bad.pop("lock_sha256"); got=hashlib.sha256(json.dumps(bad,sort_keys=True,separators=(",",":")).encode()).hexdigest(); assert got!=expected
print("P154_FINAL_LOCK_TAMPER_OK")
