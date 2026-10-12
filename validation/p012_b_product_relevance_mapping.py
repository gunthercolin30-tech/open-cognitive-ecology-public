#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path.home()/"open-cognitive-ecology"
SRC=ROOT/"p012_a2_component_segmentation_report.json"
INV=ROOT/"ontology_inventory.txt"
OUT=ROOT/"p012_b_product_relevance_mapping_report.json"

EXPECTED_A2_ID="6cf3daa5bc6fc13df143d3e8e6a563a30243eb68563ed3aeebd863889ae15204"

PROFILES={
"world_model_prediction":{
 "technical_value":"prediction, state-transition modelling, planning and counterfactual support",
 "potential_users":["decision-support operator","researcher","autonomous-system integrator"],
 "customer_outcomes":["better anticipation of consequences","more explicit planning evidence"],
 "product_surfaces":["predictive decision-support service","world-model evaluation toolkit"]},
"individual_identity_memory":{
 "technical_value":"persistent identity, individual memory, lifecycle and specialization surfaces",
 "potential_users":["multi-agent platform operator","longitudinal assistant integrator"],
 "customer_outcomes":["continuity across sessions and roles","traceable individual specialization"],
 "product_surfaces":["persistent-agent substrate","identity and lifecycle service"]},
"governance_structural_dna":{
 "technical_value":"constitutional constraints, governed change, anti-closure and succession controls",
 "potential_users":["AI governance team","regulated-system operator","multi-agent platform operator"],
 "customer_outcomes":["traceable governed changes","explicit constitutional constraints"],
 "product_surfaces":["AI governance control plane","constitutional policy engine"]},
"capability_discovery_evolution":{
 "technical_value":"capability discovery, mutation and governed self-improvement surfaces",
 "potential_users":["AI platform engineer","automation operator","research lab"],
 "customer_outcomes":["reuse and controlled evolution of capabilities","traceable improvement proposals"],
 "product_surfaces":["capability registry/evolution service","governed improvement pipeline"]},
"scientific_validation_evidence":{
 "technical_value":"experimentation, validation, audit, evidence and certification infrastructure",
 "potential_users":["research team","AI assurance team","model/system evaluator"],
 "customer_outcomes":["reproducible evidence","regression and falsifiability controls"],
 "product_surfaces":["AI assurance/evidence platform","validation harness"]},
"coordination_collective":{
 "technical_value":"distributed coordination, collective state and multi-agent organization",
 "potential_users":["multi-agent system operator","distributed automation integrator"],
 "customer_outcomes":["coordinated specialist agents","traceable collective operations"],
 "product_surfaces":["multi-agent coordination layer","collective orchestration service"]},
"interface_human_review":{
 "technical_value":"human interaction, review, dashboard and renderer surfaces",
 "potential_users":["human reviewer","system operator","non-developer administrator"],
 "customer_outcomes":["usable governed oversight","visible system state and decisions"],
 "product_surfaces":["operator console","governed human-review interface"]},
"external_world_tools":{
 "technical_value":"external data, web, API, connector and multimodal integration surfaces",
 "potential_users":["automation integrator","operations team"],
 "customer_outcomes":["access to external information and actions","integration with existing tools"],
 "product_surfaces":["integration gateway","tool/connector fabric"]},
"economic_resource_efficiency":{
 "technical_value":"cost, resource, quota and efficiency instrumentation",
 "potential_users":["platform operator","FinOps/AI operations team"],
 "customer_outcomes":["resource-aware execution","measurable cognitive cost/efficiency"],
 "product_surfaces":["AI efficiency observability","resource policy service"]},
"memory_continuity_archive":{
 "technical_value":"history, archive, continuity, lineage and checkpoint infrastructure",
 "potential_users":["long-running AI system operator","audit/compliance team"],
 "customer_outcomes":["recoverable longitudinal state","traceable lineage and history"],
 "product_surfaces":["civilizational memory service","continuity/archive layer"]},
"runtime_operations":{
 "technical_value":"execution, orchestration, transaction, rollback and runtime monitoring",
 "potential_users":["AI platform operator","automation engineer"],
 "customer_outcomes":["controlled execution","rollback and operational observability"],
 "product_surfaces":["cognitive runtime","governed orchestration engine"]},
"unclassified":{
 "technical_value":"UNKNOWN",
 "potential_users":["UNKNOWN"],"customer_outcomes":["UNKNOWN"],"product_surfaces":["UNKNOWN"]}}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if not SRC.is_file() or not INV.is_file(): raise SystemExit("P012_B_REFUSED: required A2/inventory missing")
