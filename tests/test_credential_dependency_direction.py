from ontology.credential_vault import CredentialVault, DEPENDENCIES


def test_credential_vault_accepts_rotation_result_without_monitor_dependency(
    tmp_path,
):
    rotation_result = {
        "primitive": "credential_rotation_monitor",
        "success": True,
        "rotation_due_count": 2,
    }

    result = CredentialVault(root=tmp_path).step({
        "rotation_result": rotation_result,
    })

    assert "credential_rotation_monitor" not in DEPENDENCIES
    assert result["rotation"] == rotation_result


def test_credential_vault_status_marks_missing_external_rotation_result(tmp_path):
    result = CredentialVault(root=tmp_path).status()

    assert result["success"] is True
    assert result["rotation"] == {
        "primitive": "credential_rotation_monitor",
        "status": "external_result_not_supplied",
        "success": False,
    }
