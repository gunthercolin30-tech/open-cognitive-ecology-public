from ontology import dna_severity_model as s

class SeverityString(str):
    pass

def reject(value):
    assert s.validate_severity(value)["valid"] is False
    try:
        s.severity_rank(value)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid severity accepted: %r" % (value,))

def main():
    # Lexical exactness: no whitespace/case/near-miss coercion.
    bad = (
        " ADVISORY", "ADVISORY ", " advisory ", "Advisory",
        "STANDARD\n", "\tSTRICT", "CONSTITUTIONAL\x00",
        "CONSTITUTIONAL!", "STRICTER", "CRITICAL", "UNKNOWN",
        "CОNSTITUTIONAL",  # contains Cyrillic O
    )
    for value in bad:
        reject(value)

    # A str subclass with an exact canonical value remains value-compatible;
    # P019 classifies values, not concrete Python string implementations.
    for level in s.SEVERITY_LEVELS:
        value = SeverityString(level)
        assert s.validate_severity(value)["valid"] is True
        assert s.severity_rank(value) == s.severity_rank(level)

    # Complete order matrix.
    levels = s.SEVERITY_LEVELS
    for i, left in enumerate(levels):
        for j, right in enumerate(levels):
            expected = (i > j) - (i < j)
            assert s.compare_severity(left, right) == expected

    # Transitivity.
    for a in levels:
        for b in levels:
            for c in levels:
                if s.compare_severity(a, b) <= 0 and s.compare_severity(b, c) <= 0:
                    assert s.compare_severity(a, c) <= 0

    print("P019_ADVERSARIAL_TEST_OK")

if __name__ == "__main__":
    main()
