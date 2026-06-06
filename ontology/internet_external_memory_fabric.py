"""
INTERNET_EXTERNAL_MEMORY_FABRIC

Orchestrateur de mémoire externe persistante fondé sur :
- PersistentExternalMemoryFabric
- KnowledgeAcquisitionEngine
- MultiSourceEncyclopedicIntegrationEngine
- DistributedKnowledgeAccess
"""

from __future__ import annotations

from pathlib import Path

from ontology.persistent_external_memory_fabric import PersistentExternalMemoryFabric
from ontology.knowledge_acquisition_engine import KnowledgeAcquisitionEngine
from ontology.multi_source_encyclopedic_integration_engine import (
    MultiSourceEncyclopedicIntegrationEngine,
)
from ontology.distributed_knowledge_access import DistributedKnowledgeAccess


class InternetExternalMemoryFabric:
    def __init__(self, quota_bytes: int = 500_000_000) -> None:
        self.memory = PersistentExternalMemoryFabric(quota_bytes=quota_bytes)
        self.acquisition = KnowledgeAcquisitionEngine()
        self.encyclopedic = MultiSourceEncyclopedicIntegrationEngine()
        self.distributed = DistributedKnowledgeAccess()

    def ingest(self, query: str) -> dict:
        query = (query or "").strip()
        if not query:
            return {
                "primitive": "INTERNET_EXTERNAL_MEMORY_FABRIC",
                "success": False,
                "error": "empty_query",
            }

        acquisition_result = self.acquisition.step(query)
        encyclopedic_result = self.encyclopedic.query(query)
        distributed_result = self.distributed.step()

        payload = {
            "query": query,
            "acquisition_result": acquisition_result,
            "encyclopedic_result": encyclopedic_result,
            "distributed_result": distributed_result,
        }

        key = query.lower()
        self.memory.store(key, payload)

        recalled = self.memory.recall(key)

        return {
            "primitive": "INTERNET_EXTERNAL_MEMORY_FABRIC",
            "query": query,
            "memory_key": key,
            "stored": True,
            "recalled": recalled is not None,
            "success": recalled is not None,
            "stored_keys_count": len(self.memory.list_keys()),
            "database_path": str(self.memory.db_path),
        }

    def recall(self, query: str):
        return self.memory.recall((query or "").strip().lower())

    def list_keys(self):
        return self.memory.list_keys()

    def step(self, inputs=None) -> dict:
        inputs = inputs or {}
        query = inputs.get("query", "Albert Einstein")
        return self.ingest(query)
