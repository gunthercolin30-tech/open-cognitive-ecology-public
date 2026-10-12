from oif.interface.models import ComponentSpecification, ModelViolation
for key in ("module", "class_path", "callable", "entrypoint", "python", "javascript", "shell", "eval", "exec", "import"):
    try:
        ComponentSpecification(component_id="x", component_type="card", properties={key: "danger"})
        raise AssertionError("forbidden key accepted: %s" % key)
    except ModelViolation:
        pass
try:
    ComponentSpecification(component_id="x", component_type="card", properties={"nested": {"shell": "rm -rf /"}})
    raise AssertionError("nested forbidden key accepted")
except ModelViolation:
    pass
print("OIF2B_SECURITY_OK")
