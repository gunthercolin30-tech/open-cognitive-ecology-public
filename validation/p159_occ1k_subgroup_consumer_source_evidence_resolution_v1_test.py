from validation import p159_occ1k_subgroup_consumer_source_evidence_resolution_v1 as a
def D():return a.build()
def test_21_subgroups():assert D()["counts"]["subgroups"]==21
def test_no_binding_adopted():assert all(not x["binding_adopted"] for x in D()["subgroups"])
def test_direct_only_known_semantics():
 for x in D()["subgroups"]:
  if x["evidence_strength"]=="DIRECT_SEMANTIC_ROLE_MATCH":assert x["source_object_id"] in {"F9","F10","F11","F16"}
def test_contextual_not_promoted():
 assert all(not x["binding_adopted"] for x in D()["subgroups"] if x["evidence_strength"].startswith("CONTEXTUAL"))
def test_genesis_unresolved():
 x=next(x for x in D()["subgroups"] if "GENESIS.G0" in x["rule_ids"]);assert x["evidence_strength"]=="UNRESOLVED" and not x["candidate_consumers"]
def test_hash_bound_sources():assert len(D()["inputs"]["source_hashes"])==4
def test_boundaries():
 b=D()["boundaries"];assert not b["rule_bindings_modified"] and not b["cnp_modified"] and not b["runtime_binding_created"] and not b["p160b_opened"]
def test_deterministic():assert D()==D()
