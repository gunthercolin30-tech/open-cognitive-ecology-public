# -*- coding: utf-8 -*-
from typing import Optional, Tuple
import re

CANONICAL_SCHEMA = {
    "birth_year": {
        "patterns": [
            r"^(?P<subject>.+?) est née? en (?P<object>\d{4})$",
        ],
        "template_fr": "{subject} est né(e) en {object}.",
    },
    "capital_of": {
        "patterns": [
            r"^(?P<subject>.+?) est la capitale de (?:la |le |l')?(?P<object>.+)$",
        ],
        "template_fr": "{subject} est la capitale de {object}.",
    },
    "works_at": {
        "patterns": [
            r"^(?P<subject>.+?) travaille chez (?P<object>.+)$",
        ],
        "template_fr": "{subject} travaille chez {object}.",
    },
    "profession": {
        "patterns": [
            r"^(?P<subject>.+?) est (?P<object>.+)$",
        ],
        "template_fr": "{subject} est {object}.",
    },
}


def canonicalize_statement(text: str) -> Optional[Tuple[str, str, str]]:
    text = (text or "").strip().rstrip(".")
    if not text:
        return None

    for predicate, spec in CANONICAL_SCHEMA.items():
        for pattern in spec["patterns"]:
            m = re.match(pattern, text, re.IGNORECASE)
            if m:
                return (
                    m.group("subject").strip(),
                    predicate,
                    m.group("object").strip(),
                )
    return None


def generate_response(subject: str, predicate: str, obj: str, language: str = "fr") -> str:
    spec = CANONICAL_SCHEMA.get(predicate)
    if not spec:
        return f"{subject} {predicate} {obj}."
    template = spec.get(f"template_{language}", spec.get("template_fr"))
    return template.format(subject=subject, object=obj)


def list_supported_predicates():
    return sorted(CANONICAL_SCHEMA.keys())
