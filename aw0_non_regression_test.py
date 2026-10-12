\
from ontology.ecology_blueprint import EcologyBlueprint
from ontology.cognitive_ecology import CognitiveEcologyPrimitive
from ontology.open_cognitive_ecology import OpenCognitiveEcologyPrimitive


def main():
    blueprint = EcologyBlueprint().step(inputs={}, persist=False)
    cognitive = CognitiveEcologyPrimitive().step()
    open_ecology = OpenCognitiveEcologyPrimitive().step()

    assert blueprint["primitive"] == "ECOLOGY_BLUEPRINT"
    assert cognitive["principle"] == "COGNITIVE_ECOLOGY"
    assert open_ecology["principle"] == "OPEN_COGNITIVE_ECOLOGY"
    assert "cognitive_ecology" in blueprint["reused_foundations"]
    assert "open_cognitive_ecology" in blueprint["reused_foundations"]
    assert blueprint["functional_conclusion_only"] is True
    assert blueprint["phenomenology_undetermined"] is True
    print("AW0_NON_REGRESSION_OK")


if __name__ == "__main__":
    main()
