# Contributing

Open Cognitive Ecology is an experimental research codebase. Changes should be
small enough to review and should preserve the distinction between source code
and generated runtime artifacts.

## Development setup

Use Python 3.9 or newer:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Install optional runtime integrations when working on visualization, document,
or natural-language modules:

```bash
python -m pip install -r requirements.txt
```

## Verification

Run the test suite before opening a pull request:

```bash
python -m pytest
```

Do not commit generated states, experiment exports, archives, local databases,
credentials, or ad-hoc backup files. Keep pull requests focused and describe
known limitations explicitly.

