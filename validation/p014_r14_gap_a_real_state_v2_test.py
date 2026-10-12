#!/usr/bin/env python3
import json
from pathlib import Path
p=Path.home()/"open-cognitive-ecology/validation/evidence/w0_w3_r14_semantic_review/p014_r14_gap_a_real_state_evidence_v2.json"
d=json.loads(p.read_text())
assert set(d["category_summary"])=={"data","human","infrastructure","tool_api"}
assert d["production_modified"] is False and d["canonical_compliance_proven"] is False
print("P014_R14_GAP_A_REAL_STATE_V2_FUNCTIONAL_OK")
assert "nonexistent_category" not in d["category_summary"]
print("P014_R14_GAP_A_REAL_STATE_V2_DEGRADATION_OK")
assert d["semantic_readjudication_required"] is True
print("P014_R14_GAP_A_REAL_STATE_V2_NON_REGRESSION_OK")
