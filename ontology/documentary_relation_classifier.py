\
"""AY1-D1b — conservative documentary relation classifier.

Transforms AY1-D1a page-level evidence into reviewable relation candidates.
Never validates relations and never writes validated_relations.json.
"""
from __future__ import annotations
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
import hashlib, json, os, re, tempfile, unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

PRIMITIVE = "DOCUMENTARY_RELATION_CLASSIFIER"
STATUS_READY = "DOCUMENTARY_RELATION_CLASSIFICATION_READY"
STATUS_DEGRADED = "DOCUMENTARY_RELATION_CLASSIFICATION_DEGRADED"
ALLOWED_RELATIONS = {"supports","requires","extends","generalizes","specializes","contradicts"}

PATTERNS = [
    ("contradicts", 0.98, [r"\bcontredit\b", r"\bincompatible avec\b", r"\brefute\b", r"\bs'oppose a\b"]),
    ("generalizes", 0.96, [r"\bgeneralise\b", r"\bgeneralization de\b"]),
    ("specializes", 0.96, [r"\bcas particulier de\b", r"\bspecialise\b"]),
    ("extends", 0.94, [r"\ba ete etendu(?:e)? dans\b", r"\bprolonge les resultats\b", r"\betend\b", r"\bextension de\b"]),
    ("requires", 0.93, [r"\brepose sur\b", r"\bdepend de\b", r"\bnecessite\b", r"\bpresuppose\b", r"\bfondations posees dans\b"]),
    ("supports", 0.86, [r"\bconfirme\b", r"\betaye\b", r"\bsoutient\b", r"\bcoherent avec\b"]),
]
BIBLIO = [r"\bdoi\s*:", r"https?://doi\.org", r"\bzenodo\b", r"\breferences?\b", r"\bbibliograph"]


def _canon(v: Any) -> str:
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def _sha(v: Any) -> str:
    return hashlib.sha256(_canon(v).encode()).hexdigest()

def _norm(v: Any) -> str:
    s = unicodedata.normalize("NFKD", str(v or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return " ".join(s.split())

def _atomic(path: Path, value: Any, filesystem_effect_context=None, slot: str="documentary_relation_write") -> None:
    if filesystem_effect_context is None: raise RuntimeError("governed_filesystem_effect_context_required")
    parent_slot = (slot[:-len("_write_replace")] if slot.endswith("_write_replace") else slot[:-len("_write")] if slot.endswith("_write") else slot) + "_parent_create"
    filesystem_effect_context.execute_path(parent_slot,"FS_CREATE_DIRS",path.parent)
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    filesystem_effect_context.execute_path(slot,"FS_WRITE_REPLACE_BYTES",path,text.encode("utf-8"))

def _classify(record: Mapping[str, Any]) -> dict[str, Any]:
    evidence_id = str(record.get('evidence_id') or '').strip()
    source = str(record.get('document_id') or record.get('source_document_id') or '').strip()
    target = str(record.get('referenced_document_id') or record.get('target_document_id') or '').strip()
    excerpt = str(record.get('excerpt') or '')
    if not evidence_id or not source or not target:
        return {'disposition':'rejected','reason':'missing_required_identity','evidence_id':evidence_id}
    if source == target:
        return {'disposition':'rejected','reason':'self_reference','evidence_id':evidence_id}
    text = _norm(excerpt)
    relation_hits = []
    for relation, confidence, patterns in PATTERNS:
        for pattern in patterns:
            if re.search(pattern, text):
                relation_hits.append((relation, confidence, pattern))
                break
    bib_hits = sum(bool(re.search(p, text)) for p in BIBLIO)
    if not relation_hits:
        reason = 'bibliographic_or_neutral_mention' if bib_hits else 'no_explicit_relation_marker'
        return {'disposition':'rejected','reason':reason,'evidence_id':evidence_id,'source':source,'target':target}
    relations = sorted({x[0] for x in relation_hits})
    if len(relations) != 1:
        return {'disposition':'review','reason':'multiple_relation_markers','evidence_id':evidence_id,'source':source,'target':target,'relations':relations}
    relation, confidence, marker = relation_hits[0]
    if bib_hits >= 2 and confidence < 0.95:
        return {'disposition':'review','reason':'relation_marker_in_bibliographic_context','evidence_id':evidence_id,'source':source,'target':target,'relation':relation}
    core = {'source':source,'target':target,'relation':relation,'evidence':[evidence_id]}
    return {
        'disposition':'candidate','candidate_id':'candidate:'+_sha(core)[:24],
        'source':source,'target':target,'relation':relation,
        'confidence':confidence,'evidence':[evidence_id],
        'matched_marker':marker,'requires_review':True,
        'validated':False,'auto_promotion_forbidden':True,
        'provenance':'ay1_d1b_documentary_classifier'
    }

@dataclass
class DocumentaryRelationClassifier:
    root: Path | None = None
    def __post_init__(self):
        self.root = Path(self.root) if self.root else Path.home()/'open-cognitive-ecology'
    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool=False, filesystem_effect_context=None) -> dict[str, Any]:
        supplied = dict(inputs or {})
        evidence = supplied.get('evidence', [])
        if not isinstance(evidence, list) or not all(isinstance(x, Mapping) for x in evidence):
            raise TypeError('evidence must be a list of mappings')
        results = [_classify(x) for x in evidence]
        candidates = sorted((x for x in results if x['disposition']=='candidate'), key=lambda x:x['candidate_id'])
        review = sorted((x for x in results if x['disposition']=='review'), key=lambda x:(x.get('evidence_id',''),_canon(x)))
        rejected = sorted((x for x in results if x['disposition']=='rejected'), key=lambda x:(x.get('evidence_id',''),x.get('reason','')))
        status = STATUS_READY if candidates or review or rejected else STATUS_DEGRADED
        payload = {
          'primitive':PRIMITIVE,'status':status,'schema_version':'1.0.0',
          'candidate_relations':candidates,'review_queue':review,'rejected_evidence':rejected,
          'candidate_count':len(candidates),'review_count':len(review),'rejected_count':len(rejected),
          'validated_relations_written':False,'auto_promotion_performed':False,
          'classification_hash':_sha({'candidates':candidates,'review':review,'rejected':rejected}),
          'consciousness_proven':False,'subjectivity_proven':False,'qualia_proven':False,'phenomenology_proven':False,
          'functional_conclusion_only':True,'phenomenology_undetermined':True,
        }
        if persist:
            out=self.root/'theory_evolution'/'ay1_d1b'/'latest'
            _atomic(out/'relation_candidates.json', candidates, filesystem_effect_context, 'relation_candidates_write_replace')
            _atomic(out/'review_queue.json', review, filesystem_effect_context, 'review_queue_write_replace')
            _atomic(out/'rejected_evidence.json', rejected, filesystem_effect_context, 'rejected_evidence_write_replace')
            _atomic(out/'classification_manifest.json', payload, filesystem_effect_context, 'classification_manifest_write_replace')
            forbidden=out/'validated_relations.json'
            if forbidden.exists():
                raise RuntimeError('validated_relations.json must never be written by AY1-D1b')
        return payload
