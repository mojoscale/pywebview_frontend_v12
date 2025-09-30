import inspect
import builtins
from typing import get_type_hints

ALLOWED_CORE_FUNCS = {
    "len",
    "range",
    "sum",
    "max",
    "min",
    "sorted",
    "reversed",
    "list",
    "dict",
    "str",
    "bool",
    "int",
    "float",
    "print",
}


def get_core_func_metadata(func_name: str) -> dict:
    metadata = {
        "is_allowed": False,
        "method_name": func_name,
        "args": [],
        "return_type": None,
    }

    if func_name not in ALLOWED_CORE_FUNCS or not hasattr(builtins, func_name):
        return metadata

    metadata["is_allowed"] = True

    func = getattr(builtins, func_name)

    try:
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
    except (ValueError, TypeError):
        # For built-ins without inspectable signatures
        return metadata

    args = []
    for param in sig.parameters.values():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue  # skip *args, **kwargs
        arg_name = param.name
        arg_type = type_hints.get(arg_name, "Any")

        # handle generics like list[str], dict[str, bool]
        if hasattr(arg_type, "__origin__"):
            origin = arg_type.__origin__
            if origin in [list, dict]:
                args_str = (
                    origin.__name__
                    + ","
                    + ",".join(t.__name__ for t in arg_type.__args__)
                )
            else:
                args_str = str(arg_type)
        elif hasattr(arg_type, "__name__"):
            args_str = arg_type.__name__
        else:
            args_str = str(arg_type)

        args.append({"name": arg_name, "arg_type": args_str})

    metadata["args"] = args

    ret_type = type_hints.get("return", None)
    if ret_type:
        if hasattr(ret_type, "__origin__") and ret_type.__origin__ is tuple:
            metadata["return_type"] = "list," + ",".join(
                t.__name__ for t in ret_type.__args__
            )
        elif hasattr(ret_type, "__origin__") and ret_type.__origin__ in [list, dict]:
            metadata["return_type"] = (
                ret_type.__origin__.__name__
                + ","
                + ",".join(t.__name__ for t in ret_type.__args__)
            )
        elif hasattr(ret_type, "__name__"):
            metadata["return_type"] = ret_type.__name__
        else:
            metadata["return_type"] = str(ret_type)

    return metadata
