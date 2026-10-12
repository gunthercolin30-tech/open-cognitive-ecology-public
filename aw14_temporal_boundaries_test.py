from datetime import datetime
from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

timestamps = (
    "2024-02-29T23:59:59Z",
    "2026-12-31T23:59:59+00:00",
    "2027-01-01T00:00:00Z",
)
for stamp in timestamps:
    context = build_context()
    context["certified_at_utc"] = stamp
    result = EcologicalCertifier().step(inputs=context, persist=False)
    assert result["certified_at_utc"] == stamp
    datetime.fromisoformat(stamp.replace("Z", "+00:00"))
print("AW14_TEMPORAL_BOUNDARIES_OK")
