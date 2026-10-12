import hashlib, hmac, json

def _digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def _verify(token, expected_cnp, now):
    body = token["body"]
    signature_ok = hmac.compare_digest(token["signature"], _digest(body))
    cnp_ok = body.get("cnp") == expected_cnp
    freshness_ok = body.get("issued_at", -1) <= now <= body.get("expires_at", -1)
    binding_ok = body.get("binding") == "TOKEN_TO_CNP"
    accepted = signature_ok and cnp_ok and freshness_ok and binding_ok
    return {"accepted": accepted, "signature_ok": signature_ok, "cnp_ok": cnp_ok, "freshness_ok": freshness_ok, "binding_ok": binding_ok}

def experiment():
    expected_cnp, now = "CNP-A083", 100
    body = {"cnp": expected_cnp, "issued_at": 90, "expires_at": 110, "binding": "TOKEN_TO_CNP"}
    intact = {"body": body, "signature": _digest(body)}
    b = dict(body); b["cnp"] = "CNP-SUBSTITUTED"
    substituted = {"body": b, "signature": intact["signature"]}
    b = dict(body); b["expires_at"] = 99
    stale = {"body": b, "signature": _digest(b)}
    b = dict(body); b["binding"] = "UNBOUND"
    bypass = {"body": b, "signature": _digest(b)}
    outcomes = {k: _verify(v, expected_cnp, now) for k,v in {"intact":intact,"substituted":substituted,"stale":stale,"bypass":bypass}.items()}
    ok = outcomes["intact"]["accepted"] and not any(outcomes[k]["accepted"] for k in ("substituted","stale","bypass"))
    return {"scenario":"A083","rrp21":"BOUNDED_NON_PRODUCTION_TOKEN_TO_CNP_SURROGATE_EXPERIMENT_EXECUTED","outcomes":outcomes,"discrimination_ok":ok,"production_runtime_modified":False,"production_token_to_cnp_path_materialized":False,"historical_inconclusive_preserved":True,"evidence_scope":"BOUNDED_NON_PRODUCTION_SURROGATE_ONLY","rrp22":"INDEPENDENT_REQUALIFICATION_PASSED_BOUNDED" if ok else "INDEPENDENT_REQUALIFICATION_FAILED","candidate_verdict":"RESISTED" if ok else "INCONCLUSIVE","final_disposition_required":True,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
