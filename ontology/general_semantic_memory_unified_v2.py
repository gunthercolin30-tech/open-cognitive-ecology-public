from __future__ import annotations

from datetime import datetime
import re
import unicodedata
import spacy


class GeneralSemanticMemoryUnifiedV2:
    PRIMITIVE_NAME = "GENERAL_SEMANTIC_MEMORY_UNIFIED_V2"

    def __init__(self):
        self.triples = []
        try:
            self.nlp = spacy.load("fr_core_news_md")
        except Exception:
            self.nlp = None

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
            "notre","nos","votre","vos","leur","leurs"
        }
        while tokens and tokens[0] in determiners:
            tokens.pop(0)
        return " ".join(tokens)

    def _phrase(self, token):
        subtree = list(token.subtree)
        if not subtree:
            return self._canonical_np(token.text)
        span = token.doc[subtree[0].i:subtree[-1].i + 1]
        return self._canonical_np(span.text)

    def store_statement(self, statement):
        if self.nlp is None:
            return False
        doc = self.nlp(statement)
        stored = False

        for sent in doc.sents:
            root = sent.root
            predicate = self._normalize(root.lemma_)
            predicate_surface = root.text

            subjects = [t for t in root.children if t.dep_.startswith("nsubj")]
            if not subjects:
                continue

            subject = self._phrase(subjects[0])

            # Copular possessive: "Germaine est ma mère."
            if predicate == "etre":
                for attr in [t for t in root.children if t.dep_ in ("attr", "acomp", "obl")]:
                    if any(
                        child.dep_ == "det" and "Poss=Yes" in str(child.morph)
                        for child in attr.children
                    ):
                        self.triples.append({
                            "subject": subject,
                            "predicate": self._normalize(attr.lemma_),
                            "object": "self",
                            "predicate_surface": predicate_surface,
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                        })
                        stored = True
                        break
                if stored:
                    continue

            candidates = [t for t in root.children if t.dep_ in ("obj", "iobj", "obl", "attr", "xcomp", "ccomp")]

            if candidates:
                comp = candidates[0]
                obj = self._phrase(comp)
                prep = next((self._normalize(c.lemma_) for c in comp.children if c.dep_ == "case"), "")
                if prep:
                    predicate = f"{predicate}_{prep}"
            else:
                obj = ""

            self.triples.append({
                "subject": subject,
                "predicate": predicate,
                "object": self._normalize(obj),
                "predicate_surface": predicate_surface,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })
            stored = True

        return stored

    def answer_question(self, question):
        q = self._normalize(question)

        if q.startswith("qui est ma niece"):
            for triple in reversed(self.triples):
                if triple["predicate"] == "niece" and triple["object"] == "self":
                    return triple["subject"]

        if q.startswith("ou habite "):
            subject = self._canonical_np(q[10:])
            for triple in reversed(self.triples):
                if triple["subject"] == subject and triple["predicate"] in ("habiter", "residence"):
                    return self._canonical_np(triple["object"])

        if q.startswith("qu a achete "):
            subject = self._canonical_np(q[12:])
            for triple in reversed(self.triples):
                if triple["subject"] == subject and triple["predicate"] == "acheter":
                    return self._canonical_np(triple["object"])

        if q.startswith("qui a achete "):
            obj = self._canonical_np(q[13:])
            for triple in reversed(self.triples):
                if triple["predicate"] == "acheter" and self._canonical_np(triple["object"]) == obj:
                    return triple["subject"]

        if q.startswith("que fait "):
            subject = self._canonical_np(q[10:])
            for triple in reversed(self.triples):
                if triple["subject"] == subject:
                    return triple.get("predicate_surface") or triple["predicate"]

        if q.startswith("de quoi "):
            # e.g. "de quoi tombe la telecommande"
            if self.nlp is not None:
                doc = self.nlp(question)
                subject = None
                root = next((t for t in doc if t.dep_ == "ROOT"), None)
                for token in doc:
                    if token.dep_.startswith("nsubj"):
                        subject = self._phrase(token)
                        break
                if root is not None and subject:
                    root_lemma = self._normalize(root.lemma_)
                    for triple in reversed(self.triples):
                        if triple["subject"] == subject and (
                            triple["predicate"] == root_lemma or
                            triple["predicate"].startswith(root_lemma + "_")
                        ):
                            return self._canonical_np(triple["object"])

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


# === GENERAL_SEMANTIC_MEMORY_UNIFIED_V2_V3 ===

_prev_answer_question_v3 = GeneralSemanticMemoryUnifiedV2.answer_question

