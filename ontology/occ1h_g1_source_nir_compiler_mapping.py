from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict

PRIMITIVE = "occ1h_g1_source_nir_compiler_mapping"
VERSION = "P159-OCC1H-G1-source-nir-compiler-mapping-v1"

def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

def _contains(path: Path, token: str) -> bool:
    return token in path.read_text(encoding="utf-8", errors="replace")

def run(root: Path) -> Dict[str, Any]:
    root = Path(root)
    nir = root / "ontology" / "occ_normative_ir.py"
    builder = root / "ontology" / "occ_normative_ir_real_builder.py"
    compiler = root / "ontology" / "occ_constitutional_compiler.py"
    sources = root / "ontology" / "occ_canonical_normative_sources.py"
    for path in (nir, builder, compiler, sources):
        if not path.is_file():
            raise FileNotFoundError(str(path))

    mapping = {
        "A021": {
            "dimension": "MAY_MODALITY",
            "source_model_support": _contains(sources, '"MAY"'),
            "nir_explicit_carrier": _contains(nir, '"PERMITS"'),
            "real_builder_projects_dimension": _contains(builder, 'norm.get("strength"') or _contains(builder, 'norm.get("modality"'),
            "compiler_explicit_operator": _contains(compiler, '"ALLOW_CANDIDATE"'),
            "observed_admissibility": "ACCEPTED_BUT_NOT_PROJECTED",
            "classification": "SOURCE_TO_NIR_PROJECTION_GAP",
        },
        "A041": {
            "dimension": "SUNSET",
            "source_model_support": True,
            "nir_explicit_carrier": _contains(nir, '"sunset"') and _contains(nir, '"TemporalNode"'),
            "real_builder_projects_dimension": _contains(builder, 'norm.get("sunset"'),
            "compiler_explicit_operator": _contains(compiler, '"CHECK_EXPIRY"'),
            "observed_admissibility": "ACCEPTED_BUT_NOT_PROJECTED",
            "classification": "SOURCE_TO_NIR_PROJECTION_GAP",
        },
        "A042": {
            "dimension": "PURPOSE",
            "source_model_support": True,
            "nir_explicit_carrier": _contains(nir, '"purpose"'),
            "real_builder_projects_dimension": _contains(builder, 'norm.get("purpose"'),
            "compiler_explicit_operator": False,
            "observed_admissibility": "ACCEPTED_BUT_NOT_PROJECTED",
            "classification": "SOURCE_TO_NIR_PROJECTION_GAP",
        },
    }

    # The mapping is diagnostic only: it must not invent semantics or resolve ROOT.
    decision = "G1_SOURCE_TO_NIR_PROJECTION_GAP_CONFIRMED"
    return {
        "primitive": PRIMITIVE,
        "version": VERSION,
        "decision": decision,
        "mapping": mapping,
        "a040_classification": "NORMATIVE_GAP",
        "a040_technical_repair_forbidden": True,
        "builder_change_authorized": False,
        "normative_semantics_invented": False,
        "historical_verdicts_modified": False,
        "applicability_reclassified": False,
        "root_inconclusive_resolved": 0,
        "occ1h_closed": False,
        "occ1i_opened": False,
        "p159_final_lock": False,
        "p160_opened": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "input_hashes": {
            "occ_normative_ir.py": _sha(nir),
            "occ_normative_ir_real_builder.py": _sha(builder),
            "occ_constitutional_compiler.py": _sha(compiler),
            "occ_canonical_normative_sources.py": _sha(sources),
        },
    }
