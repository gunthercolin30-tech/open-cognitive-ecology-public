from pathlib import Path
import hashlib, json, os, tempfile
from ontology import occ_governed_version_binding_resolver as resolver

SCHEMA="oce.p159.occ1a.governed_institutional_declaration_binding.v1"
DECL_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json")
BIND_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_governed_institutional_declaration_binding.json")
SYMBOLIC_CONSTITUTION="CURRENT_GOVERNED_CONSTITUTION"
SYMBOLIC_GOVERNANCE="CURRENT_GOVERNED_GOVERNANCE"

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def build(root=None):
    r=_root(root); dp=r/DECL_REL
    if not dp.is_file(): raise FileNotFoundError("DECLARATION_MISSING")
    d=_load(dp); before=_sha(dp); rv=resolver.resolve(r)
    blockers=[]
    if d.get("status")!="READY_FOR_INDEPENDENT_VERIFICATION": blockers.append("DECLARATION_NOT_READY")
    if d.get("human_confirmed") is not True: blockers.append("DECLARATION_NOT_HUMAN_CONFIRMED")
    if d.get("constitution_version")!=SYMBOLIC_CONSTITUTION: blockers.append("DECLARATION_CONSTITUTION_ALIAS_UNEXPECTED")
    if d.get("governance_version")!=SYMBOLIC_GOVERNANCE: blockers.append("DECLARATION_GOVERNANCE_ALIAS_UNEXPECTED")
    if rv.get("status")!="GOVERNED_VERSION_BINDINGS_RESOLVED": blockers.append("GOVERNED_VERSION_BINDINGS_NOT_RESOLVED")
    cv=rv.get("constitution_version"); gv=rv.get("governance_version"); ident=rv.get("p110_final_lock_identity_sha256")
    if not cv or not gv or not ident: blockers.append("RESOLVED_BINDING_FIELDS_MISSING")
    blockers=sorted(set(blockers))
    return {
      "schema":SCHEMA,
      "status":"GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_VERIFIED" if not blockers else "GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_BLOCKED",
      "blockers":blockers,
      "declaration_path":str(DECL_REL),
      "declaration_sha256":before,
      "declaration_schema":d.get("schema"),
      "declaration_status":d.get("status"),
      "human_confirmed":d.get("human_confirmed") is True,
      "source_constitution_alias":d.get("constitution_version"),
      "source_governance_alias":d.get("governance_version"),
      "constitution_version":cv if not blockers else None,
      "governance_version":gv if not blockers else None,
      "p110_final_lock_identity_sha256":ident if not blockers else None,
      "resolver_schema":rv.get("schema"),
      "resolver_status":rv.get("status"),
      "resolver_final_lock_path":rv.get("p110_final_lock_path"),
      "resolver_postlock_path":rv.get("p110_postlock_path"),
      "declaration_modified":False,
      "normative_effect":False,
      "institutional_authority_established":False,
      "authority_activated":False,
      "adoption_performed":False,
      "execution_performed":False,
      "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
      "functional_only":True,"phenomenology_undetermined":True}

def materialize(root=None):
    r=_root(root); dp=r/DECL_REL; bp=r/BIND_REL
    before=_sha(dp); x=build(r)
    if x["status"]!="GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_VERIFIED":
        return x
    bp.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode("utf-8")
    fd,tmp=tempfile.mkstemp(prefix=bp.name+".",dir=str(bp.parent))
    try:
        with os.fdopen(fd,"wb") as f:
            f.write(raw); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,bp)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    after=_sha(dp)
    if before!=after:
        raise RuntimeError("DECLARATION_MUTATED_DURING_BINDING")
    return dict(x,binding_path=str(BIND_REL),binding_sha256=hashlib.sha256(raw).hexdigest(),declaration_sha256_after=after)

def verify_materialized(root=None):
    r=_root(root); bp=r/BIND_REL; dp=r/DECL_REL
    if not bp.is_file(): return {"status":"BINDING_MISSING","blockers":["BINDING_MISSING"]}
    stored=_load(bp); fresh=build(r); blockers=[]
    if stored.get("schema")!=SCHEMA: blockers.append("BINDING_SCHEMA_INVALID")
    if stored.get("status")!="GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_VERIFIED": blockers.append("BINDING_STATUS_INVALID")
    if fresh.get("status")!="GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_VERIFIED": blockers.extend(fresh.get("blockers",[]))
    for k in ("declaration_sha256","constitution_version","governance_version","p110_final_lock_identity_sha256","resolver_schema","resolver_status"):
        if stored.get(k)!=fresh.get(k): blockers.append("BINDING_DRIFT_"+k.upper())
    if stored.get("declaration_sha256")!=_sha(dp): blockers.append("DECLARATION_HASH_DRIFT")
    for k in ("declaration_modified","normative_effect","institutional_authority_established","authority_activated","adoption_performed","execution_performed","occ1a_closed","occ1b_opened","p160_opened"):
        if stored.get(k) is not False: blockers.append("FORBIDDEN_EFFECT_"+k.upper())
    blockers=sorted(set(blockers))
    return {"status":"GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_VERIFIED" if not blockers else "GOVERNED_INSTITUTIONAL_DECLARATION_BINDING_BLOCKED",
            "blockers":blockers,"binding":stored,"fresh":fresh}
