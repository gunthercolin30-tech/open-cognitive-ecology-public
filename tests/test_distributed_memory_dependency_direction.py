from ontology.civilizational_historical_archive import (
    DEPENDENCIES as ARCHIVE_DEPENDENCIES,
)
from ontology.distributed_civilizational_memory import (
    DEPENDENCIES as MEMORY_DEPENDENCIES,
)
from ontology.inter_individual_coordination_protocol import (
    DEPENDENCIES as COORDINATION_DEPENDENCIES,
)
from ontology.memory_openness_refinement import (
    DEPENDENCIES as OPENNESS_DEPENDENCIES,
)


def test_distributed_memory_does_not_depend_on_downstream_consumers():
    assert "distributed_civilizational_memory" in ARCHIVE_DEPENDENCIES
    assert "distributed_civilizational_memory" in OPENNESS_DEPENDENCIES
    assert "trajectory_coordination" in COORDINATION_DEPENDENCIES

    assert "civilizational_historical_archive" not in MEMORY_DEPENDENCIES
    assert "memory_openness_refinement" not in MEMORY_DEPENDENCIES
    assert "inter_individual_coordination_protocol" not in MEMORY_DEPENDENCIES
