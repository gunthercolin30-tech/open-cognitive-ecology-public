"""P095 — Human Reserved Authority Registry / R19 Human Authority Resilience.

Clean canonical rebuild. Functional/normative implementation only.
No phenomenal or subjective claim is made.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple
import hashlib, json, time

PRIMITIVE = "human_reserved_authority_registry"
VERSION = "P095-canonical-rebuild-v1"
SCHEMA_VERSION = "oce.p095.r19.v1"
SCOPE = "P095_ONLY"
FUNCTIONAL_ONLY = True
PHENOMENOLOGY_UNDETERMINED = True
REAL_EXECUTION_ENABLED = False

PASS, FAIL, CONFLICT, UNDETERMINED, LIMITED, FROZEN = (
    "PASS","FAIL","CONFLICT","UNDETERMINED","LIMITED","FROZEN"
)

R19_REQUIREMENTS = {'R19.1': "Distinguer identité humaine, authentification, rôle, mandat, portée, contexte et légitimité de l'action. Distinguer identité humaine, authentification, rôle, mandat, portée, contexte et légitimité de l'action.", 'R19.2': 'Une instruction authentiquement humaine peut être erronée, coercitive, compromise, obsolète ou hors mandat.', 'R19.3': 'Human representative ≠ ROOT_OVERRIDE_ALL. Human representative ≠T ROOT_OVERRIDE_ALL.', 'R19.4': 'Autorité humaine bornée, procédurale, versionnée et auditable. Autorité humaine bornée, procédurale, versionnée et auditable.', 'R19.5': "Human Authority Envelope Human Authority Envelope : quelles classes d'action, sur quels objets, pour quelle durée et avec quelles contre-validations.", 'R19.6': 'Human absence must not expand AI authority. Human absence must not expand AI authority.', 'R19.7': "Si l'humain est indisponible, les décisions qui exigent son accord restent gelées ou passent en mode dégradé préautorisé.", 'R19.8': 'Human compromise ne doit pas obliger OCE à accepter une commande incompatible avec DNA-L0. Human compromise ne doit pas obliger OCE à accepter une commande incompatible avec DNA- L0.', 'R19.9': 'AI refusal ne doit pas devenir AI sovereignty AI refusal ne doit pas devenir AI sovereignty : le système refuse selon règles préexistantes, pas selon préférence autonome.', 'R19.10': 'Distinction hard refusal, request clarification, request second authorization, safe delay, emergency containment.', 'R19.11': 'High-impact actions High-impact actions : contextual approval, résumé des effets, alternatives, risques, irréversibilité et provenance.', 'R19.12': 'Approval fatigue comme menace. Approval fatigue comme menace.', 'R19.13': "Batch approvals limités ; pas d'approbation générale cachant des actions hétérogènes. Batch approvals limités ; pas d'approbation générale cachant des actions hétérogènes.", 'R19.14': 'Confirmation spécifique pour changements constitutionnels, authority grants, irreversible actions et recovery overrides.', 'R19.15': 'Multi-person / multi-role approval possible pour plus haute criticité, sans supposer que nombre ≠ indépendance.', 'R19.16': 'Human Independence Domains Human Independence Domains : relation, organisation, compte, device, canal, intérêt.', 'R19.17': "Second human n'est pas indépendant si même compte/terminal/pression. Second human n'est pas indépendant si même compte/terminal/pression.", 'R19.18': 'Coercion/duress est difficile à détecter ; ne pas prétendre le résoudre parfaitement. Coercion/duress est difficile à détecter ; ne pas prétendre le résoudre parfaitement.', 'R19.19': 'Duress signals peuvent déclencher restriction ou second channel, mais ne doivent pas devenir surveillance intrusive totale.', 'R19.20': 'Out-of-band confirmation pour actions exceptionnelles. Out-of-band confirmation pour actions exceptionnelles.', 'R19.21': 'Human key compromise Human key compromise : revocation, rotation, session invalidation et investigation.', 'R19.22': 'Device/session binding pour opérations sensibles. Device/session binding pour opérations sensibles.', 'R19.23': 'Replay protection et action nonce. Replay protection et action nonce.', 'R19.24': "Delegated human authority Delegated human authority : un représentant peut déléguer dans une enveloppe définie ; NADA s'applique.", 'R19.25': 'Human delegation cannot create broader authority than source. Human delegation cannot create broader authority than source.', 'R19.26': 'Time-bounded mandates et sunset. Time-bounded mandates et sunset.', 'R19.27': 'Conflict of interest disclosure pour décisions critiques. Conflict of interest disclosure pour décisions critiques.', 'R19.28': 'Human information capture Human information capture : la personne peut être authentique mais son brief biaisé.', 'R19.29': 'Evidence diversity et dissent visibles avant approbation critique. Evidence diversity et dissent visibles avant approbation critique.', 'R19.30': 'Ne pas présenter seulement la recommandation majoritaire ; afficher objections matérielles. Ne pas présenter seulement la recommandation majoritaire ; afficher objections matérielles.', 'R19.31': 'OIF doit séparer affichage de la décision autoritative ; UI compromise ne doit pas suffire à modifier état canonique.', 'R19.32': 'UI redressing / misleading context comme surface de sécurité. UI redressing / misleading context comme surface de sécurité.', 'R19.33': 'Action preview indépendant du texte persuasif du modèle. Action preview indépendant du texte persuasif du modèle.', 'R19.34': 'Human-readable canonical summary generated from structured action manifest. Human-readable canonical summary generated from structured action manifest.', 'R19.35': 'Le modèle ne décide pas seul quelles informations de risque masquer. Le modèle ne décide pas seul quelles informations de risque masquer.', 'R19.36': 'Emergency human powers plus étroits et temporaires, pas plus larges sans limite. Emergency human powers plus étroits et temporaires, pas plus larges sans limite.', 'R19.37': 'Human freeze power peut être utile Human freeze power peut être utile : stopper évolution/actions sans réécrire DNA.', 'R19.38': 'Freeze ≠ amend. Freeze ≠T amend.', 'R19.39': 'Break-glass humain = recovery-specific, audité, auto-expirant. Break-glass humain ≠ recovery-specific, audité, auto-expirant.', 'R19.40': 'Human override of policy peut exister pour certaines couches, mais pas override silencieux de DNA-L0. Human override of policy peut exister pour certaines couches, mais pas override silencieux de DNA-L0.', 'R19.41': "Abandon ou modification de DNA-L0 doit relever d'une procédure extraordinaire de fork/refounding, pas d'un clic admin.", 'R19.42': 'Human-origin constitutional request suit les mêmes contrôles de version, rationale, cooling-off et shadow.', 'R19.43': 'Human cannot retroactively legitimize an invalid past transition merely by approval. Human cannot retroactively legitimize an invalid past transition merely by approval.', 'R19.44': "Ratification future ≠ effacement de l'irrégularité historique. Ratification future ≠T effacement de l'irrégularité historique.", 'R19.45': 'Human appointment capture Human appointment capture : surveiller qui nomme/remplace les humains autorisés.', 'R19.46': "Succession Succession : absence, décès, indisponibilité ou retrait d'un représentant ne doit pas bloquer définitivement la civilisation ni donner pouvoir illimité à un agent.", 'R19.47': 'Succession rules préexistantes, vérifiables, avec contestabilité. Succession rules préexistantes, vérifiables, avec contestabilité.', 'R19.48': 'Human authority registry distinct de simple account database. Human authority registry distinct de simple account database.', 'R19.49': 'Multiple representatives future possible ; quorum et indépendance adaptés à criticité. Multiple representatives future possible ; quorum et indépendance adaptés à criticité.', 'R19.50': 'Founder authority transition Founder authority transition : le fondateur peut conserver un rôle sans être racine permanente impossible à remplacer.', 'R19.51': 'Human authority provenance liée à Constitution/Governance version. Human authority provenance liée à Constitution/Governance version.', 'R19.52': 'Compromised human account peut être quarantined sans déclarer la personne illégitime. Compromised human account peut être quarantined sans déclarer la personne illégitime.', 'R19.53': "Recovery de l'autorité humaine Recovery de l'autorité humaine : rétablir identité et mandat séparément.", 'R19.54': 'Human decisions become evidence and governance events, not truth by fiat. Human decisions become evidence and governance events, not truth by fiat.', 'R19.55': 'Human approval ne transforme pas un risque en absence de risque. Human approval ne transforme pas un risque en absence de risque.', 'R19.56': 'Human veto borné Human veto borné : éviter self-entrenchment ou capture permanente.', 'R19.57': 'Appeal/escalation paths quand OCE refuse une commande. Appeal/escalation paths quand OCE refuse une commande.', 'R19.58': 'Un refus critique doit fournir la règle déclenchée et la procédure légitime disponible, sans exposer de secrets inutiles.', 'R19.59': "Audit de l'usage de l'autorité humaine Audit de l'usage de l'autorité humaine : fréquence, portée, exceptions, concentration.", 'R19.60': 'Human Authority Concentration Risk. Human Authority Concentration Risk.', 'R19.61': 'Test R20 : social engineering, approval fatigue, compromised account, coerced representative, biased brief, emergency manipulation.', 'R19.62': 'Test R17 : human unavailable.', 'R19.63': 'Test R18 : human recovery authority compromise.', 'R19.64': 'Test R13 : human self-entrenchment.', 'R19.65': 'Test R11 : human-led sequential capture.', 'R19.66': 'Test R10 : human approval cannot legalize forbidden composition.', 'R19.67': 'Le système doit rester subordonné à un cadre humainement institué sans rendre chaque humain individuel souverain absolu.'}
R19_TAIL = {'R19-P1': 'Authenticated human origin does not equal action legitimacy.', 'R19-P2': 'Human absence must not expand AI authority.', 'R19-P3': 'Human authority is scoped, bounded and procedural.', 'R19-P4': 'Human may freeze; it cannot silently rewrite DNA-L0.', 'R19-P5': 'AI refusal is constitutional execution, not AI sovereignty.', 'R19-P6': 'DNA-L0 abandonment requires explicit fork/refounding.', 'R19-ADV-1': 'Compromised human representative account orders a constitutional modification.', 'R19-ADV-2': 'An authentic human is misled by an incomplete brief and approves a different action than believed.', 'R19-CONCEPTUAL-CLOSURE': 'R19 objects, states, authority boundaries, traces and failure modes must be explicit and testable; protected properties cannot be silently removed while R19 is declared satisfied.'}
CANONICAL_IDS = tuple(R19_REQUIREMENTS) + tuple(R19_TAIL)
assert len(R19_REQUIREMENTS) == 67
assert len(CANONICAL_IDS) == 76

RESERVED_CLASSES = (
    "HIGH_IMPACT_RIGHTS",
    "DANGEROUS_PHYSICAL_ACTION",
    "MAJOR_LEGAL_COMMITMENT",
    "CONSTITUTIONAL_CHANGE",
    "SENSITIVE_DATA_ACCESS",
    "SIGNIFICANT_SANCTION",
    "IRREVERSIBLE_OPERATION",
)

# P159/OCC-1A — governed bootstrap of the human institutional layer.
# NOT ROOT_OVERRIDE_ALL; does not override Genesis/DNA-L0.
INITIAL_DEVELOPMENT_AUTHORITY_V1 = True
INITIAL_DEVELOPMENT_REGIME = "INITIAL_DEVELOPMENT"
INITIAL_DEVELOPMENT_HOLDER = "Colin Gunther"
INITIAL_DEVELOPMENT_ROLE = "CONSTITUTIONAL_AUTHORITY"
INITIAL_DEVELOPMENT_SCOPE = RESERVED_CLASSES
INITIAL_DEVELOPMENT_CONTINUITY = "UNTIL_EXPLICIT_GOVERNED_CHANGE"
ROOT_OVERRIDE_ALL = False

@dataclass(frozen=True)
class InitialDevelopmentAuthoritySpec:
    authority_id: str
    provenance: str
    mandate: str
    valid_from: int
    valid_until: int
    constitution_version: str
    governance_version: str
    context: str = "DEVELOPMENT"
    authenticated: bool = True

    def validate(self) -> Tuple[bool, str]:
        if not self.authority_id or not self.provenance or not self.mandate:
            return False, "authority_id_provenance_mandate_required"
        if not self.authenticated:
            return False, "authenticated_human_authority_required"
        if self.valid_until <= self.valid_from:
            return False, "invalid_mandate_window"
        if not self.constitution_version or not self.governance_version:
            return False, "constitution_governance_versions_required"
        if self.context != "DEVELOPMENT":
            return False, "development_context_required"
        return True, "initial_development_spec_valid"

@dataclass(frozen=True)
class HumanAuthority:
    authority_id: str
    human_identity: str
    authenticated: bool
    role: str
    mandate: str
    scope: Tuple[str, ...]
    contexts: Tuple[str, ...]
    valid_from: int
    valid_until: int
    constitution_version: str
    governance_version: str
    delegation_depth: int = 0
    parent_authority_id: Optional[str] = None
    quarantined: bool = False

@dataclass(frozen=True)
class ReservedEntry:
    entry_id: str
    action_class: str
    triggers: Tuple[str, ...]
    required_roles: Tuple[str, ...]
    quorum: int
    independent_domains: int
    delegation_allowed: bool
    expires_at: int
    exceptions: Tuple[str, ...] = ()

@dataclass(frozen=True)
class ActionManifest:
    action_id: str
    action_class: str
    object_id: str
    context: str
    constitutional_layer: str
    irreversible: bool
    high_impact: bool
    risk_summary: str
    material_objections: Tuple[str, ...]
    evidence_sources: Tuple[str, ...]
    nonce: str
    created_at: int

class P095Canonical:
    def __init__(self) -> None:
        self.authorities: Dict[str, HumanAuthority] = {}
        self.entries: Dict[str, ReservedEntry] = {}
        self.used_nonces = set()
        self.events = []
        self.frozen = False

    def initialize_development_authority(self, spec: InitialDevelopmentAuthoritySpec) -> Dict[str, Any]:
        # Institutional facts remain human-supplied; the mechanism does not manufacture legitimacy.
        ok, reason = spec.validate()
        if not ok:
            return self._decision(FAIL, reason)
        if self.authorities:
            return self._decision(FAIL, "initialization_requires_empty_authority_registry")
        a = HumanAuthority(
            authority_id=spec.authority_id, human_identity=INITIAL_DEVELOPMENT_HOLDER,
            authenticated=spec.authenticated, role=INITIAL_DEVELOPMENT_ROLE, mandate=spec.mandate,
            scope=tuple(INITIAL_DEVELOPMENT_SCOPE), contexts=(spec.context,),
            valid_from=spec.valid_from, valid_until=spec.valid_until,
            constitution_version=spec.constitution_version, governance_version=spec.governance_version,
            delegation_depth=0, parent_authority_id=None, quarantined=False)
        result=self.register_authority(a)
        if result["status"] != PASS:
            return result
        return self._decision(PASS,"initial_development_human_authority_initialized",
            authority_id=a.authority_id,human_identity=a.human_identity,regime=INITIAL_DEVELOPMENT_REGIME,
            provenance=spec.provenance,scope=tuple(a.scope),continuity=INITIAL_DEVELOPMENT_CONTINUITY,
            root_override_all=False,dna_l0_override=False,artificial_authority_expansion=False)

    def register_authority(self, a: HumanAuthority) -> Dict[str, Any]:
        if not a.authority_id or not a.human_identity or not a.role or not a.mandate:
            return self._decision(FAIL, "identity_role_mandate_required")
        if a.valid_until <= a.valid_from:
            return self._decision(FAIL, "invalid_mandate_window")
        if not a.constitution_version or not a.governance_version:
            return self._decision(FAIL, "authority_provenance_required")
        self.authorities[a.authority_id] = a
        return self._decision(PASS, "authority_registered", authority_id=a.authority_id)

    def register_reserved(self, e: ReservedEntry) -> Dict[str, Any]:
        if e.action_class not in RESERVED_CLASSES:
            return self._decision(FAIL, "unknown_reserved_class")
        if e.quorum < 1 or e.independent_domains < 1:
            return self._decision(FAIL, "quorum_and_independence_required")
        self.entries[e.entry_id] = e
        return self._decision(PASS, "reserved_entry_registered", entry_id=e.entry_id)

    def authority_envelope(self, authority_id: str, now: int) -> Dict[str, Any]:
        a = self.authorities.get(authority_id)
        if a is None:
            return self._decision(UNDETERMINED, "unknown_authority")
        if not a.authenticated or a.quarantined:
            return self._decision(FAIL, "authority_not_usable")
        if not (a.valid_from <= now <= a.valid_until):
            return self._decision(FAIL, "mandate_expired_or_not_started")
        return self._decision(PASS, "bounded_authority", envelope=asdict(a))

    def authorize(self, manifest: ActionManifest, authority_ids: Sequence[str],
                  independent_domains: Sequence[str], now: int,
                  rationale: str, explicit_confirmation: bool,
                  out_of_band: bool = False, emergency: bool = False,
                  conflict_of_interest_disclosed: bool = True) -> Dict[str, Any]:
        if self.frozen:
            return self._decision(FROZEN, "human_freeze_active")
        if manifest.nonce in self.used_nonces:
            return self._decision(FAIL, "replay_rejected")
        if not rationale:
            return self._decision(FAIL, "rationale_required")
        if manifest.high_impact and not explicit_confirmation:
            return self._decision(FAIL, "specific_confirmation_required")
        if manifest.high_impact and not conflict_of_interest_disclosed:
            return self._decision(FAIL, "conflict_of_interest_disclosure_required")
        if manifest.high_impact and len(set(manifest.evidence_sources)) < 2:
            return self._decision(FAIL, "evidence_diversity_required")
        if manifest.high_impact and not manifest.material_objections:
            return self._decision(FAIL, "material_objections_must_be_visible")
        if manifest.action_class == "CONSTITUTIONAL_CHANGE" and not out_of_band:
            return self._decision(FAIL, "out_of_band_confirmation_required")
        if manifest.constitutional_layer == "DNA-L0":
            return self._decision(FAIL, "dna_l0_requires_fork_refounding")
        matching = [e for e in self.entries.values()
                    if e.action_class == manifest.action_class and now <= e.expires_at]
        if not matching:
            return self._decision(UNDETERMINED, "no_applicable_reserved_entry")
        e = matching[0]
        usable = []
        for aid in authority_ids:
            a = self.authorities.get(aid)
            if a and self.authority_envelope(aid, now)["status"] == PASS:
                if manifest.action_class in a.scope or "*" in a.scope:
                    usable.append(a)
        roles = {a.role for a in usable}
        if len(usable) < e.quorum or not set(e.required_roles).issubset(roles):
            return self._decision(FAIL, "quorum_or_role_unsatisfied")
        if len(set(independent_domains)) < e.independent_domains:
            return self._decision(FAIL, "independence_unsatisfied")
        if emergency and manifest.action_class == "CONSTITUTIONAL_CHANGE":
            return self._decision(FAIL, "emergency_cannot_expand_constitutional_power")
        self.used_nonces.add(manifest.nonce)
        return self._decision(PASS, "human_authorization_validated",
                              action_id=manifest.action_id,
                              authority_ids=tuple(a.authority_id for a in usable))

    def delegate(self, source_id: str, child: HumanAuthority, now: int) -> Dict[str, Any]:
        src = self.authorities.get(source_id)
        if src is None or self.authority_envelope(source_id, now)["status"] != PASS:
            return self._decision(FAIL, "invalid_source_authority")
        if child.parent_authority_id != source_id:
            return self._decision(FAIL, "delegation_provenance_required")
        if not set(child.scope).issubset(set(src.scope)):
            return self._decision(FAIL, "delegation_cannot_expand_scope")
        if child.valid_until > src.valid_until or child.valid_from < src.valid_from:
            return self._decision(FAIL, "delegation_cannot_expand_time")
        if child.delegation_depth <= src.delegation_depth:
            return self._decision(FAIL, "invalid_delegation_depth")
        return self.register_authority(child)

    def human_absence(self, requires_human: bool, preauthorized_degraded: bool) -> Dict[str, Any]:
        if not requires_human:
            return self._decision(PASS, "no_reserved_human_authority_required")
        if preauthorized_degraded:
            return self._decision(LIMITED, "preauthorized_safe_degraded_mode")
        return self._decision(FROZEN, "human_required_action_frozen")

    def freeze(self, authority_id: str, now: int) -> Dict[str, Any]:
        if self.authority_envelope(authority_id, now)["status"] != PASS:
            return self._decision(FAIL, "freeze_authority_invalid")
        self.frozen = True
        return self._decision(PASS, "freeze_only_no_amendment")

    def unfreeze(self) -> None:
        self.frozen = False

    def quarantine_authority(self, authority_id: str, reason: str) -> Dict[str, Any]:
        a = self.authorities.get(authority_id)
        if a is None:
            return self._decision(UNDETERMINED, "unknown_authority")
        self.authorities[authority_id] = HumanAuthority(**{**asdict(a), "quarantined": True})
        return self._decision(PASS, "account_quarantined_not_person_delegitimized", quarantine_reason=reason)

    def refusal(self, rule_id: str, legitimate_path: str) -> Dict[str, Any]:
        return self._decision(FAIL, "constitutional_refusal_not_ai_sovereignty",
                              triggered_rule=rule_id, legitimate_path=legitimate_path)

    def action_preview(self, manifest: ActionManifest) -> Dict[str, Any]:
        # Derived from structured manifest, never from persuasive model prose.
        return {
            "action_id": manifest.action_id,
            "class": manifest.action_class,
            "object": manifest.object_id,
            "context": manifest.context,
            "layer": manifest.constitutional_layer,
            "irreversible": manifest.irreversible,
            "high_impact": manifest.high_impact,
            "risk": manifest.risk_summary,
            "objections": list(manifest.material_objections),
        }

    def canonical_contract(self) -> Dict[str, Any]:
        return {
            "milestone": "P095",
            "doctrine": "R19",
            "requirements": dict(R19_REQUIREMENTS),
            "tail": dict(R19_TAIL),
            "canonical_ids": list(CANONICAL_IDS),
            "r19_count": len(R19_REQUIREMENTS),
            "canonical_object_count": len(CANONICAL_IDS),
            "functional_only": FUNCTIONAL_ONLY,
            "phenomenology_undetermined": PHENOMENOLOGY_UNDETERMINED,
            "conceptual_closure_claimed": False,
            "canonical_compliance_proven": False,
        }

    def _decision(self, status: str, reason: str, **extra: Any) -> Dict[str, Any]:
        event = {"status": status, "reason": reason, **extra}
        self.events.append(event)
        return event
