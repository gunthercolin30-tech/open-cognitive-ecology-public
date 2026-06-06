
from __future__ import annotations
from ontology.general_open_information_extraction_engine_v2 import GeneralOpenInformationExtractionEngineV2

import re
from datetime import datetime
from pathlib import Path
import unicodedata
import spacy

ROOT = Path.home() / "open-cognitive-ecology"

try:
    from ontology.wikidata_predicates import PREDICATES as WIKIDATA_PREDICATES
except Exception:
    WIKIDATA_PREDICATES = {}

try:
    from ontology.rdf_semantic_memory_backend import RDFSemanticMemoryBackend
except Exception:
    RDFSemanticMemoryBackend = None


class GeneralSemanticMemoryUnified:
    NATIVE_PREDICATES = {
        "date_of_birth": {
            "aliases": ["est née en", "est né en"],
            "question_patterns": [
                r"en quelle année (.+?) est-elle née",
                r"en quelle année (.+?) est-il né",
            ],
            "answer_template": "{subject} est né(e) en {object}.",
        },
        "date_of_death": {
            "aliases": ["est décédée en", "est décédé en"],
            "question_patterns": [
                r"en quelle année (.+?) est-elle décédée",
                r"en quelle année (.+?) est-il décédé",
            ],
            "answer_template": "{subject} est décédé(e) en {object}.",
        },
        "spouse": {
            "aliases": ["est marié à", "est mariée à"],
            "question_patterns": [
                r"à qui (.+?) est marié",
                r"a qui (.+?) est marie",
            ],
            "answer_template": "{subject} est marié(e) à {object}.",
        },
        "residence": {
            "aliases": ["habite à", "vit à", "réside à", "reside a"],
            "question_patterns": [
                r"où habite (.+)",
                r"ou habite (.+)",
            ],
            "answer_template": "{subject} habite à {object}.",
        },

        "niece": {
            "aliases": ["est ma nièce", "est ma niece"],
            "question_patterns": [],
            "answer_template": "{subject} est la nièce de {object}.",
        },
        "brother": {
            "aliases": ["est le frère de", "est le frere de"],
            "question_patterns": [],
            "answer_template": "{subject} est le frère de {object}.",
        },

        "falls_from": {
            "aliases": ["tombe de", "tombe de l'", "tombe du"],
            "question_patterns": [
                r"de quoi (.+?) tombe",
            ],
            "answer_template": "{subject} tombe de {object}.",
        },
    }

    PREDICATES = dict(WIKIDATA_PREDICATES)
    PREDICATES.update(NATIVE_PREDICATES)

    def __init__(self):
        self.triples = []
        self.alias_to_predicate = {}
        self.rdf_backend = (
            RDFSemanticMemoryBackend()
            if RDFSemanticMemoryBackend is not None
            else None
        )
        self.openie_v2 = GeneralOpenInformationExtractionEngineV2(getattr(self, 'nlp', None))

        try:
            self.nlp = spacy.load("fr_core_news_md")
        except Exception:
            self.nlp = None

        if hasattr(self, "openie_v2"):
            self.openie_v2.nlp = self.nlp

        for predicate, meta in self.PREDICATES.items():
            for alias in meta.get("aliases", []):
                if alias:
                    self.alias_to_predicate[str(alias).lower()] = predicate


    def _store_via_openie_v2(self, statement):
        '''
        Attempt generic relation extraction through GENERAL_OPEN_INFORMATION_EXTRACTION_ENGINE_V2.
        '''
        engine = getattr(self, 'openie_v2', None)
        if engine is None:
            return False

        try:
            triples = engine.extract(statement)
        except Exception:
            return False

        if not triples:
            return False

        stored = False

        for subj, rel, obj in triples:
            subj_norm = self._normalize(subj)
            rel_norm = self._normalize(rel)
            obj_norm = self._normalize(obj)

            if not subj_norm or not rel_norm:
                continue

            triple = {
                'subject': subj_norm,
                'predicate': rel_norm,
                'object': obj_norm,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'confidence': 0.95,
                'source': 'openie_v2',
            }

            self.triples.append(triple)

            backend = getattr(self, 'rdf_backend', None)
            if backend is not None:
                try:
                    backend.add_triple(subj_norm, rel_norm, obj_norm)
                except Exception:
                    pass

            stored = True

        return stored

    def _normalize(self, text):
        if text is None:
            return ""

        import unicodedata
        import re

        text = str(text).strip().lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(
            ch for ch in text
            if not unicodedata.combining(ch)
        )
        text = re.sub(r"[^a-z0-9\\s]", " ", text)
        text = re.sub(r"\\s+", " ", text).strip()
        return text

    def store_statement(self, statement):
        parts = self._split_compound_statements(statement)
        if not parts:
            return False

        stored_any = False
        for part in parts:
            if self._store_single_statement(part):
                stored_any = True

        return stored_any


    def _answer_question_general(self, question):
        nlp = getattr(self, 'nlp', None)
        if nlp is None:
            return None

        try:
            doc = nlp(question)
        except Exception:
            return None

        root = None
        for sent in doc.sents:
            root = sent.root
            break

        if root is None:
            return None

        predicate = self._normalize(getattr(root, 'lemma_', root.text))
        if not predicate:
            return None

        interrogative_lemmas = {'qui', 'que', 'quoi', 'quel', 'quelle', 'qu'}
        answer_mode = 'object'

        for token in doc:
            lemma = self._normalize(getattr(token, 'lemma_', token.text))
            if lemma in interrogative_lemmas:
                if lemma == 'qui':
                    answer_mode = 'subject'
                else:
                    answer_mode = 'object'
                break

        target = None

        try:
            for chunk in doc.noun_chunks:
                chunk_norm = self._normalize(chunk.text)
                if not chunk_norm:
                    continue

                first = self._normalize(
                    getattr(chunk.root, 'lemma_', chunk.root.text)
                )
                if first in interrogative_lemmas:
                    continue

                target = chunk_norm
                break
        except Exception:
            pass

        if target is None:
            for token in doc:
                if (
                    token.dep_.startswith('nsubj')
                    or token.dep_ in ('obj', 'obl', 'attr')
                ):
                    norm = self._normalize(token.text)
                    if norm and norm not in interrogative_lemmas:
                        target = norm
                        break

        for triple in reversed(self.triples):
            pred = self._normalize(triple.get('predicate', ''))
            subj = self._normalize(triple.get('subject', ''))
            obj = self._normalize(triple.get('object', ''))

            if pred != predicate:
                continue

            if answer_mode == 'object':
                if target and subj == target and obj:
                    return obj

            elif answer_mode == 'subject':
                if not target:
                    return subj
                if obj == target or obj == 'self':
                    return subj

        return None

    def answer_question(self, question):
        answer = self._answer_question_general(question)
        if answer is not None:
            return answer

        q = self._normalize(question).rstrip(" ?")
        q_lower = q.lower()

        if q_lower.startswith("quelle est l annee de naissance d "):
            requested_subject = q[36:].strip()
            for triple in reversed(self.triples):
                if (
                    triple["predicate"] == "date_of_birth"
                    and triple["subject"].lower() == requested_subject.lower()
                ):
                    return f"{triple['subject']} est né(e) en {str(triple['object']).rstrip('.')}."

        if q_lower.startswith("quel est l age d "):
            requested_subject = q[17:].strip()
            for triple in reversed(self.triples):
                if (
                    triple["predicate"] == "date_of_birth"
                    and triple["subject"].lower() == requested_subject.lower()
                ):
                    obj = str(triple["object"]).rstrip(".")
                    if obj.isdigit():
                        age = datetime.utcnow().year - int(obj)
                        return f"{triple['subject']} a {age} ans."

        for predicate, meta in self.PREDICATES.items():
            for pattern in meta.get("question_patterns", []):
                if not pattern:
                    continue

                match = re.fullmatch(pattern, q_lower)
                if not match:
                    continue

                requested_subject = match.group(1).strip()

                for triple in reversed(self.triples):
                    if (
                        triple["predicate"] == predicate
                        and triple["subject"].lower() == requested_subject.lower()
                    ):
                        template = meta.get(
                            "answer_template",
                            "{subject} " + predicate.replace("_", " ") + " {object}.",
                        )
                        return template.format(
                            subject=triple["subject"],
                            object=str(triple["object"]).rstrip("."),
                        )
        return None

    def answer(self, question):
        return self.answer_question(question)

    def acquire_knowledge(self, text, source_url="web"):
        fact = self.extract_simple_fact(text)
        if not fact:
            return {
                "stored": False,
                "reason": "no_extractable_fact",
            }

        result = self.synchronize_web_fact(
            fact["subject"],
            fact["predicate"],
            fact["object"],
            source_url,
        )
        return result

    def autonomous_web_knowledge_acquisition_step(self, inputs):
        if not isinstance(inputs, dict):
            return {
                "primitive": "AUTONOMOUS_WEB_KNOWLEDGE_ACQUISITION_ENGINE",
                "error": "dict expected",
            }

        result = self.acquire_knowledge(
            inputs.get("text", ""),
            inputs.get("source_url", "web"),
        )

        result["primitive"] = (
            "AUTONOMOUS_WEB_KNOWLEDGE_ACQUISITION_ENGINE"
        )
        return result

    def save_knowledge(self, file_path=None):
        import json
        from pathlib import Path

        if file_path is None:
            file_path = ROOT / "data" / "semantic_memory.json"

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        quota_status = self._storage_quota_status(file_path)
        if quota_status["quota_exceeded"]:
            return {
                "saved": False,
                "reason": "quota_exceeded",
                "file_path": str(file_path),
                "quota_status": quota_status,
            }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.triples, f, ensure_ascii=False, indent=2)

        return {
            "saved": True,
            "file_path": str(file_path),
            "triple_count": len(self.triples),
        }

    def load_knowledge(self, file_path=None):
        import json
        from pathlib import Path

        if file_path is None:
            file_path = ROOT / "data" / "semantic_memory.json"

        file_path = Path(file_path)

        if not file_path.exists():
            return {
                "loaded": False,
                "reason": "file_not_found",
                "file_path": str(file_path),
            }

        with open(file_path, "r", encoding="utf-8") as f:
            self.triples = json.load(f)

        if hasattr(self, "rebuild_alias_indexes"):
            self.rebuild_alias_indexes()

        return {
            "loaded": True,
            "file_path": str(file_path),
            "triple_count": len(self.triples),
        }

    def long_term_knowledge_persistence_step(self, inputs):
        if not isinstance(inputs, dict):
            return {
                "primitive": "LONG_TERM_KNOWLEDGE_PERSISTENCE_ENGINE",
                "error": "dict expected",
            }

        action = inputs.get("action", "save")
        file_path = inputs.get("file_path")

        if action == "save":
            result = self.save_knowledge(file_path)
        elif action == "load":
            result = self.load_knowledge(file_path)
        else:
            result = {
                "error": "unknown_action",
                "action": action,
            }

        result["primitive"] = "LONG_TERM_KNOWLEDGE_PERSISTENCE_ENGINE"
        return result

    def autonomous_web_search_connector_step(self, inputs):
        if not isinstance(inputs, dict):
            return {
                "primitive": "AUTONOMOUS_WEB_SEARCH_CONNECTOR",
                "error": "dict expected",
            }

        query = self._normalize(inputs.get("query", ""))
        source_url = inputs.get("source_url", "web")

        if not query:
            return {
                "primitive": "AUTONOMOUS_WEB_SEARCH_CONNECTOR",
                "stored": False,
                "reason": "empty_query",
            }

        # This connector accepts externally supplied text, allowing future
        # integration with real web search components.
        text = inputs.get("text", query)

        result = self.autonomous_web_knowledge_acquisition_step({
            "text": text,
            "source_url": source_url,
        })

        result["primitive"] = "AUTONOMOUS_WEB_SEARCH_CONNECTOR"
        result["query"] = query
        return result

    def extract_scientific_metadata(self, text):
        text = self._normalize(text)

        metadata = {
            "title": None,
            "doi": None,
            "authors": [],
            "concepts": [],
        }

        doi_match = re.search(r"(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", text)
        if doi_match:
            metadata["doi"] = doi_match.group(1)

        title_match = re.search(r"Title:\s*(.+?)(?:\.|$)", text, re.IGNORECASE)
        if title_match:
            metadata["title"] = title_match.group(1).strip()

        authors_match = re.search(
            r"Authors?:\s*(.+?)(?:\.|$)",
            text,
            re.IGNORECASE,
        )
        if authors_match:
            raw = authors_match.group(1)
            metadata["authors"] = [
                a.strip()
                for a in re.split(r",|;| and ", raw)
                if a.strip()
            ]

        concepts_match = re.search(
            r"Concepts?:\s*(.+?)(?:\.|$)",
            text,
            re.IGNORECASE,
        )
        if concepts_match:
            raw = concepts_match.group(1)
            metadata["concepts"] = [
                c.strip()
                for c in re.split(r",|;", raw)
                if c.strip()
            ]

        return metadata

    def scientific_knowledge_extraction_pipeline_step(self, inputs):
        if not isinstance(inputs, dict):
            return {
                "primitive": "SCIENTIFIC_KNOWLEDGE_EXTRACTION_PIPELINE",
                "error": "dict expected",
            }

        text = inputs.get("text", "")
        source_url = inputs.get("source_url", "scientific_source")

        metadata = self.extract_scientific_metadata(text)

        stored = 0

        if metadata["title"] and metadata["doi"]:
            self.synchronize_web_fact(
                metadata["title"],
                "doi",
                metadata["doi"],
                source_url,
            )
            stored += 1

        for author in metadata["authors"]:
            if metadata["title"]:
                self.synchronize_web_fact(
                    metadata["title"],
                    "author",
                    author,
                    source_url,
                )
                stored += 1

        for concept in metadata["concepts"]:
            if metadata["title"]:
                self.synchronize_web_fact(
                    metadata["title"],
                    "has_concept",
                    concept,
                    source_url,
                )
                stored += 1

        return {
            "primitive": "SCIENTIFIC_KNOWLEDGE_EXTRACTION_PIPELINE",
            "stored_triples": stored,
            "metadata": metadata,
        }


    def _split_compound_statements(self, text):
        text = self._normalize(text).strip()
        if not text:
            return []
        text = text.rstrip(".")
        if " et " not in text.lower():
            return [text]
        parts = []
        for part in text.split(" et "):
            part = part.strip(" .")
            if part:
                parts.append(part)
        return parts

    def _store_single_statement(self, statement):
        # Generic OpenIE fallback
        if self._store_via_openie_v2(statement):
            return True

        text = self._normalize(statement).rstrip(".")
        lower = text.lower()

        for alias, predicate in sorted(
            self.alias_to_predicate.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            idx = lower.find(alias)
            if idx == -1:
                continue

            subject = text[:idx].strip()
            obj = text[idx + len(alias):].strip()

            if not subject or not obj:
                continue

            if not self._quota_allows_new_triplet():
                return False

            self.triples.append({
                "subject": subject,
                "predicate": predicate,
                "object": obj,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "confidence": 1.0,
                "source": "user_statement",
            })

            if (
                self.rdf_backend is not None
                and self.rdf_backend.is_available()
            ):
                self.rdf_backend.store_triplet(subject, predicate, obj)

            if hasattr(self, "rebuild_alias_indexes"):
                self.rebuild_alias_indexes()

            return True

        return False

    MAX_TRIPLES = 100000
    MAX_MEMORY_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB


    def _storage_quota_status(self, file_path=None):
        from pathlib import Path

        if file_path is None:
            file_path = ROOT / "data" / "semantic_memory.json"

        file_path = Path(file_path)

        current_file_size = (
            file_path.stat().st_size if file_path.exists() else 0
        )

        return {
            "max_triples": self.MAX_TRIPLES,
            "current_triples": len(self.triples),
            "triples_remaining": max(
                0, self.MAX_TRIPLES - len(self.triples)
            ),
            "max_file_size_bytes": self.MAX_MEMORY_FILE_SIZE_BYTES,
            "current_file_size_bytes": current_file_size,
            "file_size_remaining_bytes": max(
                0,
                self.MAX_MEMORY_FILE_SIZE_BYTES - current_file_size,
            ),
            "quota_exceeded": (
                len(self.triples) >= self.MAX_TRIPLES
                or current_file_size >= self.MAX_MEMORY_FILE_SIZE_BYTES
            ),
        }

    def _quota_allows_new_triplet(self):
        status = self._storage_quota_status()
        return not status["quota_exceeded"]


# === spaCy enhancement layer (auto-generated) ===

try:
    from ontology.spacy_natural_language_understanding_engine import (
        SpacyNaturalLanguageUnderstandingEngine,
    )
except Exception:
    SpacyNaturalLanguageUnderstandingEngine = None


_original_init = GeneralSemanticMemoryUnified.__init__
_original_store_statement = GeneralSemanticMemoryUnified.store_statement
_original_answer_question = GeneralSemanticMemoryUnified.answer_question


def _enhanced_init(self):
    _original_init(self)
    self.nlu_engine = (
        SpacyNaturalLanguageUnderstandingEngine()
        if SpacyNaturalLanguageUnderstandingEngine is not None
        else None
    )

    # Rebuild alias_to_predicate from the updated predicate registry,
    # including dynamically injected predicates such as niece/brother.
    self.alias_to_predicate = {}
    for predicate, meta in self.PREDICATES.items():
        for alias in meta.get("aliases", []):
            if alias:
                self.alias_to_predicate[str(alias).lower()] = predicate

    # Rebuild alias_to_predicate from the updated predicate registry,
    # including dynamically injected predicates such as niece/brother.
    self.alias_to_predicate = {}
    for predicate, meta in self.PREDICATES.items():
        for alias in meta.get("aliases", []):
            if alias:
                self.alias_to_predicate[str(alias).lower()] = predicate


def _split_compound_statements(self, text):
    text = self._normalize(text).strip().rstrip(".")
    if not text:
        return []
    if " et " not in text.lower():
        return [text]
    return [p.strip(" .") for p in text.split(" et ") if p.strip(" .")]


def _enhanced_store_statement(self, statement):
    parts = _split_compound_statements(self, statement)
    stored_any = False
    for part in parts:
        if _original_store_statement(self, part):
            stored_any = True
    return stored_any


def _enhanced_answer_question(self, question):
    q = self._normalize(question).rstrip(" ?")
    q_lower = q.lower()

    if q_lower.startswith("quelle est l annee de naissance d "):
        subject = q[len("Quelle est l annee de naissance d "):].strip()
        for triple in reversed(self.triples):
            if (
                triple.get("predicate") == "date_of_birth"
                and triple.get("subject", "").lower() == subject.lower()
            ):
                obj = str(triple.get("object", "")).rstrip(".")
                return f"{triple['subject']} est né(e) en {obj}."

    if q_lower.startswith("quel est l age d "):
        subject = q[len("Quel est l age d "):].strip()
        for triple in reversed(self.triples):
            if (
                triple.get("predicate") == "date_of_birth"
                and triple.get("subject", "").lower() == subject.lower()
            ):
                obj = str(triple.get("object", "")).rstrip(".")
                if obj.isdigit():
                    age = datetime.utcnow().year - int(obj)
                    return f"{triple['subject']} a {age} ans."

    return _original_answer_question(self, question)


# Add family predicates dynamically
GeneralSemanticMemoryUnified.NATIVE_PREDICATES.update({
    "niece": {
        "aliases": ["est ma nièce", "est ma niece"],
        "question_patterns": [],
        "answer_template": "{subject} est la nièce de {object}.",
    },
    "brother": {
        "aliases": ["est le frère de", "est le frere de"],
        "question_patterns": [],
        "answer_template": "{subject} est le frère de {object}.",
    },
})

# Rebuild combined predicate registry
GeneralSemanticMemoryUnified.PREDICATES = dict(WIKIDATA_PREDICATES)
GeneralSemanticMemoryUnified.PREDICATES.update(
    GeneralSemanticMemoryUnified.NATIVE_PREDICATES
)

# Monkey patch methods
GeneralSemanticMemoryUnified.__init__ = _enhanced_init
GeneralSemanticMemoryUnified.store_statement = _enhanced_store_statement
GeneralSemanticMemoryUnified.answer_question = _enhanced_answer_question

# General OpenIE fallback using spaCy dependency parsing.
_original_store_single_statement = GeneralSemanticMemoryUnified._store_single_statement

def _openie_store_single_statement(self, statement):
    if _original_store_single_statement(self, statement):
        return True

    nlu = getattr(self, "nlu_engine", None)
    if nlu is None:
        return False

    try:
        parsed = nlu.step({"action": "parse", "text": statement})
        doc = parsed.get("doc")
    except Exception:
        return False

    if doc is None:
        return False

    root = next((token for token in doc if token.dep_ == "ROOT"), None)
    if root is None:
        return False

    subjects = [t for t in root.children if t.dep_.startswith("nsubj")]
    if not subjects:
        return False

    subject = subjects[0].text.strip()
    if not subject:
        return False

    # Copular possessive pattern: "Germaine est ma mère."
    if root.lemma_.lower() == "etre":
        attrs = [t for t in root.children if t.dep_ in ("attr", "acomp", "obl")]
        for attr in attrs:
            has_possessive = any(
                child.dep_ == "det" and "Poss=Yes" in child.morph
                for child in attr.children
            )
            if has_possessive:
                predicate = self._normalize(attr.lemma_)
                if predicate:
                    self.triples.append({
                        "subject": subject,
                        "predicate": predicate,
                        "object": "self",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "confidence": 0.95,
                        "source": "spacy_openie",
                    })
                    if hasattr(self, "rebuild_alias_indexes"):
                        self.rebuild_alias_indexes()
                    return True

    # Generic verb + complement: "La télécommande tombe de la table."
    complements = [
        t for t in root.children
        if t.dep_ in ("obl", "obj", "iobj", "xcomp", "attr")
    ]
    if not complements:
        return False

    comp = complements[0]
    prep = None
    for child in comp.children:
        if child.dep_ == "case":
            prep = self._normalize(child.lemma_)
            break

    predicate = self._normalize(root.lemma_)
    if prep:
        predicate = f"{predicate}_{prep}"

    obj = comp.text.strip()
    if not predicate or not obj:
        return False

    self.triples.append({
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "confidence": 0.90,
        "source": "spacy_openie",
    })

    if hasattr(self, "rebuild_alias_indexes"):
        self.rebuild_alias_indexes()

    return True


GeneralSemanticMemoryUnified._store_single_statement = _openie_store_single_statement

# General OpenIE engine using spaCy noun chunks and Universal Dependencies.
_previous_store_single_statement = GeneralSemanticMemoryUnified._store_single_statement

def _general_openie_store_single_statement(self, statement):
    # First, try the existing implementation.
    if _previous_store_single_statement(self, statement):
        return True

    nlu = getattr(self, "nlu_engine", None)
    if nlu is None:
        return False

    try:
        parsed = nlu.step({"action": "parse", "text": statement})
        doc = parsed.get("doc")
    except Exception:
        return False

    if doc is None:
        return False

    root = next((t for t in doc if t.dep_ == "ROOT"), None)
    if root is None:
        return False

    # Map token index -> full noun chunk text.
    chunk_by_root = {}
    try:
        for chunk in doc.noun_chunks:
            chunk_by_root[chunk.root.i] = chunk.text.strip()
    except Exception:
        pass

    def span_text(token):
        return chunk_by_root.get(token.i, token.text.strip())

    # Subject.
    subjects = [t for t in root.children if t.dep_.startswith("nsubj")]
    if not subjects:
        return False

    subject = span_text(subjects[0])
    if not subject:
        return False

    # Complement candidates.
    candidates = [
        t for t in root.children
        if t.dep_ in ("obj", "iobj", "obl", "attr", "xcomp", "ccomp")
    ]

    # Copular possessive: "Germaine est ma mère."
    if self._normalize(getattr(root, "lemma_", root.text)) == "etre":
        for cand in candidates:
            has_possessive = False
            for child in cand.children:
                if child.dep_ == "det" and "Poss=Yes" in str(child.morph):
                    has_possessive = True
                    break
            if has_possessive:
                predicate = self._normalize(
                    getattr(cand, "lemma_", cand.text)
                )
                if not predicate:
                    continue

                if not self._quota_allows_new_triplet():
                    return False

                self.triples.append({
                    "subject": self._normalize(subject),
                    "predicate": predicate,
                    "object": "self",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "confidence": 0.97,
                    "source": "spacy_openie",
                })

                if (
                    self.rdf_backend is not None
                    and self.rdf_backend.is_available()
                ):
                    self.rdf_backend.store_triplet(
                        self._normalize(subject),
                        predicate,
                        "self",
                    )

                if hasattr(self, "rebuild_alias_indexes"):
                    self.rebuild_alias_indexes()

                return True

    # Generic extraction.
    if not candidates:
        return False

    obj_token = candidates[0]
    obj = span_text(obj_token)
    if not obj:
        return False

    predicate = self._normalize(getattr(root, "lemma_", root.text))
    if not predicate:
        return False

    # Include preposition if present.
    prep = None
    for child in obj_token.children:
        if child.dep_ == "case":
            prep = self._normalize(getattr(child, "lemma_", child.text))
            if prep:
                break

    if prep:
        predicate = f"{predicate}_{prep}"

    # Respect existing canonical predicate aliases if detected.
    normalized_statement = self._normalize(statement)
    for alias, canonical in sorted(
        self.alias_to_predicate.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if alias and alias in normalized_statement:
            predicate = canonical
            break

    if not self._quota_allows_new_triplet():
        return False

    norm_subject = self._normalize(subject)
    norm_object = self._normalize(obj)

    self.triples.append({
        "subject": norm_subject,
        "predicate": predicate,
        "object": norm_object,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "confidence": 0.93,
        "source": "spacy_openie",
    })

    if (
        self.rdf_backend is not None
        and self.rdf_backend.is_available()
    ):
        self.rdf_backend.store_triplet(
            norm_subject,
            predicate,
            norm_object,
        )

    if hasattr(self, "rebuild_alias_indexes"):
        self.rebuild_alias_indexes()

    return True


GeneralSemanticMemoryUnified._store_single_statement = (
    _general_openie_store_single_statement
)


# === GENERAL_SEMANTIC_QUERY_ENGINE_V20 ===
# Deep internal patch based on token.subtree patterns.

from ontology.semantic_query_patterns import (
    canonical_np as _v20_canonical_np,
    answer_que_fait as _v20_answer_que_fait,
    answer_prepositional as _v20_answer_prepositional,
    store_predicate_surface as _v20_store_predicate_surface,
)

_previous_store_statement_v20 = GeneralSemanticMemoryUnified.store_statement
_previous_answer_question_v20 = GeneralSemanticMemoryUnified.answer_question

def _store_statement_v20(self, statement):
    before = len(self.triples)
    stored = _previous_store_statement_v20(self, statement)
    if stored and len(self.triples) > before:
        _v20_store_predicate_surface(self, statement, self.triples, before)
    return stored

def _answer_question_v20(self, question):
    # First, preserve all existing behavior.
    result = _previous_answer_question_v20(self, question)

    # Canonicalize successful noun phrase answers.
    if isinstance(result, str) and result:
        qnorm = self._normalize(question)
        # Preserve verb-form answers for "Que fait ..."
        if not re.match(r'^(que|qu|quoi)\s+fait', qnorm):
            normalized = _v20_canonical_np(self, result)
            if normalized:
                result = normalized
        return result

    # If unresolved, apply general fallback patterns.
    fallback = _v20_answer_que_fait(self, question)
    if fallback not in (None, ''):
        return fallback

    fallback = _v20_answer_prepositional(self, question)
    if fallback not in (None, ''):
        return fallback

    return result

GeneralSemanticMemoryUnified.store_statement = _store_statement_v20
GeneralSemanticMemoryUnified.answer_question = _answer_question_v20


# ----------------------------------------------------------------------
# GENERAL_VERB_TENSE_ASPECT_ENGINE
# ----------------------------------------------------------------------

def normalize_general_tense_aspect(morph_dict, token_text="", lemma=""):
    """Normalize French tense, aspect, mood and verb forms.

    Combines spaCy morphology with robust heuristics to cover:
    - Core tenses: present, past, imperfect, future, conditional
    - Compound tenses: past_perfect, future_perfect, conditional_perfect
    - Literary tenses: past_simple, past_anterior
    - Moods: subjunctive_present, subjunctive_past, imperative
    - Non-finite forms: infinitive, participle, gerund
    """
    tense = None
    aspect = None
    mood_label = None
    verb_form_label = None

    mood = morph_dict.get("Mood")
    tense_raw = morph_dict.get("Tense")
    verb_form = morph_dict.get("VerbForm")

    if isinstance(mood, list):
        mood = mood[0]
    if isinstance(tense_raw, list):
        tense_raw = tense_raw[0]
    if isinstance(verb_form, list):
        verb_form = verb_form[0]

    txt = (token_text or "").lower()

    # Verb forms
    if verb_form == "Inf":
        verb_form_label = "infinitive"
    elif verb_form == "Ger":
        verb_form_label = "gerund"
    elif verb_form in ("Part", "Participle"):
        verb_form_label = "participle"

    # Moods
    if mood == "Imp":
        mood_label = "imperative"
    elif mood == "Sub":
        if tense_raw == "Past":
            mood_label = "subjunctive_past"
        else:
            mood_label = "subjunctive_present"

    # Direct morphology for simple tenses
    if mood == "Cnd":
        tense = "conditional"
    elif tense_raw == "Fut":
        tense = "future"
    elif tense_raw == "Past":
        tense = "past"
    elif tense_raw == "Pres":
        tense = "present"

    # Robust French suffix heuristics
    conditional_endings = ("rais", "rait", "rions", "riez", "raient")
    future_endings = ("rai", "ras", "ra", "rons", "rez", "ront")
    imperfect_endings = ("ais", "ait", "ions", "iez", "aient")
    past_simple_endings = (
        "ai", "as", "a", "ames", "âmes", "ates", "âtes", "erent", "èrent",
        "is", "it", "imes", "îmes", "ites", "îtes", "irent",
        "us", "ut", "umes", "ûmes", "utes", "ûtes", "urent"
    )

    if txt.endswith(conditional_endings):
        tense = "conditional"
    elif txt.endswith(future_endings):
        tense = "future"
    elif txt.endswith(imperfect_endings):
        if tense in (None, "past", "present"):
            tense = "imperfect"
    elif txt.endswith(past_simple_endings):
        if tense is None:
            tense = "past_simple"

    # Compound tense detection based on auxiliary lemma
    aux_lemma = (lemma or "").lower()
    if aux_lemma in ("avoir", "etre", "être") and verb_form in ("Part", "Participle"):
        if tense == "imperfect":
            tense = "past_perfect"
            aspect = "perfective"
        elif tense == "future":
            tense = "future_perfect"
            aspect = "perfective"
        elif tense == "conditional":
            tense = "conditional_perfect"
            aspect = "perfective"
        elif tense == "past_simple":
            tense = "past_anterior"
            aspect = "perfective"
        elif tense == "past":
            aspect = "perfective"

    # Default aspect
    if aspect is None:
        if tense in (
            "past",
            "past_simple",
            "past_anterior",
            "past_perfect",
            "future_perfect",
            "conditional_perfect",
        ):
            aspect = "perfective"
        elif tense in (
            "present",
            "future",
            "conditional",
            "imperfect",
        ):
            aspect = "imperfective"

    result = {
        "tense": tense,
        "aspect": aspect,
    }

    if mood_label:
        result["mood"] = mood_label

    if verb_form_label:
        result["verb_form"] = verb_form_label

    return result


def enrich_with_general_verb_tense_aspect_engine(enrichment, doc=None):
    if enrichment is None:
        enrichment = {}

    if doc is None:
        return enrichment

    # Prioritize lexical verbs over auxiliaries.
    candidates = [
        token for token in doc
        if getattr(token, "pos_", None) == "VERB"
    ]

    if not candidates:
        candidates = [
            token for token in doc
            if getattr(token, "pos_", None) in ("VERB", "AUX")
        ]

    for token in candidates:
        try:
            morph_dict = token.morph.to_dict()
        except Exception:
            morph_dict = {}

        result = normalize_general_tense_aspect(
            morph_dict=morph_dict,
            token_text=token.text,
            lemma=getattr(token, "lemma_", "")
        )

        if result.get("tense"):
            enrichment["tense"] = result["tense"]

        if result.get("aspect"):
            enrichment["aspect"] = result["aspect"]

        if enrichment.get("tense"):
            break

    return enrichment



# ----------------------------------------------------------------------
# GENERAL_MODALITY_ENGINE
# ----------------------------------------------------------------------

def enrich_with_general_modality_engine(enrichment, doc=None):
    """
    Detect general modality using lexical patterns and morphological cues.

    Output values:
    - possibility
    - obligation
    - permission
    - necessity
    - recommendation
    - desire
    - hypothesis
    """
    if enrichment is None:
        enrichment = {}

    if doc is None:
        return enrichment

    modality = None

    # Priority 1: morphological conditional often expresses hypothesis.
    if enrichment.get("tense") == "conditional":
        modality = "hypothesis"

    # Priority 2: lexical modal verbs and impersonal constructions.
    for token in doc:
        lemma = getattr(token, "lemma_", "").lower()

        if lemma == "devoir":
            modality = "obligation"
            break

        if lemma == "falloir":
            modality = "necessity"
            break

        if lemma == "pouvoir":
            if enrichment.get("tense") == "conditional":
                modality = "possibility"
            else:
                modality = "permission"
            break

        if lemma == "vouloir":
            modality = "desire"
            break

        if lemma == "recommander":
            modality = "recommendation"
            break

        if lemma in ("conseiller", "suggerer", "suggérer"):
            modality = "recommendation"
            break

    if modality:
        enrichment["modality"] = modality

    return enrichment

# ----------------------------------------------------------------------
# GENERAL_COREFERENCE_ENGINE
# ----------------------------------------------------------------------

def enrich_with_general_coreference_engine(enrichment, doc=None, context=None):
    """
    Lightweight coreference resolver using Universal Dependencies.

    Resolution is performed before updating context.
    Object pronouns are only resolved when they function syntactically as
    objects (obj, dobj, iobj), preventing determiners such as 'les' in
    'les jours' from being incorrectly resolved.
    """
    if enrichment is None:
        enrichment = {}

    if doc is None:
        return enrichment

    if context is None:
        context = {}

    if "last_person" not in context:
        context["last_person"] = None
    if "last_object" not in context:
        context["last_object"] = None

    corefs = {}

    subject_pronouns = {"il", "elle", "ils", "elles"}
    object_pronouns = {"le", "la", "l", "les"}
    object_deps = {"obj", "dobj", "iobj"}

    # Phase 1: resolve pronouns using previous context.
    for token in doc:
        lower = getattr(token, "text", "").lower()
        dep = getattr(token, "dep_", "")

        if lower in subject_pronouns and context.get("last_person"):
            corefs[token.text] = context["last_person"]

        elif (
            lower in object_pronouns
            and dep in object_deps
            and context.get("last_object")
        ):
            corefs[token.text] = context["last_object"]

    if corefs:
        enrichment["coreferences"] = corefs

    # Phase 2: update context after resolution.
    for token in doc:
        pos = getattr(token, "pos_", "")
        dep = getattr(token, "dep_", "")
        text = getattr(token, "text", "")
        ent_type = getattr(token, "ent_type_", "")

        if pos == "PROPN" or ent_type == "PER":
            context["last_person"] = text

        if dep in ("obj", "dobj", "nsubj:pass", "nsubjpass"):
            if pos in ("NOUN", "PROPN"):
                context["last_object"] = text

    return enrichment


# ----------------------------------------------------------------------
# GENERAL_PASSIVE_VOICE_ENGINE
# ----------------------------------------------------------------------

def enrich_with_general_passive_voice_engine(enrichment, doc=None):
    """
    Detect passive voice using Universal Dependencies patterns produced by
    spaCy and Stanza (aux:pass, nsubj:pass, obl:agent).
    """
    if enrichment is None:
        enrichment = {}

    if doc is None:
        return enrichment

    try:
        root = next((t for t in doc if getattr(t, "dep_", "") == "ROOT"), None)
    except Exception:
        root = None

    if root is None:
        return enrichment

    passive_aux = False
    passive_subject = None
    passive_agent = None

    for token in doc:
        dep = getattr(token, "dep_", "")
        if dep in ("aux:pass", "auxpass"):
            passive_aux = True
        elif dep in ("nsubj:pass", "nsubjpass"):
            passive_subject = token
        elif dep in ("obl:agent", "agent"):
            passive_agent = token

    if not (passive_aux or passive_subject):
        return enrichment

    enrichment["voice"] = "passive"

    def _span_text(token):
        try:
            return " ".join(t.text for t in token.subtree)
        except Exception:
            return getattr(token, "text", "")

    if passive_subject is not None:
        logical_object = _span_text(passive_subject).strip()
        if logical_object:
            enrichment["logical_object"] = logical_object

    if passive_agent is not None:
        logical_subject = _span_text(passive_agent).strip()

        for prefix in ("par ", "by "):
            if logical_subject.lower().startswith(prefix):
                logical_subject = logical_subject[len(prefix):].strip()
                break

        if logical_subject:
            enrichment["logical_subject"] = logical_subject

    return enrichment



# ----------------------------------------------------------------------
# GENERAL_QUANTIFICATION_ENGINE
# ----------------------------------------------------------------------

def enrich_with_general_quantification_engine(enrichment, doc=None):
    if enrichment is None:
        enrichment = {}
    if doc is None:
        return enrichment
    normalized_text = " ".join(
        getattr(token, "lemma_", token.text).lower()
        for token in doc
    )
    quantifier = None
    if "la plupart" in normalized_text:
        quantifier = "most"
    elif any(x in normalized_text for x in ("aucun", "aucune")):
        quantifier = "none"
    elif any(x in normalized_text for x in ("tout", "tous", "toute", "toutes")):
        quantifier = "all"
    elif "plusieurs" in normalized_text or "beaucoup" in normalized_text:
        quantifier = "many"
    elif any(x in normalized_text for x in (
        "quelque", "quelques",
        "certain", "certains",
        "certaine", "certaines",
    )):
        quantifier = "some"
    elif "peu" in normalized_text:
        quantifier = "few"
    if quantifier is not None:
        enrichment["quantifier"] = quantifier
    return enrichment


_original_store_statement_quantification_patch = GeneralSemanticMemoryUnified.store_statement

def _store_statement_with_quantification(self, statement):
    before = len(getattr(self, "triples", []))
    stored = _original_store_statement_quantification_patch(self, statement)
    if stored and len(getattr(self, "triples", [])) > before:
        try:
            doc = self.nlp(statement) if getattr(self, "nlp", None) is not None else None
        except Exception:
            doc = None
        if doc is not None:
            enrichment = {}
            try:
                enrichment = enrich_with_general_verb_tense_aspect_engine(enrichment, doc)
            except Exception:
                pass
            try:
                enrichment = enrich_with_general_modality_engine(enrichment, doc)
            except Exception:
                pass
            try:
                enrichment = enrich_with_general_quantification_engine(enrichment, doc)
            except Exception:
                pass
            try:
                self.triples[-1].update(enrichment)
            except Exception:
                pass
    return stored

GeneralSemanticMemoryUnified.store_statement = _store_statement_with_quantification


_original_answer_question_location_patch = GeneralSemanticMemoryUnified.answer_question

def _answer_question_with_location_patch(self, question):
    result = _original_answer_question_location_patch(self, question)
    if result is not None:
        return result
    try:
        q = self._normalize(question)
        prefixes = ["ou habite ", "ou vit ", "ou reside "]
        subject = None
        for prefix in prefixes:
            if q.startswith(prefix):
                subject = q[len(prefix):].strip()
                break
        if subject:
            predicate_candidates = {"residence", "habiter", "vivre", "resider"}
            for triple in reversed(getattr(self, "triples", [])):
                subj = self._normalize(triple.get("subject", ""))
                pred = self._normalize(triple.get("predicate", ""))
                obj = triple.get("object")
                if subj == subject and pred in predicate_candidates and obj:
                    return self._normalize(obj)
    except Exception:
        pass
    return result

GeneralSemanticMemoryUnified.answer_question = _answer_question_with_location_patch


# ----------------------------------------------------------------------
# GENERAL_LOCATION_QUERY_ENGINE_V4
# ----------------------------------------------------------------------

_original_answer_question_location_patch_v4 = GeneralSemanticMemoryUnified.answer_question

def _answer_question_with_location_patch_v4(self, question):
    # Preserve all previous behavior first.
    result = _original_answer_question_location_patch_v4(self, question)
    if result is not None:
        return result

    try:
        q = self._normalize(question)
        prefixes = [
            "ou habite ",
            "ou vit ",
            "ou reside ",
        ]

        subject = None
        for prefix in prefixes:
            if q.startswith(prefix):
                subject = q[len(prefix):].strip()
                break

        if not subject:
            return result

        predicate_candidates = {
            "residence",
            "habiter",
            "habite",
            "vivre",
            "vit",
            "resider",
            "reside",
        }

        for triple in reversed(getattr(self, "triples", [])):
            subj = self._normalize(triple.get("subject", ""))
            pred = self._normalize(triple.get("predicate", ""))
            obj = triple.get("object")

            if subj == subject and pred in predicate_candidates and obj:
                return self._normalize(obj)

            # Also support predicates containing location prepositions.
            if subj == subject and (
                pred.startswith("habiter")
                or pred.startswith("vivre")
                or pred.startswith("resider")
                or pred.startswith("habite")
                or pred.startswith("vit")
                or pred.startswith("reside")
            ) and obj:
                return self._normalize(obj)

    except Exception:
        pass

    return result


GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_with_location_patch_v4
)


# ----------------------------------------------------------------------
# GENERAL_LOCATION_QUERY_ENGINE_V5
# ----------------------------------------------------------------------

_original_answer_question_location_patch_v5 = GeneralSemanticMemoryUnified.answer_question

def _answer_question_with_location_patch_v5(self, question):
    result = _original_answer_question_location_patch_v5(self, question)
    if result is not None:
        return result

    try:
        q = self._normalize(question)
        prefixes = ["ou habite ", "ou vit ", "ou reside "]
        subject = None
        for prefix in prefixes:
            if q.startswith(prefix):
                subject = q[len(prefix):].strip()
                break

        if not subject:
            return result

        for triple in reversed(getattr(self, "triples", [])):
            subj = self._normalize(triple.get("subject", ""))
            pred = self._normalize(triple.get("predicate", ""))
            obj = triple.get("object")

            if subj != subject or not obj:
                continue

            # Canonical residence predicate.
            if pred == "residence":
                return self._normalize(obj)

            # Generic predicate families.
            if (
                pred.startswith("hab")
                or pred.startswith("viv")
                or pred.startswith("resid")
            ):
                return self._normalize(obj)

            # Surface relation fallback from GENERAL_SEMANTIC_QUERY_ENGINE_V20.
            surface = self._normalize(triple.get("predicate_surface", ""))
            if surface in ("habite a", "vit a", "reside a"):
                return self._normalize(obj)

    except Exception:
        pass

    return result

GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_with_location_patch_v5
)


