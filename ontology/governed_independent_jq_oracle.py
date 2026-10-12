from __future__ import annotations
import os, subprocess
from pathlib import Path
JQ=Path("/usr/bin/jq")
ARGV=("-cS",".")
TIMEOUT_SECONDS=5.0
MAX_STDIN_BYTES=1_048_576
NO_DESCENDANTS=True
READ_ONLY_ORACLE=True
def jq_canonicalize(serialized_json: str):
    if not isinstance(serialized_json,str):
        raise TypeError("serialized_json must be str")
    payload=serialized_json.encode("utf-8")
    if len(payload)>MAX_STDIN_BYTES:
        return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":"oracle_stdin_too_large"}
    if not JQ.is_file() or JQ.is_symlink():
        return {"status":"EFFECT_NOT_REACHED","reason":"independent_jq_oracle_not_available"}
    env={k:v for k in ("PATH","HOME","TMPDIR","LANG","LC_ALL") if (v:=os.environ.get(k)) is not None}
    try:
        cp=subprocess.run([str(JQ),*ARGV],input=payload,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            timeout=TIMEOUT_SECONDS,shell=False,check=False,close_fds=True,env=env,start_new_session=True)
    except subprocess.TimeoutExpired as exc:
        return {"status":"EFFECT_STATE_INDETERMINATE","reason":"oracle_timeout","stdout":exc.stdout or b"","stderr":exc.stderr or b""}
    except Exception:
        return {"status":"EFFECT_STATE_INDETERMINATE","reason":"oracle_transport_failure","stdout":b"","stderr":b""}
    return {"status":"EFFECT_CONFIRMED" if cp.returncode==0 else "EFFECT_FAILED_CONFIRMED",
            "returncode":cp.returncode,"stdout":cp.stdout,"stderr":cp.stderr}
