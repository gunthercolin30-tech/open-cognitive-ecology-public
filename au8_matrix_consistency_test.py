from ontology.comparative_dashboard import ComparativeDashboard


def main():
    r = ComparativeDashboard().step(
        inputs={},
        persist=False,
    )

    similarity = r["similarity_matrix"]
    distance = r["distance_matrix"]

    assert isinstance(similarity, dict)
    assert isinstance(distance, dict)
    assert set(similarity) == set(distance)

    for a in similarity:
        assert a in similarity[a]
        assert a in distance[a]

        assert abs(float(similarity[a][a]) - 1.0) < 1e-12
        assert abs(float(distance[a][a])) < 1e-12

        for b in similarity:
            assert b in similarity[a]
            assert b in distance[a]

            assert abs(
                float(similarity[a][b]) -
                float(similarity[b][a])
            ) < 1e-12

            assert abs(
                float(distance[a][b]) -
                float(distance[b][a])
            ) < 1e-12

            assert 0.0 <= float(similarity[a][b]) <= 1.0
            assert 0.0 <= float(distance[a][b]) <= 1.0

    print("AU8_MATRIX_CONSISTENCY_OK")


if __name__ == "__main__":
    main()
