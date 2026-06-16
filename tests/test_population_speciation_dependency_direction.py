from ontology.civilizational_runtime_speciation import (
    DEPENDENCIES as SPECIATION_DEPENDENCIES,
)
from ontology.distributed_population_runtime import (
    DEPENDENCIES as POPULATION_DEPENDENCIES,
)


def test_speciation_consumes_population_without_reverse_dependency():
    assert "distributed_population_runtime" in SPECIATION_DEPENDENCIES
    assert "civilizational_runtime_speciation" not in POPULATION_DEPENDENCIES
