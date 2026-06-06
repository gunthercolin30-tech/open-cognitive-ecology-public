"""Persistent Multi-Scale Memory"""

PRIMITIVE = "persistent_multi_scale_memory"

DEPENDENCIES = [
    "autobiographical_memory",
    "memory_consolidation",
    "temporal_self_continuity",
    "genealogical_continuity",
    "monitoring",
]


class PersistentMultiScaleMemory:
    def __init__(self):
        self.instant = []
        self.consolidated = []
        self.long_term = []
        self.genealogical = []

    def record(self, event, scale="instant"):
        getattr(self, scale).append(event)

    def consolidate(self):
        self.consolidated.extend(self.instant)
        self.instant = []

    def archive(self):
        self.long_term.extend(self.consolidated)
        self.consolidated = []

    def register_lineage(self, entry):
        self.genealogical.append(entry)

    def diagnostics(self):
        return {
            "primitive": PRIMITIVE,
            "instant_events": len(self.instant),
            "consolidated_events": len(self.consolidated),
            "long_term_events": len(self.long_term),
            "genealogical_entries": len(self.genealogical),
        }
