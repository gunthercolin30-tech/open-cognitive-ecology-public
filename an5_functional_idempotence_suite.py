from ontology.countermodel_generator import CountermodelGenerator

VOLATILE_KEYS = {
    "timestamp",
    "timestamp_utc",
    "run_id",
    "execution_id",
    "generated_at",
    "diagnostics",
}

def normalize(x):
    if isinstance(x, dict):
        return {
            k: normalize(v)
            for k, v in x.items()
            if k not in VOLATILE_KEYS
        }
    if isinstance(x, list):
        return [normalize(v) for v in x]
    return x

g = CountermodelGenerator()

r1 = normalize(g.step(persist=False))
r2 = normalize(g.step(persist=False))

assert r1 == r2

print("AN5_FUNCTIONAL_IDEMPOTENCE_OK")