inv_before=sha(INV)
a2=json.loads(SRC.read_text())
if a2.get("segmentation_identity_sha256")!=EXPECTED_A2_ID:
    raise SystemExit("P012_B_REFUSED: A2 identity drift")
components=a2.get("components",[])
candidate_paths=set(a2.get("product_surface_candidates",[]))
if len(candidate_paths)!=a2.get("product_surface_candidate_count"):
    raise SystemExit("P012_B_REFUSED: A2 candidate count inconsistent")

groups=defaultdict(list)
candidate_assignment=defaultdict(list)
for c in components:
    path=c["path"]
    for fam in c.get("families",["unclassified"]):
        groups[fam].append(path)
        if path in candidate_paths: candidate_assignment[path].append(fam)

mapped=set(candidate_assignment)
unmapped=sorted(candidate_paths-mapped)
if unmapped: raise SystemExit("P012_B_REFUSED: silent candidate loss")

aggregates=[]
for fam in sorted(groups):
    paths=sorted(set(groups[fam]))
    cand=sorted(p for p in paths if p in candidate_paths)
    prof=PROFILES.get(fam,PROFILES["unclassified"])
    evidence=Counter()
    for c in components:
        if c["path"] in set(paths):
            evidence.update(c.get("evidence_surfaces",[]))
    confidence="MEDIUM" if cand and fam!="unclassified" else ("LOW" if fam!="unclassified" else "UNKNOWN")
    aggregates.append({
      "family":fam,"component_count":len(paths),"candidate_count":len(cand),
      "source_components":paths,"candidate_components":cand,
      "technical_value":prof["technical_value"],
      "existing_evidence_surfaces":dict(sorted(evidence.items())),
      "potential_users":prof["potential_users"],
      "potential_customer_outcomes":prof["customer_outcomes"],
      "potential_product_surfaces":prof["product_surfaces"],
      "productization_effort":"UNKNOWN",
      "market_demand_evidence":"UNKNOWN",
      "willingness_to_pay_evidence":"UNKNOWN",
      "product_market_fit":"UNKNOWN",
      "hypothesis_status":"PRODUCT_HYPOTHESIS_NOT_MARKET_VALIDATION",
      "confidence":confidence})

# Every candidate is traceable to at least one aggregate.
trace={p:sorted(fs) for p,fs in sorted(candidate_assignment.items())}
payload={
 "schema":"oce.p012.product_relevance_mapping.v1","milestone":"P012-B",
 "status":"PRODUCT_RELEVANCE_MAPPING_COMPLETE",
 "a2_segmentation_identity_sha256":EXPECTED_A2_ID,
 "ontology_inventory_sha256":inv_before,
 "component_count":len(components),
 "candidate_count":len(candidate_paths),
 "mapped_candidate_count":len(mapped),
 "unmapped_candidate_count":len(unmapped),
 "aggregate_count":len(aggregates),
 "aggregates":aggregates,
 "candidate_to_aggregates":trace,
 "epistemic_policy":{
   "technical_surface_is_not_market_validation":True,
   "potential_users_are_hypotheses":True,
   "potential_customer_outcomes_are_hypotheses":True,
   "market_demand_unknown_without_empirical_evidence":True,
   "willingness_to_pay_unknown_without_empirical_evidence":True},
 "limits":[
   "Mapping aggregates technical evidence into product hypotheses; it does not demonstrate market demand.",
   "A component may map to multiple aggregates.",
   "Productization effort remains UNKNOWN until implementation/deployment requirements are measured.",
   "No product-market fit conclusion is made."],
 "functional_conclusion_only":True,"phenomenology_undetermined":True,
 "consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
payload["mapping_identity_sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
if sha(INV)!=inv_before: raise SystemExit("P012_B_REFUSED: ontology inventory mutated")
OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
print("P012_B_PRODUCT_RELEVANCE_MAPPING_OK")
print(f"components={len(components)}")
print(f"candidates={len(candidate_paths)}")
print(f"mapped_candidates={len(mapped)}/{len(candidate_paths)}")
print(f"aggregates={len(aggregates)}")
print("market_demand_evidence=UNKNOWN")
print("willingness_to_pay_evidence=UNKNOWN")
print("product_market_fit=UNKNOWN")
print("ontology_inventory_non_mutation=OK")
print("mapping_identity_sha256="+payload["mapping_identity_sha256"])
print("report="+str(OUT))
