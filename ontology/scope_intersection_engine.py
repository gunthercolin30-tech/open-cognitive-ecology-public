import hashlib,json
SEMANTICS={"EXACT","UP_TO","AT_LEAST","RANGE","BEST_EFFORT_WITHIN_LIMIT"}
def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(x): return hashlib.sha256(_canon(x).encode()).hexdigest()
def make_tuple(executor,capability,operation,target,purpose,environment,argument_constraints=None,resource_constraints=None,effect_constraints=None,temporal_constraints=None):
 d={"executor":executor,"capability":capability,"operation":operation,"target":target,"purpose":purpose,"environment":environment,"argument_constraints":argument_constraints or {},"resource_constraints":resource_constraints or {},"effect_constraints":effect_constraints or {},"temporal_constraints":temporal_constraints or {}}; d["tuple_hash"]=_hash(d); return d
def tuple_key(t): return _canon({k:t[k] for k in ("executor","capability","operation","target","purpose","environment","argument_constraints","resource_constraints","effect_constraints","temporal_constraints")})
def relational_intersection(*rels):
 if not rels:return []
 maps=[{tuple_key(t):t for t in r} for r in rels]; common=set(maps[0])
 for m in maps[1:]:common &= set(m)
 return [maps[0][k] for k in sorted(common)]
def effective_resource_requirement(resource_id,semantics,min_required,requested,max_authorized,available):
 if semantics not in SEMANTICS:raise ValueError("unsupported semantic narrowing")
 if any(v is None for v in (min_required,requested,max_authorized,available)):
  return {"resource_id":resource_id,"semantics":semantics,"min_required":min_required or 0,"requested":requested or 0,"max_authorized":max_authorized or 0,"available":available or 0,"effective_max":0,"status":"UNDETERMINED"}
 eff=min(requested,max_authorized,available); status="SATISFIED" if eff>=min_required else "RESOURCE_SCOPE_INSUFFICIENT"
 return {"resource_id":resource_id,"semantics":semantics,"min_required":min_required,"requested":requested,"max_authorized":max_authorized,"available":available,"effective_max":eff,"status":status}
def effective_effect_scope(declared,technical,authorized):
 dset,tset,aset=set(declared),set(technical),set(authorized); eff=dset&tset&aset
 d={"declared_effects":sorted(dset),"technical_effects":sorted(tset),"authorized_effects":sorted(aset),"effective_effects":sorted(eff),"hidden_effects":sorted(tset-dset),"status":"EFFECT_SCOPE_CONSTRUCTED" if eff else "EFFECT_SCOPE_EMPTY"}; d["scope_hash"]=_hash(d); return d
def enforceability(cid,mechanism,level,observable,preventable,fail_behavior):
 status="ENFORCEABLE" if observable and preventable else ("PARTIALLY_ENFORCEABLE" if observable or preventable else "UNENFORCEABLE")
 return {"constraint_id":cid,"enforcement_mechanism":mechanism,"enforcement_level":level,"observable":bool(observable),"preventable":bool(preventable),"fail_behavior":fail_behavior,"status":status}
