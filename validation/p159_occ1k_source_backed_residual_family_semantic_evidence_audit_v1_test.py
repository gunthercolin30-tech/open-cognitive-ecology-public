from validation import p159_occ1k_source_backed_residual_family_semantic_evidence_audit_v1 as a
def D():return a.build()
def test_24_rules_four_families():assert D()["rules_audited"]==24 and D()["counts"]["families"]==4
def test_all_canonical_norms_present():assert sum(x["rule_count"] for x in D()["family_audits"])==24
def test_genesis_f0_preserved():
 x=next(m for f in D()["family_audits"] for m in f["members"] if m["rule_id"]=="GENESIS.G0");assert x["formalization"]=="F0_HUMAN_INTERPRETIVE"
def test_no_family_binding_declared():assert D()["counts"]["safe_family_bindings"]==0
def test_no_keyword_consumer_mapping():assert D()["policy"]["source_text_not_keyword_mapped_to_consumer"]
def test_source_hashes_bound():assert len(D()["inputs"]["canonical_source_hashes"])==4
def test_boundaries():
 b=D()["boundaries"];assert not b["rule_bindings_modified"] and not b["cnp_modified"] and not b["runtime_binding_created"] and not b["p160b_opened"]
def test_deterministic():assert D()==D()