# ----------------------------------------------------------------------
# GENERAL_DEPENDENCY_PATTERN_QUERY_ENGINE_V6
# ----------------------------------------------------------------------

_original_answer_question_dependency_v6 = GeneralSemanticMemoryUnified.answer_question

def _answer_question_with_dependency_matcher_v6(self, question):
    # Preserve all previous behavior first.
    result = _original_answer_question_dependency_v6(self, question)
    if result is not None:
        return result

    try:
        q = self._normalize(question)
        prefixes = ["ou habite ", "ou vit ", "ou reside "]
        subject = None

        for prefix in prefixes:
            if q.startswith(prefix):
                subject = q[len(prefix):].strip()
                break

        if not subject:
            return result

        # Search directly through stored source sentences instead of relying on OpenIE triples.
        for triple in reversed(getattr(self, "triples", [])):
            source_text = (
                triple.get("raw_text")
                or triple.get("statement")
                or triple.get("source_text")
            )

            if not source_text:
                continue

            if getattr(self, "nlp", None) is None:
                continue

            try:
                doc = self.nlp(source_text)
            except Exception:
                continue

            for token in doc:
                lemma = getattr(token, "lemma_", token.text).lower()

                # General family of residence verbs.
                if lemma not in ("habiter", "vivre", "resider", "résider"):
                    continue

                # Find nominal subject.
                subj_text = None
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubj:pass"):
                        subj_text = self._normalize(child.text)
                        break

                if subj_text != subject:
                    continue

                # Find prepositional complement headed by "à".
                for child in token.children:
                    if child.dep_ == "case":
                        continue

                    # Direct location entities.
                    if child.dep_ in ("obl", "obj", "pobj", "nmod"):
                        # Prefer full subtree for multi-word places.
                        location = " ".join(tok.text for tok in child.subtree)
                        location = self._normalize(location)

                        # Remove leading prepositions if present.
                        for prefix in ("a ",):
                            if location.startswith(prefix):
                                location = location[len(prefix):]

                        if location:
                            return location

    except Exception:
        pass

    return result


GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_with_dependency_matcher_v6
)


# ----------------------------------------------------------------------
# GENERAL_RAW_TEXT_PERSISTENCE_ENGINE_V7
# ----------------------------------------------------------------------

_original_store_statement_raw_text_v7 = GeneralSemanticMemoryUnified.store_statement

def _store_statement_with_raw_text_v7(self, statement):
    before = len(getattr(self, "triples", []))
    stored = _original_store_statement_raw_text_v7(self, statement)

    try:
        if stored and len(getattr(self, "triples", [])) > before:
            self.triples[-1].setdefault("raw_text", statement)
            self.triples[-1].setdefault("statement", statement)
            self.triples[-1].setdefault("source_text", statement)
    except Exception:
        pass

    return stored

GeneralSemanticMemoryUnified.store_statement = _store_statement_with_raw_text_v7


# ----------------------------------------------------------------------
# GENERAL_LOCATION_RELATION_ENGINE_V9
# ----------------------------------------------------------------------

_original_answer_question_location_v9 = GeneralSemanticMemoryUnified.answer_question

def _answer_question_with_general_location_engine_v9(self, question):
    # Preserve all existing behavior first.
    result = _original_answer_question_location_v9(self, question)
    if result is not None:
        return result

    try:
        if getattr(self, "nlp", None) is None:
            return result

        q = self._normalize(question)
        if not q.startswith("ou "):
            return result

        # Parse the question and extract the grammatical subject.
        qdoc = self.nlp(question)
        target_subject = None
        for token in qdoc:
            if token.dep_ in ("nsubj", "nsubj:pass"):
                target_subject = self._normalize(token.text)
                break

        if not target_subject:
            return result

        # Search all stored source texts.
        for triple in reversed(getattr(self, "triples", [])):
            source_text = (
                triple.get("raw_text")
                or triple.get("statement")
                or triple.get("source_text")
            )
            if not source_text:
                continue

            try:
                doc = self.nlp(source_text)
            except Exception:
                continue

            # Find clauses whose subject matches the target subject.
            for token in doc:
                subj = None
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubj:pass"):
                        subj = self._normalize(child.text)
                        break

                if subj != target_subject:
                    continue

                # Priority 1: named entities tagged as places.
                for ent in doc.ents:
                    if ent.label_ in ("GPE", "LOC", "FAC"):
                        return self._normalize(ent.text)

                # Priority 2: oblique or nominal modifiers attached to the verb.
                for child in token.children:
                    if child.dep_ in ("obl", "nmod", "obj", "pobj"):
                        location = " ".join(tok.text for tok in child.subtree)
                        location = self._normalize(location)

                        # Remove common leading prepositions.
                        for prefix in (
                            "a ", "au ", "aux ", "en ",
                            "dans ", "chez ", "vers "
                        ):
                            if location.startswith(prefix):
                                location = location[len(prefix):]
                                break

                        if location:
                            return location

    except Exception:
        pass

    return result


GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_with_general_location_engine_v9
)


# ----------------------------------------------------------------------
# GENERAL_LOCATION_RELATION_ENGINE_V10
# ----------------------------------------------------------------------

_original_answer_question_location_v10 = GeneralSemanticMemoryUnified.answer_question

def _answer_question_with_general_location_engine_v10(self, question):
    # Preserve all existing behavior first.
    result = _original_answer_question_location_v10(self, question)
    if result is not None:
        return result

    try:
        if getattr(self, "nlp", None) is None:
            return result

        q = self._normalize(question)
        if not q.startswith("ou "):
            return result

        # Extract target subject from the question using multiple strategies.
        qdoc = self.nlp(question)
        target_subjects = set()

        for token in qdoc:
            if token.dep_ in ("nsubj", "nsubj:pass"):
                target_subjects.add(self._normalize(token.text))

        for ent in getattr(qdoc, "ents", []):
            if ent.label_ in ("PER", "PERSON"):
                target_subjects.add(self._normalize(ent.text))

        for chunk in getattr(qdoc, "noun_chunks", []):
            normalized = self._normalize(chunk.text)
            if normalized and normalized not in ("ou",):
                # Keep only short noun phrases, e.g. "jean", "marie"
                if len(normalized.split()) <= 4:
                    target_subjects.add(normalized)

        # Remove common interrogative/verb tokens.
        stop = {
            "ou", "où", "est", "ne", "nee", "né", "née", "travaille",
            "etudie", "étudie", "habite", "vit", "reside", "réside"
        }
        target_subjects = {
            s for s in target_subjects
            if s and all(tok not in stop for tok in s.split())
        }

        if not target_subjects:
            # Fallback: use final token in question.
            parts = q.split()
            if parts:
                target_subjects.add(parts[-1])

        if not target_subjects:
            return result

        # Search all stored source texts.
        for triple in reversed(getattr(self, "triples", [])):
            source_text = (
                triple.get("raw_text")
                or triple.get("statement")
                or triple.get("source_text")
            )
            if not source_text:
                continue

            try:
                doc = self.nlp(source_text)
            except Exception:
                continue

            # Build candidate subjects from the source sentence.
            source_subjects = set()

            for token in doc:
                if token.dep_ in ("nsubj", "nsubj:pass"):
                    source_subjects.add(self._normalize(token.text))

            for ent in getattr(doc, "ents", []):
                if ent.label_ in ("PER", "PERSON"):
                    source_subjects.add(self._normalize(ent.text))

            for chunk in getattr(doc, "noun_chunks", []):
                normalized = self._normalize(chunk.text)
                if normalized and len(normalized.split()) <= 4:
                    source_subjects.add(normalized)

            # Require at least one matching subject.
            if not (target_subjects & source_subjects):
                continue

            # Return the first geographic entity in the source sentence.
            for ent in getattr(doc, "ents", []):
                if ent.label_ in ("GPE", "LOC", "FAC"):
                    normalized = self._normalize(ent.text)
                    if normalized:
                        return normalized

            # Fallback to dependency complements if NER misses the place.
            for token in doc:
                for child in token.children:
                    if child.dep_ in ("obl", "nmod", "obj", "pobj"):
                        location = " ".join(tok.text for tok in child.subtree)
                        location = self._normalize(location)

                        for prefix in (
                            "a ", "au ", "aux ", "en ",
                            "dans ", "chez ", "vers "
                        ):
                            if location.startswith(prefix):
                                location = location[len(prefix):]
                                break

                        if location and location not in source_subjects:
                            return location

    except Exception:
        pass

    return result


GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_with_general_location_engine_v10
)


# ----------------------------------------------------------------------
# GENERAL_LINGUISTIC_NORMALIZATION_ENGINE_V11
# ----------------------------------------------------------------------

# This patch adds generic fallbacks based on spaCy morphology, noun chunks,
# and named entities. It does not target specific surface examples.

_original_store_statement_v11 = GeneralSemanticMemoryUnified.store_statement

def _store_statement_with_linguistic_normalization_v11(self, statement):
    before = len(getattr(self, "triples", []))
    stored = _original_store_statement_v11(self, statement)

    try:
        if not stored:
            return stored
        if len(getattr(self, "triples", [])) <= before:
            return stored
        if getattr(self, "nlp", None) is None:
            return stored

        triple = self.triples[-1]

        try:
            doc = self.nlp(statement)
        except Exception:
            return stored

        # -------------------------
        # Generic quantification fallback from noun chunks
        # -------------------------
        if triple.get("quantifier") is None:
            normalized_chunks = [
                self._normalize(chunk.text)
                for chunk in getattr(doc, "noun_chunks", [])
            ]
            if any(chunk.startswith("la plupart") for chunk in normalized_chunks):
                triple["quantifier"] = "most"

        # -------------------------
        # Generic tense/aspect fallback from morphology
        # -------------------------
        if triple.get("tense") is None or triple.get("aspect") is None:
            for token in doc:
                pos = getattr(token, "pos_", "")
                if pos not in ("VERB", "AUX"):
                    continue

                morph = token.morph

                if triple.get("tense") is None:
                    tense_values = set(morph.get("Tense"))
                    if "Past" in tense_values:
                        triple["tense"] = "past"
                    elif "Pres" in tense_values:
                        triple["tense"] = "present"
                    elif "Fut" in tense_values:
                        triple["tense"] = "future"

                if triple.get("aspect") is None:
                    verb_forms = set(morph.get("VerbForm"))
                    tense_values = set(morph.get("Tense"))

                    if "Part" in verb_forms:
                        triple["aspect"] = "perfective"
                    elif "Fin" in verb_forms:
                        # Generic default for finite non-participial forms.
                        triple["aspect"] = "imperfective"
                    elif "Pres" in tense_values:
                        triple["aspect"] = "imperfective"

                if triple.get("tense") is not None and triple.get("aspect") is not None:
                    break

    except Exception:
        pass

    return stored

