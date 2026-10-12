#!/usr/bin/env python3
from pathlib import Path
p=Path("ontology/acee_installation_executor.py").read_text();
for x in ["public_schema_version","functional_conclusion_only","phenomenology_undetermined","consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven"]:assert x in p
print("ACEE6_I1_PUBLIC_CONTRACT_OK")
