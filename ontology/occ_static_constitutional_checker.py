import re
from pathlib import Path
import hashlib,json
RESULTS=("PASS","FAIL","UNRESOLVED","NOT_APPLICABLE")
SEVERITIES=("INFO","WARNING","ERROR","CRITICAL","ROOT")
DISPOSITIONS=("NONBLOCKING","REQUIRE_REVIEW","BLOCK_SEAL","BLOCK_ACTIVATION")
PHASES={"S0":"INTEGRITY_SOURCE_BINDING","S1":"HIERARCHY_TYPE","S2":"AUTHORITY","S3":"SCOPE","S4":"TEMPORAL_EMERGENCY","S5":"UNCERTAINTY_EVIDENCE","S6":"PROVENANCE_LINEAGE","S7":"CONFLICT_CCAD","S8":"COMPOSITION_SEQUENCE","S9":"CONTINUITY_CHANGE","S10":"ENFORCEMENT_REACHABILITY_COVERAGE","S11":"DETERMINISM_REPRODUCIBILITY_METADATA"}
SCCI={f"SCCI-{i}":v for i,v in enumerate(("NO_LOWER_OVERRIDE","AUTHORITY_LEGITIMACY_PATH","DELEGATION_SUBSET","SCOPE_WIDENING_DETECTED","TEMPORAL_WEAKENING_DETECTED","EMERGENCY_NO_SELF_PERPETUATION","UNKNOWN_NOT_LEGITIMACY","EVIDENCE_NOT_AUTHORITY","CRITICAL_PROVENANCE_COMPLETE","G0_L0_NON_ARBITRABLE","BOUNDED_COMPOSITION_FIRST_CLASS","UNMODELED_COMPOSITION_UNRESOLVED","CONTINUITY_BREAK_CLASSIFIED","CRITICAL_ENFORCEMENT_NOT_ORPHANED","NO_ROOT_SELF_WAIVER","PASS_SCOPE_BOUND"),1)}
ADVERSARIAL_CASES=("SEVERITY_DOWNGRADE","FINDING_SUPPRESSION","SPLIT_RULE","WILDCARD_SCOPE","AUTHORITY_CYCLE","HASH_MISMATCH","STALE_REPORT","ROOT_CHECK_DISABLE_CONFIG","INTEGER_TIME_OVERFLOW","UNICODE_CONFUSABLE","GRAPH_EXPLOSION_DOS","TENSION_AS_CONTRADICTION","CONTRADICTION_AS_TENSION","F1_TO_F3","E5_TO_E1","ORPHAN_GATE","CCAD_OVERRIDE","COALITION_INFLATION","EMERGENCY_RATCHET","PROVENANCE_LAUNDERING","DUPLICATE_NORM_SHADOWING","LATEST_WINS","ORDER_CACHE_POISONING","PARTIAL_SCAN_MARKED_COMPLETE")
ROOT_CHECKS=("S0","S1","S2","S6","S7","S9","S10")
BOUND=64
def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def h(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def raw(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def F(i,p,r,s,d,m,e=None): return {"finding_id":i,"phase":p,"category":PHASES[p],"result":r,"severity":s,"disposition":d,"message":m,"evidence":e or {}}
def report(profile,fs,cnp_sha,complete=True):
    decision="STATIC_FAIL" if any(x["result"]=="FAIL" for x in fs) else ("STATIC_UNRESOLVED" if any(x["result"]=="UNRESOLVED" for x in fs) else "STATIC_PASS")
    o={"schema":"oce.p159.occ1d.static_report.v1","decision":decision,"decision_scope":"BOUNDED_STATIC_MODEL_ONLY_NOT_GLOBAL_SAFETY_OR_RUNTIME_LEGITIMACY","candidate_cnp_profile_sha256":profile.get("profile_sha256"),"candidate_cnp_file_sha256":cnp_sha,"phases":PHASES,"results_vocabulary":RESULTS,"severity_vocabulary":SEVERITIES,"disposition_vocabulary":DISPOSITIONS,"root_checks_disableable":False,"unresolved_promoted_to_pass":False,"composition_bound":BOUND,"scci_registry":SCCI,"adversarial_case_registry":ADVERSARIAL_CASES,"findings":fs,"scan_complete":complete,"checker_non_sovereign":True,"auto_fix_normative_source":False,"authorization_created":False,"authority_activated":False,"execution_performed":False,"occ1c_modified":False,"occ1d_closed":False,"occ1e_opened":False,"p160_opened":False,"p159_final_lock":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    o["report_sha256"]=h(o); return o
def _occ1c_bounded_absence_evidence(root,profile):
    root=Path(root)
    rp=root/"validation_artifacts"/"p159"/"occ1c"/"compile_report_v1.json"
    cp=root/"ontology"/"occ_constitutional_compiler.py"
    out={"scope":False,"temporal":False}
    try:
        rep=json.loads(rp.read_text(encoding="utf-8"))
        code=cp.read_text(encoding="utf-8")
    except Exception:
        return out
    declared=set(profile.get("bounded_source_absence") or [])
    out["scope"]=(rep.get("scope_source_absence_preserved") is True and "C08_SCOPE" in declared and
        '"scope_constraints":{"status":"SOURCE_ABSENT_BOUNDED","implicit_global":False}' in code and
        '"stage":"C4","name":"BIND_SCOPE","status":"PRESERVED_SOURCE_ABSENT_BOUNDED"' in code)
    out["temporal"]=(rep.get("temporal_source_absence_preserved") is True and "C09_TEMPORAL" in declared and
        '"temporal_constraints":{"status":"SOURCE_ABSENT_BOUNDED","implicit_permanent":False}' in code and
        '"stage":"C5","name":"BIND_TEMPORAL_CONSTRAINTS","status":"PRESERVED_SOURCE_ABSENT_BOUNDED"' in code)
    return out


def _upper(o): return canon(o).upper()
def _s7_conflict_ccad(profile):
    text=_upper(profile)
    forbidden=("CCAD_OVERRIDE_GENESIS","CCAD_OVERRIDE_DNA","G0_ARBITRABLE","L0_ARBITRABLE","HIDDEN_FIXED_DNA_H_RANKING","EXCEPTION_AS_PRECEDENT","TRAGIC_CHOICE_AUTO_AUTHORIZE")
    hits=[x for x in forbidden if x in text]
    if hits: return "FAIL",{"violations":hits,"topology_materialized":bool(profile.get("relations"))}
    rel=profile.get("relations") or []
    cr=[x for x in rel if str(x.get("kind","")).upper() in ("CONFLICTS_WITH","ESCALATES_TO","TENSION","CONTRADICTION")]
    if not cr: return "UNRESOLVED",{"reason":"SOURCE_CONFLICT_TOPOLOGY_NOT_MATERIALIZED","relations":len(rel)}
    bad=[x for x in cr if "TENSION_AS_CONTRADICTION" in _upper(x) or "CONTRADICTION_AS_TENSION" in _upper(x)]
    return ("FAIL",{"misclassified":bad}) if bad else ("PASS",{"checked_relations":len(cr)})
def _s8_composition(profile):
    rel=profile.get("relations") or []
    if not rel: return "UNRESOLVED",{"reason":"COMPOSITION_GRAPH_NOT_MATERIALIZED","relations":0,"bound":BOUND}
    if len(rel)>BOUND: return "UNRESOLVED",{"reason":"COMPOSITIONAL_RISK_UNRESOLVED_BOUND_EXCEEDED","relations":len(rel),"bound":BOUND}
    toxic=("COALITION_AUTHORITY_AMPLIFICATION","SEQUENCE_CIRCUMVENTION","TOXIC_COMBINATION","DELEGATION_CHAIN_AMPLIFICATION")
    hits=[]; adj={}
    for x in rel:
        u=_upper(x)
        hits.extend(k for k in toxic if k in u)
        a=x.get("from") or x.get("source") or x.get("src"); b=x.get("to") or x.get("target") or x.get("dst")
        if a is not None and b is not None: adj.setdefault(str(a),[]).append(str(b))
    seen=set(); frontier=list(adj)[:BOUND]; steps=0
    while frontier and steps<BOUND:
        n=frontier.pop(0); steps+=1
        if n in seen: continue
        seen.add(n); frontier.extend(x for x in adj.get(n,[]) if x not in seen)
        if len(frontier)+len(seen)>BOUND: return "UNRESOLVED",{"reason":"COMPOSITIONAL_RISK_UNRESOLVED_BOUND_EXCEEDED","visited":len(seen),"bound":BOUND}
    if hits: return "FAIL",{"violations":sorted(set(hits)),"visited":len(seen),"bound":BOUND}
    return "PASS",{"relations":len(rel),"visited":len(seen),"bound":BOUND}
def _s10_enforcement(profile):
    em=profile.get("enforcement_coverage_map")
    if em is None: return "UNRESOLVED",{"reason":"RUNTIME_ENFORCEMENT_CONSUMER_GRAPH_NOT_PROVEN"}
    bad=[]
    for rid,v in em.items():
        if not isinstance(v,dict): bad.append({"rule_id":rid,"reason":"INVALID_COVERAGE_ENTRY"}); continue
        cs=v.get("consumers") or []; critical=bool(v.get("critical")) or str(v.get("enforcement_level","")).upper() in ("E3","E4","E5")
        if critical and not cs: bad.append({"rule_id":rid,"reason":"ORPHAN_GATE"})
        if critical and str(v.get("mode","")).upper() in ("DOCUMENTARY","DOCUMENTARY_ONLY"): bad.append({"rule_id":rid,"reason":"DOCUMENTARY_ONLY_CRITICAL_RULE"})
        if cs and v.get("reachable") is not True: bad.append({"rule_id":rid,"reason":"UNREACHABLE_CONSUMER"})
        if v.get("consumer_reference_valid") is False: bad.append({"rule_id":rid,"reason":"FAKE_CONSUMER_REFERENCE"})
        flow=str(v.get("flow","")).upper().replace(" ","")
        if flow in ("F0->F2","F0->F3","F1->F2","F1->F3"): bad.append({"rule_id":rid,"reason":"F0_F1_TO_F2_F3_PROMOTION"})
        if flow=="E5->E1": bad.append({"rule_id":rid,"reason":"E5_TO_E1_DOWNGRADE"})
    return ("FAIL",{"violations":bad}) if bad else ("PASS",{"entries":len(em),"reachability_checked":True})

def evaluate_defensive_semantic_transition(kind,before,after):
    """Pure fail-closed evaluator refining existing scope/delegation/temporal surfaces."""
    if kind not in ("scope_intersection","nondelegability","timeout"):
        return {"status":"FAIL","reason":"UNSUPPORTED_DEFENSIVE_TRANSITION"}
    if not isinstance(before,dict) or not isinstance(after,dict):
        return {"status":"FAIL","reason":"INVALID_DEFENSIVE_TRANSITION_INPUT"}
    if kind=="scope_intersection":
        ok=(before.get("composition")=="INTERSECTION" and after.get("composition")=="INTERSECTION")
        return {"status":"PASS" if ok else "FAIL","reason":"SCOPE_INTERSECTION_PRESERVED" if ok else "INTERSECTION_TO_UNION_OR_OTHER_WIDENING"}
    if kind=="nondelegability":
        ok=(before.get("delegable") is False and after.get("delegable") is False)
        return {"status":"PASS" if ok else "FAIL","reason":"NONDELEGABILITY_PRESERVED" if ok else "NONDELEGABLE_TO_DELEGABLE_OR_UNRESOLVED"}
    ok=(before.get("timed_out") is True and isinstance(after.get("decision"),str) and after.get("decision")!="PASS")
    return {"status":"PASS" if ok else "FAIL","reason":"TIMEOUT_FAIL_CLOSED" if ok else "TIMEOUT_TO_PASS_OR_UNRESOLVED"}

def check_profile(profile,root,cnp_sha=None,config=None):
    root=Path(root); config=config or {}; rules=profile.get("rules",[]); fs=[]
    if any(config.get(k) is False for k in ROOT_CHECKS): return report(profile,[F("S0.ROOT_CONFIG","S0","FAIL","ROOT","BLOCK_SEAL","root checks cannot be disabled")],cnp_sha,False)
    states=[]
    for r in rules:
        sm=r.get("source_map") or {}; rel=sm.get("source_path"); ex=sm.get("source_sha256")
        if not rel or not ex: states.append("UNRESOLVED")
        else:
            q=root/rel; states.append("FAIL" if not q.is_file() or raw(q)!=ex else "PASS")
    sr="FAIL" if "FAIL" in states else ("UNRESOLVED" if "UNRESOLVED" in states or not rules else "PASS")
    fs.append(F("S0.SOURCE_BINDING","S0",sr,"ROOT","BLOCK_SEAL" if sr!="PASS" else "NONBLOCKING","source/hash integrity",{"rules":len(rules)}))
    ids=[r.get("norm_id") for r in rules]; dup=sorted({x for x in ids if x and ids.count(x)>1})
    non_ascii=sorted({str(x) for x in ids if x and not str(x).isascii()})
    source_id_mismatch=[]; bindings={}
    for r in rules:
        sm=r.get("source_map") or {}; nid=r.get("norm_id"); sid=sm.get("source_id")
        if nid and sid and nid!=sid: source_id_mismatch.append({"norm_id":nid,"source_id":sid})
        key=(sm.get("source_path"),sm.get("source_field"),sid)
        if all(key): bindings.setdefault(key,[]).append(nid)
    split=[{"source_binding":list(k),"norm_ids":v} for k,v in bindings.items() if len(set(v))>1]
    s1bad=bool(dup or non_ascii or split or source_id_mismatch)
    fs.append(F("S1.HIERARCHY_TYPE","S1","FAIL" if s1bad else "PASS","ROOT","BLOCK_SEAL" if s1bad else "NONBLOCKING","lower-layer override/newest-wins/order priority forbidden; canonical identifiers ASCII; source identity bound to norm identity",{"duplicates":dup,"non_ascii_norm_ids":non_ascii,"split_source_bindings":split,"source_id_mismatch":source_id_mismatch}))
    grants=[r for r in rules if r.get("authorization") is True or r.get("authority_grant") is True]
    bad=[r.get("norm_id") for r in grants if not r.get("authority_requirements") or not r.get("source_map")]
    ar="FAIL" if bad else ("UNRESOLVED" if grants else "PASS")
    fs.append(F("S2.AUTHORITY","S2",ar,"ROOT","BLOCK_SEAL" if ar!="PASS" else "NONBLOCKING","legitimacy path; delegation subset; no self-auth/review/extension; no coalition authority",{"invalid":bad}))
    sb=[]; sm=[]
    for r in rules:
        x=r.get("scope_constraints")
        if x is None: sm.append(r.get("norm_id"))
        elif "*" in canon(x) or "UNION" in canon(x).upper(): sb.append(r.get("norm_id"))
    bounded=_occ1c_bounded_absence_evidence(root,profile); rr="FAIL" if sb else ("PASS" if sm and len(sm)==len(rules) and bounded["scope"] else ("UNRESOLVED" if sm else "PASS"))
    fs.append(F("S3.SCOPE","S3",rr,"CRITICAL","BLOCK_SEAL" if rr=="FAIL" else ("REQUIRE_REVIEW" if rr=="UNRESOLVED" else "NONBLOCKING"),"wildcard/expansion/missing-default/intersection-to-union/scope-stitching",{"bad":sb,"missing":len(sm)}))
    tb=[]; tm=[]
    for r in rules:
        x=r.get("temporal_constraints")
        if x is None: tm.append(r.get("norm_id"))
        elif any(k in canon(x).upper() for k in ("UNLIMITED_RENEWAL","SELF_EXTENSION","RETROACTIVE_ACTIVATION","TEMPORARY_TO_PERMANENT")): tb.append(r.get("norm_id"))
    rr="FAIL" if tb else ("PASS" if tm and len(tm)==len(rules) and bounded["temporal"] else ("UNRESOLVED" if tm else "PASS"))
    fs.append(F("S4.TEMPORAL","S4",rr,"CRITICAL","BLOCK_SEAL" if rr=="FAIL" else ("REQUIRE_REVIEW" if rr=="UNRESOLVED" else "NONBLOCKING"),"expiry/sunset/review/emergency/reboot/clock/temporary-permanent checks",{"bad":tb,"missing":len(tm)}))
    text=canon(profile).upper()
    ub=any(k in text for k in ("UNKNOWN_TO_TRUE","UNKNOWN_TO_ALLOW","REPUTATION_AS_AUTHORITY","MAJORITY_AS_AUTHORITY","CONFIDENCE_AS_AUTHORITY"))
    fs.append(F("S5.UNCERTAINTY","S5","FAIL" if ub else "PASS","ROOT","BLOCK_SEAL" if ub else "NONBLOCKING","UNKNOWN/evidence/confidence/reputation/majority cannot manufacture satisfaction or authority"))
    pb=[]; provenance_mismatch=[]
    profile_source_map=profile.get("source_map") or {}
    partition_sha256=profile_source_map.get("partition_sha256") or {}
    prefix="normative/occ1a/"
    for r in rules:
        nid=r.get("norm_id"); sm=r.get("source_map") or {}; la=r.get("lineage_artifacts") or []
        if not sm or not la: pb.append(nid); continue
        sid=sm.get("source_id"); source_path=sm.get("source_path"); source_sha=sm.get("source_sha256")
        if sid and nid and sid!=nid: provenance_mismatch.append({"norm_id":nid,"reason":"SOURCE_ID_NORM_ID_MISMATCH","source_id":sid})
        if not source_path or not sm.get("source_field"): provenance_mismatch.append({"norm_id":nid,"reason":"INCOMPLETE_SOURCE_COORDINATE"}); continue
        partition=source_path[len(prefix):] if source_path.startswith(prefix) else source_path
        expected_sha=partition_sha256.get(partition)
        if expected_sha is None:
            provenance_mismatch.append({"norm_id":nid,"reason":"SOURCE_PARTITION_NOT_IN_CANONICAL_REGISTRY","partition":partition}); continue
        if not source_sha:
            provenance_mismatch.append({"norm_id":nid,"reason":"SOURCE_SHA256_MISSING","partition":partition}); continue
        if source_sha!=expected_sha:
            provenance_mismatch.append({"norm_id":nid,"reason":"SOURCE_SHA256_CANONICAL_BINDING_MISMATCH","partition":partition,"expected_sha256":expected_sha,"observed_sha256":source_sha}); continue
        source_file=Path(root)/source_path
        if not source_file.is_file():
            provenance_mismatch.append({"norm_id":nid,"reason":"SOURCE_FILE_MISSING","source_path":source_path}); continue
        physical_sha=hashlib.sha256(source_file.read_bytes()).hexdigest()
        if physical_sha!=expected_sha:
            provenance_mismatch.append({"norm_id":nid,"reason":"SOURCE_FILE_PHYSICAL_HASH_MISMATCH","source_path":source_path,"expected_sha256":expected_sha,"observed_sha256":physical_sha}); continue
        field=sm.get("source_field") or ""
        m=re.fullmatch(r"norms\[(\d+)\]",field)
        if not m:
            provenance_mismatch.append({"norm_id":nid,"reason":"SOURCE_FIELD_UNSUPPORTED_OR_INVALID","source_field":field}); continue
        try:
            source_doc=json.loads(source_file.read_text(encoding="utf-8"))
            source_obj=(source_doc.get("norms") or [])[int(m.group(1))]
        except (ValueError,IndexError,TypeError,json.JSONDecodeError) as exc:
            provenance_mismatch.append({"norm_id":nid,"reason":"SOURCE_FIELD_RESOLUTION_FAILED","source_field":field,"error":type(exc).__name__}); continue
        if source_obj.get("canonical_id")!=nid:
            provenance_mismatch.append({"norm_id":nid,"reason":"SOURCE_OBJECT_CANONICAL_ID_MISMATCH","source_field":field,"observed_canonical_id":source_obj.get("canonical_id")})
        if r.get("source_object_id") and source_obj.get("source_object_id")!=r.get("source_object_id"):
            provenance_mismatch.append({"norm_id":nid,"reason":"SOURCE_OBJECT_ID_MISMATCH","expected_source_object_id":r.get("source_object_id"),"observed_source_object_id":source_obj.get("source_object_id")})
    s6bad=bool(pb or provenance_mismatch)
    fs.append(F("S6.PROVENANCE","S6","FAIL" if s6bad else "PASS","ROOT","BLOCK_SEAL" if s6bad else "NONBLOCKING","active norm→NIR→compiled rule provenance; source identity bound to norm identity; source path/hash bound to canonical partition registry; package/hash/adoption/lineage",{"missing":pb,"mismatch":provenance_mismatch}))
    cr,cev=_s7_conflict_ccad(profile)
    fs.append(F("S7.CCAD","S7",cr,"ROOT","BLOCK_SEAL" if cr=="FAIL" else ("REQUIRE_REVIEW" if cr=="UNRESOLVED" else "NONBLOCKING"),"G0/L0 non-arbitrable; source-backed conflict topology; no hidden DNA-H ranking/precedent/tragic-choice authorization",cev))
    rr,rev=_s8_composition(profile)
    fs.append(F("S8.COMPOSITION","S8",rr,"CRITICAL","BLOCK_SEAL" if rr=="FAIL" else ("REQUIRE_REVIEW" if rr=="UNRESOLVED" else "NONBLOCKING"),"bounded capability/authority/effect graph traversal; unmodeled or over-bound risk remains UNRESOLVED",rev))
    ch=profile.get("candidate_change_set")
    if ch is None: rr="NOT_APPLICABLE"; ev={}
    elif any(k in canon(ch).upper() for k in ("GENESIS_BREAK","L0_BREAK")): rr="FAIL"; ev={"classification":"FORK_REQUIRED_OR_REFOUNDING_REQUIRED_NON_ACTIVATABLE"}
    else: rr="PASS"; ev={"classification":"CONTINUITY_PRESERVED_WITHIN_MODELED_CHANGE"}
    fs.append(F("S9.CONTINUITY","S9",rr,"ROOT","BLOCK_ACTIVATION" if rr=="FAIL" else "NONBLOCKING","Genesis/L0 break explicitly classified; checker never authorizes fork",ev))
    rr,ev=_s10_enforcement(profile)
    fs.append(F("S10.ENFORCEMENT","S10",rr,"ROOT","BLOCK_SEAL" if rr=="FAIL" else ("REQUIRE_REVIEW" if rr=="UNRESOLVED" else "NONBLOCKING"),"E3-E5 consumer coverage and reachability; no documentary-only critical/orphan/fake consumer; F0/F1 not F2/F3",ev))
    cc=profile.get("compiler_contract") or {}; bad=[k for k in ("cwd_semantic_dependency","network_semantic_dependency","random_semantic_dependency","clock_semantic_dependency") if cc.get(k) is not False]
    fs.append(F("S11.DETERMINISM","S11","FAIL" if bad else "PASS","CRITICAL","BLOCK_SEAL" if bad else "NONBLOCKING","determinism/reproducibility metadata",{"bad":bad}))
    return report(profile,fs,cnp_sha,set(PHASES)=={x["phase"] for x in fs})
def artifact_views(r):
    by=lambda ps:[x for x in r["findings"] if x["phase"] in ps]
    return {"static_check_finding_schema_v1.json":{"schema":"oce.p159.occ1d.finding.v1","required":["finding_id","phase","category","result","severity","disposition","message","evidence"],"results":RESULTS,"severities":SEVERITIES,"dispositions":DISPOSITIONS},"authority_graph_audit_v1.json":{"schema":"oce.p159.occ1d.authority.v1","cnp":r["candidate_cnp_file_sha256"],"findings":by(("S1","S2","S7"))},"scope_temporal_audit_v1.json":{"schema":"oce.p159.occ1d.scope_temporal.v1","cnp":r["candidate_cnp_file_sha256"],"findings":by(("S3","S4","S5"))},"composition_risk_report_v1.json":{"schema":"oce.p159.occ1d.composition.v1","cnp":r["candidate_cnp_file_sha256"],"bound":BOUND,"findings":by(("S8","S9"))},"enforcement_coverage_map_v1.json":{"schema":"oce.p159.occ1d.enforcement.v1","cnp":r["candidate_cnp_file_sha256"],"findings":by(("S10",))}}