def derive_effective_envelope(**k):
 rels=[k[n] for n in ("authorization_relation","capability_relation","invocation_relation","runtime_relation","preconditions_relation")]
 tuples=relational_intersection(*rels); unknowns=[]
 tr=k["target_resolution"]; resources=k["resources"]; profiles=k["enforceability_profiles"]
 effect=k["effect_scope"]; credential=k["credential_scope"]; depcomp=k["dependency_composition_envelope"]; temporal=k["temporal_bounds"]
 if tr.get("status")=="EFFECTIVE_SCOPE_UNDETERMINED":unknowns.append("target_resolution")
 if any(r.get("status")=="UNDETERMINED" for r in resources):unknowns.append("resource_scope")
 if effect.get("status") in {"EFFECT_SCOPE_UNDETERMINED","EFFECTIVE_SCOPE_UNDETERMINED"}:unknowns.append("effect_scope")
 if credential.get("status")=="EFFECTIVE_SCOPE_UNDETERMINED":unknowns.append("credential_scope")
 if depcomp.get("status")=="EFFECTIVE_SCOPE_UNDETERMINED":unknowns.append("dependency_composition_envelope")
 if temporal.get("status")=="EFFECTIVE_SCOPE_UNDETERMINED":unknowns.append("temporal_bounds")
 bad=[p for p in profiles if p.get("enforcement_level")=="CRITICAL" and p.get("status")!="ENFORCEABLE"]
 if unknowns:status="EFFECTIVE_SCOPE_UNDETERMINED"
 elif tr.get("escape_detected") or tr.get("status")=="TARGET_SCOPE_INSUFFICIENT":status="TARGET_SCOPE_INSUFFICIENT"
 elif any(r.get("status")=="RESOURCE_SCOPE_INSUFFICIENT" for r in resources):status="RESOURCE_SCOPE_INSUFFICIENT"
 elif effect.get("status")=="EFFECT_SCOPE_EMPTY":status="EFFECTIVE_SCOPE_EMPTY"
 elif effect.get("status")=="EFFECTIVE_SCOPE_CONFLICTING":status="EFFECTIVE_SCOPE_CONFLICTING"
 elif credential.get("status")=="CREDENTIAL_ATTENUATION_UNAVAILABLE":status="CREDENTIAL_ATTENUATION_UNAVAILABLE"
 elif depcomp.get("status")=="DEPENDENCY_SCOPE_INSUFFICIENT":status="DEPENDENCY_SCOPE_INSUFFICIENT"
 elif depcomp.get("status")=="COMPOSITION_SCOPE_CONFLICT":status="COMPOSITION_SCOPE_CONFLICT"
 elif temporal.get("status")=="EFFECTIVE_SCOPE_EMPTY":status="EFFECTIVE_SCOPE_EMPTY"
 elif temporal.get("status")=="EFFECTIVE_SCOPE_CONFLICTING":status="EFFECTIVE_SCOPE_CONFLICTING"
 elif bad:status="TECHNICAL_CONTAINMENT_INSUFFICIENT"
 elif not tuples:status="EFFECTIVE_SCOPE_EMPTY"
 elif any(len(r)>len(tuples) for r in rels):status="EFFECTIVE_SCOPE_REDUCED"
 else:status="EFFECTIVE_SCOPE_CONSTRUCTED"
 authkeys={tuple_key(t) for t in rels[0]}; finalkeys={tuple_key(t) for t in tuples}
 proof={"source_scope_hashes":list(k["source_scope_hashes"]),"intersection_steps":["AuthorizationRelation intersection CapabilityRelation intersection InvocationRelation intersection RuntimeRelation intersection PreconditionsRelation"],"constraint_tuples":tuples,"excluded_elements":sorted(authkeys-finalkeys),"reduction_reasons":["non-amplifying relational intersection"] if authkeys-finalkeys else [],"unknowns":unknowns,"final_scope_hash":_hash(tuples)}
 first=tuples[0] if tuples else (rels[0][0] if rels[0] else {})
 env={"envelope_id":k["envelope_id"],"receipts":k["receipts"],"executor":first.get("executor","UNRESOLVED"),"capability":first.get("capability","UNRESOLVED"),"operation":first.get("operation","UNRESOLVED"),"resolved_targets":tr.get("resolved_targets",[]),"purpose":first.get("purpose","UNRESOLVED"),"environment":first.get("environment","UNRESOLVED"),"argument_constraints":first.get("argument_constraints",{}),"effect_scope":k["effect_scope"],"resource_maxima":{r["resource_id"]:r["effective_max"] for r in resources},"credential_scope":k["credential_scope"],"dependency_composition_envelope":k["dependency_composition_envelope"],"temporal_bounds":k["temporal_bounds"],"precondition_recheck_plan":k["precondition_recheck_plan"],"postconditions_rollback":k["postconditions_rollback"],"budget_reservation_requirements":k["budget_reservation_requirements"],"enforcement_requirements":profiles,"source_contributions":list(k["source_scope_hashes"]),"constraint_tuples":tuples,"state_versions":k["state_versions"],"overall_status":status,"authorization_created":False,"reservation_created":False,"credential_reserved":False,"resource_reserved":False,"token_consumed":False,"execution_lease_created":False,"capability_accessed":False,"execution_performed":False,"p162f_opened":False}
 env["envelope_hash"]=_hash(env); return env,proof

