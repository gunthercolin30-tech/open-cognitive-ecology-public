from copy import deepcopy
from ontology import dna_inheritance as d

# Exact lexical compatibility vocabulary: reject case, whitespace, near-misses,
# boolean/proof-like tokens, and a Cyrillic-O confusable.
base = {
    "capability_id": "cap:adv",
    "compatibility": "COMPATIBLE",
    "against_inheritance_id": "P020:adv:1",
    "rationale": "adversarial fixture",
    "provenance": "P020-adversarial",
    "version": "1",
}
for bad in (
    "compatible", " COMPATIBLE", "COMPATIBLE ", "COMPATIBL",
    "PASS", "TRUE", "UNKNOWN", "", "CОMPATIBLE",
):
    x = dict(base); x["compatibility"] = bad
    try: d.validate_capability_declaration(x)
    except ValueError: pass
    else: raise AssertionError(f"invalid compatibility accepted: {bad!r}")

# No inheritance shortcuts, reversals, self-edges, or skipped levels.
for source in d.INHERITANCE_LEVELS:
    for target in d.INHERITANCE_LEVELS:
        expected = (source, target) in d.INHERITANCE_EDGES
        try:
            d.validate_inheritance_edge(source, target)
            actual = True
        except ValueError:
            actual = False
        assert actual is expected, (source, target, expected, actual)

# Validators must not mutate caller-owned data.
cap_before = deepcopy(base)
assert d.validate_capability_declaration(base)
assert base == cap_before

print("P020_ADVERSARIAL_TEST_OK")
