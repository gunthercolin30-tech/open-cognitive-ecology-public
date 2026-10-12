from ontology.recovery_engine import RecoveryEngine


DIMENSIONS = (
    "stability",
    "integration",
    "continuity",
    "governance",
    "complexity",
    "diversity",
    "recovery_capacity",
    "openness",
)


def state(value):
    return {
        dimension: value
        for dimension in DIMENSIONS
    }


def observation(day, value):
    return {
        "timestamp_utc": f"2027-09-{day:02d}T00:00:00Z",
        "state_vector": state(value),
        "data_quality": 0.98,
        "synthetic": True,
    }


def build_inputs(values):
    return {
        "degeneration_result": {
            "degeneration_detected": True,
            "degeneration_status":
                "FUNCTIONAL_PROGRESSIVE_DEGENERATION_DETECTED",
        },
        "baseline": state(0.88),
        "observations": [
            observation(day, value)
            for day, value in enumerate(values, start=1)
        ],
    }


# Même tendance globale :
# baseline → creux → récupération progressive.
clean_values = [
    0.88,
    0.42,
    0.52,
    0.56,
    0.60,
    0.63,
    0.66,
    0.68,
    0.69,
]

noisy_values = [
    0.88,
    0.42,
    0.55,
    0.49,
    0.63,
    0.60,
    0.67,
    0.64,
    0.69,
]

engine = RecoveryEngine()

clean = engine.step(
    inputs=build_inputs(clean_values),
    persist=False,
)

noisy_first = engine.step(
    inputs=build_inputs(noisy_values),
    persist=False,
)

noisy_second = engine.step(
    inputs=build_inputs(noisy_values),
    persist=False,
)


accepted_statuses = {
    "FUNCTIONAL_RECOVERY_EMERGING",
    "FUNCTIONAL_PARTIAL_RECOVERY_DETECTED",
}

assert clean["recovery_detected"] is True
assert noisy_first["recovery_detected"] is True

assert clean["recovery_status"] in accepted_statuses
assert noisy_first["recovery_status"] in accepted_statuses

assert clean["transient_rebound_detected"] is False
assert noisy_first["transient_rebound_detected"] is False

assert noisy_first["baseline_restored"] is False
assert noisy_first["new_regime_reconstruction"] is False

# Le bruit modéré ne doit pas modifier fortement le score.
score_delta = abs(
    clean["recovery_score"]
    - noisy_first["recovery_score"]
)

assert score_delta <= 0.15

# La persistance reste fonctionnellement suffisante.
assert noisy_first["persistence_score"] >= 0.70

# Déterminisme.
assert (
    noisy_first["recovery_hash"]
    == noisy_second["recovery_hash"]
)
assert (
    noisy_first["recovery_score"]
    == noisy_second["recovery_score"]
)
assert (
    noisy_first["recovery_status"]
    == noisy_second["recovery_status"]
)

# Garde-fous épistémologiques.
assert noisy_first["consciousness_proven"] is False
assert noisy_first["qualia_proven"] is False
assert noisy_first["subjectivity_proven"] is False
assert noisy_first["phenomenology_proven"] is False
assert noisy_first["functional_conclusion_only"] is True
assert noisy_first["phenomenology_undetermined"] is True

print("AV6_NOISE_ROBUSTNESS_OK")
