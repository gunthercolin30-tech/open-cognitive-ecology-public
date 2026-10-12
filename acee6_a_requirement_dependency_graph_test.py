from acee6_a_hardening_contract import REQUIREMENT_DEPENDENCIES
from acee6_test_requirements_registry import TEST_REQUIREMENTS


def main():
    identifiers = {item["test_id"] for item in TEST_REQUIREMENTS}
    outgoing = {identifier: [] for identifier in identifiers}
    indegree = {identifier: 0 for identifier in identifiers}
    for target, dependencies in REQUIREMENT_DEPENDENCIES.items():
        assert target in identifiers
        for source in dependencies:
            assert source in identifiers
            assert source != target
            outgoing[source].append(target)
            indegree[target] += 1
    queue = sorted(node for node, degree in indegree.items() if degree == 0)
    visited = []
    while queue:
        node = queue.pop(0)
        visited.append(node)
        for target in outgoing[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
                queue.sort()
    assert len(visited) == len(identifiers)
    print("ACEE6_A_REQUIREMENT_DEPENDENCY_GRAPH_OK")


if __name__ == "__main__":
    main()
