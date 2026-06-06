"""Reusable semantic query patterns based on standard spaCy dependency features."""

def normalize_with_engine(engine, text):
    return engine._normalize(text)

def canonical_np(engine, text):
    nlp = getattr(engine, "nlp", None)
    if nlp is None or not text:
        return normalize_with_engine(engine, text)
    try:
        doc = nlp(str(text))
        tokens = [t.text for t in doc if t.dep_ != "det" and not t.is_punct]
        if tokens:
            return normalize_with_engine(engine, " ".join(tokens))
    except Exception:
        pass
    return normalize_with_engine(engine, text)

def store_predicate_surface(engine, statement, triples, start_index):
    nlp = getattr(engine, "nlp", None)
    if nlp is None:
        return
    try:
        doc = nlp(statement)
        root = next((t for t in doc if t.dep_ == "ROOT"), None)
        if root is None:
            return
        for triple in triples[start_index:]:
            if isinstance(triple, dict):
                triple["predicate_surface"] = root.text
    except Exception:
        pass

def answer_que_fait(engine, question):
    nlp = getattr(engine, "nlp", None)
    if nlp is None:
        return None
    try:
        doc = nlp(question)
        non_punct = [t for t in doc if not t.is_punct]
        if len(non_punct) < 2:
            return None
        if engine._normalize(non_punct[1].lemma_) != "faire":
            return None
        chunks = list(doc.noun_chunks)
        if not chunks:
            return None
        target = canonical_np(engine, chunks[-1].text)
        for triple in reversed(engine.triples):
            if engine._normalize(triple.get("subject", "")) == target:
                surface = triple.get("predicate_surface")
                if surface:
                    return engine._normalize(surface)
    except Exception:
        return None
    return None

def answer_prepositional(engine, question):
    nlp = getattr(engine, "nlp", None)
    if nlp is None:
        return None
    try:
        doc = nlp(question)
        root = next((t for t in doc if t.dep_ == "ROOT"), None)
        if root is None:
            return None
        root_lemma = engine._normalize(root.lemma_)
        chunks = list(doc.noun_chunks)
        if not chunks:
            return None
        target = canonical_np(engine, chunks[-1].text)
        for triple in reversed(engine.triples):
            if engine._normalize(triple.get("subject", "")) != target:
                continue
            predicate = engine._normalize(triple.get("predicate", ""))
            if predicate == root_lemma or predicate.startswith(root_lemma + "_"):
                obj = triple.get("object", "")
                if obj and obj != "self":
                    return canonical_np(engine, obj)
    except Exception:
        return None
    return None


# === SUBTREE-BASED PATTERNS V2 ===

def phrase_from_token(engine, token):
    """Reconstruct a full syntactic phrase using token.subtree (spaCy best practice)."""
    try:
        subtree = list(token.subtree)
        if not subtree:
            return normalize_with_engine(engine, token.text)
        start = subtree[0].i
        end = subtree[-1].i + 1
        span = token.doc[start:end]
        return canonical_np(engine, span.text)
    except Exception:
        return canonical_np(engine, token.text)

def answer_que_fait(engine, question):
    nlp = getattr(engine, "nlp", None)
    if nlp is None:
        return None
    try:
        doc = nlp(question)
        non_punct = [t for t in doc if not t.is_punct]
        if len(non_punct) < 2:
            return None
        if engine._normalize(non_punct[1].lemma_) != "faire":
            return None

        target = None
        for token in doc:
            if token.dep_.startswith("nsubj") or token.dep_ in ("obj", "obl", "attr"):
                lemma = engine._normalize(getattr(token, "lemma_", token.text))
                if lemma not in {"que", "quoi", "qui", "quel", "quelle", "qu"}:
                    target = phrase_from_token(engine, token)
                    break

        if not target:
            return None

        for triple in reversed(engine.triples):
            if engine._normalize(triple.get("subject", "")) == target:
                surface = triple.get("predicate_surface")
                if surface:
                    return engine._normalize(surface)
    except Exception:
        return None
    return None

def answer_prepositional(engine, question):
    nlp = getattr(engine, "nlp", None)
    if nlp is None:
        return None
    try:
        doc = nlp(question)
        root = next((t for t in doc if t.dep_ == "ROOT"), None)
        if root is None:
            return None

        root_lemma = engine._normalize(root.lemma_)
        target = None

        for token in doc:
            if token.dep_.startswith("nsubj") or token.dep_ in ("obj", "obl", "attr"):
                lemma = engine._normalize(getattr(token, "lemma_", token.text))
                if lemma not in {"que", "quoi", "qui", "quel", "quelle", "qu"}:
                    target = phrase_from_token(engine, token)
                    break

        if not target:
            return None

        for triple in reversed(engine.triples):
            if engine._normalize(triple.get("subject", "")) != target:
                continue

            predicate = engine._normalize(triple.get("predicate", ""))
            if predicate == root_lemma or predicate.startswith(root_lemma + "_"):
                obj = triple.get("object", "")
                if obj and obj != "self":
                    return canonical_np(engine, obj)
    except Exception:
        return None
    return None

