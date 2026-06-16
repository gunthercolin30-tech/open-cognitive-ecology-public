from ontology.constitutional_benchmarks import (
    DEPENDENCIES as BENCHMARK_DEPENDENCIES,
)
from ontology.constitutional_stress_tests import (
    DEPENDENCIES as STRESS_TEST_DEPENDENCIES,
)
from ontology.runtime_constitutional_integration import (
    DEPENDENCIES as RUNTIME_INTEGRATION_DEPENDENCIES,
)


def test_constitutional_evaluation_dependencies_follow_consumer_chain():
    assert "constitutional_stress_tests" in BENCHMARK_DEPENDENCIES
    assert "constitutional_benchmarks" in RUNTIME_INTEGRATION_DEPENDENCIES

    assert "constitutional_benchmarks" not in STRESS_TEST_DEPENDENCIES
    assert "runtime_constitutional_integration" not in STRESS_TEST_DEPENDENCIES
