from copy import deepcopy
from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

certifier = EcologicalCertifier()
base = build_context()
mutants = []

m1 = deepcopy(base)
m1["module_statuses"]["AW0_ecology_blueprint"] = "FAILED"
mutants.append(not certifier.step(inputs=m1, persist=False)["ecology_complete"])

m2 = deepcopy(base)
m2["evidence_manifest"] = []
mutants.append(not certifier.step(inputs=m2, persist=False)["ecology_complete"])

m3 = deepcopy(base)
m3["test_manifest"] = []
mutants.append(not certifier.step(inputs=m3, persist=False)["ecology_complete"])

m4 = deepcopy(base)
m4["civilization_theorem"]["civilization_theorem_status"] = "FAILED"
mutants.append(not certifier.step(inputs=m4, persist=False)["ecology_complete"])

killed = sum(bool(value) for value in mutants)
score = killed / len(mutants)
assert killed == len(mutants)
assert score == 1.0
print(f"AW14_MUTATION_SCORE_OK score={score:.2f} killed={killed} total={len(mutants)}")
