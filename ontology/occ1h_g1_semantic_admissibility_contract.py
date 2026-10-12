from __future__ import annotations
from pathlib import Path
import ast, json, re
from hashlib import sha256

PRIMITIVE = "occ1h_g1_semantic_admissibility_contract"
VERSION = "P159-OCC1H-G1-semantic-admissibility-contract-v1"
PARTITIONS = (
    "normative/occ1a/genesis/genesis.yaml",
    "normative/occ1a/dna/dna_h.yaml",
    "normative/occ1a/dna/dna_l0.yaml",
    "normative/occ1a/dna/dna_l1.yaml",
    "normative/occ1a/ccad/ccad_principles.yaml",
    "normative/occ1a/ccad/ccad_arbitration_rules.yaml",
)

def _sha(path):
    return sha256(path.read_bytes()).hexdigest()

def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def _norms(obj):
    if isinstance(obj, dict):
        for key in ("norms", "records", "items", "entries"):
            if isinstance(obj.get(key), list):
                return obj[key]
        for value in obj.values():
            if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
                return value
    if isinstance(obj, list):
        return obj
    return []

def _tuple_constant(text, name):
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return tuple(ast.literal_eval(node.value))
    return ()

def qualify(root: Path):
    root = Path(root)
    source_model = root / "ontology" / "occ_canonical_normative_sources.py"
    nir = root / "ontology" / "occ_normative_ir.py"
    builder = root / "ontology" / "occ_normative_ir_real_builder.py"
    schema = root / "schemas" / "p159_occ1a_normative_source_package_v1.schema.json"
    required = [root / "ontology_inventory.txt", source_model, nir, builder]
    required += [root / rel for rel in PARTITIONS]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(str(path))

    sm = source_model.read_text(encoding="utf-8", errors="replace")
    nt = nir.read_text(encoding="utf-8", errors="replace")
    bt = builder.read_text(encoding="utf-8", errors="replace")
    strengths = _tuple_constant(sm, "NORMATIVE_STRENGTHS")
    req_match = re.search(r'req=\((.*?)\)', sm, re.S)
    required_fields = set(re.findall(r'"([^"]+)"', req_match.group(1))) if req_match else set()

    records = []
    for rel in PARTITIONS:
        records.extend(_norms(_load(root / rel)))

    keys = set()
    for record in records:
        if isinstance(record, dict):
            keys.update(record.keys())

    schema_permissive = None
    if schema.is_file():
        schema_permissive = (_load(schema).get("additionalProperties") is True)

    evidence = {
        "A021": {
            "dimension": "MAY_MODALITY",
            "canonical_source_contract_support": ("MAY" in strengths and "strength" in required_fields),
            "current_partition_explicit_instance": any(
                str(r.get("strength", "")).upper() == "MAY" or str(r.get("modality", "")).upper() == "MAY"
                for r in records if isinstance(r, dict)
            ),
            "nir_carrier": '"PERMITS"' in nt,
            "synthetic_input_tolerated": True,
            "builder_projects_dimension": ('norm.get("strength"' in bt or 'norm.get("modality"' in bt),
        },
        "A041": {
            "dimension": "SUNSET",
            "canonical_source_contract_support": ("sunset" in required_fields),
            "current_partition_explicit_instance": any("sunset" in r for r in records if isinstance(r, dict)),
            "nir_carrier": ('"TemporalNode"' in nt and '"sunset"' in nt),
            "synthetic_input_tolerated": True,
            "builder_projects_dimension": 'norm.get("sunset"' in bt,
        },
        "A042": {
            "dimension": "PURPOSE",
            "canonical_source_contract_support": ("purpose" in required_fields),
            "current_partition_explicit_instance": any("purpose" in r for r in records if isinstance(r, dict)),
            "nir_carrier": '"purpose"' in nt,
            "synthetic_input_tolerated": True,
            "builder_projects_dimension": 'norm.get("purpose"' in bt,
        },
    }

    for row in evidence.values():
        if row["current_partition_explicit_instance"]:
            qualification = "CANONICALLY_INSTANTIATED"
        elif row["canonical_source_contract_support"]:
            qualification = "SEMANTICALLY_ADMISSIBLE_NOT_INSTANTIATED"
        elif row["synthetic_input_tolerated"]:
            qualification = "SYNTACTICALLY_TOLERATED_ONLY"
        else:
            qualification = "UNDETERMINED"
        row["qualification"] = qualification

    return {
        "primitive": PRIMITIVE,
        "version": VERSION,
        "decision": "G1_SEMANTIC_ADMISSIBILITY_QUALIFIED_FAIL_CLOSED",
        "records": evidence,
        "observed_current_partition_keys": sorted(keys),
        "current_partition_record_count": len(records),
        "schema_permissive_if_present": schema_permissive,
        "parser_acceptance_is_semantic_admissibility": False,
        "nir_carrier_is_source_admissibility": False,
        "a040_classification": "NORMATIVE_GAP",
        "a040_technical_repair_forbidden": True,
        "canonical_sources_modified": False,
        "builder_modified": False,
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
            "source_model": _sha(source_model),
            "nir": _sha(nir),
            "builder": _sha(builder),
            **{rel: _sha(root / rel) for rel in PARTITIONS},
        },
    }
