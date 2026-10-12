"""Versioned declarative schemas for Open Interface Framework."""
from pathlib import Path

SCHEMA_ROOT = Path(__file__).resolve().parent
OIF_INTERFACE_SCHEMA_V1 = SCHEMA_ROOT / "oif_interface_schema_v1.json"

__all__ = ("OIF_INTERFACE_SCHEMA_V1", "SCHEMA_ROOT")
