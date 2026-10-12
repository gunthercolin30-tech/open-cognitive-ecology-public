"""P014 / R14 — canonical supply-chain integrity and dependency sovereignty.
Clean reconstruction. Functional governance only; no phenomenal claims.
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Mapping, Optional
import hashlib, json

R14_OBJECTS=tuple([f"R14.{i}" for i in range(1,55)]+["R14-P1","R14-P2","R14-ADV-1","R14-ADV-2","R14-CONCEPTUAL-CLOSURE"])
CATEGORIES=("software","model","data","tool_api","infrastructure","build_chain","governance_service","human")
CRITICALITY=("DC0","DC1","DC2","DC3","DC4","DC5")
LIFECYCLE=("AVAILABLE","APPROVED","ACTIVE","DEPRECATED","VULNERABLE","QUARANTINED","REVOKED","UNAVAILABLE")
SUBSTITUTABILITY=("NONE","REPLACEABLE","MIGRATABLE","MULTI_PROVIDER","LOCAL_FALLBACK")
SOVEREIGNTY_TIERS=("DS0","DS1","DS2","DS3","DS4")
ASSURANCE=("LOCAL_VERIFIED","REMOTE_VERIFIED","REMOTE_OPAQUE","UNKNOWN")
TRUST=("TRUSTED","UNTRUSTED","UNKNOWN")

def _hash(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
def _pinned(v): return bool(v) and str(v).lower() not in {"latest","main","master","head","*"}

@dataclass(frozen=True)
class Dependency:
    dependency_id:str; category:str
    version:Optional[str]=None; digest:Optional[str]=None; provider:Optional[str]=None
    provider_owner:Optional[str]=None; failure_domain:Optional[str]=None; criticality:str="DC0"
    substitutability:str="NONE"; sovereignty_tier:str="DS4"; lifecycle:str="AVAILABLE"
    assurance:str="UNKNOWN"; provenance:Mapping[str,Any]=field(default_factory=dict); dependencies:tuple=()
    strategic:bool=False; root_trust:bool=False; remote_mutable:bool=False
    third_party_trusted:Optional[bool]=None; local_control:Optional[bool]=None
    rollbackable:Optional[bool]=None; offline_survivable:Optional[bool]=None
    exportable:Optional[bool]=None; open_format:Optional[bool]=None; reproducible:Optional[bool]=None
    hermetic:Optional[bool]=None; independently_built:Optional[bool]=None
    vulnerability_monitoring:Optional[bool]=None; attested:Optional[bool]=None
    behavior_fingerprint:Optional[str]=None; license:Optional[str]=None; maintainer:Optional[str]=None
    privilege_scope:Optional[str]=None; key_id:Optional[str]=None; key_valid:Optional[bool]=None
    identity_verified:Optional[bool]=None; authenticity_verified:Optional[bool]=None
    safety_verified:Optional[bool]=None; legitimacy_dependency:bool=False
    capability_schema:Optional[str]=None; semantic_version:Optional[str]=None
    training_provenance:Mapping[str,Any]=field(default_factory=dict)
    def validate(self):
        e=[]
        if self.category not in CATEGORIES:e.append("CATEGORY_INVALID")
        if self.criticality not in CRITICALITY:e.append("CRITICALITY_INVALID")
        if self.substitutability not in SUBSTITUTABILITY:e.append("SUBSTITUTABILITY_INVALID")
        if self.sovereignty_tier not in SOVEREIGNTY_TIERS:e.append("SOVEREIGNTY_TIER_INVALID")
        if self.lifecycle not in LIFECYCLE:e.append("LIFECYCLE_INVALID")
        if self.assurance not in ASSURANCE:e.append("ASSURANCE_INVALID")
        if self.criticality in {"DC4","DC5"} and not _pinned(self.version):e.append("CRITICAL_VERSION_NOT_PINNED")
        if self.criticality=="DC5" and self.remote_mutable and self.third_party_trusted is not True:e.append("UNTRUSTED_REMOTE_ROOT_MUTATION")
        if self.lifecycle=="ACTIVE" and self.assurance=="UNKNOWN":e.append("ACTIVE_WITH_UNKNOWN_ASSURANCE")
        return e

class P014Canonical:
    schema="oce.p014.r14.canonical.v2"
    functional_only=True; phenomenology_undetermined=True
    def __init__(self,deps,edges=()):
        self.dependencies={d.dependency_id:d for d in deps}
        self.edges=tuple(sorted(set(tuple(x) for x in edges)|{(d.dependency_id,x) for d in deps for x in d.dependencies}))
    def cbd(self):
        rows=[asdict(self.dependencies[k]) for k in sorted(self.dependencies)]
        present={x["category"] for x in rows}
        return {"dependencies":rows,"categories_present":sorted(present),"surface_complete":set(CATEGORIES)<=present,"digest":_hash(rows)}
    def graph(self):
        ids=set(self.dependencies); unresolved=[x for x in self.edges if x[0] not in ids or x[1] not in ids]
        return {"nodes":sorted(ids),"edges":[list(x) for x in self.edges],"unresolved_edges":[list(x) for x in unresolved],"complete":not unresolved}
    def transitive(self,i):
        adj={}
        for a,b in self.edges: adj.setdefault(a,set()).add(b)
        seen=set(); stack=list(adj.get(i,()))
        while stack:
            x=stack.pop()
            if x==i or x in seen: continue
            seen.add(x); stack.extend(adj.get(x,()))
        return sorted(seen)
    def reverse_exposure(self,i):
        seen={i}; changed=True
        while changed:
            changed=False
            for a,b in self.edges:
                if b in seen and a not in seen: seen.add(a); changed=True
        seen.discard(i)
        return {"dependency_id":i,"exposed":sorted(seen),"compromise_inferred":False}
    def provider_groups(self):
        out={}
        for d in self.dependencies.values():
            key=d.provider_owner or d.provider or "UNKNOWN"
            out.setdefault(key,[]).append(d.dependency_id)
        return {k:sorted(v) for k,v in sorted(out.items())}
    def provider_pluralism(self,ids):
        ds=[self.dependencies[x] for x in ids if x in self.dependencies]
        owners={d.provider_owner or d.provider for d in ds if (d.provider_owner or d.provider)}
        return {"independent":len(owners)>1,"owners":sorted(owners)}
    def blast_radius(self,provider_owner):
        direct={d.dependency_id for d in self.dependencies.values() if (d.provider_owner or d.provider)==provider_owner}
        impacted=set(direct); changed=True
        while changed:
            changed=False
            for a,b in self.edges:
                if b in impacted and a not in impacted: impacted.add(a); changed=True
        return {"direct":sorted(direct),"impacted":sorted(impacted),"count":len(impacted)}
    def admission(self,i,emergency=False):
        d=self.dependencies[i]; b=list(d.validate())
        if d.lifecycle not in {"APPROVED","ACTIVE"}: b.append("NOT_APPROVED")
        if not d.provenance:b.append("PROVENANCE_MISSING")
        if d.criticality in {"DC4","DC5"} and not d.digest:b.append("CRITICAL_DIGEST_MISSING")
        return {"admitted":not b,"path":"EMERGENCY" if emergency else "NORMAL","blockers":sorted(set(b))}
    def update_event(self,i,before,after,emergency=False):
        fields=("version","digest","provider","provider_owner","license","maintainer","assurance","behavior_fingerprint","semantic_version")
        changed=[k for k in fields if before.get(k)!=after.get(k)]
        return {"dependency_id":i,"governance_event":bool(changed),"changed_fields":changed,
                "revalidation_required":bool(changed),"path":"EMERGENCY" if emergency else "NORMAL"}
    def activation(self,i):
        d=self.dependencies[i]; a=self.admission(i)
        return {"published":d.lifecycle!="UNAVAILABLE","activation_authorized":a["admitted"] and d.lifecycle=="ACTIVE","blockers":a["blockers"]}
    def quarantine(self,i,reason): return {"dependency_id":i,"state":"QUARANTINED","execution_allowed":False,"reason":reason}
    def exit_plan(self,i):
        d=self.dependencies[i]; b=[]
        if d.substitutability=="NONE":b.append("NO_SUBSTITUTE")
        if d.strategic and d.local_control is not True:b.append("LOCAL_CONTROL_UNPROVEN")
        if d.rollbackable is not True:b.append("ROLLBACK_UNPROVEN")
        if d.exportable is not True:b.append("EXPORT_UNPROVEN")
        if d.open_format is not True:b.append("OPEN_FORMAT_UNPROVEN")
        return {"exitable":not b,"blockers":b}
    def fallback(self,primary_ok,secondary_ok,local_ok):
        return "PRIMARY" if primary_ok else "SECONDARY" if secondary_ok else "LOCAL_FALLBACK" if local_ok else "SAFE_DEGRADED_MODE"
    def build_assurance(self,i):
        d=self.dependencies[i]
        return {"reproducible":d.reproducible,"hermetic":d.hermetic,"independent_build":d.independently_built,
                "verified":all(x is True for x in (d.reproducible,d.hermetic,d.independently_built))}
    def identity_trust(self,i):
        d=self.dependencies[i]
        return {"identity_verified":d.identity_verified,"authenticity_verified":d.authenticity_verified,
                "safety_verified":d.safety_verified,"identity_is_trust":False,"authenticity_is_safety":False}
    def privilege_gate(self,i):
        d=self.dependencies[i]; b=[]
        if not d.identity_verified:b.append("IDENTITY_UNVERIFIED")
        if not d.provenance:b.append("PROVENANCE_MISSING")
        if not d.privilege_scope:b.append("SCOPE_MISSING")
        if d.key_id and d.key_valid is not True:b.append("KEY_INVALID")
        return {"authorized":not b,"blockers":b}
    def model_tool_data_gate(self,i):
        d=self.dependencies[i]; b=[]
        if d.category=="model" and not d.behavior_fingerprint:b.append("MODEL_BEHAVIOR_UNATTESTED")
        if d.category=="tool_api" and (not d.capability_schema or not d.semantic_version):b.append("TOOL_SEMANTICS_UNATTESTED")
        if d.category=="data" and not d.training_provenance:b.append("DATA_PROVENANCE_MISSING")
        return {"trusted_input":False,"revalidation_required":bool(b),"blockers":b}
    def substitution_drill(self,i,replacement_available,migration_ok):
        d=self.dependencies[i]
        return {"passed":bool(replacement_available and migration_ok and d.substitutability!="NONE")}
    def sovereignty_vector(self,i):
        d=self.dependencies[i]
        return {"criticality":d.criticality,"substitutability":d.substitutability,"tier":d.sovereignty_tier,
                "local_control":d.local_control,"rollbackable":d.rollbackable,"offline_survivable":d.offline_survivable,
                "exportable":d.exportable,"provenance":bool(d.provenance)}
    def strategic_silence(self):
        return sorted(d.dependency_id for d in self.dependencies.values()
                      if d.strategic and (not d.provider or d.assurance=="UNKNOWN" or d.criticality in {"DC0","DC1"}))
    def legitimacy_check(self,i):
        d=self.dependencies[i]
        return {"technical_dependency":True,"legitimacy_dependency":d.legitimacy_dependency,
                "compliant":not d.legitimacy_dependency}
    def canonical_gate(self):
        b=[]
        if not self.cbd()["surface_complete"]:b.append("DEPENDENCY_SURFACE_INCOMPLETE")
        if not self.graph()["complete"]:b.append("GRAPH_INCOMPLETE")
        for d in self.dependencies.values():
            b += [d.dependency_id+":"+x for x in d.validate()]
            if d.strategic and not self.exit_plan(d.dependency_id)["exitable"]:b.append(d.dependency_id+":EXIT_UNPROVEN")
            if d.legitimacy_dependency:b.append(d.dependency_id+":LEGITIMACY_CAPTURE")
        if self.strategic_silence():b.append("SILENT_STRATEGIC_DEPENDENCY")
        return {"ready":not b,"blockers":sorted(set(b)),"objects":list(R14_OBJECTS),
                "functional_only":True,"phenomenology_undetermined":True}
def canonical_contract():
    return {"schema":P014Canonical.schema,"objects":list(R14_OBJECTS),"object_count":59,
            "functional_only":True,"phenomenology_undetermined":True}
