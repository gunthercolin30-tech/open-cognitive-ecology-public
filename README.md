# Open Cognitive Ecology

Open Cognitive Ecology is an experimental research framework for persistent
cognitive agents operating under conditions of non-closure.

It explores how cognitive, ecological, social, and civilizational systems can
remain adaptive when their environment, goals, memories, and constraints cannot
be fully closed or specified in advance.

## What This Repository Contains

This public snapshot contains the source code, tests, ontology modules,
documentation, and replication metadata needed to inspect and run the current
Open Cognitive Ecology framework.

The project currently focuses on:

- constraint-based cognition and open-ended adaptation
- persistent agents and memory architectures
- narrative continuity and identity preservation
- ontology organization and dependency direction
- ecological, social, and civilizational governance primitives
- publication, replication, and traceability scaffolding
- preservation of possibility under changing constraints

## Research Status

Open Cognitive Ecology is an evolving research prototype. It is not a finished
product, a deployed autonomous system, or a claim of operational general
intelligence.

The repository should be read as:

- an experimental ontology and runtime architecture
- a testable research scaffold
- a public replication snapshot
- a basis for discussion, review, and further development

Interfaces and experimental modules may change as the framework is refined.

## Repository structure

- `ontology/`: cognitive, ecological, governance, and civilizational primitives
- `runtime/`: runtime activation and scheduling components
- `agents/`, `memory/`, and `cognitive_graph/`: persistent-agent foundations
- `tests/`: focused tests for foundational ontology primitives
- `visualization/`: optional rendering and visual-analysis modules
- `docs/`: conceptual documentation, architecture notes, and validation guides
- `config/`: organization and validation configuration
- `validation/`: lightweight validation and integration helpers

Generated histories, runtime states, experiment exports, local databases, and
archives are intentionally excluded from the public snapshot.

## Quickstart

Open Cognitive Ecology supports Python 3.10 and newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pytest
```

Expected result:

```text
934 passed
```

The exact runtime may vary by machine and Python version.

## Optional Integrations

Optional visualization, document, and NLP integrations are listed separately:

```bash
python -m pip install -r requirements.txt
```

These optional dependencies are not required for the core test suite.

## Public Snapshot Policy

The public repository is intentionally kept source-focused. It should not
contain local runtime state, generated dashboards, private archives, backups,
credential material, local databases, or unpublished experiment outputs.

The following categories are intentionally excluded from publication:

- backups and cold-storage archives
- generated runtime histories and local state
- local dashboards and metrics exports
- private conversation or memory archives
- local databases and cache files
- credentials, tokens, and secrets

No API keys or external credentials are required to run the public test suite.

## Replication Notes

For a basic replication check:

1. Clone the public repository.
2. Create a Python 3.10+ virtual environment.
3. Install `requirements-dev.txt`.
4. Run `python -m pytest`.

See [docs/replication_quickstart.md](docs/replication_quickstart.md) for a
step-by-step replication checklist.

The current public release is intended to be reproducible without networked
runtime side effects, external service credentials, or private local artifacts.

## Current Public Release

The first synchronized public release is:

- `v0.1.0` - Initial public synchronized release

It includes ontology organization cleanup, public replication metadata, CI
validation on Python 3.10 and 3.12, and the resolved `pytest` security advisory.

## Contributing and Security

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance and
[SECURITY.md](SECURITY.md) for private vulnerability reporting.