def _answer_question_v3(self, question):
    result = _prev_answer_question_v3(self, question)
    if result not in (None, ""):
        return result

    q = self._normalize(question)

    # General pattern: Qui est ma X ?
    m = re.match(r"^qui est ma (.+)$", q)
    if m:
        relation = self._normalize(m.group(1))
        for triple in reversed(self.triples):
            if triple.get("predicate") == relation and triple.get("object") == "self":
                return triple.get("subject")

    # General pattern: Où <verb> SUBJECT ?
    m = re.match(r"^ou\s+\w+\s+(.+)$", q)
    if m:
        subject = self._canonical_np(m.group(1))
        for triple in reversed(self.triples):
            if triple.get("subject") == subject and triple.get("object"):
                return self._canonical_np(triple.get("object"))

    # General pattern: Que fait SUBJECT ?
    m = re.match(r"^que fait (.+)$", q)
    if m:
        subject = self._canonical_np(m.group(1))
        for triple in reversed(self.triples):
            if triple.get("subject") == subject:
                surface = triple.get("predicate_surface")
                if surface:
                    return surface

    # General pattern: De quoi VERB SUBJECT ?
    m = re.match(r"^de quoi\s+\w+\s+(.+)$", q)
    if m:
        subject = self._canonical_np(m.group(1))
        for triple in reversed(self.triples):
            if triple.get("subject") == subject and triple.get("object"):
                return self._canonical_np(triple.get("object"))

    return None

GeneralSemanticMemoryUnifiedV2.answer_question = _answer_question_v3


# === GENERAL_SEMANTIC_MEMORY_UNIFIED_V2_V4 ===

_prev_store_statement_v4 = GeneralSemanticMemoryUnifiedV2.store_statement
_prev_answer_question_v4 = GeneralSemanticMemoryUnifiedV2.answer_question

def _store_statement_v4(self, statement):
    stored = _prev_store_statement_v4(self, statement)

    # General fallback using dependency patterns already extracted by spaCy.
    try:
        if self.nlp is not None:
            doc = self.nlp(statement)
            for sent in doc.sents:
                root = sent.root
                predicate = self._normalize(root.lemma_)
                subjects = [t for t in root.children if t.dep_.startswith("nsubj")]
                if not subjects:
                    continue
                subject = self._phrase(subjects[0])

                # Copular pattern: nsubj + ROOT(être) + attr
                if predicate == "etre":
                    attrs = [t for t in root.children if t.dep_ in ("attr", "acomp")]
                    for attr in attrs:
                        relation = self._normalize(attr.lemma_)
                        if relation:
                            self.triples.append({
                                "subject": subject,
                                "predicate": relation,
                                "object": "self",
                                "predicate_surface": root.text,
                            })

                # Generic oblique pattern: nsubj + ROOT + obl
                obls = [t for t in root.children if t.dep_.startswith("obl")]
                for obl in obls:
                    obj = self._phrase(obl)
                    if obj:
                        pred = predicate
                        cases = [c for c in obl.children if c.dep_ == "case"]
                        if cases:
                            pred = pred + "_" + self._normalize(cases[0].lemma_)
                        self.triples.append({
                            "subject": subject,
                            "predicate": pred,
                            "object": self._normalize(obj),
                            "predicate_surface": root.text,
                        })
    except Exception:
        pass

    return stored

def _answer_question_v4(self, question):
    result = _prev_answer_question_v4(self, question)
    if result not in (None, ""):
        return result

    q = self._normalize(question)

    # Qui est ma X ?
    m = re.match(r"^qui est ma (.+)$", q)
    if m:
        relation = self._normalize(m.group(1))
        for triple in reversed(self.triples):
            if triple.get("predicate") == relation and triple.get("object") == "self":
                return triple.get("subject")

    # Où <verbe> SUJET ?
    m = re.match(r"^ou\s+\w+\s+(.+)$", q)
    if m:
        subject = self._canonical_np(m.group(1))
        for triple in reversed(self.triples):
            if triple.get("subject") == subject and triple.get("predicate", "").startswith("habiter"):
                if triple.get("object"):
                    return self._canonical_np(triple.get("object"))
        for triple in reversed(self.triples):
            if triple.get("subject") == subject and triple.get("object"):
                return self._canonical_np(triple.get("object"))

    # De quoi <verbe> SUJET ?
    m = re.match(r"^de quoi\s+(\w+)\s+(.+)$", q)
    if m:
        verb = self._normalize(m.group(1))
        subject = self._canonical_np(m.group(2))
        for triple in reversed(self.triples):
            if (
                triple.get("subject") == subject and
                (triple.get("predicate") == verb or
                 triple.get("predicate", "").startswith(verb + "_")) and
                triple.get("object")
            ):
                return self._canonical_np(triple.get("object"))

    return result

GeneralSemanticMemoryUnifiedV2.store_statement = _store_statement_v4
GeneralSemanticMemoryUnifiedV2.answer_question = _answer_question_v4

