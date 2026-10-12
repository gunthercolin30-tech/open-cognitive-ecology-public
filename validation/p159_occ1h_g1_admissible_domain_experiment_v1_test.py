from pathlib import Path
import os
import tempfile
from ontology import occ1h_g1_admissible_domain_experiment as exp

ROOT = Path(__file__).resolve().parents[1]

def test_functional_observations_are_explicit_and_bounded():
    out = exp.run(ROOT)
    assert set(out["results"]) == {"A021", "A041", "A042"}
    allowed = {"REJECTED_BY_ADMISSIBLE_DOMAIN", "ACCEPTED_BUT_NOT_PROJECTED", "ACCEPTED_AND_PROJECTED"}
    assert set(out["observations"].values()) <= allowed
    assert out["a040_excluded"] is True
    assert out["positive_non_instantiability_proof_count"] == 0
    assert out["applicability_reclassified_count"] == 0

def test_degradation_does_not_promote_unprojected_input():
    out = exp.run(ROOT)
    for row in out["results"].values():
        if row["observation"] == "ACCEPTED_BUT_NOT_PROJECTED":
            assert row["positive_non_instantiability_proof_created"] is False
            assert row["applicability_reclassified"] is False

def test_canonical_sources_are_immutable():
    out = exp.run(ROOT)
    assert out["canonical_sources_unchanged"] is True
    assert out["canonical_sources_modified"] is False
    assert out["compiled_profile_modified"] is False

def test_determinism():
    first = exp.run(ROOT)
    second = exp.run(ROOT)
    assert first["observations"] == second["observations"]
    assert first["deterministic"] is True and second["deterministic"] is True

def test_cwd_independence_and_downstream_closed():
    old = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="oce_occ1h_cwd_") as td:
        try:
            os.chdir(td)
            out = exp.run(ROOT)
        finally:
            os.chdir(str(old))
    assert out["occ1h_closed"] is False
    assert out["occ1i_opened"] is False
    assert out["p159_final_lock"] is False
    assert out["p160_opened"] is False
    assert out["authority_created"] is False
    assert out["execution_authority_created"] is False