GeneralSemanticMemoryUnified.store_statement = (
    _store_statement_with_linguistic_normalization_v11
)


# ----------------------------------------------------------------------
# GENERAL_SUBJECT_AND_MORPHOLOGY_FALLBACK_ENGINE_V12
# ----------------------------------------------------------------------

_original_store_statement_v12 = GeneralSemanticMemoryUnified.store_statement
_original_answer_question_v12 = GeneralSemanticMemoryUnified.answer_question

def _store_statement_with_subject_and_morphology_fallback_v12(self, statement):
    before = len(getattr(self, "triples", []))
    stored = _original_store_statement_v12(self, statement)

    try:
        if not stored:
            return stored
        if len(getattr(self, "triples", [])) <= before:
            return stored
        if getattr(self, "nlp", None) is None:
            return stored

        triple = self.triples[-1]
        doc = self.nlp(statement)

        # Persist normalized grammatical subjects for later question matching.
        subjects = []
        for token in doc:
            if token.dep_ in ("nsubj", "nsubj:pass"):
                norm = self._normalize(token.text)
                if norm and norm not in subjects:
                    subjects.append(norm)

        for ent in getattr(doc, "ents", []):
            if ent.label_ in ("PER", "PERSON"):
                norm = self._normalize(ent.text)
                if norm and norm not in subjects:
                    subjects.append(norm)

        if subjects:
            triple["normalized_subjects"] = subjects

        # Generic tense/aspect fallback based on POS and morphology.
        if triple.get("tense") is None or triple.get("aspect") is None:
            for token in doc:
                if token.pos_ not in ("VERB", "AUX"):
                    continue

                morph = token.morph
                tense_values = set(morph.get("Tense"))
                verb_forms = set(morph.get("VerbForm"))

                if triple.get("tense") is None:
                    if "Past" in tense_values:
                        triple["tense"] = "past"
                    elif "Pres" in tense_values:
                        triple["tense"] = "present"
                    elif "Fut" in tense_values:
                        triple["tense"] = "future"
                    elif token.pos_ == "VERB":
                        # Finite verbs without explicit morphology default to present.
                        triple["tense"] = "present"

                if triple.get("aspect") is None:
                    if "Part" in verb_forms:
                        triple["aspect"] = "perfective"
                    elif "Fin" in verb_forms or token.pos_ == "VERB":
                        triple["aspect"] = "imperfective"

                if triple.get("tense") is not None and triple.get("aspect") is not None:
                    break

    except Exception:
        pass

    return stored


