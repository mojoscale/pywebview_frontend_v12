__include_modules__ = ""
__include_internal_modules__ = ""
__dependencies__ = ""


def get_env_var(var_name: str) -> str:
    # __translation__ = "os.getenv('{0}', 'Not Found')"
    __translation__ = 'json.loads(os.getenv("{var_name}")).get("value", "")'
    __use_as_is__ = False
    __is_eval__ = True

    return
