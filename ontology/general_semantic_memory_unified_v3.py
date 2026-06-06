
from __future__ import annotations

from datetime import datetime
import re
import unicodedata

try:
    import spacy
except Exception:
    spacy = None



# General overrides for French past participles and other forms that some spaCy
# models may fail to lemmatize to infinitives consistently.
LEMMA_OVERRIDES = {
    "achete": "acheter",
    "achetee": "acheter",
    "achetes": "acheter",
    "achetees": "acheter",
    "cree": "creer",
    "creee": "creer",
    "crees": "creer",
    "envoye": "envoyer",
    "envoyee": "envoyer",
    "envoyes": "envoyer",
    "nettoye": "nettoyer",
    "nettoyee": "nettoyer",
    "nettoyes": "nettoyer",
    "employe": "employer",
    "employee": "employer",
    "employes": "employer",
}


class GeneralSemanticMemoryUnifiedV3:
    PRIMITIVE_NAME = "GENERAL_SEMANTIC_MEMORY_UNIFIED_V3"

    def __init__(self):
        self.triples = []
        self.nlp = None
        if spacy is not None:
            for model in ("fr_core_news_md", "fr_core_news_sm"):
                try:
                    self.nlp = spacy.load(model)
                    break
                except Exception:
                    pass

    def _normalize(self, text):
        if text is None:
            return ""
        text = str(text).strip().lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _canonical_np(self, text):
        tokens = self._normalize(text).split()
        determiners = {
            "le","la","les","un","une","des","du","de","d","l",
            "mon","ma","mes","ton","ta","tes","son","sa","ses",
            "notre","nos","votre","vos","leur","leurs",
            "a","au","aux"
        }
        while tokens and tokens[0] in determiners:
            tokens.pop(0)
        return " ".join(tokens)

    def _lemma(self, text):
        if not text:
            return ""
        if self.nlp is not None:
            doc = self.nlp(text)
            for tok in doc:
                if tok.is_alpha:
                    lemma = self._normalize(tok.lemma_)
                    return LEMMA_OVERRIDES.get(lemma, lemma)
        lemma = self._normalize(text)
        return LEMMA_OVERRIDES.get(lemma, lemma)

    def _add(self, subject, predicate, obj, surface):
        self.triples.append({
            "subject": self._canonical_np(subject),
            "predicate": self._lemma(predicate),
            "object": self._canonical_np(obj),
            "predicate_surface": surface,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

    def _store_with_spacy(self, statement):
        if self.nlp is None:
            return False
        stored = False
        doc = self.nlp(statement)
        for sent in doc.sents:
            root = sent.root
            subjects = [
                tok for tok in root.children
                if tok.dep_.startswith("nsubj") or tok.dep_.startswith("csubj")
            ]
            if not subjects:
                continue

            values = [
                tok for tok in root.children
                if tok.dep_ in {"obj", "iobj", "attr", "acomp", "xcomp", "ccomp"}
                or tok.dep_ == "obl"
                or tok.dep_.startswith("obl:")
            ]

            for subj in subjects:
                subj_span = sent.doc[subj.left_edge.i:subj.right_edge.i + 1]
                subject = subj_span.text

                if not values:
                    self._add(subject, root.lemma_, "", root.text)
                    stored = True
                    continue

                for value in values:
                    value_span = sent.doc[value.left_edge.i:value.right_edge.i + 1]
                    obj = value_span.text
                    if self._lemma(root.lemma_) == "etre" and value.dep_ in {"attr", "acomp"}:
                        self._add(subject, value.lemma_, "self", root.text)
                    else:
                        self._add(subject, root.lemma_, obj, root.text)
                    stored = True
        return stored

    def _store_regex_fallback(self, statement):
        s = statement.strip()

        patterns = [
            (r"^\s*(.+?)\s+est\s+ma\s+(.+?)\s*\.?\s*$", lambda m: self._add(m.group(1), m.group(2), "self", "est")),
            (r"^\s*(.+?)\s+habite\s+[àa]\s+(.+?)\s*\.?\s*$", lambda m: self._add(m.group(1), "habiter", m.group(2), "habite")),
            (r"^\s*(.+?)\s+tombe\s+de\s+(.+?)\s*\.?\s*$", lambda m: self._add(m.group(1), "tomber", m.group(2), "tombe")),
            (r"^\s*(.+?)\s+dort\b.*$", lambda m: self._add(m.group(1), "dormir", "", "dort")),
        ]

        for pat, fn in patterns:
            m = re.match(pat, s, re.IGNORECASE)
            if m:
                fn(m)
                return True
        return False

    def store_statement(self, statement):
        return self._store_with_spacy(statement) or self._store_regex_fallback(statement)

    def _find(self, predicate=None, subject=None, obj=None):
        p = self._lemma(predicate) if predicate is not None else None
        s = self._canonical_np(subject) if subject is not None else None
        o = self._canonical_np(obj) if obj is not None else None
        for t in reversed(self.triples):
            if p is not None and t["predicate"] != p:
                continue
            if s is not None and t["subject"] != s:
                continue
            if o is not None and t["object"] != o:
                continue
            return t
        return None

    def answer_question(self, question):
        q = self._normalize(question)

        m = re.match(r"^qui est ma (.+)$", q)
        if m:
            t = self._find(predicate=m.group(1), obj="self")
            return t["subject"] if t else None

        m = re.match(r"^ou \w+ (.+)$", q)
        if m:
            t = self._find(predicate="habiter", subject=m.group(1))
            return t["object"] if t else None

        m = re.match(r"^(qu|que|quoi) a (.+)$", q)
        if m:
            parts = m.group(2).split()
            if len(parts) >= 2:
                verb_surface = parts[0]
                subject = " ".join(parts[1:])
                t = self._find(predicate=verb_surface, subject=subject)
                return t["object"] if t else None

        m = re.match(r"^qui a (.+)$", q)
        if m:
            parts = m.group(1).split()
            if len(parts) >= 2:
                verb_surface = parts[0]
                obj = " ".join(parts[1:])
                t = self._find(predicate=verb_surface, obj=obj)
                return t["subject"] if t else None

        m = re.match(r"^que fait (.+)$", q)
        if m:
            t = self._find(subject=m.group(1))
            return t["predicate_surface"] if t else None

        m = re.match(r"^de quoi \w+ (.+)$", q)
        if m:
            t = self._find(subject=m.group(1))
            return t["object"] if t else None

        return None

    def answer(self, question):
        return self.answer_question(question)

    def step(self, inputs):
        if not isinstance(inputs, dict):
            return {"primitive": self.PRIMITIVE_NAME, "error": "dict expected"}
        if "statement" in inputs:
            return {"primitive": self.PRIMITIVE_NAME, "stored": self.store_statement(inputs["statement"])}
        if "question" in inputs:
            return {"primitive": self.PRIMITIVE_NAME, "answer": self.answer_question(inputs["question"])}
        return {"primitive": self.PRIMITIVE_NAME, "status": "idle"}
