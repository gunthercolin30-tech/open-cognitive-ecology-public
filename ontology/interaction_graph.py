"""AW2 — canonical functional interaction graph over AW1 RF identifiers."""
from __future__ import annotations
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
import hashlib, json, math, os, re, tempfile
from collections import deque
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple
ROOT = Path.home() / "open-cognitive-ecology"

class InteractionGraph:
    primitive="INTERACTION_GRAPH"; step_id="AW2"; public_schema_version="1.0"
    allowed_interaction_types={"INFORMATION_EXCHANGE","COORDINATION","COOPERATION","COMPETITION","CONFLICT","ALIGNMENT","COALITION","MERGING","FRAGMENTATION","MEMORY_TRANSMISSION","NO_MEASURABLE_INTERACTION","UNSPECIFIED"}
    default_interactions=[{"interaction_id":"AW2-I-ALPHA-BETA","source_rf_id":"RF-AW1-ALPHA","target_rf_id":"RF-AW1-BETA","interaction_type":"INFORMATION_EXCHANGE","directed":True,"weight":0.5,"confidence":0.5,"synthetic":True}]
    def __init__(self, root: Optional[Path]=None):
        self.root=Path(root) if root is not None else ROOT
        self.output_dir=self.root/"rf_ecology"/"AW2_interaction_graph"
    @staticmethod
    def _canonical_json(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    @classmethod
    def _hash(cls,v): return hashlib.sha256(cls._canonical_json(v).encode()).hexdigest()
    @staticmethod
    def _safe_id(v,fallback):
        raw=str(v or fallback).strip().upper(); safe=re.sub(r"[^A-Z0-9._:-]+","-",raw); safe=re.sub(r"-{2,}","-",safe).strip("-"); return safe or fallback
    @staticmethod
    def _string_list(v): return sorted({str(x).strip() for x in v if str(x).strip()}) if isinstance(v,list) else []
    @staticmethod
    def _finite(v):
        try: x=float(v)
        except (TypeError,ValueError): return 0.0,False
        return (x,True) if math.isfinite(x) else (0.0,False)
    @staticmethod
    def _time(v):
        if v in (None,""): return None,True
        text=str(v).strip()
        try: dt=datetime.fromisoformat(text.replace("Z","+00:00"))
        except ValueError: return text,False
        if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00","Z"),True
    def _registry(self, inputs):
        supplied=inputs.get("multi_rf_registry")
        if isinstance(supplied,Mapping) and isinstance(supplied.get("registry"),list): return deepcopy(dict(supplied))
        from ontology.multi_rf_registry import MultiRFRegistry
        records=inputs.get("rf_records")
        return MultiRFRegistry(root=self.root).step(inputs={"rf_records":deepcopy(records)} if isinstance(records,list) else {},persist=False)
    def _items(self, inputs):
        x=inputs.get("interactions",inputs.get("edges",inputs.get("interaction_events")))
        if x is None: x=deepcopy(self.default_interactions)
        if isinstance(x,Mapping): x=x.get("interactions") or x.get("edges") or x.get("interaction_events")
        return [deepcopy(i) for i in x if isinstance(i,Mapping)] if isinstance(x,list) else []
    def _normalize(self,item,index):
        issues=[]; source=self._safe_id(item.get("source_rf_id",item.get("source")),f"RF-MISSING-SOURCE-{index:04d}"); target=self._safe_id(item.get("target_rf_id",item.get("target")),f"RF-MISSING-TARGET-{index:04d}")
        directed=bool(item.get("directed",True)); typ=str(item.get("interaction_type",item.get("type","UNSPECIFIED"))).upper(); typ=typ if typ in self.allowed_interaction_types else "UNSPECIFIED"
        wr,wok=self._finite(item.get("weight",1.0)); cr,cok=self._finite(item.get("confidence",1.0))
        if not wok: issues.append({"issue_type":"INVALID_WEIGHT","edge_index":index})
        if not cok: issues.append({"issue_type":"INVALID_CONFIDENCE","edge_index":index})
        obs,ok1=self._time(item.get("observed_at_utc")); start,ok2=self._time(item.get("valid_from_utc")); end,ok3=self._time(item.get("valid_until_utc"))
        for field,ok in (("observed_at_utc",ok1),("valid_from_utc",ok2),("valid_until_utc",ok3)):
            if not ok: issues.append({"issue_type":"INVALID_TIMESTAMP","field":field,"edge_index":index})
        if start and end and ok2 and ok3 and datetime.fromisoformat(end.replace("Z","+00:00")) < datetime.fromisoformat(start.replace("Z","+00:00")): issues.append({"issue_type":"TEMPORAL_ORDER_VIOLATION","edge_index":index})
        allow=bool(item.get("allow_self_loop",False))
        if source==target and not allow: issues.append({"issue_type":"UNAUTHORIZED_SELF_LOOP","edge_index":index,"rf_id":source})
        if not directed and target<source: source,target=target,source
        edge={"interaction_id":self._safe_id(item.get("interaction_id",item.get("edge_id")),f"AW2-I-{index:04d}"),"source_rf_id":source,"target_rf_id":target,"interaction_type":typ,"directed":directed,"weight":round(max(0,min(1,wr)),6),"confidence":round(max(0,min(1,cr)),6),"observed_at_utc":obs,"valid_from_utc":start,"valid_until_utc":end,"allow_self_loop":allow,"synthetic":bool(item.get("synthetic",False)),"evidence_refs":self._string_list(item.get("evidence_refs",[])),"metadata":deepcopy(item.get("metadata") if isinstance(item.get("metadata"),dict) else {}),"functional_only":True,"phenomenology_claim_allowed":False}
        edge["edge_hash"]=self._hash(edge); return edge,issues
    def _build(self,inputs,valid_ids):
        by_id={}; collisions=[]; issues=[]; exact=0
        for idx,item in enumerate(self._items(inputs),1):
            edge,local=self._normalize(item,idx); issues.extend(local); missing=sorted({x for x in (edge["source_rf_id"],edge["target_rf_id"]) if x not in valid_ids})
            if missing: issues.append({"issue_type":"ORPHAN_EDGE","interaction_id":edge["interaction_id"],"missing_rf_ids":missing})
            prior=by_id.get(edge["interaction_id"])
            if prior is None: by_id[edge["interaction_id"]]=edge
            elif prior["edge_hash"]==edge["edge_hash"]: exact+=1
            else: collisions.append({"interaction_id":edge["interaction_id"],"collision_type":"CONFLICTING_INTERACTION_ID","existing_edge_hash":prior["edge_hash"],"incoming_edge_hash":edge["edge_hash"],"resolution":"REJECT_INCOMING_REQUIRE_EXPLICIT_REVISION"})
        return sorted(by_id.values(),key=lambda e:e["interaction_id"]),sorted(collisions,key=lambda c:c["interaction_id"]),exact,sorted(issues,key=self._canonical_json)
    @staticmethod
    def _components(ids,edges):
        g={x:set() for x in ids}
        for e in edges: g[e["source_rf_id"]].add(e["target_rf_id"]); g[e["target_rf_id"]].add(e["source_rf_id"])
        seen=set(); out=[]
        for s in sorted(g):
            if s in seen: continue
            q=deque([s]); seen.add(s); members=[]
            while q:
                x=q.popleft(); members.append(x)
                for y in sorted(g[x]):
                    if y not in seen: seen.add(y); q.append(y)
            out.append({"component_id":f"AW2-C-{len(out)+1:04d}","rf_ids":sorted(members),"node_count":len(members)})
        return out
    @staticmethod
    def _atomic(path,payload,filesystem_effect_context=None):
        if filesystem_effect_context is None: raise RuntimeError("governed_filesystem_effect_context_required")
        filesystem_effect_context.execute_path("interaction_graph_parent_create","FS_CREATE_DIRS",path.parent)
        data=(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode("utf-8")
        filesystem_effect_context.execute_path("interaction_graph_write_replace","FS_WRITE_REPLACE_BYTES",path,data)

    def _load(self):
        p=self.output_dir/"latest_interaction_graph.json"
        if not p.exists(): return None
        try: x=json.loads(p.read_text(encoding="utf-8"))
        except Exception: return None
        return x if isinstance(x,dict) and isinstance(x.get("edges"),list) else None
    def step(self,inputs:Optional[Dict[str,Any]]=None,persist:bool=False,filesystem_effect_context=None):
        inp=deepcopy(inputs) if isinstance(inputs,dict) else {}; load=bool(inp.get("load_existing",False)); old=self._load() if load else None
        if old is not None:
            inp=dict(inp); inp["interactions"]=deepcopy(old["edges"]); inp.setdefault("multi_rf_registry",{"registry":deepcopy(old.get("nodes",[])),"multi_rf_registry_ready":True})
        reg=self._registry(inp); nodes=deepcopy(reg.get("registry",[])) if isinstance(reg.get("registry"),list) else []; ready_reg=bool(reg.get("multi_rf_registry_ready",False)); ids=sorted({str(n.get("rf_id","")).strip() for n in nodes if isinstance(n,Mapping) and str(n.get("rf_id","")).strip()}); valid=set(ids)
        all_edges,collisions,exact,issues=self._build(inp,valid); edges=[e for e in all_edges if e["source_rf_id"] in valid and e["target_rf_id"] in valid]
        adjacency={x:set() for x in ids}
        for e in edges: adjacency[e["source_rf_id"]].add(e["target_rf_id"]); adjacency.setdefault(e["target_rf_id"],set()); adjacency[e["target_rf_id"]].update([e["source_rf_id"]] if not e["directed"] else [])
        adjacency={k:sorted(v) for k,v in sorted(adjacency.items())}; components=self._components(ids,edges); connected={x for e in edges for x in (e["source_rf_id"],e["target_rf_id"])}; isolated=sorted(valid-connected)
        incoming={x:0 for x in ids}; outgoing={x:0 for x in ids}; undirected={x:0 for x in ids}
        for e in edges:
            s,t=e["source_rf_id"],e["target_rf_id"]
            if e["directed"]: outgoing[s]+=1; incoming[t]+=1
            else: undirected[s]+=1; undirected[t]+=int(t!=s)
        degrees=[{"rf_id":x,"incoming_degree":incoming[x],"outgoing_degree":outgoing[x],"undirected_degree":undirected[x],"total_degree":incoming[x]+outgoing[x]+undirected[x]} for x in ids]
        orphan=[i for i in issues if i.get("issue_type")=="ORPHAN_EDGE"]; temporal=[i for i in issues if i.get("issue_type") in {"INVALID_TIMESTAMP","TEMPORAL_ORDER_VIOLATION"}]; numeric=[i for i in issues if i.get("issue_type") in {"INVALID_WEIGHT","INVALID_CONFIDENCE"}]; loops=[i for i in issues if i.get("issue_type")=="UNAUTHORIZED_SELF_LOOP"]
        policy={"nodes_must_be_registered_aw1_rf_ids":True,"orphan_edges_are_invalid":True,"exact_duplicate_edges_are_deduplicated":True,"conflicting_interaction_ids_are_rejected":True,"directed_and_undirected_edges_are_distinct":True,"undirected_edge_endpoints_are_canonicalized":True,"self_loops_require_explicit_authorization":True,"weights_and_confidence_are_bounded_0_1":True,"non_finite_numbers_are_invalid":True,"temporal_order_must_be_consistent":True,"graph_structure_does_not_imply_shared_rf":True,"graph_structure_does_not_imply_coalition":True,"graph_structure_does_not_imply_conflict":True}
        guards={"epistemic_scope":"functional_rf_interaction_graph_only","interaction_does_not_prove_consciousness":True,"connectivity_does_not_prove_collective_subjectivity":True,"density_does_not_prove_collective_qualia":True,"components_do_not_prove_phenomenal_unity":True,"coordination_edges_do_not_prove_collective_consciousness":True,"consciousness_proven":False,"qualia_proven":False,"subjectivity_proven":False,"phenomenology_proven":False,"collective_consciousness_proven":False,"collective_qualia_proven":False,"collective_subjectivity_proven":False,"collective_phenomenology_proven":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
        graph_hash=self._hash({"rf_ids":ids,"edges":edges}); contract_hash=self._hash({"graph_hash":graph_hash,"graph_policy":policy,"epistemic_guards":guards}); ok=bool(ready_reg and ids and not collisions and not issues); status="RF_INTERACTION_GRAPH_READY" if ok else "RF_INTERACTION_GRAPH_INCOMPLETE"
        result={"primitive":self.primitive,"step":self.step_id,"public_schema_version":self.public_schema_version,"status":status,"interaction_graph_status":status,"interaction_graph_ready":ok,"registry_ready":ready_reg,"nodes":nodes,"node_ids":ids,"node_count":len(ids),"edges":edges,"edge_count":len(edges),"directed_edge_count":sum(bool(e["directed"]) for e in edges),"undirected_edge_count":sum(not bool(e["directed"]) for e in edges),"self_loop_count":sum(e["source_rf_id"]==e["target_rf_id"] for e in edges),"isolated_node_ids":isolated,"isolated_node_count":len(isolated),"adjacency":adjacency,"degree_table":degrees,"components":components,"component_count":len(components),"density":0.0 if len(ids)<2 else round(min(1.0,len(edges)/(len(ids)*(len(ids)-1))),6),"collisions":collisions,"collision_count":len(collisions),"exact_duplicate_count":exact,"validation_issues":issues,"validation_issue_count":len(issues),"orphan_edges":orphan,"orphan_edge_count":len(orphan),"temporal_issues":temporal,"temporal_issue_count":len(temporal),"invalid_numeric_issues":numeric,"invalid_numeric_issue_count":len(numeric),"unauthorized_self_loops":loops,"unauthorized_self_loop_count":len(loops),"allowed_interaction_types":sorted(self.allowed_interaction_types),"graph_policy":policy,"epistemic_guards":guards,"graph_hash":graph_hash,"contract_hash":contract_hash,"inputs_observed":sorted(inp.keys()),"load_existing_requested":load,"persist_requested":bool(persist),"persisted":False,"output_path":None,"timestamp_utc":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"consciousness_proven":False,"qualia_proven":False,"subjectivity_proven":False,"phenomenology_proven":False,"collective_consciousness_proven":False,"collective_qualia_proven":False,"collective_subjectivity_proven":False,"collective_phenomenology_proven":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
        if persist and ok:
            p=self.output_dir/"latest_interaction_graph.json"; payload=deepcopy(result); payload.update({"persisted":True,"output_path":str(p)}); self._atomic(p,payload,filesystem_effect_context); result.update({"persisted":True,"output_path":str(p)})
        return result
