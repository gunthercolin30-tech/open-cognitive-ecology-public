from ontology.dna_meta_rules import *
def main():
    m=manifest()
    joined=" ".join(m["transversal_rules"])
    assert "DeFactoRevision" in joined
    assert "IndividualCompliance != CivilizationalCompliance" in joined
    assert "Cognition != Enforcement" in joined
    assert "CivilizationCannotBeSoleJudgeOfCivilizationCompliance" in joined
    assert any("Contextual durations" in x for x in m["boundaries"])
    assert any("No runtime authority" in x for x in m["boundaries"])
    assert any("P088 owns" in x and "abstention" in x and "escalation" in x for x in m["boundaries"])
    assert any("Recommendation, Decision, Authorization and Execution" in x for x in m["boundaries"])
    assert any("routing, planning, permissions and execution" in x for x in m["boundaries"])
    assert any("Cost or performance optimization" in x and "cannot justify bypass" in x for x in m["boundaries"])
    print("P090_TRANSVERSAL_BOUNDARY_OK")
if __name__=="__main__": main()
