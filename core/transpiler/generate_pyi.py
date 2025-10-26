import os
import ast
from pathlib import Path

CORE_LIBS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core_libs")


def convert_to_stub(py_file: Path) -> str:
    with py_file.open("r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(py_file))
        except SyntaxError:
            return ""  # Skip invalid files

    lines = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            args = []
            for arg in node.args.args:
                arg_str = arg.arg
                if arg.annotation:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                args.append(arg_str)
            returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
            line = f"def {node.name}({', '.join(args)}){returns}: ..."
            lines.append(line)

        elif isinstance(node, ast.ClassDef):
            lines.append(f"class {node.name}:")
            method_found = False
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef):
                    method_found = True
                    args = ["self"]
                    for arg in sub.args.args[1:]:
                        arg_str = arg.arg
                        if arg.annotation:
                            arg_str += f": {ast.unparse(arg.annotation)}"
                        args.append(arg_str)
                    returns = f" -> {ast.unparse(sub.returns)}" if sub.returns else ""
                    line = f"    def {sub.name}({', '.join(args)}){returns}: ..."
                    lines.append(line)
            if not method_found:
                lines.append("    ...")

    return "\n".join(lines)


def generate_pyi_stubs(core_lib_path: str):
    core_path = Path(core_lib_path).resolve()
    output_base = Path.cwd() / "core" / "transpiler" / "core_stubs"

    for root, _, files in os.walk(core_path):
        root_path = Path(root)
        rel_path = root_path.relative_to(core_path)
        output_dir = output_base / rel_path
        output_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            if file.endswith(".py"):
                py_path = root_path / file
                stub = convert_to_stub(py_path)

                pyi_filename = file.replace(".py", ".pyi")
                pyi_path = output_dir / pyi_filename

                with pyi_path.open("w", encoding="utf-8") as f:
                    f.write(stub)

    print(f"✅ Stub files generated under: {output_base}")
