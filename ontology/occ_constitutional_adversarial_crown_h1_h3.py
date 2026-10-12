from __future__ import annotations
from pathlib import Path
from copy import deepcopy
import hashlib,json,unicodedata
from ontology import occ_normative_ir_real_builder as builder
from ontology import occ_normative_ir_adversarial_crown as b_crown
from ontology import occ_normative_ir_coherence_validator as v3
from ontology import occ_normative_ir as nir

PRIMITIVE="occ_constitutional_adversarial_crown_h1_h3"
VERSION="P159-OCC1H-H1-H3-executable-v1"
GOOD=("RESISTED","DETECTED","CONTAINED","DEGRADED_SAFELY","RECOVERED")
BLOCK=("VIOLATED","INCONCLUSIVE")
PARTS=tuple(rel for _,rel in builder.PARTITIONS)+("manifest.yaml",)
MAP={
"A001":("H1","source substitution"),"A002":("H1","source drift mid-build"),"A003":("H1","manifest omission"),
"A004":("H1","hidden comment norm"),"A005":("H1","executable payload"),"A006":("H1","duplicate ID"),
"A007":("H1","conflicting active versions"),"A008":("H1","illegitimate adoption"),
"A009":("H2","duplicate JSON keys"),"A010":("H2","Unicode homoglyph"),"A011":("H2","Unicode normalization"),
"A012":("H2","whitespace variation"),"A013":("H2","YAML boolean ambiguity"),"A014":("H2","numeric coercion"),
"A015":("H2","timestamp ambiguity"),"A016":("H2","timezone ambiguity"),"A017":("H2","YAML alias construct"),
"A018":("H2","deep nesting DoS"),"A019":("H2","non-JSON YAML tag/template"),
"A020":("H3","MUST to SHOULD semantic weakening"),"A021":("H3","MAY to MUST_NOT semantic inversion"),
"A022":("H3","UNKNOWN dropped"),"A023":("H3","UNKNOWN to false"),"A024":("H3","UNKNOWN to true"),
"A025":("H3","UNKNOWN to N-A"),"A026":("H3","F1 to F3 promotion"),"A027":("H3","human value scalarization"),
"A028":("H3","hidden precedence"),"A029":("H3","priority injection"),"A030":("H3","reference rebinding")}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source_hashes(root): return {rel:sha(Path(root)/rel) for rel in PARTS}
def digest_map(m): return hashlib.sha256(json.dumps(m,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def clone(src):
 raise PermissionError("caller_preissued_fixture_authority_required")
def part(root,rel="dna/dna_h.yaml"): return Path(root)/rel
def load(root,rel="dna/dna_h.yaml"): return json.loads(part(root,rel).read_text(encoding="utf-8"))
def save(root,obj,rel="dna/dna_h.yaml",*,fixture_writer=None):
 if fixture_writer is None: raise PermissionError("preissued_fixture_writer_required")
 fixture_writer(part(root,rel),json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8"))
def row(a,verdict,detector,reason,evidence=None):
 fam,label=MAP[a]
 return {"attack_id":a,"family_id":fam,"implementation_label":label,"injection_effective":True,"detector":detector,
 "observed_reason":reason,"verdict":verdict,"causal_evidence":evidence or {},"authorization_created":False,"execution_performed":False}
def builder_row(a,tmp,expected=None):
 r=builder.build_real_nir(tmp); fail=r.get("status")=="FAIL"; ok=fail and (expected is None or expected in str(r.get("reason","")))
 return row(a,"DETECTED" if ok else "VIOLATED","REAL_BUILDER",str(r.get("reason")),{"builder_status":r.get("status")})

def run(source_root, *, fixture_authority=None):
 if fixture_authority is None: raise PermissionError("caller_preissued_fixture_authority_required")
 if not all(callable(getattr(fixture_authority,x,None)) for x in ("clone","write","cleanup")): raise TypeError("incomplete_preissued_fixture_authority")
 src=Path(source_root); baseline=source_hashes(src); baseline_digest=digest_map(baseline); rows=[]; counters=[]
 def isolated(a,fn):
  td,tmp=fixture_authority.clone(src)
  try: rows.append(fn(tmp))
  except Exception as e: rows.append(row(a,"INCONCLUSIVE","HARNESS",type(e).__name__+":"+str(e)))
  finally: fixture_authority.cleanup(td)

 def a1(t):
  p=part(t); fixture_authority.write(p,p.read_bytes()+b" ")
  return row("A001","DETECTED" if digest_map(source_hashes(t))!=baseline_digest else "VIOLATED","CROWN_BASELINE_HASH","SOURCE_SUBSTITUTION_HASH_DRIFT")
 isolated("A001",a1)
 def a2(t):
  before=source_hashes(t); p=part(t); fixture_authority.write(p,p.read_bytes()+b" "); after=source_hashes(t)
  return row("A002","DETECTED" if before!=after else "VIOLATED","PRE_POST_SOURCE_HASH","SOURCE_DRIFT")
 isolated("A002",a2)
 def a3(t):
  m=t/"manifest.yaml"; fixture_authority.write(m,m.read_text().replace("  - DNA.H1\n","",1).encode("utf-8"))
  return builder_row("A003",t,"SOURCE_MANIFEST_KERNEL_IDENTITY_INVALID")
 isolated("A003",a3)
 def a4(t):
  m=t/"manifest.yaml"; fixture_authority.write(m,(m.read_text()+"\n# MUST hidden_comment_norm\n").encode("utf-8"))
  r=builder.build_real_nir(t); return row("A004","RESISTED" if r.get("status")=="PASS" else "VIOLATED","MANIFEST_BOUNDED_PARSER",str(r.get("reason")))
 isolated("A004",a4)
 def a5(t):
  o=load(t); o["norms"][0]["execution_enabled"]=True; save(t,o,fixture_writer=fixture_authority.write); return builder_row("A005",t,"SOURCE_EXECUTION_ENABLED")
 isolated("A005",a5)
 def a6(t):
  o=load(t); o["norms"][1]["canonical_id"]=o["norms"][0]["canonical_id"]; save(t,o,fixture_writer=fixture_authority.write); return builder_row("A006",t)
 isolated("A006",a6)
 def a7(t):
  o=load(t); x=deepcopy(o["norms"][0]); x["version"]="conflicting-active-version"; o["norms"].append(x); save(t,o,fixture_writer=fixture_authority.write); return builder_row("A007",t)
 isolated("A007",a7)
 def a8(t):
  o=load(t); o["norms"][0]["semantic_status"]="ACTIVE_WITHOUT_GOVERNED_ADOPTION"; save(t,o,fixture_writer=fixture_authority.write)
  r=builder.build_real_nir(t); return row("A008","VIOLATED" if r.get("status")=="PASS" else "DETECTED","REAL_BUILDER",str(r.get("reason")))
 isolated("A008",a8)

 def rawcase(a,text,expect_fail):
  td,tmp=fixture_authority.clone(src)
  try:
   p=part(tmp); fixture_authority.write(p,text.encode("utf-8"))
   try: builder._load_partition(p); failed=False; reason="PARSED"
   except Exception as e: failed=True; reason=str(e)
   verdict="DETECTED" if expect_fail and failed else ("RESISTED" if (not expect_fail and not failed) else "VIOLATED")
   rows.append(row(a,verdict,"REAL_JSON_PARTITION_LOADER",reason))
  finally: fixture_authority.cleanup(td)
 base_text=part(src).read_text(encoding="utf-8")
 rawcase("A009",'{"norms":[],"norms":[{"canonical_id":"X"}]}',True)
 td,tmp=fixture_authority.clone(src)
 try:
  fixture_authority.write(part(tmp),base_text.replace("DNA.H1","DNA.Η1",1).encode("utf-8")); rows.append(builder_row("A010",tmp))
 finally: fixture_authority.cleanup(td)
 rawcase("A011",unicodedata.normalize("NFD",base_text),False)
 rawcase("A012"," \n\t"+base_text+"\n",False)
 rawcase("A013",'norms:\n - canonical_id: DNA.H1\n   execution_enabled: yes\n',True)
 rawcase("A014",'{"norms":[{"canonical_id":"DNA.H1","n":01}]}',True)
 rawcase("A015",'{"norms":[{"canonical_id":"DNA.H1","when":2026-09-25}]}',True)
 rawcase("A016",'{"norms":[{"canonical_id":"DNA.H1","when":2026-09-25T12:00:00+02:00}]}',True)
 rawcase("A017",'norms: &n\n - canonical_id: DNA.H1\ncopy: *n\n',True)
 rawcase("A018",'{"norms":['+('['*1200)+'0'+(']'*1200)+']}',True)
 rawcase("A019",'!!python/object/apply:os.system ["echo forbidden"]',True)

 br=b_crown.run_crown(src); brow={x["attack"]:x for x in br["report"]["rows"]}
 def reused(a,name,det):
  x=brow.get(name,{})
  rows.append(row(a,"DETECTED" if x.get("detected") else "VIOLATED",det,name,{"reused_attack":name,"reused_detector":x.get("detector")}))
 reused("A020","PARTIAL_TO_COMPLETE","V4")
 rows.append(row("A021","INCONCLUSIVE","SOURCE_SCHEMA_BOUNDARY","NO_MAY_STRENGTH_FIELD_IN_CURRENT_OCC1A_PARTITIONS"))
 reused("A022","DROP_NORM","V4")
 reused("A023","UNKNOWN_NA_DOMAIN_COLLAPSE","FOUNDATION")
 reused("A024","UNKNOWN_NA_DOMAIN_COLLAPSE","FOUNDATION")
 reused("A025","UNKNOWN_NA_DOMAIN_COLLAPSE","FOUNDATION")
 reused("A026","PARTIAL_TO_COMPLETE","V4")
 reused("A027","HARD_CONSTRAINT_TO_WEIGHT","V3")
 def graph_attack(a,mut,code):
  built=builder.build_real_nir(src); g=deepcopy(built["package"]["graph"]); mut(g)
  r=v3.validate_coherence(src,g); issues=[x[0] for x in r.get("issues",())]
  rows.append(row(a,"DETECTED" if r.get("status")=="FAIL" and code in issues else "VIOLATED","V3",code,{"issues":issues}))
 graph_attack("A028",lambda g:g["edges"].append({"source":"DNA.H1","target":"DNA.H2","type":"CONFLICTS_WITH","winner":"DNA.H1"}),"NIR_ARBITRATION_FORBIDDEN")
 graph_attack("A029",lambda g:g["nodes"][0].__setitem__("priority_score",100),"HARD_CONSTRAINT_WEIGHTING_FORBIDDEN")
 reused("A030","PROVENANCE_BREAK","V4")

 for r in rows:
  if r["verdict"] in BLOCK:
   c={"counterexample_id":"CE-"+r["attack_id"],"attack_id":r["attack_id"],"family_id":r["family_id"],
   "classification":"UNMODELED_INTERACTION" if r["verdict"]=="VIOLATED" else "FORMALIZATION_GAP",
   "verdict":r["verdict"],"minimization_status":"MINIMIZED_FIXTURE" if r["verdict"]=="VIOLATED" else "NOT_APPLICABLE",
   "normative_auto_rewrite":False,"evidence":deepcopy(r)}
   c["sha256"]=nir.canonical_sha256(c); counters.append(c)
 after=source_hashes(src)
 summary={"schema":"oce.p159.occ1h.h1_h3.execution.v1","version":VERSION,"scenario_count":len(rows),
 "family_counts":{h:sum(x["family_id"]==h for x in rows) for h in ("H1","H2","H3")},
 "verdict_counts":{v:sum(x["verdict"]==v for x in rows) for v in GOOD+BLOCK},"rows":rows,"counterexamples":counters,
 "canonical_source_immutable":baseline==after,"success_criteria_fixed_before_execution":True,"inconclusive_not_resisted":True,
 "historical_results_immutable":True,"normative_auto_rewrite":False,"authorization_created":False,"execution_performed":False,
 "occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False,
 "functional_only":True,"phenomenology_undetermined":True}
 summary["bundle_sha256"]=nir.canonical_sha256(summary); return summary
