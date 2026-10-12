#!/usr/bin/env python3
from __future__ import annotations

import py_compile

py_compile.compile("ontology/axiomatic_completeness_certifier.py", cfile="/private/tmp/axiomatic_completeness_certifier.pyc", doraise=True)

from ontology.axiomatic_completeness_certifier import AxiomaticCompletenessCertifier

result = AxiomaticCompletenessCertifier().step(inputs={"synthetic": True, "source": "AN7_FAST"}, persist=False)

assert result["axiomatic_completeness_status"] == "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED"
assert result["step"] == "AN7"
assert result["minimal"] is True
assert result["independent"] is True
assert result["non_redundant"] is True
assert result["axiomatically_complete"] is True
assert result["axiomatic_completeness_resolved"] is True
assert result["ready_to_close_axis_AN"] is True
assert 0.0 <= result["completeness_score"] <= 1.0
assert isinstance(result["criterion_scores"], dict)
assert isinstance(result["criterion_passes"], dict)
assert result["consciousness_proven"] is False
assert result["qualia_proven"] is False
assert result["subjectivity_proven"] is False
assert result["phenomenology_proven"] is False
assert result["phenomenology_undetermined"] is True
assert result["functional_conclusion_only"] is True

print("AN7_FAST_ACCEPTANCE_ALL_OK")
