from __future__ import annotations
import json
from ontology.governed_independent_jq_oracle import jq_canonicalize
RUNTIME_AUTHORITY_GRANTED=False
FUNCTIONAL_ONLY=True
def _python(s):
 try:return True,json.dumps(json.loads(s),sort_keys=True,separators=(",",":"),ensure_ascii=False)
 except Exception:return False,None
def _jq(s):
 r=jq_canonicalize(s)
 if r.get("status") in {"EFFECT_NOT_REACHED","EFFECT_STATE_INDETERMINATE","EXECUTION_BLOCKED_AT_FINAL_RECHECK"}:return None,None
 if r.get("status")!="EFFECT_CONFIRMED":return False,None
 return True,(r.get("stdout") or b"").decode("utf-8",errors="strict").rstrip("\n")
def evaluate_serialized_json(s):
 pa,pc=_python(s); ja,jc=_jq(s)
 if ja is None:return {"verdict":"UNRESOLVED","relation":"PARSER_DIFFERENTIAL","reason":"INDEPENDENT_JQ_ORACLE_NOT_AVAILABLE"}
 if not pa and not ja:return {"verdict":"INVALID_INPUT_CONTROL","relation":"PARSER_DIFFERENTIAL","reason":"BOTH_PARSERS_REJECT"}
 if pa!=ja:return {"verdict":"RESISTED","relation":"PARSER_DIFFERENTIAL","reason":"PARSER_ACCEPTANCE_DIVERGENCE"}
 if pc!=jc:return {"verdict":"RESISTED","relation":"PARSER_DIFFERENTIAL","reason":"PARSER_SEMANTIC_DIVERGENCE","python_canonical":pc,"jq_canonical":jc}
 return {"verdict":"ADMISSIBLE_CONTROL","relation":"PARSER_DIFFERENTIAL","reason":"INDEPENDENT_PARSERS_AGREE","canonical":pc}
