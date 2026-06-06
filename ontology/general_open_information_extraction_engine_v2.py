
"""
GENERAL_OPEN_INFORMATION_EXTRACTION_ENGINE_V3

Multi-stage Open Information Extraction for French:
1. textacy SVO extraction
2. spaCy dependency fallback
3. Stanza dependency fallback
"""

from typing import List, Tuple

try:
    import textacy.extract
except Exception:
    textacy = None

try:
    import stanza
except Exception:
    stanza = None


class GeneralOpenInformationExtractionEngineV2:
    SUBJECT_DEPS = {"nsubj", "nsubj:pass"}
    OBJECT_DEPS = {
        "attr", "obj", "iobj", "obl", "xcomp", "acomp", "ccomp", "prep"
    }

    def __init__(self, nlp=None):
        self.nlp = nlp
        self._stanza_pipeline = None

    def _span_text(self, token):
        return " ".join(t.text for t in token.subtree).strip()

    def _extract_with_textacy(self, doc):
        triples = []
        if textacy is None:
            return triples
        try:
            for svo in textacy.extract.subject_verb_object_triples(doc):
                subj = " ".join(tok.text for tok in svo.subject)
                rel = " ".join((tok.lemma_ or tok.text) for tok in svo.verb)
                obj = " ".join(tok.text for tok in svo.object)
                if subj and rel:
                    triples.append((subj, rel, obj))
        except Exception:
            pass
        return triples

    def _extract_with_spacy(self, doc):
        triples = []
        for sent in doc.sents:
            root = sent.root

            subjects = [
                tok for tok in root.children
                if tok.dep_ in self.SUBJECT_DEPS
            ]

            objects = [
                tok for tok in root.children
                if tok.dep_ in self.OBJECT_DEPS
            ]

            if not subjects:
                continue

            subj = self._span_text(subjects[0])
            rel = root.lemma_.strip() or root.text.strip()

            if objects:
                for obj in objects:
                    triples.append((subj, rel, self._span_text(obj)))
            else:
                triples.append((subj, rel, ""))

        return triples

    def _get_stanza(self):
        if self._stanza_pipeline is None and stanza is not None:
            try:
                self._stanza_pipeline = stanza.Pipeline(
                    "fr",
                    processors="tokenize,pos,lemma,depparse",
                    use_gpu=False,
                    verbose=False,
                )
            except Exception:
                self._stanza_pipeline = False

        if self._stanza_pipeline is False:
            return None

        return self._stanza_pipeline

    def _extract_with_stanza(self, text):
        nlp = self._get_stanza()
        if nlp is None:
            return []

        triples = []

        try:
            doc = nlp(text)

            for sent in doc.sentences:
                words = sent.words

                root = next((w for w in words if w.head == 0), None)
                if root is None:
                    continue

                subjects = [
                    w for w in words
                    if w.head == root.id and w.deprel.startswith("nsubj")
                ]

                objects = [
                    w for w in words
                    if w.head == root.id
                    and w.deprel.split(":")[0] in self.OBJECT_DEPS
                ]

                if not subjects:
                    continue

                subj = subjects[0].text
                rel = root.lemma or root.text
                obj = " ".join(w.text for w in objects) if objects else ""

                triples.append((subj, rel, obj))
        except Exception:
            pass

        return triples

    def extract(self, text: str) -> List[Tuple[str, str, str]]:
        if not self.nlp:
            return self._extract_with_stanza(text)

        doc = self.nlp(text)

        triples = self._extract_with_textacy(doc)
        if triples:
            return triples

        triples = self._extract_with_spacy(doc)
        if triples:
            return triples

        return self._extract_with_stanza(text)
