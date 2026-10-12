from validation import p159_occ1k_source_backed_rule_consumer_derivation_audit_v1 as a
def D(): return a.build()
def test_48_rules(): assert D()["counts"]["rules"]==48
def test_exact_consumers(): assert set(D()["allowed_consumers"])==set(a.ALLOWED)
def test_ccad_contract_binding(): assert all(set(x["guaranteed_contract_consumers"])=={"NormResolver","CCAD"} for x in D()["rules"] if x["rule_id"].startswith("CCAD."))
def test_dna_not_overpromoted(): assert all(x["unresolved_reasons"] for x in D()["rules"] if x["rule_id"].startswith("DNA."))
def test_genesis_preserved_unresolved():
 x=next(x for x in D()["rules"] if x["rule_id"]=="GENESIS.G0"); assert not x["guaranteed_contract_consumers"] and x["unresolved_reasons"]
def test_no_keyword_binding(): assert D()["derivation_policy"]["keyword_only_binding_forbidden"]
def test_boundaries():
 b=D()["boundaries"]; assert not b["cnp_modified"] and not b["rule_bindings_modified"] and not b["runtime_binding_created"] and not b["p160b_opened"]
def test_deterministic(): assert D()==D()
