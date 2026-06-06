# Open Cognitive Ecology

An experimental framework for persistent cognitive agents operating under conditions of non-closure.

The project explores:

- open dynamics
- constraint-based cognition
- persistent agents
- memory architectures
- narrative continuity
- evolving ontologies
- preservation of possibility

## Repository structure

- `ontology/`: cognitive, ecological, governance, and civilizational primitives
- `runtime/`: runtime activation and scheduling components
- `agents/`, `memory/`, and `cognitive_graph/`: persistent-agent foundations
- `tests/`: focused tests for foundational ontology primitives
- `visualization/`: optional rendering and visual-analysis modules

Generated histories, runtime states, experiment exports, local databases, and
archives are intentionally excluded from active development commits.

## Development

Open Cognitive Ecology supports Python 3.9 and newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pytest
```

Optional visualization, document, and NLP integrations can be installed with:

```bash
python -m pip install -r requirements.txt
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance and
[SECURITY.md](SECURITY.md) for private vulnerability reporting.

## Status

This repository is an evolving research framework. Interfaces and experimental
modules may change as the ontology and runtime architecture are refined.
