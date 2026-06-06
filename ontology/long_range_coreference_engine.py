
import re


class LongRangeCoreferenceEngine:
    def __init__(self, language: str = "fr"):
        self.language = language
        self._client = None


    def backend(self) -> str:
        if hasattr(self, "_model") and self._model is not None:
            return "fastcoref"
        return "heuristic"

    def _get_client(self):
        if self._client is not None:
            return self._client

        import stanza
        from stanza.server import CoreNLPClient

        self._client = CoreNLPClient(
            annotators=[
                "tokenize",
                "ssplit",
                "pos",
                "lemma",
                "ner",
                "parse",
                "depparse",
                "coref",
            ],
            timeout=120000,
            memory="4G",
            be_quiet=True,
            properties={"tokenize.language": self.language},
        )
        self._client.start()
        return self._client


    def resolve(self, text: str) -> str:
        if not text or not text.strip():
            return text

        if not hasattr(self, "_model"):
            self._model = None
            try:
                from fastcoref import FCoref
                self._model = FCoref()
            except Exception:
                self._model = None

        if not hasattr(self, "_spacy_nlp"):
            self._spacy_nlp = None
            try:
                import spacy
                try:
                    self._spacy_nlp = spacy.load("fr_core_news_sm")
                except Exception:
                    self._spacy_nlp = spacy.blank("fr")
            except Exception:
                self._spacy_nlp = None

        if self._model is None or self._spacy_nlp is None:
            return text

        try:
            preds = self._model.predict(texts=[text])
            if not preds:
                return text

            clusters = preds[0].get_clusters(as_strings=True)
            if not clusters:
                return text

            pronouns = {
                "il", "elle", "ils", "elles", "lui", "leur",
                "he", "she", "they", "him", "her", "them", "it"
            }

            def normalize(s):
                return re.sub(r"\s+", " ", str(s).strip())

            def is_pronoun(s):
                return normalize(s).lower() in pronouns

            def features(mention):
                doc = self._spacy_nlp(normalize(mention))
                gender = None
                number = None
                common = False
                proper = False
                length = 0

                for tok in doc:
                    if tok.is_space:
                        continue
                    length += 1
                    if tok.pos_ == "NOUN":
                        common = True
                    if tok.pos_ == "PROPN":
                        proper = True
                    if gender is None:
                        vals = tok.morph.get("Gender")
                        if vals:
                            gender = vals[0]
                    if number is None:
                        vals = tok.morph.get("Number")
                        if vals:
                            number = vals[0]

                return {
                    "gender": gender,
                    "number": number,
                    "common": common,
                    "proper": proper,
                    "length": length,
                }

            def compatible(pron, cand):
                p = features(pron)
                c = features(cand)

                if p["gender"] and c["gender"] and p["gender"] != c["gender"]:
                    return False
                if p["number"] and c["number"] and p["number"] != c["number"]:
                    return False
                return True

            def score(cand):
                if is_pronoun(cand):
                    return -10**9
                f = features(cand)
                return (
                    (10000 if f["common"] else 0) +
                    (1000 if f["proper"] else 0) +
                    f["length"]
                )

            pronoun_map = {}

            for cluster in clusters:
                mentions = [normalize(m) for m in cluster if normalize(m)]
                nominals = [m for m in mentions if not is_pronoun(m)]
                if not nominals:
                    continue

                for mention in mentions:
                    if not is_pronoun(mention):
                        continue

                    candidates = [c for c in nominals if compatible(mention, c)]
                    if not candidates:
                        candidates = nominals

                    best = max(candidates, key=score)
                    if score(best) > -10**9:
                        pronoun_map[mention.lower()] = best

            if not pronoun_map:
                return text

            # Remplacement token par token sans dépendre de tok.pos_
            doc = self._spacy_nlp(text)
            out = []

            for tok in doc:
                key = tok.text.lower()

                if key in pronoun_map:
                    rep = pronoun_map[key]
                    if tok.text[:1].isupper() and rep:
                        rep = rep[:1].upper() + rep[1:]
                    out.append(rep + tok.whitespace_)
                else:
                    out.append(tok.text_with_ws)

            return "".join(out)

        except Exception:
            return text

