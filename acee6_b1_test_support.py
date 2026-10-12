from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from acee5_hardening_test_support import valid_context
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate


def valid_acee5_decision(root: Path, proposal_id: str = "proposal-b1"):
    context = valid_context(root, proposal_id=proposal_id)
    return AceeGovernedCodeGenerationGate(root=root).step(context, persist=False)


def fixed_now():
    return datetime.now(timezone.utc)
