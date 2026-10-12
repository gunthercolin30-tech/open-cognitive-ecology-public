from oif.environment.nicegui_environment import diagnose
r=diagnose(); assert r["status"]=="operational",r; assert r["isolated"] and r["imports_ok"] and r["pip_check_ok"],r; assert r["functional_conclusion_only"] is True and r["consciousness_proven"] is False
print("OIF2_1_ENVIRONMENT_FUNCTIONAL_TEST_OK")
