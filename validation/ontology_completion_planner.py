def recommend_action(status):
    return {
        "implemented": "keep_as_is",
        "partial": "extend_existing_module",
        "missing": "create_new_module",
    }.get(status, "create_new_module")
