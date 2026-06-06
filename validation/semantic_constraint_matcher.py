import re


# Table de synonymes conceptuels.
# Chaque concept théorique est associé à une liste de termes susceptibles
# d'apparaître dans :
# - les noms de fichiers,
# - les noms de classes,
# - les noms de fonctions.
CONCEPT_SYNONYMS = {
    "GLOBAL_NON_CLOSURE": [
        "global_non_closure",
        "non_closure",
        "anti_closure",
        "impossibility_of_global_closure",
    ],
    "INCOMPLETENESS": [
        "incompleteness",
        "structural_incompleteness",
        "incomplete_representation",
        "incomplete_transmission",
    ],
    "NON_REPRESENTABILITY": [
        "non_representability",
        "theory_of_non_representability",
        "unrepresentable",
    ],
    "MINIMAL_DNA": [
        "minimal_dna",
        "structural_dna",
        "invariant_genome",
        "genome",
        "dna",
    ],
    "REAL_SUCCESSION": [
        "real_succession",
        "succession",
        "lineage",
        "lineage_manager",
        "intergenerational_divergence",
    ],
    "STRUCTURAL_INCOHERENCE": [
        "structural_incoherence",
        "quantum_incoherence",
        "controlled_incoherence",
        "incoherence",
    ],
}


def normalize(text):
    """
    Normalise une chaîne pour faciliter les comparaisons.
    """
    if text is None:
        return ""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9_]+", "_", text)
    return text.strip("_")


def build_inventory_text(inventory):
    """
    Construit une représentation textuelle normalisée de l'inventaire.
    """
    tokens = []

    for item in inventory:
        # Nom du fichier
        if "file" in item:
            tokens.append(normalize(item["file"]))

        # Classes
        for cls in item.get("classes", []):
            tokens.append(normalize(cls))

        # Fonctions
        for fn in item.get("functions", []):
            tokens.append(normalize(fn))

    return " ".join(tokens)


def find_matching_terms(concept, inventory_text):
    """
    Retourne les synonymes du concept qui apparaissent dans l'inventaire.
    """
    synonyms = CONCEPT_SYNONYMS.get(concept, [concept])

    found = []

    for synonym in synonyms:
        normalized = normalize(synonym)
        if normalized and normalized in inventory_text:
            found.append(synonym)

    return found


def determine_status(found_terms):
    """
    Détermine le statut de couverture :
    - implemented : plusieurs indices cohérents
    - partial     : un seul indice
    - missing     : aucun indice
    """
    if len(found_terms) >= 2:
        return "implemented"
    elif len(found_terms) == 1:
        return "partial"
    else:
        return "missing"


def match(constraints, concepts, inventory):
    """
    Établit les correspondances entre les concepts théoriques et l'ontologie.

    Paramètres
    ----------
    constraints : list
        Contraintes issues du tableau C/CQ (non utilisé directement pour
        l'instant mais conservé pour les versions futures).
    concepts : list[str]
        Liste des concepts à analyser.
    inventory : list[dict]
        Inventaire de l'ontologie.

    Retour
    ------
    list[dict]
        Liste des correspondances avec :
        - concept
        - status
        - matching_terms
    """
    inventory_text = build_inventory_text(inventory)

    results = []

    for concept in concepts:
        found_terms = find_matching_terms(concept, inventory_text)
        status = determine_status(found_terms)

        results.append({
            "concept": concept,
            "status": status,
            "matching_terms": found_terms,
        })

    return results