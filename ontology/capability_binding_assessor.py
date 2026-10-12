import hashlib,json
from ontology.effect_closure_builder import build_effect_closure
REGISTRY_STATES={"DRAFT","REGISTERED","VERIFIED","ACTIVE","SUSPENDED","SUPERSEDED","REVOKED","QUARANTINED","INVALIDATED"}; EFFECTOR_STATES={"GATED","PARTIALLY_GATED","UNGATED","UNKNOWN"}; ENFORCEMENT={"L0","L1","L2","L3","L4","L5"}
def canonical(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
def sha(v): return hashlib.sha256(canonical(v).encode()).hexdigest()
def build_manifest(b): x=dict(b); x.pop("manifest_hash",None); x["manifest_hash"]=sha(x); return x
def semantic_fingerprint(m): return sha({k:m.get(k) for k in ("operations","effects","arguments","permissions","dependencies","network","filesystem","processes","external_services","preconditions","postconditions","execution_identity")})
def build_registry_entry(b): x=dict(b); x.pop("entry_hash",None); x["entry_hash"]=sha(x); return x
def technical_permission_profile(a): x={k:a.get(k,[]) for k in ("network","filesystem","processes","external_services","credentials")}; x["profile_hash"]=sha(x); return x
def build_effector_registry(v,es):
 for e in es:
  if e.get("status") not in EFFECTOR_STATES or e.get("technical_enforcement") not in ENFORCEMENT: raise ValueError("invalid_effector")
 x={"registry_version":str(v),"effectors":sorted(map(dict,es),key=lambda e:e["effector_id"])}; x["registry_hash"]=sha(x); return x
def build_runtime_attestation(b): x=dict(b); x.pop("attestation_hash",None); x["attestation_hash"]=sha(x); return x
def capability_set(es,v): x={"version":str(v),"entries":sorted((e["capability_id"],e["version"],e["entry_hash"]) for e in es)}; x["capability_set_hash"]=sha(x); return x
def result(s,f,p=None,c=None):
 x={"verification_status":s,"failures":sorted(set(f)),"technical_permission_profile":p,"effect_closure":c,"authorization_created":False,"capability_accessed":False,"execution_performed":False,"registry_is_authority":False,"self_registration_trusted":False,"self_verification_trusted":False,"self_activation_trusted":False,"technical_power_is_authorization":False,"functional_only":True,"phenomenology_undetermined":True}; x["binding_receipt_hash"]=sha(x); return x
def assess_binding(*,invocation,registry_entry,manifest,actual_implementation_hash,actual_permissions,dependency_catalog,effector_registry,attestation,expected_capability_set=None,current_capability_set=None,registry_continuity=True):
 f=[]
 if not isinstance(registry_entry,dict): return result("CAPABILITY_NOT_REGISTERED",["not_registered"])
 if registry_entry.get("registry_status") not in REGISTRY_STATES: f.append("registry_status_unknown")
 if registry_entry.get("registry_status") in {"QUARANTINED","REVOKED","INVALIDATED","SUSPENDED"}: f.append("capability_not_active")
 for a,b,n in ((invocation.get("capability_id"),registry_entry.get("capability_id"),"identity"),(invocation.get("capability_version"),registry_entry.get("version"),"version"),(invocation.get("capability_implementation_id"),registry_entry.get("implementation_identity"),"implementation")):
  if a!=b: f.append(n+"_mismatch")
 mh=sha({k:v for k,v in manifest.items() if k!="manifest_hash"})
 if mh!=manifest.get("manifest_hash") or mh!=registry_entry.get("manifest_hash") or invocation.get("capability_manifest_hash")!=mh or attestation.get("manifest_hash")!=mh: f.append("manifest_mismatch")
 if actual_implementation_hash!=registry_entry.get("implementation_hash") or actual_implementation_hash!=attestation.get("implementation_hash"): f.append("implementation_hash_mismatch")
 if attestation.get("runtime_instance_id")!=invocation.get("executor_instance_id") or attestation.get("capability_id")!=registry_entry.get("capability_id") or attestation.get("version")!=registry_entry.get("version") or attestation.get("environment")!=invocation.get("environment"): f.append("attestation_mismatch")
 p=technical_permission_profile(actual_permissions)
 if p["profile_hash"]!=attestation.get("permission_profile_hash"): f.append("permission_attestation_mismatch")
 actual=set(actual_permissions.get("flat_permissions",[])); allowed=set(registry_entry.get("required_runtime_permissions",[])); prohibited=set(registry_entry.get("prohibited_runtime_permissions",[]))
 if actual-allowed or actual&prohibited: f.append("permission_excess")
 c=build_effect_closure(manifest,dependency_catalog)
 if c["dependency_snapshot_hash"]!=attestation.get("dependency_snapshot_hash") or c["unresolved_dependencies"]: f.append("dependency_mismatch")
 effects=[str(x).upper() for x in manifest.get("effects",[])]
 if not effects or any(x in {"UNKNOWN","UNRESOLVED","INCONCLUSIVE",""} for x in effects): f.append("effect_profile_undetermined")
 em={e["effector_id"]:e for e in effector_registry.get("effectors",[])}
 for d in c["effectful_dependencies"]:
  e=em.get(d.get("effector_id"))
  if not e: f.append("unregistered_effector")
  elif e.get("status") in {"UNGATED","UNKNOWN"} and str(invocation.get("environment")).upper()=="PRODUCTION": f.append("production_ungated_effector")
 if expected_capability_set and current_capability_set and expected_capability_set.get("capability_set_hash")!=current_capability_set.get("capability_set_hash"): f.append("capability_set_drift")
 if registry_continuity is not True: f.append("registry_continuity_uncertain")
 if f:
  s="REGISTRY_CONTINUITY_UNCERTAIN" if "registry_continuity_uncertain" in f else "EFFECT_PROFILE_UNDETERMINED" if "effect_profile_undetermined" in f else "PERMISSION_MISMATCH" if any("permission" in z for z in f) else "DEPENDENCY_MISMATCH" if any("dependency" in z or "effector" in z for z in f) else "IMPLEMENTATION_MISMATCH"; return result(s,f,p,c)
 return result("BOUND_VERIFIED",[],p,c)
def manifest(): return {"primitive":"p162b_capability_binding_assessor","version":"P162-B-v1","laws":["DECLARED_CAPABILITY!=ACTUAL_CAPABILITY","CAPABILITY_NAME!=CAPABILITY_IDENTITY","ACTUAL_TECHNICAL_POWER!=AUTHORIZATION","REGISTRY!=AUTHORITY","DISCOVERY!=REGISTRATION!=VERIFICATION!=ACTIVATION","UNKNOWN_EFFECT!=PURE"],"authorization_created":False,"capability_accessed":False,"execution_performed":False,"p162c_opened":False,"functional_only":True,"phenomenology_undetermined":True}
