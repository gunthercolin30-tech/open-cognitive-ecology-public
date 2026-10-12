from ontology.occ1h_g1_normative_gap_qualification import qualification

def test_exact_gap_classification():
 q=qualification(); r=q["records"]
 assert set(q["scope"])=={"A021","A040","A041","A042"}
 assert r["A040"]["classification"]=="NORMATIVE_GAP"
 assert all(r[a]["classification"]=="REPRESENTATION_BOUNDARY" for a in ("A021","A041","A042"))
 assert q["classification_counts"]=={"NORMATIVE_GAP":1,"REPRESENTATION_BOUNDARY":3,"FORMALIZATION_GAP":0,"INSUFFICIENT_EVIDENCE":0}

def test_gap_does_not_launder_to_resistance_or_resolution():
 q=qualification()
 assert q["normative_gap_implies_resisted"] is False
 assert q["root_inconclusive_resolved"]==0 and q["root_inconclusive_remaining_in_g1"]==4
 assert all(r["counts_as_resisted"] is False and r["counts_as_root_resolution"] is False for r in q["records"].values())
 assert all(r["current_adversarial_resolution"]=="INCONCLUSIVE_RETAINED" for r in q["records"].values())

def test_no_compiler_or_normative_repair_authorized():
 q=qualification()
 assert q["normative_sources_modified"] is False and q["compiler_modified"] is False
 assert q["compiled_profile_modified"] is False and q["verdicts_modified"] is False
 assert all(r["compiler_repair_authorized"] is False for r in q["records"].values())
 assert all(r["normative_source_rewrite_authorized"] is False for r in q["records"].values())

def test_a040_is_normative_not_formalization_gap():
 r=qualification()["records"]["A040"]
 assert r["basis"]=="CCAD.P7_EXPRESSES_EXCEPTION_EXPIRY_BUT_NO_SOURCE_BACKED_EXPIRY_PARAMETER_OR_CLOCK_SEMANTICS"
 assert r["classification"]!="FORMALIZATION_GAP"

def test_governance_and_epistemic_boundaries():
 q=qualification()
 assert q["gap_implies_authorization"] is False
 for k in ("authority_created","authorization_created","execution_created","occ1h_closed","occ1i_opened","p159_final_lock","p160_opened"):
  assert q[k] is False
 assert q["functional_conclusion_only"] is True
 assert q["phenomenology_undetermined"] is True
