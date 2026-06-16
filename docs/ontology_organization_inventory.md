# Inventaire logique des ontologies

Inventaire genere sans importer ni deplacer les modules.
Les classements issus de regles de nommage sont des hypotheses d'audit.

## Synthese

- Modules classes : 800
- Modules canoniques : 199
- Entrees du registre hierarchique : 204
- Extensions hierarchiques explicites : 5
- Divergences de niveaux canoniques : 0
- Aretes de dependances internes : 2179
- Cycles de dependances : 0
- Modules appartenant a un cycle : 0
- Taille du plus grand cycle : 0
- Cycles qualifies pour revue : 0
- Signaux de revue semantique : 0
- Candidats a la normalisation d'identite : 0
- Familles de variantes auditees : 5
- Variantes depassees encore referencees : 0
- Erreurs de validation : 0
- Erreurs de syntaxe detectees : 0
- References de dependances non resolues : 45
- Identifiants de dependances non resolus : 29
- Composants absents confirmes : 0
- Decisions residuelles de cloture : 0

## Roles

| Role | Modules |
|---|---:|
| `concept` | 199 |
| `derived_concept` | 241 |
| `integration` | 41 |
| `maintenance` | 5 |
| `observability` | 67 |
| `runtime` | 192 |
| `support` | 4 |
| `validation` | 51 |

## Revue semantique

Ces signaux indiquent une classification ou une frontiere d'effets a confirmer. Ils ne sont pas des erreurs.

| Severite | Signal | Modules |
|---|---|---:|

### Signaux prioritaires


## Normalisation des identites

Cette file distingue les composants operationnels reellement anonymes des variantes, facades, utilitaires et points d'entree. Elle ne modifie aucun module.

| Priorite | Categorie | Modules |
|---|---|---:|

### Identites prioritaires


## Autorite des variantes

Les familles ci-dessous sont derivees des marqueurs de version et de reparation. Une autorite candidate n'est pas promue automatiquement au statut canonique.

| Decision | Famille | Autorite | Variantes |
|---|---|---|---:|
| `active_variant_only` | `general_open_information_extraction_engine` | `aucune` | 1 |
| `active_variant_only` | `scientific_status_dashboard` | `aucune` | 1 |
| `candidate_authority` | `complex_query_resolution_engine` | `complex_query_resolution_engine` | 1 |
| `confirmed_authority` | `dependency_registry` | `dependency_registry` | 1 |
| `confirmed_authority` | `general_semantic_memory_unified` | `general_semantic_memory_unified` | 2 |

### Detail des familles

- `general_open_information_extraction_engine` : autorite `aucune` (`active_variant_only`) ; variantes `general_open_information_extraction_engine_v2` ; references actives depuis `external_response_parser`, `general_semantic_memory_unified` ; `document_de_facto_authority_or_add_stable_base`.
- `scientific_status_dashboard` : autorite `aucune` (`active_variant_only`) ; variantes `final_scientific_status_dashboard` ; references actives depuis `embodied_coupling_dashboard_exporter`, `longitudinal_autonomous_conversation_validation`, `reflexive_threshold_dashboard` ; `document_de_facto_authority_or_add_stable_base`.
- `complex_query_resolution_engine` : autorite `complex_query_resolution_engine` (`candidate_authority`) ; variantes `general_complex_query_resolution_engine_v4` ; references actives depuis `general_semantic_memory_unified_v3_integration` ; `confirm_candidate_or_keep_family_experimental`.
- `dependency_registry` : autorite `dependency_registry` (`confirmed_authority`) ; variantes `dependency_registry_CLEAN` ; `retain_authority_and_exclude_variants_from_discovery`.
- `general_semantic_memory_unified` : autorite `general_semantic_memory_unified` (`confirmed_authority`) ; variantes `general_semantic_memory_unified_v3_integration`, `general_semantic_memory_unified_v3_runtime_hook` ; references actives depuis `general_semantic_memory_unified_runtime_activation`, `general_semantic_memory_unified_v3_runtime_hook` ; `retain_authority_and_exclude_variants_from_discovery`.

### Variantes depassees encore actives

- Aucune variante depassee encore referencee.

### File de migration des variantes

- Aucune migration de variante requise.

## Revue des cycles de dependances

Les cycles sont qualifies sans modifier les declarations de dependances. Les aretes candidates restent des hypotheses de decouplage a verifier.


## Decisions residuelles de cloture


## Hierarchie

Le noyau canonique documente couvre les niveaux 0 a 9. Les extensions meta ci-dessous appartiennent au registre hierarchique sans appartenir au noyau documentaire.

- `ontological_attractor_mapping` : niveau 9.
- `ontology_topology_governance` : niveau 9.
- `reflexive_ontology_governor` : niveau 10.
- `semantic_density_tracker` : niveau 9.
- `topological_pressure_monitor` : niveau 9.

### Concepts canoniques avec effets

- `corpus_simulation_engine` : profil `filesystem`.

## Topologie des dependances

Les cycles sont des constats d'organisation. Ils ne sont pas consideres invalides automatiquement.

### Composantes cycliques


### File de decouplage logique

La priorite combine taille, densite, reciprocite et melange de roles. Elle ne prescrit aucun deplacement.


### Couplages de roles dominants

