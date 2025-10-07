import os
import ast
import json

CORE_MODULES_DIR = os.path.join(os.path.dirname(__file__), "transpiler", "core_libs")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "core_modules_index.json")


def extract_function_info(node: ast.FunctionDef) -> dict:
    args = node.args.args
    defaults_count = len(node.args.defaults)
    non_default_count = len(args) - defaults_count

    args_with_types = []
    for i, arg in enumerate(args):
        arg_name = arg.arg
        arg_type = ast.unparse(arg.annotation) if arg.annotation else None

        if i < non_default_count:
            default_val = None
        else:
            default_val = ast.unparse(node.args.defaults[i - non_default_count])

        # Compose signature part
        if arg_type and default_val:
            formatted = f"{arg_name}: {arg_type} = {default_val}"
        elif arg_type:
            formatted = f"{arg_name}: {arg_type}"
        elif default_val:
            formatted = f"{arg_name} = {default_val}"
        else:
            formatted = arg_name

        args_with_types.append(formatted)

    # Return type
    return_type = f" -> {ast.unparse(node.returns)}" if node.returns else ""

    signature = f"({', '.join(args_with_types)}){return_type}"

    return {
        "name": node.name,
        "signature": signature,
        "doc": ast.get_docstring(node) or "No docstring available",
    }


def extract_class_info(node: ast.ClassDef) -> dict:
    methods = [
        extract_function_info(n) for n in node.body if isinstance(n, ast.FunctionDef)
    ]
    return {
        "name": node.name,
        "doc": ast.get_docstring(node) or "No docstring available",
        "methods": methods,
    }


def extract_global_vars(nodes: list) -> list:
    vars_info = []
    for node in nodes:
        if isinstance(node, ast.Assign):
            targets = [ast.unparse(t) for t in node.targets]
            value = ast.unparse(node.value)
            for var in targets:
                if var.startswith("__") and var.endswith("__"):
                    continue  # Skip dunder vars
                vars_info.append({"name": var, "value": value})
    return vars_info


def parse_module(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        print(f"⚠️ Skipping {filepath}: Syntax error -> {e}")
        return {}

    top_level_nodes = tree.body

    # FIXED: Changed "ModuleEntry" to "doc" to match TypeScript expectations
    return {
        "doc": ast.get_docstring(tree)
        or "No module docstring available",  # ← CHANGED THIS LINE
        "functions": [
            extract_function_info(n)
            for n in top_level_nodes
            if isinstance(n, ast.FunctionDef)
        ],
        "classes": [
            extract_class_info(n)
            for n in top_level_nodes
            if isinstance(n, ast.ClassDef)
        ],
        "variables": extract_global_vars(top_level_nodes),
    }


def generate_index() -> dict:
    index = {}
    for root, _, files in os.walk(CORE_MODULES_DIR):
        for fname in files:
            if fname.endswith(".py"):
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, CORE_MODULES_DIR)
                module_name = rel_path.replace(os.sep, ".").rsplit(".py", 1)[0]
                module_info = parse_module(full_path)
                index[module_name] = module_info
    return index


def main():
    index = generate_index()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print(f"✅ Index generated at: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
