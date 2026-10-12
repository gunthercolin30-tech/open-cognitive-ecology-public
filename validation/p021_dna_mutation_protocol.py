from ontology import dna_mutation_protocol as d
assert d.validate_mutation_protocol()
assert len(d.MUTATION_STAGES)==9 and d.MUTATION_STAGES[0]=="PROPOSAL" and d.MUTATION_STAGES[-1]=="HISTORIZATION"
print("P021_DNA_MUTATION_PROTOCOL_OK")
