from __future__ import annotations
from oif.interface.serialization import SerializationViolation, load_yaml_mapping

def reject(text):
    try:
        load_yaml_mapping(text)
    except SerializationViolation:
        return
    raise AssertionError("unsafe YAML accepted")

for sample in (
    "- a\n- b\n", "42\n", "true\n", "a: 1\n---\nb: 2\n",
    "? [a, b]\n: value\n", "x: .nan\n", "x: .inf\n", "x: -.inf\n",
    "value: !!python/object/apply:os.system ['echo forbidden']\n",
    "a: &a [*a]\n",
):
    reject(sample)

bomb = "a: &a [x]\n"
previous = "a"
for index in range(40):
    name = "k%d" % index
    bomb += "%s: &%s [*%s]\n" % (name, name, previous)
    previous = name
reject(bomb)

print("OIF2C_YAML_ADVERSARIAL_CAMPAIGN_OK")