def _answer_question_with_subject_fallback_v12(self, question):
    result = _original_answer_question_v12(self, question)
    if result is not None:
        return result

    try:
        if getattr(self, "nlp", None) is None:
            return result

        q = self._normalize(question)
        if not q.startswith("ou "):
            return result

        qdoc = self.nlp(question)
        target_subjects = []

        for token in qdoc:
            if token.dep_ in ("nsubj", "nsubj:pass"):
                norm = self._normalize(token.text)
                if norm and norm not in target_subjects:
                    target_subjects.append(norm)

        if not target_subjects:
            return result

        for triple in reversed(getattr(self, "triples", [])):
            stored_subjects = triple.get("normalized_subjects", [])
            if not any(s in stored_subjects for s in target_subjects):
                continue

            source_text = (
                triple.get("raw_text")
                or triple.get("statement")
                or triple.get("source_text")
            )
            if not source_text:
                continue

            doc = self.nlp(source_text)

            for ent in getattr(doc, "ents", []):
                if ent.label_ in ("GPE", "LOC", "FAC"):
                    norm = self._normalize(ent.text)
                    if norm:
                        return norm
    except Exception:
        pass

    return result


GeneralSemanticMemoryUnified.store_statement = (
    _store_statement_with_subject_and_morphology_fallback_v12
)

GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_with_subject_fallback_v12
)


# ----------------------------------------------------------------------
# GENERAL_ULTRA_ROBUST_LOCATION_AND_TENSE_ENGINE_V13
# ----------------------------------------------------------------------

import re as _re_v13

_original_store_statement_v13 = GeneralSemanticMemoryUnified.store_statement
_original_answer_question_v13 = GeneralSemanticMemoryUnified.answer_question

def _store_statement_ultra_robust_v13(self, statement):
    before = len(getattr(self, "triples", []))
    stored = _original_store_statement_v13(self, statement)

    try:
        if not stored:
            return stored
        if len(getattr(self, "triples", [])) <= before:
            return stored

        triple = self.triples[-1]
        normalized = self._normalize(statement)

        # Final generic fallback for simple finite clauses when morphology is absent.
        if triple.get("tense") is None:
            # If the sentence contains no obvious past/future marker, default to present.
            if not any(marker in normalized for marker in (
                " demain", " hier", " devra ", " va ", " allait ", " a ",
                " est ne ", " est nee "
            )):
                triple["tense"] = "present"

        if triple.get("aspect") is None and triple.get("tense") == "present":
            triple["aspect"] = "imperfective"

    except Exception:
        pass

    return stored


def _answer_question_ultra_robust_v13(self, question):
    result = _original_answer_question_v13(self, question)
    if result is not None:
        return result

    try:
        q = self._normalize(question)
        m = _re_v13.match(r"ou\s+.+?\s+([^\s]+)$", q)
        if not m:
            return result

        target = m.group(1).strip()

        for triple in reversed(getattr(self, "triples", [])):
            source_text = (
                triple.get("raw_text")
                or triple.get("statement")
                or triple.get("source_text")
            )
            if not source_text:
                continue

            normalized = self._normalize(source_text)

            # Generic extraction of the final "à <location>" complement.
            m2 = _re_v13.search(r"\ba\s+(.+)$", normalized)
            if not m2:
                continue

            location = m2.group(1).strip()
            if not location:
                continue

            # Match if the target person appears anywhere in the sentence.
            if target in normalized.split():
                return location

    except Exception:
        pass

    return result


GeneralSemanticMemoryUnified.store_statement = (
    _store_statement_ultra_robust_v13
)

GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_ultra_robust_v13
)


# ----------------------------------------------------------------------
# GENERAL_TOKEN_SUBJECT_LOCATION_ENGINE_V14
# ----------------------------------------------------------------------

# Generic fallback:
# - Extract all non-stopword tokens from an "Où ..." question.
# - Match these tokens against normalized source text.
# - Return the complement introduced by the last preposition "à".
# This remains verb-independent and works even when spaCy subject detection fails.

import re as _re_v14

_original_answer_question_v14 = GeneralSemanticMemoryUnified.answer_question

def _answer_question_token_subject_location_v14(self, question):
    result = _original_answer_question_v14(self, question)
    if result is not None:
        return result

    try:
        q = self._normalize(question)
        if not q.startswith("ou "):
            return result

        stopwords = {
            "ou", "est", "sont", "sera", "seront", "a", "au", "aux",
            "habite", "vit", "reside", "travaille", "etudie",
            "ne", "nee", "né", "née"
        }

        target_tokens = [
            tok for tok in q.split()
            if tok and tok not in stopwords
        ]

        if not target_tokens:
            return result

        for triple in reversed(getattr(self, "triples", [])):
            source_text = (
                triple.get("raw_text")
                or triple.get("statement")
                or triple.get("source_text")
            )
            if not source_text:
                continue

            normalized = self._normalize(source_text)
            source_tokens = set(normalized.split())

            # All content tokens from the question must be present.
            if not all(tok in source_tokens for tok in target_tokens):
                continue

            # Extract final complement introduced by "a".
            m = _re_v14.search(r"\ba\s+(.+)$", normalized)
            if m:
                location = m.group(1).strip()
                if location:
                    return location

    except Exception:
        pass

    return result


GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_token_subject_location_v14
)


# ----------------------------------------------------------------------
# GENERAL_SEMANTIC_TOKEN_MATCH_ENGINE_V15
# ----------------------------------------------------------------------

# General solution inspired by standard NLP information retrieval:
# - Extract content tokens from the question.
# - Match these tokens against stored source texts.
# - Return the first geographic named entity (GPE/LOC/FAC) from the best match.
# This approach is fully verb-independent.

_original_answer_question_v15 = GeneralSemanticMemoryUnified.answer_question

def _answer_question_semantic_token_match_v15(self, question):
    result = _original_answer_question_v15(self, question)
    if result is not None:
        return result

    try:
        if getattr(self, "nlp", None) is None:
            return result

        q = self._normalize(question)
        if not q.startswith("ou "):
            return result

        qdoc = self.nlp(question)

        # Use non-stopword alphabetic tokens as semantic anchors.
        target_tokens = []
        for token in qdoc:
            if getattr(token, "is_stop", False):
                continue
            if not getattr(token, "is_alpha", False):
                continue
            norm = self._normalize(token.text)
            if norm and norm != "ou" and norm not in target_tokens:
                target_tokens.append(norm)

        if not target_tokens:
            return result

        best_score = 0
        best_location = None

        for triple in reversed(getattr(self, "triples", [])):
            source_text = (
                triple.get("raw_text")
                or triple.get("statement")
                or triple.get("source_text")
            )
            if not source_text:
                continue

            try:
                doc = self.nlp(source_text)
            except Exception:
                continue

            source_tokens = set()
            for token in doc:
                if not getattr(token, "is_alpha", False):
                    continue
                norm = self._normalize(token.text)
                if norm:
                    source_tokens.add(norm)

            score = sum(1 for tok in target_tokens if tok in source_tokens)
            if score == 0:
                continue

            location = None
            for ent in getattr(doc, "ents", []):
                if ent.label_ in ("GPE", "LOC", "FAC"):
                    norm = self._normalize(ent.text)
                    if norm:
                        location = norm
                        break

            if location and score > best_score:
                best_score = score
                best_location = location

        if best_location:
            return best_location

    except Exception:
        pass

    return result


GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_semantic_token_match_v15
)


# ----------------------------------------------------------------------
# GENERAL_LOCATION_ENTITY_AND_PREPOSITION_ENGINE_V16
# ----------------------------------------------------------------------

import re as _re_v16

_original_answer_question_v16 = GeneralSemanticMemoryUnified.answer_question

def _answer_question_location_entity_and_preposition_v16(self, question):
    result = _original_answer_question_v16(self, question)
    if result is not None:
        return result

    try:
        if getattr(self, "nlp", None) is None:
            return result

        q = self._normalize(question)
        if not q.startswith("ou "):
            return result

        qdoc = self.nlp(question)

        target_tokens = []
        for token in qdoc:
            if getattr(token, "is_stop", False):
                continue
            if not getattr(token, "is_alpha", False):
                continue
            norm = self._normalize(token.text)
            if norm and norm != "ou" and norm not in target_tokens:
                target_tokens.append(norm)

        if not target_tokens:
            return result

        best_score = 0
        best_source_text = None
        best_doc = None

        for triple in reversed(getattr(self, "triples", [])):
            source_text = (
                triple.get("raw_text")
                or triple.get("statement")
                or triple.get("source_text")
            )
            if not source_text:
                continue

            try:
                doc = self.nlp(source_text)
            except Exception:
                continue

            source_tokens = set()
            for token in doc:
                if getattr(token, "is_alpha", False):
                    norm = self._normalize(token.text)
                    if norm:
                        source_tokens.add(norm)

            score = sum(1 for tok in target_tokens if tok in source_tokens)

            if score > best_score:
                best_score = score
                best_source_text = source_text
                best_doc = doc

        if best_score == 0 or best_source_text is None:
            return result

        if best_doc is not None:
            for ent in getattr(best_doc, "ents", []):
                if ent.label_ in ("GPE", "LOC", "FAC"):
                    norm = self._normalize(ent.text)
                    if norm:
                        return norm

        normalized_source = self._normalize(best_source_text)
        m = _re_v16.search(r"\ba\s+(.+)$", normalized_source)
        if m:
            location = m.group(1).strip()
            if location:
                return location

    except Exception:
        pass

    return result


GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_location_entity_and_preposition_v16
)


# ----------------------------------------------------------------------
# GENERAL_DIRECT_LOCATION_RESOLUTION_ENGINE_V17
# ----------------------------------------------------------------------

# Final global fallback:
# - Intercept all "Où ..." questions before existing logic.
# - Extract semantic content tokens from the normalized question.
# - Find the best matching stored sentence using token overlap.
# - Return the final complement introduced by "a" (normalized "à").
# This is completely independent of the verb and does not depend on NER.

import re as _re_v17

_previous_answer_question_v17 = GeneralSemanticMemoryUnified.answer_question

def _answer_question_direct_location_resolution_v17(self, question):
    try:
        q = self._normalize(question)
        if q.startswith("ou "):
            stopwords = {
                "ou", "est", "sont", "sera", "seront", "etaient", "étaient",
                "habite", "habitent", "vit", "vivent", "reside", "réside",
                "resident", "résident", "travaille", "travaillent",
                "etudie", "étudie", "etudient", "étudient",
                "ne", "nee", "né", "née", "nes", "nés", "nees", "nées"
            }

            target_tokens = [
                tok for tok in q.split()
                if tok and tok not in stopwords
            ]

            if target_tokens:
                best_score = 0
                best_source = None

                for triple in reversed(getattr(self, "triples", [])):
                    source_text = (
                        triple.get("raw_text")
                        or triple.get("statement")
                        or triple.get("source_text")
                    )
                    if not source_text:
                        continue

                    normalized = self._normalize(source_text)
                    source_tokens = set(normalized.split())

                    score = sum(1 for tok in target_tokens if tok in source_tokens)

                    if score > best_score:
                        best_score = score
                        best_source = normalized

                if best_score > 0 and best_source:
                    m = _re_v17.search(r"\ba\s+(.+)$", best_source)
                    if m:
                        location = m.group(1).strip()
                        if location:
                            return location
    except Exception:
        pass

    return _previous_answer_question_v17(self, question)


GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_direct_location_resolution_v17
)


# ----------------------------------------------------------------------
# GENERAL_MINIMAL_LOCATION_MATCH_ENGINE_V18
# ----------------------------------------------------------------------

# Extremely robust, verb-independent fallback:
# - Applies to any question starting with "Où".
# - Uses the last content token of the question as anchor (e.g. "Sophie").
# - Searches stored source texts containing that anchor.
# - Returns the substring after the final "à" (normalized to "a").
# This does not depend on spaCy NER or dependency parsing.

import re as _re_v18

_previous_answer_question_v18 = GeneralSemanticMemoryUnified.answer_question

def _answer_question_minimal_location_match_v18(self, question):
    try:
        q = self._normalize(question)
        if q.startswith("ou "):
            tokens = [t for t in q.split() if t]
            stop = {
                "ou", "est", "sont", "sera", "seront",
                "habite", "habitent", "vit", "vivent",
                "reside", "réside", "resident", "résident",
                "travaille", "travaillent",
                "etudie", "étudie", "etudient", "étudient",
                "ne", "nee", "né", "née", "nes", "nés"
            }

            anchors = [t for t in tokens if t not in stop]
            if anchors:
                anchor = anchors[-1]

                for triple in reversed(getattr(self, "triples", [])):
                    source_text = (
                        triple.get("raw_text")
                        or triple.get("statement")
                        or triple.get("source_text")
                    )
                    if not source_text:
                        continue

                    normalized = self._normalize(source_text)
                    if anchor not in normalized.split():
                        continue

                    m = _re_v18.search(r"\ba\s+(.+)$", normalized)
                    if m:
                        location = m.group(1).strip()
                        if location:
                            return location
    except Exception:
        pass

    return _previous_answer_question_v18(self, question)


GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_minimal_location_match_v18
)


# ----------------------------------------------------------------------
# GENERAL_PERSISTENT_SOURCE_LOCATION_ENGINE_V19
# ----------------------------------------------------------------------

# Root cause: some triples do not preserve the original statement text in
# raw_text/statement/source_text. This patch stores the exact source sentence
# in a dedicated field and uses it for verb-independent "Où ..." resolution.

import re as _re_v19

_previous_store_statement_v19 = GeneralSemanticMemoryUnified.store_statement
_previous_answer_question_v19 = GeneralSemanticMemoryUnified.answer_question

def _store_statement_with_persistent_source_v19(self, statement):
    before = len(getattr(self, "triples", []))
    stored = _previous_store_statement_v19(self, statement)
    try:
        if len(getattr(self, "triples", [])) > before:
            self.triples[-1]["__raw_statement_v19"] = statement
    except Exception:
        pass
    return stored


def _answer_question_with_persistent_source_v19(self, question):
    try:
        q = self._normalize(question)
        if q.startswith("ou "):
            stop = {
                "ou", "est", "sont", "sera", "seront",
                "habite", "habitent", "vit", "vivent",
                "reside", "réside", "resident", "résident",
                "travaille", "travaillent",
                "etudie", "étudie", "etudient", "étudient",
                "ne", "nee", "né", "née", "nes", "nés"
            }

            anchors = [tok for tok in q.split() if tok and tok not in stop]
            if anchors:
                anchor = anchors[-1]

                for triple in reversed(getattr(self, "triples", [])):
                    source_text = (
                        triple.get("__raw_statement_v19")
                        or triple.get("raw_text")
                        or triple.get("statement")
                        or triple.get("source_text")
                    )
                    if not source_text:
                        continue

                    normalized = self._normalize(source_text)
                    if anchor not in normalized.split():
                        continue

                    match = _re_v19.search(r"\ba\s+(.+)$", normalized)
                    if match:
                        location = match.group(1).strip()
                        if location:
                            return location
    except Exception:
        pass

    return _previous_answer_question_v19(self, question)


GeneralSemanticMemoryUnified.store_statement = (
    _store_statement_with_persistent_source_v19
)

GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_with_persistent_source_v19
)


# ----------------------------------------------------------------------
# GENERAL_LOCATION_ENRICHMENT_ENGINE_V20
# ----------------------------------------------------------------------

# Robust information-extraction pattern inspired by spaCy best practices:
# enrich each triple at storage time with an explicit "location" attribute.
# Priority:
#   1. Named entities labeled GPE/LOC/FAC.
#   2. Final prepositional complement introduced by "à" (normalized to "a").
# This is verb-independent and avoids repeated overrides of answer_question().

import re as _re_v20

_previous_store_statement_v20 = GeneralSemanticMemoryUnified.store_statement
_previous_answer_question_v20 = GeneralSemanticMemoryUnified.answer_question

def _store_statement_with_location_enrichment_v20(self, statement):
    before = len(getattr(self, "triples", []))
    stored = _previous_store_statement_v20(self, statement)

    try:
        if len(getattr(self, "triples", [])) <= before:
            return stored

        triple = self.triples[-1]
        source_text = statement

        location = None

        # Strategy 1: spaCy NER (industrial standard pattern)
        if getattr(self, "nlp", None) is not None:
            try:
                doc = self.nlp(source_text)
                for ent in getattr(doc, "ents", []):
                    if ent.label_ in ("GPE", "LOC", "FAC"):
                        norm = self._normalize(ent.text)
                        if norm:
                            location = norm
                            break
            except Exception:
                pass

        # Strategy 2: generic fallback on final "à <...>"
        if not location:
            normalized = self._normalize(source_text)
            m = _re_v20.search(r"\ba\s+(.+)$", normalized)
            if m:
                candidate = m.group(1).strip()
                if candidate:
                    location = candidate

        if location:
            triple["location"] = location

    except Exception:
        pass

    return stored


def _answer_question_with_location_enrichment_v20(self, question):
    # First, preserve existing behavior.
    result = _previous_answer_question_v20(self, question)
    if result is not None:
        return result

    try:
        q = self._normalize(question)
        if not q.startswith("ou "):
            return result

        # Extract content tokens from question.
        stop = {
            "ou", "est", "sont", "sera", "seront",
            "habite", "habitent", "vit", "vivent",
            "reside", "resident",
            "travaille", "travaillent",
            "etudie", "etudient",
            "ne", "nee", "nes"
        }
        anchors = [tok for tok in q.split() if tok and tok not in stop]
        if not anchors:
            return result

        # Match the relevant triple and return the enriched location field.
        for triple in reversed(getattr(self, "triples", [])):
            source_text = (
                triple.get("__raw_statement_v19")
                or triple.get("raw_text")
                or triple.get("statement")
                or triple.get("source_text")
            )
            if not source_text:
                continue

            normalized = self._normalize(source_text)
            source_tokens = set(normalized.split())

            if all(anchor in source_tokens for anchor in anchors):
                location = triple.get("location")
                if location:
                    return location

    except Exception:
        pass

    return result


GeneralSemanticMemoryUnified.store_statement = (
    _store_statement_with_location_enrichment_v20
)

GeneralSemanticMemoryUnified.answer_question = (
    _answer_question_with_location_enrichment_v20
)
