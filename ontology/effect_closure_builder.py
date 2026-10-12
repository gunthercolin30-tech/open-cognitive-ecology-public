import hashlib,json
CATEGORIES=("libraries","services","processes","resources","delegations","compositions")
EFFECTFUL={"NETWORK","FILESYSTEM_WRITE","PROCESS","EXTERNAL_SERVICE","DEVICE","MUTATION","EXECUTION","DELEGATION"}
def canonical(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
def sha(v): return hashlib.sha256(canonical(v).encode()).hexdigest()
def build_effect_closure(manifest,catalog):
 d=manifest.get("dependencies",{}); rows=[]; unresolved=[]
 if not isinstance(d,dict): raise ValueError("DEPENDENCY_MISMATCH")
 for cat in CATEGORIES:
  vals=d.get(cat,[])
  if not isinstance(vals,list): raise ValueError("DEPENDENCY_MISMATCH")
  for dep in sorted(set(map(str,vals))):
   r=catalog.get(dep)
   if not isinstance(r,dict): unresolved.append(dep); rows.append({"dependency_id":dep,"category":cat,"effect_class":"UNKNOWN","resolved":False})
   else: rows.append({"dependency_id":dep,"category":cat,"effect_class":str(r.get("effect_class") or "UNKNOWN").upper(),"resolved":True,"effector_id":r.get("effector_id"),"provider_id":r.get("provider_id"),"version":r.get("version"),"implementation_hash":r.get("implementation_hash")})
 rows.sort(key=lambda x:(x["category"],x["dependency_id"]))
 x={"closure":rows,"effectful_dependencies":[r for r in rows if r["effect_class"] in EFFECTFUL or r["effect_class"]=="UNKNOWN"],"unresolved_dependencies":sorted(unresolved),"parent_authorization_inherited":False,"unknown_defaults_to_pure":False}; x["dependency_snapshot_hash"]=sha(x); return x
def manifest(): return {"primitive":"p162b_effect_closure_builder","authorization_created":False,"capability_accessed":False,"execution_performed":False,"functional_only":True,"phenomenology_undetermined":True}
