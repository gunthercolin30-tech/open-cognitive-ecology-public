from __future__ import annotations

import copy
import importlib

EXPECTED_ORDER = (
    "DNA-0", "DNA-1", "DNA-2", "DNA-3", "DNA-4",
    "DNA-5", "DNA-6", "DNA-7", "DNA-X",
)

FORBIDDEN_LATER_MILESTONE_RESPONSIBILITIES = (
    "registry",
    "rule_contract",
    "severity_model",
    "inheritance_engine",
    "mutation_protocol",
    "versioning_lineage",
)

def _load():
    return importlib.import_module("ontology.dna_stack")

def _extract_stack(module):
    candidates = (
        "OCE_DNA_STACK", "DNA_STACK", "DNA_LAYERS", "P016_DNA_STACK",
    )
    for name in candidates:
        if hasattr(module, name):
            return getattr(module, name)
    for name, value in vars(module).items():
        if "STACK" in name.upper() and isinstance(value, (dict, tuple, list)):
            return value
    raise AssertionError("P016 adversarial: no DNA stack structure found")

def _ids(stack):
    if isinstance(stack, dict):
        return tuple(stack.keys())
    ids = []
    for item in stack:
        if isinstance(item, str):
            ids.append(item)
        elif isinstance(item, dict):
            for key in ("id", "layer_id", "layer", "name"):
                if key in item:
                    ids.append(item[key])
                    break
        else:
            for key in ("id", "layer_id", "layer", "name"):
                if hasattr(item, key):
                    ids.append(getattr(item, key))
                    break
    return tuple(ids)

def _validate_shape(ids):
    assert ids == EXPECTED_ORDER, f"invalid DNA layer order/content: {ids!r}"
    assert len(ids) == len(set(ids)), "duplicate DNA layer detected"

def main():
    module = _load()
    stack = _extract_stack(module)
    ids = _ids(stack)
    _validate_shape(ids)

    # Attack 1: deletion must be detectable.
    deleted = tuple(x for x in ids if x != "DNA-4")
    try:
        _validate_shape(deleted)
    except AssertionError:
        pass
    else:
        raise AssertionError("layer deletion was not detected")

    # Attack 2: permutation must be detectable.
    permuted = list(ids)
    permuted[0], permuted[1] = permuted[1], permuted[0]
    try:
        _validate_shape(tuple(permuted))
    except AssertionError:
        pass
    else:
        raise AssertionError("layer permutation was not detected")

    # Attack 3: duplication/substitution must be detectable.
    duplicated = list(ids)
    duplicated[-1] = "DNA-7"
    try:
        _validate_shape(tuple(duplicated))
    except AssertionError:
        pass
    else:
        raise AssertionError("layer duplication/substitution was not detected")

    # Attack 4: P016 is composition only; it must not silently own later machinery.
    public_names = {name.lower() for name in vars(module) if not name.startswith("_")}
    for forbidden in FORBIDDEN_LATER_MILESTONE_RESPONSIBILITIES:
        assert forbidden not in public_names, (
            f"P016 scope inflation: later responsibility exposed: {forbidden}"
        )

    # Attack 5: no P016-level claim of runtime authority/enforcement proof.
    text = module.__file__
    from pathlib import Path
    source = Path(text).read_text(encoding="utf-8", errors="replace").lower()
    forbidden_claims = (
        "runtime_authority = true",
        "runtime_authority=true",
        "enforcement_proven = true",
        "enforcement_proven=true",
        "unknown_promotion = true",
        "unknown_promotion=true",
    )
    for claim in forbidden_claims:
        assert claim not in source, f"forbidden P016 authority/evidence claim: {claim}"

    print("P016_ADVERSARIAL_TEST_OK")

if __name__ == "__main__":
    main()
