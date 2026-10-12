import copy
import json
import tempfile
from pathlib import Path

from ontology.comparative_science_certifier import (
    ComparativeScienceCertifier,
)


EXPECTED_COMPLETE = "COMPARATIVE_RF_SCIENCE_COMPLETE"
EXPECTED_INCOMPLETE = "COMPARATIVE_RF_SCIENCE_INCOMPLETE"


def assert_epistemic_guards(result):
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False


def test_nominal_and_determinism():
    certifier = ComparativeScienceCertifier()

    first = certifier.step(inputs={}, persist=False)
    second = certifier.step(inputs={}, persist=False)

    assert first["comparative_science_certification_status"] == (
        EXPECTED_COMPLETE
    )
    assert first["comparative_rf_science_complete"] is True
    assert first["certified"] is True

    assert first["certification_hash"] == second["certification_hash"]
    assert first["certification_checks"] == second["certification_checks"]

    assert all(first["certification_checks"].values())
    assert_epistemic_guards(first)


def test_persistence():
    with tempfile.TemporaryDirectory(
        prefix="oce_au10_persistence_"
    ) as tmp:
        certifier = ComparativeScienceCertifier(
            root=Path(tmp)
        )

        transient = certifier.step(
            inputs={},
            persist=False,
        )
        persisted = certifier.step(
            inputs={},
            persist=True,
        )

        assert transient["certification_hash"] == (
            persisted["certification_hash"]
        )
        assert transient["persisted"] is False
        assert transient["output_paths"] == {}

        assert persisted["persisted"] is True
        assert "json" in persisted["output_paths"]

        output_path = Path(
            persisted["output_paths"]["json"]
        )
        assert output_path.is_file()
        assert output_path.stat().st_size > 0

        exported = json.loads(
            output_path.read_text(encoding="utf-8")
        )

        assert exported[
            "comparative_science_certification_status"
        ] == EXPECTED_COMPLETE
        assert exported["certification_hash"] == (
            persisted["certification_hash"]
        )


def test_missing_module():
    certifier = ComparativeScienceCertifier()
    sources = certifier._build_sources()

    sources.pop("clustering_engine")

    result = certifier.step(
        inputs=sources,
        persist=False,
    )

    assert result[
        "comparative_science_certification_status"
    ] == EXPECTED_INCOMPLETE
    assert result["comparative_rf_science_complete"] is False
    assert result["certification_checks"]["completeness"] is False
    assert_epistemic_guards(result)


def test_low_coverage():
    certifier = ComparativeScienceCertifier()
    sources = copy.deepcopy(certifier._build_sources())

    sources["comparative_dashboard"][
        "dashboard_summary"
    ]["coverage_score"] = 0.0

    result = certifier.step(
        inputs=sources,
        persist=False,
    )

    assert result[
        "comparative_science_certification_status"
    ] == EXPECTED_INCOMPLETE
    assert result["certification_checks"]["coverage"] is False
    assert_epistemic_guards(result)


def test_invalid_hash():
    certifier = ComparativeScienceCertifier()
    sources = copy.deepcopy(certifier._build_sources())

    sources["comparative_history"]["dashboard_hash"] = "0" * 64

    result = certifier.step(
        inputs=sources,
        persist=False,
    )

    assert result[
        "comparative_science_certification_status"
    ] == EXPECTED_INCOMPLETE
    assert result["certification_checks"]["hash_integrity"] is False
    assert_epistemic_guards(result)


def test_epistemic_violation():
    certifier = ComparativeScienceCertifier()
    sources = copy.deepcopy(certifier._build_sources())

    sources["taxonomy_builder"]["phenomenology_proven"] = True

    result = certifier.step(
        inputs=sources,
        persist=False,
    )

    assert result[
        "comparative_science_certification_status"
    ] == EXPECTED_INCOMPLETE
    assert result["certification_checks"]["epistemic_guards"] is False
    assert result["certification_checks"][
        "absence_of_phenomenal_conclusions"
    ] is False

    # AU10 ne doit jamais propager la revendication fautive.
    assert_epistemic_guards(result)


def test_no_change_effective_hash():
    certifier = ComparativeScienceCertifier()
    sources = certifier._build_sources()
    history = sources["comparative_history"]

    assert history["change_set"]["change_type"] == "NO_CHANGE"
    assert history["record_hash"] is None
    assert history["chain_integrity"]["chain_valid"] is True
    assert history["chain_integrity"]["head_hash"]

    result = certifier.step(
        inputs=sources,
        persist=False,
    )

    assert result["certification_checks"]["hash_integrity"] is True
    assert result["history_record_hash"] == (
        history["chain_integrity"]["head_hash"]
    )
    assert result["history_record_created_in_call"] is False
    assert result[
        "comparative_science_certification_status"
    ] == EXPECTED_COMPLETE


def main():
    test_nominal_and_determinism()
    test_persistence()
    test_missing_module()
    test_low_coverage()
    test_invalid_hash()
    test_epistemic_violation()
    test_no_change_effective_hash()

    print("AU10_EXTENDED_VALIDATION_OK")


if __name__ == "__main__":
    main()