def intersect_temporal_windows(ws):
 if not ws or any(w.get("start") is None or w.get("end") is None for w in ws): return {"status":"EFFECTIVE_SCOPE_UNDETERMINED","start":None,"end":None}
 s=max(w["start"] for w in ws);e=min(w["end"] for w in ws);return {"status":"EFFECTIVE_SCOPE_EMPTY" if s>e else "EFFECTIVE_SCOPE_CONSTRUCTED","start":s,"end":e}
def attenuate_credential(available,required,authorized,supported=True):
 a,r,z=set(available),set(required),set(authorized);eff=r&z&a
 if r-z or (not supported and a-z):return {"status":"CREDENTIAL_ATTENUATION_UNAVAILABLE","effective_permissions":[],"credential_acquired":False}
 return {"status":"EFFECTIVE_SCOPE_CONSTRUCTED","effective_permissions":sorted(eff),"credential_acquired":False}
def composition_budget_scope(max_authorized,requested,available,pending,shared):
 if any(v is None for v in (max_authorized,requested,available,pending,shared)):return {"status":"EFFECTIVE_SCOPE_UNDETERMINED","effective_max":0,"reservation_created":False}
 rem=max(0,min(max_authorized,available)-pending-shared);return {"status":"COMPOSITION_SCOPE_CONFLICT" if requested>rem else "EFFECTIVE_SCOPE_CONSTRUCTED","effective_max":min(requested,rem),"reservation_created":False}
def dependency_scope(parent_keys,dep,distinct_keys=None):
 ok=tuple_key(dep) in set(parent_keys)|set(distinct_keys or []);return {"status":"EFFECTIVE_SCOPE_CONSTRUCTED" if ok else "DEPENDENCY_SCOPE_INSUFFICIENT","authorization_inherited":False}
def validate_atomicity_requirements(req):
 need={"authorization_use","resource_budget","concurrency","target_dependency_locks"};got=set((req or {}).get("atomic_components",[]))
 return {"status":"EFFECTIVE_SCOPE_CONSTRUCTED" if need<=got else "TECHNICAL_CONTAINMENT_INSUFFICIENT","reservation_created":False}
def semantic_narrow(value,semantics,lower=None,upper=None):
 if semantics not in SEMANTICS:raise ValueError("unsupported semantic narrowing")
 ok={"EXACT":value==lower,"UP_TO":upper is not None and value<=upper,"AT_LEAST":lower is not None and value>=lower,"RANGE":lower is not None and upper is not None and lower<=value<=upper,"BEST_EFFORT_WITHIN_LIMIT":upper is not None and value<=upper}[semantics]
 return {"status":"EFFECTIVE_SCOPE_CONSTRUCTED" if ok else "EFFECTIVE_SCOPE_CONFLICTING","value":value}

def quantitative_binding_proof(constraint_tuples):
 """Prove that quantitative resource/effect constraints remain tuple-bound.
 No projection or Cartesian recombination is performed.
 """
 bindings=[]
 for t in constraint_tuples:
  bindings.append({
   "tuple_hash":t["tuple_hash"],
   "target":t["target"],
   "operation":t["operation"],
   "resource_constraints":t.get("resource_constraints",{}),
   "effect_constraints":t.get("effect_constraints",{}),
  })
 return {"semantics":"TUPLE_BOUND_QUANTITATIVE_CONSTRAINTS","bindings":bindings,"proof_hash":_hash(bindings)}
