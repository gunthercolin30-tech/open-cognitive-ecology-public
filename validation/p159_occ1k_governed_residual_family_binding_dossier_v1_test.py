from validation import p159_occ1k_governed_residual_family_binding_dossier_v1 as a
def D():return a.build()
def test_four_families_24_rules():assert (D()["counts"]["families"],D()["counts"]["rules"])==(4,24)
def test_no_proven_additional_consumer_yet():assert D()["counts"]["families_with_proven_additional_consumer"]==0
def test_family_not_evidence():assert D()["semantics"]["family_membership_is_not_consumer_evidence"]
def test_uniform_candidates_not_evidence():assert D()["semantics"]["uniform_candidate_set_is_not_binding_evidence"]
def test_no_automatic_family_binding():assert all(not x["automatic_family_binding_permitted"] for x in D()["families"])
def test_source_evidence_required():assert all(x["decision_state"]=="SOURCE_SEMANTIC_EVIDENCE_REQUIRED" for x in D()["families"])
def test_boundaries():
 b=D()["boundaries"];assert not b["binding_layer_modified"] and not b["cnp_modified"] and not b["runtime_binding_created"] and not b["p160b_opened"]
def test_deterministic():assert D()==D()
