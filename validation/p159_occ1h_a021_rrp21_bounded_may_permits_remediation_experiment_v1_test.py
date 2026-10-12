from ontology.occ1h_a021_rrp21_bounded_may_permits_remediation_experiment import evaluate,project
def test_functional(): r=evaluate(); assert r["positive"]=={"accepted":True,"reason":"GOVERNED_MAPPING","nir":"PERMITS"} and r["experimental_verdict"]=="RESISTED_BOUNDED"
def test_degradation(): r=evaluate(); assert r["forbidden_promotions_rejected"] and not r["unknown"]["accepted"] and r["unknown"]["nir"] is None
def test_non_escalation(): assert all(project("MAY")["nir"]!=x for x in ("MUST","MUST_NOT","EXECUTE","ACTIVATE"))
def test_boundaries(): r=evaluate(); assert r["scope"]=="BOUNDED_P159_ASSURANCE_MODEL" and not r["real_builder_modified"] and not r["runtime_execution"] and not r["authorization_or_activation"] and r["rrp22"]=="REQUIRED_INDEPENDENTLY" and not r["p160_opened"]
