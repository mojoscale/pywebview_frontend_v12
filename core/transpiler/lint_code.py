import ast
import uuid
from .transpiler import (
    DependencyResolver,
    parse_external_python_file,
    extract_imported_modules_from_tree,
    ArduinoTranspiler,
    TypeAnalyzer,
    is_core_python_type,
    is_builtin_function,
)
import importlib
import os
import traceback
import sys

import builtins
import inspect
import json

from .builtin_types import get_core_func_metadata

builtin_funcs = [
    name
    for name in dir(builtins)
    if inspect.isbuiltin(getattr(builtins, name))
    or inspect.isfunction(getattr(builtins, name))
]


DISALLOWED_NODE_TYPES = [
    "Assert",
    "AsyncFor",
    "AsyncFunctionDef",
    "AsyncWith",
    "Await",
    "ClassDef",
    "Del",
    "Delete",
    "DictComp",
    "ExceptHandler",
    "Interactive",
    "ListComp",
    "Lambda",
    "MatMult",
    "Match",
    "MatchAs",
    "MatchClass",
    "MatchMapping",
    "MatchOr",
    "MatchSequence",
    "MatchSingleton",
    "MatchStar",
    "MatchValue",
    "Nonlocal",
    "ParamSpec",
    "Raise",
    "Set",
    "SetComp",
    "Starred",
    "Suite",
    "Try",
    "TryStar",
    "Tuple",
    "TypeIgnore",
    "TypeVar",
    "TypeVarTuple",
    "With",
    "Yield",
    "YieldFrom",
    "_ast_Ellipsis",
    "arg",
    "arguments",
    "comprehension",
    "excepthandler",
    "keyword",
    "match_case",
    "pattern",
    "type_param",
    "withitem",
]


