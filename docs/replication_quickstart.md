# Replication Quickstart

This guide describes a minimal local replication check for the public Open
Cognitive Ecology snapshot.

The goal is to verify that the repository can be cloned, installed, and tested
without private files, generated runtime artifacts, external service accounts,
or API credentials.

## Requirements

- Python `3.10` or newer
- `git`
- A POSIX-like shell, or equivalent commands on your platform

No OpenAI, GitHub, Zenodo, OpenRouter, or other external API token is required
for the core replication check.

## Clone

```bash
git clone https://github.com/gunthercolin30-tech/open-cognitive-ecology-public.git
cd open-cognitive-ecology-public
```

## Create an Environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Install Test Dependencies

```bash
python -m pip install -r requirements-dev.txt
```

## Run the Test Suite

```bash
python -m pytest
```

Expected result for release `v0.1.0` and the synchronized public snapshot:

```text
934 passed
```

The exact runtime may vary by machine and Python version.

## Optional Integrations

Optional visualization, document, and NLP dependencies are not needed for the
core tests. Install them only if you want to explore modules that use those
integrations:

```bash
python -m pip install -r requirements.txt
```

## What Is Not Included

The public snapshot intentionally excludes local and generated artifacts such as:

- runtime histories
- local dashboards and metrics exports
- backups and cold-storage archives
- local databases and caches
- private conversation or memory archives
- credentials, tokens, and secrets

These exclusions are part of the replication boundary. The public repository is
intended to contain source, tests, documentation, and metadata rather than local
runtime state.

## Suggested Verification Checklist

After running the tests, a minimal replication report can record:

- repository URL
- commit hash
- Python version
- operating system
- dependency installation result
- test result

Example:

```text
Repository: gunthercolin30-tech/open-cognitive-ecology-public
Commit: <commit-hash>
Python: 3.12.x
Result: 934 passed
External credentials used: none
```

## Troubleshooting

If dependency installation fails, first confirm the active Python version:

```bash
python --version
```

The test dependency set requires Python `3.10` or newer.

If tests fail after local experiments, return to a clean checkout and rerun the
core replication commands.