| Role source | Role cible | Aretes |
|---|---|---:|
| `derived_concept` | `derived_concept` | 488 |
| `runtime` | `runtime` | 242 |
| `derived_concept` | `concept` | 234 |
| `runtime` | `derived_concept` | 181 |
| `runtime` | `observability` | 113 |
| `derived_concept` | `runtime` | 96 |
| `runtime` | `concept` | 85 |
| `observability` | `observability` | 72 |
| `validation` | `runtime` | 65 |
| `observability` | `runtime` | 62 |
| `integration` | `runtime` | 61 |
| `validation` | `derived_concept` | 58 |

## Statuts

| Statut | Modules |
|---|---:|
| `canonical` | 202 |
| `compatibility` | 5 |
| `experimental` | 591 |
| `superseded` | 2 |

## Profils d'execution

| Profil | Modules |
|---|---:|
| `filesystem` | 162 |
| `network` | 5 |
| `pure` | 611 |
| `stateful` | 4 |
| `subprocess` | 18 |

## Confiance du classement

| Confiance | Modules |
|---|---:|
| `established` | 268 |
| `inferred` | 532 |

## Dependances non resolues

Ces categories sont des hypotheses de tri. Elles distinguent les references abstraites probables des composants operationnels probablement absents ou renommes.

| Categorie | References |
|---|---:|
| `abstract_capability` | 31 |
| `alias_candidate` | 8 |
| `deprecated_reference` | 1 |
| `external_tool` | 3 |
| `internalized_capability` | 2 |

| Source de resolution | References |
|---|---:|
| `policy_decision` | 45 |

| Confiance de resolution | References |
|---|---:|
| `high` | 39 |
| `medium` | 6 |

### Composants manquants ou renommes a examiner

- `constitutional_alignment` (3 reference(s)) : priorite `medium`, `alias_candidate`, confiance `high` ; requis par `constitutional_alert_system`, `constitutional_legislative_assembly`, `recursive_self_improvement_governor`. Remplacement : `constitutional_alignment_field`. Suggestions heuristiques : aucune suggestion.
- `global_viability_score` (2 reference(s)) : priorite `medium`, `alias_candidate`, confiance `medium` ; requis par `civilizational_intelligence_growth_index`, `constitutional_alert_system`. Remplacement : `global_viability_certificate`. Suggestions heuristiques : aucune suggestion.
- `historical_metrics_harvester` (2 reference(s)) : priorite `medium`, `alias_candidate`, confiance `medium` ; requis par `extended_certification_continuity_tracker`, `longitudinal_trend_stability_analyzer`. Remplacement : `longitudinal_metrics_archive`. Suggestions heuristiques : aucune suggestion.
- `civilizational_independence_certification` (1 reference(s)) : priorite `medium`, `deprecated_reference`, confiance `high` ; requis par `extended_longitudinal_readiness_certification`. Remplacement : `distributed_civilizational_continuity_certification`. Suggestions heuristiques : aucune suggestion.
- `distributed_governance_metrics` (1 reference(s)) : priorite `medium`, `alias_candidate`, confiance `high` ; requis par `distributed_civilizational_certifier`. Remplacement : `distributed_governance_metrics_extraction`. Suggestions heuristiques : aucune suggestion.

### Capacites abstraites confirmees

- `belief_revision` : utilise par `internal_conflict_monitoring`, `uncertainty_awareness`.
- `bifurcation_process` : utilise par `adaptive_civilizational_bifurcation`.
- `constraint_conflict_detection` : utilise par `internal_conflict_monitoring`.
- `distributed_scheduler_ecology` : utilise par `civilizational_scheduler_ecosystem`, `scheduler_mutation_ecology`.
- `episodic_memory` : utilise par `autobiographical_memory`.
- `error_tracking` : utilise par `self_confidence_calibration`.
- `future_self_projection` : utilise par `global_temporal_binding`.
- `global_workspace` : utilise par `conscious_access_control`, `consciousness_readiness_index`, `global_self_broadcast`.
- `goal_conflict_detection` : utilise par `internal_conflict_monitoring`.
- `goal_management` : utilise par `global_temporal_binding`, `reflective_goal_revision`.
- `institutional_viability` : utilise par `constitutional_legislative_assembly`, `meta_governance_council`.
- `intergenerational_transmission_process` : utilise par `intergenerational_symbolic_transition`.
- `meta_scheduler_fragmentation_governance` : utilise par `civilizational_scheduler_ecosystem`, `scheduler_mutation_ecology`.
- `performance_monitoring` : utilise par `self_confidence_calibration`.
- `phenomenological_topology` : utilise par `reflexive_topology_self_revision`.
- `report_generation` : utilise par `consciousness_readiness_index`, `genealogical_evolution_dashboard`, `introspective_reporting`, `self_narrative_generation`.
- `runtime_scheduler_pluralization` : utilise par `scheduler_mutation_ecology`.
- `salience_engine` : utilise par `conscious_access_control`.
- `trajectory_optimality` : utilise par `continuation_optimality`.
- `working_memory` : utilise par `experiential_stream_integration`.
- `world_continuation_conditions` : utilise par `continuation_optimality`.

## Modules a confirmer

Les modules suivants possedent encore un classement de repli ou une erreur d'analyse.

- Aucun module restant.