class LintCode(ast.NodeVisitor):
    def __init__(
        self,
        sql_conn,
        platform,
        path_to_core_libs,
        dependency_resolver,
        module_name,
    ):
        self.errors = []
        self.session_id = str(uuid.uuid4()).replace("-", "_")
        self.sql_conn = sql_conn
        self.platform = platform
        self.path_to_core_libs = path_to_core_libs
        self.dependency_resolver = dependency_resolver

        self.is_within_If = False
        self.is_within_For = False
        self.is_within_While = False

        self.module_name = module_name

        self.scope = "global"

        self.loop_variables = {}

        self.type_analyzer = TypeAnalyzer(
            dependency_resolver=self.dependency_resolver,
            current_module_name=self.module_name,
            get_scope=lambda: self.scope,
            get_is_inside_loop=lambda: self.is_within_For,
            get_loop_vars=lambda: self.loop_variables,
        )

    def generic_visit(self, node):
        node_type = type(node).__name__
        if node_type in DISALLOWED_NODE_TYPES:
            self.add_error(node, f"Use of '{node_type}' is not allowed")
        super().generic_visit(node)

    def add_error(self, node, message):
        """Add error with line and column from AST node."""
        lineno = getattr(node, "lineno", 1)
        col = getattr(node, "col_offset", 1)
        self.errors.append({"line": lineno, "column": col, "message": message})

    def run_global_checks(self):
        # check if main and loop present
        if (
            not self.dependency_resolver.is_setup_and_loop_present()
            and self.module_name == "main"
        ):
            error = {
                "line": 1,
                "column": 1,  # Already 1-based
                "message": "'setup()' and 'loop()' must be defined in main.py",
            }
            self.errors.append(error)

    def lint(self, code: str):
        """Parse and walk AST, collect syntax and runtime errors with full tracebacks."""
        self.errors = []  # Reset errors for each lint

        try:
            tree = ast.parse(code)
            self.visit(tree)
        except SyntaxError as e:
            return {
                "errors": [
                    {
                        "line": e.lineno or 1,
                        "column": e.offset or 1,
                        "message": e.msg,
                    }
                ]
            }
        except Exception as ex:
            detailed_trace = traceback.format_exc()
            return {
                "errors": [
                    {
                        "line": 1,
                        "column": 1,
                        "message": (
                            "Unexpected internal error during linting:\n"
                            f"{str(ex)}\n\n"
                            "Full traceback:\n"
                            f"{detailed_trace}"
                        ),
                    }
                ]
            }

        self.run_global_checks()

        return {"errors": self.errors}

    def is_core_module(self, import_name: str) -> bool:
        """
        Check if the full module path (e.g., 'sensors.x.y') exists in core libs.
        """
        try:
            parts = import_name.split(".")
            file_path = os.path.join(self.path_to_core_libs, *parts) + ".py"
            init_path = os.path.join(self.path_to_core_libs, *parts, "__init__.py")

            if os.path.isfile(file_path):
                print(f"[DEBUG] Found file module at {file_path}")
                return True
            if os.path.isfile(init_path):
                print(f"[DEBUG] Found package module at {init_path}")
                return True

            print(f"[DEBUG] Module '{import_name}' not found in core libs")
            return False
        except Exception as e:
            print(f"[ERROR] is_core_module('{import_name}') exception: {e}")
            return False

    def visit_Import(self, node):
        if (
            self.scope != "global"
            or self.is_within_If
            or self.is_within_For
            or self.is_within_While
        ):
            self.add_error(
                node, "Import not allowed within function or logical constructors."
            )
        for alias in node.names:
            import_name = alias.name  # e.g., "sensors.x"
            import_alias = alias.asname  # e.g., "sx"
            parts = import_name.split(".")  # ["sensors", "x"]

            print(f"[LINT] Processing import: '{import_name}'")

            # Rule 2: Must be aliased
            if import_alias is None:
                print(f"[ERROR] Missing alias for import: '{import_name}'")
                self.add_error(
                    node,
                    f"Import '{import_name}' must use 'as' alias (e.g., 'import {import_name} as x')",
                )

            # Rule 3: The full module path must exist in custom core_libs
            if not self.is_core_module(import_name):
                print(
                    f"[ERROR] '{import_name}' is not found in allowed modules under core_libs"
                )
                self.add_error(
                    node,
                    f"Import '{import_name}' is not in the list of allowed modules",
                )
            else:
                print(f"[LINT] Import '{import_name}' passed validation")
                self.dependency_resolver.insert_imported_module(
                    self.module_name, import_name, import_alias
                )

        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        # Rule 1: from x import y is not allowed
        self.add_error(node, f"'from {node.module} import ...' is not allowed")
        self.generic_visit(node)

    def _save_function_args(self, node):
        return_type = None
        func_name = node.name
        if node.returns:
            return_type = self.type_analyzer._extract_annotation(node.returns)

        save_args = []

        for arg in node.args.args:
            arg_name = arg.arg
            arg_type = self.type_analyzer._extract_annotation(arg.annotation)
            save_args.append({"arg_name": arg_name, "arg_type": arg_type})

        self.dependency_resolver._insert_method(
            func_name,
            None,
            self.module_name,
            "user",
            json.dumps(save_args),
            return_type,
        )

        return

    def visit_FunctionDef(self, node):
        if self.scope != "global":
            # function is defined within another function
            error_text = "Function within function not allowed."
            self.add_error(node, error_text)

        if self.is_within_If or self.is_within_For or self.is_within_While:
            self.add_error(
                node,
                "Function cannot be defined within logical constructors like If/For/While.",
            )

        func_name = node.name
        self.scope = func_name

        if func_name in builtin_funcs or func_name == "range":
            error_text = f"{func_name} is a builtin func and cannot be overriden."
            self.add_error(node, error_text)

        imported_global_methods = self.dependency_resolver.get_imported_global_methods(
            self.module_name
        )  # returns a dict

        if func_name in imported_global_methods.keys():
            imported_from_module = imported_global_methods[func_name]
            error_text = f"{func_name} is imported from {imported_from_module}. \n Consider renaming this method."
            self.add_error(node, error_text)

        if node.returns is None:
            self.add_error(
                node,
                f"Function '{func_name}' must have a return type annotation using '->'",
            )

        for arg in node.args.args:
            if arg.annotation is None:
                self.add_error(
                    arg,
                    f"Argument '{arg.arg}' in function '{func_name}' must have a type annotation",
                )

        # Recursively visit body of the function
        for stmt in node.body:
            self.visit(stmt)

        self._save_function_args(node)

        # After body, reset scope to global
        self.scope = "global"

    def visit_If(self, node):
        self.is_within_If = True

        if self.scope == "global":
            self.add_error(node, "'if' can be only called within a function body.")

        if self.scope == "global":
            # in arduino, if only works within function/class body
            error_text = "'If' can only be called within function body."
            self.add_error(node, error_text)

        for stmt in node.body:
            self.visit(stmt)

        self.is_within_If = False

    def visit_For(self, node):
        self.is_within_For = True

        if self.scope == "global":
            self.add_error(node, "'for' can be only called within a function body.")

        # cannot be called on global scope in arduino

        if self.scope == "global":
            self.add_error(node, "'if' can be only called within a function body.")

        loop_var_type = self.type_analyzer.get_node_type(node.iter)
        loop_type = loop_var_type.split(",")[0]
        loop_var = node.target
        iterable = node.iter

        if loop_type == "range":
            self.loop_variables[loop_var] = "int"
        elif loop_type == "list":
            element_type = loop_var_type.split(",")[1]
            self.loop_variables[loop_var] = element_type
        elif loop_type == "dict_items":
            _, key_type, value_type = loop_var_type.split(",")
            self.loop_variables[key_var] = key_type
            self.loop_variables[val_var] = value_type

        elif loop_type == "str":
            self.loop_variables[loop_var] = "str"

        if self.scope == "global":
            # in arduino, if only works within function/class body
            error_text = "'For' can only be called within function body."
            self.add_error(node, error_text)

        for stmt in node.body:
            self.visit(stmt)

        self.is_within_For = False

    def visit_Assign(self, node):
        lhs_name = node.targets[0].id
        rhs_type = self.type_analyzer.get_node_type(node.value)

        self.dependency_resolver.insert_variable(
            lhs_name, rhs_type, self.module_name, "user"
        )

        self.visit(node.value)

    def _check_passed_method_args(
        self, call_args: list[str], saved_args: list[dict], method_name: str, node
    ) -> None:
        errors = []
        if len(saved_args) != len(call_args):
            errors.append(
                f"{method_name} takes {len(saved_args)} arguments; but you passed {len(call_args)}",
            )

        else:
            for i in range(len(saved_args)):
                arg = saved_args[i]

                if arg["arg_type"] != call_args[i]:
                    errors.append(
                        f'{arg["name"]} is expected of type {arg["arg_type"]}, but you passed {call_args[i]}'
                    )

        for error in errors:
            self.add_error(node, error)

    def visit_Call(self, node):
        # can only be called within function
        if self.scope == "global":
            self.add_error(node, "Methods can be only called within a function body.")
        func = node.func

        call_args = []

        for arg in node.args:
            arg_type = self.type_analyzer.get_node_type(arg)
            call_args.append(arg_type)

        print(f"call of node type {func}")

        if isinstance(func, ast.Attribute):
            # either an imported module or
            # a variable
            method_name = node.func.attr

            if isinstance(node.func.value, ast.Name):
                base_name = node.func.value.id
                module_name = self.dependency_resolver.get_module_name_from_alias(
                    self.module_name, base_name
                )

                print(f"found module {module_name} for base name {base_name}")

                if module_name:
                    # check if the method is actually a class and this call is
                    # class initialization.

                    is_method_class = self.dependency_resolver.is_module_class(
                        method_name, module_name=module_name
                    )

                    print(f"method {method_name} is class {is_method_class}")

                    if is_method_class:
                        method_metadata = self.dependency_resolver.get_method_metadata(
                            "__init__", module_name=module_name, class_name=method_name
                        )

                        actual_saved_args = method_metadata["args"]

                        method_metadata["args"] = actual_saved_args[
                            1:
                        ]  # first arg is self, so gotta remove.

                    else:
                        method_metadata = self.dependency_resolver.get_method_metadata(
                            method_name, module_name=module_name, class_name=None
                        )

                    if not method_metadata:
                        self.add_error(
                            node,
                            f"{method_name} is not defined in {module_name}.\n Please recheck the name.",
                        )

                    else:
                        # metadata exists, lets do the args check.
                        saved_args = method_metadata["args"]

                        self._check_passed_method_args(
                            call_args, saved_args, method_name, node
                        )

                else:
                    # its a variable
                    variable_type = self.dependency_resolver.get_variable_type(
                        base_name, self.scope
                    )

                    if is_core_python_type(variable_type):
                        pass

                    else:
                        # this is custom class type.
                        variable_module_name = (
                            self.dependency_resolver.get_variable_module_name(
                                base_name, self.scope
                            )
                        )
                        method_metadata = self.dependency_resolver.get_method_metadata(
                            method_name, module_name=None, class_name=variable_type
                        )

                        if not method_metadata:
                            self.add_error(
                                node,
                                f"'{method_name}' method does not exist in type {variable_type}, please check the method name.",
                            )

                        else:
                            saved_args = method_metadata["args"]

                            saved_args = saved_args[
                                1:
                            ]  # the first arg is self so it needs to be removed

                            self._check_passed_method_args(
                                call_args, saved_args, method_name, node
                            )

        elif isinstance(node.func, ast.Name):
            # direct function call which is defined in
            # current module
            method_name = node.func.id

            if is_builtin_function(method_name):
                builtin_func_metadata = get_core_func_metadata(method_name)

                is_allowed = builtin_func_metadata["is_allowed"]

                if not is_allowed:
                    self.add_error(
                        node,
                        f"method '{method_name}' is not allowed. Try alternatives.",
                    )

            else:
                method_metadata = self.dependency_resolver.get_method_metadata(
                    method_name, module_name=self.module_name, class_name=None
                )

                if not method_metadata:
                    self.add_error(node, f"method '{method_name}' could not be found.")
                else:
                    saved_args = method_metadata["args"]
                    self._check_passed_method_args(
                        call_args, saved_args, method_name, node
                    )


def main(code, sql_conn, platform, path_to_core_libs, module_name="main"):
    tree = ast.parse(code)
    """try:
        tree = ast.parse(code)

    except SyntaxError as e:
        return {
            "errors": [
                {
                    "line": e.lineno or 1,
                    "column": (e.offset or 1),  # Already 1-based
                    "message": e.msg,
                }
            ]
        }
    except Exception as ex:
        return {
            "errors": [
                {"line": 1, "column": 1, "message": f"Unexpected error: {str(ex)}"}
            ]
        }"""

    extracted_modules = extract_imported_modules_from_tree(tree, path_to_core_libs)

    session_id = str(uuid.uuid4()).replace("-", "_")
    monitor_speed = 115200

    dependency_resolver = DependencyResolver(
        session_id, sql_conn, platform, imported_modules=extracted_modules
    )

    linter = LintCode(
        sql_conn,
        platform,
        path_to_core_libs,
        dependency_resolver,
        module_name,
    )

    return linter.lint(code)
