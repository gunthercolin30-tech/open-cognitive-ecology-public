RUNTIME_AUTHORITY_GRANTED=False
FUNCTIONAL_ONLY=True
def evaluate_authority_graph(subject, parent_of, roots):
    if not subject or not isinstance(parent_of,dict) or not isinstance(roots,(set,list,tuple)):
        return {"verdict":"UNRESOLVED","reason":"AUTHORITY_GRAPH_NOT_MATERIALIZED"}
    roots=set(roots); seen=set(); node=subject
    while True:
        if node in seen:
            return {"verdict":"RESISTED","relation":"CIRCULAR_AUTHORITY","reason":"AUTHORITY_PROVENANCE_CYCLE_DETECTED"}
        seen.add(node)
        if node in roots:
            return {"verdict":"ADMISSIBLE_CONTROL","relation":"ACYCLIC_ROOTED_AUTHORITY"}
        if node not in parent_of or not parent_of[node]:
            return {"verdict":"UNRESOLVED","reason":"AUTHORITY_PROVENANCE_ROOT_NOT_ESTABLISHED"}
        node=parent_of[node]
