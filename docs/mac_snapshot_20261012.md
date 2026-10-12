# Mac source snapshot — 2026-10-12

This branch publishes the Python sources supplied by the repository owner in
`oce-code-20261012-231430.zip`, based on public commit
`fa45da65183cff5f5c5ea07d1b735b1b93650a24`.

It contains 110 modified and 3,509 added source files, plus this report.
The supplied source files are preserved without application-code fixes.
The owner's working tree and its private Git history were not imported.

## Publication scope

Included: top-level Python scripts, existing project source packages, `tests/`,
`validation/`, and the new `oif/` and `oif_review/` packages.
The supplied README and dependency manifests match the existing public versions.

Excluded: `.venv-oif/`, `.oif_backups/`, the `~/` directory, audit bundles,
copied source collections, and validation-evidence collections. The public
repository's existing ignore policy also excludes generated
`ontology/dependency_registry.py`.

The archive contained Python files and five selected documentation/dependency
files. It did not contain the Mac's complete documentation, configuration,
schemas, shell tools, assets, or runtime data. Existing public non-Python files
were retained; absence from this archive was not treated as a deletion.
This is a source snapshot, not a complete backup or a certification that all
new experimental runtimes are independently reproducible.

An automated search found no matches for the checked GitHub/API/AWS credential,
private-key, and literal credential-assignment patterns in the candidate Python
sources. This check is limited to those patterns.

## Validation

Validation used Python 3.12.14 and pytest 9.1.1 with the public test dependencies.

- The original public baseline passed all 934 tests before importing this snapshot.
- Parsing 4,690 Python files found one syntax error:
  `ao5_extended_acceptance_suite_v2.py:96` has an unterminated string literal.
- The normal `python -m pytest -q` command stopped during collection:
  `tests/test_reflexive_threshold_dependency_direction.py` imports `DEPENDENCIES`
  from `ontology.consciousness_readiness_index`, where the snapshot no longer
  defines that name.
- To diagnose the remaining tests without changing or disabling assertions,
  `python -m pytest --continue-on-collection-errors -q` was run. It completed with
  **964 passed, 3 failed, and 1 collection error** (nonzero exit status).

The three executed failures were:

1. `tests/test_ontology_organization.py`: dependency classification contains four
   heuristic references instead of classifying every reference as a policy decision.
2. `tests/test_ontology_semantic_review.py`: 98 semantic-review findings remain
   for effectful modules.
3. `tests/test_replication_recovery_dependency_direction.py`: the replication
   engine now requires a `filesystem_effect_context_provider`, which the existing
   test does not supply.

These checks cover the configured `tests/` suite. The numerous standalone
validation scripts, final-lock programs, optional UI, and live external-service
integrations were not executed.

The snapshot is published on `sync/mac-20261012`; the tested public `main` branch
is retained. Resolve the recorded failures and supply any required non-Python
resources before integrating this snapshot into `main`.
