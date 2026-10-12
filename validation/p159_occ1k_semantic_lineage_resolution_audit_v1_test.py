from validation import p159_occ1k_semantic_lineage_resolution_audit_v1 as a
def test_48_lineages(): r=a.build(); assert r["rule_count"]==48 and r["lineage_complete"]
def test_expected_class_distribution():
    c=a.build()["compilation_class_counts"]; assert c["CC1_DETERMINISTIC_ENFORCEMENT"]==0 and c["CC2_RUNTIME_EVALUATION"]==47 and c["CC3_ESCALATION_HUMAN_CCAD_REQUIRED"]==1
def test_source_and_nir_identity_present(): assert all(x["source_norm_ids"] and x["nir_node_ids"] for x in a.build()["rules"])
def test_no_consumer_inference_from_class(): assert all(not x["consumer_mapping_derivable_from_compilation_class"] for x in a.build()["rules"])
def test_semantic_gap_preserved(): assert not a.build()["findings"]["unique_rule_to_consumer_mapping_derivable"]
def test_boundaries():
    b=a.build()["boundaries"]; assert b["fl_b3"]=="BLOCKED" and not any(b[k] for k in ("cnp_modified","canonical_source_modified","runtime_binding_created","runtime_enforcement_proven","authorization_created","execution_performed","lock_ready","lock_granted","p160b_opened"))
def test_deterministic(): assert a.build()==a.build()
