from ontology.occ1h_g1_attack_applicability_resolution import qualification

def test_scope_and_immutability():
 q=qualification(); assert set(q["scope"])=={"A021","A040","A041","A042"}
 assert q["historical_verdicts_immutable"] is True
 assert all(r["historical_verdict"]=="INCONCLUSIVE" for r in q["records"].values())

def test_precommitted_criteria_unchanged():
 q=qualification(); assert q["success_criteria_modified"] is False
 assert all(r["success_criteria_fixed_before_execution"] for r in q["records"].values())
 assert all(r["success_criteria_modified"] is False for r in q["records"].values())

def test_no_laundering_noninstantiability_to_resistance():
 q=qualification(); assert q["source_absent_implies_resisted"] is False
 assert q["root_inconclusive_resolved"]==0 and q["root_inconclusive_remaining_in_g1"]==4
 assert all(r["current_adversarial_resolution"]=="INCONCLUSIVE_RETAINED" for r in q["records"].values())

def test_a040_distinct():
 r=qualification()["records"]
 assert r["A040"]["applicability"]=="PRINCIPLE_PRESENT_BUT_OPERATIONAL_EXPIRY_SEMANTICS_UNDERSPECIFIED"
 assert all("LACKS_SOURCE_BACKED" in r[a]["applicability"] for a in ("A021","A041","A042"))

def test_boundaries_closed():
 q=qualification(); assert q["normative_semantics_invented"] is False and q["verdicts_modified"] is False
 for k in ("authority_created","authorization_created","execution_created","occ1h_closed","occ1i_opened","p159_final_lock","p160_opened"):
  assert q[k] is False
 assert q["functional_conclusion_only"] is True and q["phenomenology_undetermined"] is True
