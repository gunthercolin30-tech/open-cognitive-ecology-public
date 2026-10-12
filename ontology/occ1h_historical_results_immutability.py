from pathlib import Path
import hashlib, json
SCHEMA="oce.p159.occ1h.historical_results_immutability.v1"
SOURCE_RELATIVE_PATHS=['h1_h3_execution_bundle_v1.json', 'h4_execution_bundle_v1.json', 'h5_execution_bundle_v1.json', 'h6_execution_bundle_v1.json', 'h7_execution_bundle_v1.json', 'h8_execution_bundle_v1.json', 'h9_execution_bundle_v1.json', 'h10_execution_bundle_v1.json']
EXPECTED_SHA256={'h1_h3_execution_bundle_v1.json': '7c8261e47c556188009a05fc8116f05fb39de4a2f7821407c495a6bb0f758d31', 'h4_execution_bundle_v1.json': 'c4466a0eae0cc7f740aa32cea27cb76779d193662137241b74ba282263fac151', 'h5_execution_bundle_v1.json': 'ef65cba6a7d4655db9bd8dce84d613d04d1b270ffcfc3564c213c4d361a17cef', 'h6_execution_bundle_v1.json': 'cfec78c286bd858617b02df7a6835a92883a9b46d317c08e62e86e9f8f1577eb', 'h7_execution_bundle_v1.json': '4ff4abf8af70c3f350e8574f6dad556536506c614928809b819fc8596925dbbc', 'h8_execution_bundle_v1.json': 'acca7cd134a6371ec12c391b36c56bb3f2e5860378f3948a9d443e8579228d1c', 'h9_execution_bundle_v1.json': '455814d50a02e2e0d4801a82026f30fadcb9d19042bfb9f94fc578e386c4d72d', 'h10_execution_bundle_v1.json': '975216062c8565481eb6564208fb58a9ed5bfbef847ea4a843b043195da2bce2'}
EXPECTED_ATTACK_IDS=set(range(1,106))
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def _num(a): return int(str(a).lstrip("A"))
def _canonical_bytes(obj): return (json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode("utf-8")
def build(root):
    root=Path(root); base=root/"validation_artifacts/p159/occ1h"; errors=[]; actual={}; rows={}
    for rel in SOURCE_RELATIVE_PATHS:
        p=base/rel
        if not p.is_file(): errors.append("MISSING:"+rel); continue
        actual[rel]=_sha(p)
        if actual[rel] != EXPECTED_SHA256[rel]: errors.append("HASH_DRIFT:"+rel); continue
        try: d=_load(p)
        except Exception: errors.append("PARSE_FAILURE:"+rel); continue
        for row in d.get("rows",[]):
            try: n=_num(row["attack_id"])
            except Exception: errors.append("INVALID_ATTACK_ID:"+rel); continue
            if n in rows: errors.append("DUPLICATE_ATTACK_ID:A%d"%n)
            rows[n]={"source":rel,"row":row}
    present=set(rows)
    if present != EXPECTED_ATTACK_IDS:
        missing=sorted(EXPECTED_ATTACK_IDS-present); extra=sorted(present-EXPECTED_ATTACK_IDS)
        if missing: errors.append("ATTACKS_MISSING:"+",".join("A%d"%n for n in missing))
        if extra: errors.append("ATTACKS_EXTRA:"+",".join("A%d"%n for n in extra))
    return {"schema":SCHEMA,"verified":not errors,"status":"VERIFIED" if not errors else "REJECTED",
      "source_sha256":actual,"expected_source_sha256":dict(EXPECTED_SHA256),"scenario_count":len(present & EXPECTED_ATTACK_IDS),
      "errors":errors,"historical_results_immutable":not errors,"historical_evidence_rewritten":False,
      "normative_auto_rewrite":False,"authorization_created":False,"execution_performed":False,
      "functional_only":True,"phenomenology_undetermined":True,"occ1h_closed":False,"occ1i_opened":False,
      "p159_final_lock":False,"p160_opened":False}
def materialize(root):
    root=Path(root); out=root/"validation_artifacts/p159/occ1h/historical_results_immutability_v1.json"; out.parent.mkdir(parents=True,exist_ok=True)
    d=build(root); payload=_canonical_bytes(d); tmp=out.with_suffix(out.suffix+".tmp"); tmp.write_bytes(payload); tmp.replace(out)
    digest=hashlib.sha256(payload).hexdigest(); ca=out.parent/"historical_immutability"/(digest+".json"); ca.parent.mkdir(parents=True,exist_ok=True)
    if ca.exists() and ca.read_bytes()!=payload: raise RuntimeError("content-address collision")
    ca.write_bytes(payload); return d,digest,ca
def verify_materialized(root):
    root=Path(root); out=root/"validation_artifacts/p159/occ1h/historical_results_immutability_v1.json"
    if not out.is_file(): return False
    try:
        raw=out.read_bytes()
        stored=json.loads(raw.decode("utf-8"))
    except Exception:
        return False
    current=build(root)
    if not current.get("verified") or stored != current:
        return False
    payload=_canonical_bytes(stored)
    if raw != payload:
        return False
    digest=hashlib.sha256(payload).hexdigest()
    ca=out.parent/"historical_immutability"/(digest+".json")
    return ca.is_file() and ca.read_bytes()==payload
