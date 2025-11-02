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
    extract_annotation_type,
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
    "IfExp",
]


def has_invalid_chars(s: str) -> bool:
    """
    Checks whether the given string contains characters
    outside the valid ASCII printable range (32–126).

    Args:
        s (str): Input string.

    Returns:
        bool: True if the string contains any invalid characters.
    """
    for ch in s:
        code = ord(ch)
        if code < 32 or code > 126:
            return True
    return False


def safe_visit(method):
    """Decorator to catch unexpected exceptions at node level."""

    def wrapper(self, node, *args, **kwargs):
        try:
            return method(self, node, *args, **kwargs)
        except Exception as ex:
            lineno = getattr(node, "lineno", 1)
            col = getattr(node, "col_offset", 1)
            # Add a soft, user-facing error instead of killing the linter
            msg = (
                f"⚠️ Internal error while checking this line: "
                f"{type(ex).__name__} - {ex}. "
                f"Try simplifying or rewriting this line."
            )
            self.errors.append({"line": lineno, "column": col, "message": msg})
            # Print traceback for your own debugging
            print("⚠️ [LINTER CRASH TRACEBACK]")
            traceback.print_exc()
            return None

    return wrapper


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

    def _assign_parents(self, tree):
        """Assign parent references to all AST nodes."""
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

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
            self._assign_parents(tree)
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
            # Capture traceback details
            tb = sys.exc_info()[2]
            extracted = traceback.extract_tb(tb)
            detailed_trace = traceback.format_exc()

            # Try to find the first relevant frame inside *your own* project files
            offending_line = 1
            offending_file = None
            offending_func = None

            for frame in reversed(extracted):  # go from inner to outer
                if "lint_code.py" in frame.filename or "transpiler" in frame.filename:
                    offending_line = frame.lineno
                    offending_file = frame.filename
                    offending_func = frame.name
                    break
            else:
                # fallback: last frame of the traceback
                if extracted:
                    offending_line = extracted[-1].lineno
                    offending_file = extracted[-1].filename
                    offending_func = extracted[-1].name

            return {
                "errors": [
                    {
                        "line": offending_line,
                        "column": 1,
                        "message": (
                            "Unexpected internal error during linting:\n"
                            f"{type(ex).__name__}: {str(ex)}\n"
                            f"File: {offending_file or '<unknown>'}, "
                            f"Function: {offending_func or '<unknown>'}, "
                            f"Line: {offending_line}\n\n"
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

    def visit_Subscript(self, node):
        pass
        """expression = node.value
        expression_type = self.type_analyzer.get_node_type(expression)

        base_type = expression_type.split(",")[0]
        print(f"found base type {base_type} and expression type {expression_type}")

        if base_type not in ("str", "list", "dict"):
            self.add_error(node, f"Invalid use of Subscript on type '{base_type}.")"""

    def visit_IfExp(self, node):
        self.add_error(node, f"One lined if expressions are not allowed.")

    def visit_List(self, node: ast.List):
        """Validate literal lists: all elements same type, and of allowed scalar types."""
        # ALLOWED_TYPES = (ast.Constant,)

        # ✅ Detect empty list
        if len(node.elts) == 0:
            parent = getattr(node, "parent", None)
            # Not assigned, not part of an annotation, not in a call, not in return
            if not isinstance(
                parent, (ast.Assign, ast.AnnAssign, ast.Call, ast.Return, ast.keyword)
            ):
                self.add_error(
                    node,
                    "Empty list literal '[]' used as a standalone expression. "
                    "It must be assigned or annotated explicitly.",
                )
        ALLOWED_VALUE_TYPES = ("str", "int", "float", "bool")

        element_types = []

        for elt in node.elts:
            # val = elt.value
            val_type = self.type_analyzer.get_node_type(elt)
            if val_type not in ALLOWED_VALUE_TYPES:
                self.add_error(
                    node,
                    f"List elements must be literal constants (int, str, float, bool). Found: {val_type}",
                )
                continue
            element_types.append(val_type)

            """if not isinstance(elt, ALLOWED_TYPES):
                self.add_error(
                    node,
                    f"List elements must be literal constants (int, str, float, bool). Found: {type(elt).__name__}",
                )
                continue

            val = elt.value
            if not isinstance(val, ALLOWED_VALUE_TYPES):
                self.add_error(
                    node,
                    f"Invalid list element type: {type(val).__name__}. Allowed: int, str, float, bool.",
                )
                continue

            element_types.append(type(val).__name__)"""

        # Check uniformity
        if element_types:
            first_type = element_types[0]
            for t in element_types[1:]:
                if t != first_type:
                    self.add_error(
                        node,
                        f"List elements must be of the same type. Found both '{first_type}' and '{t}'.",
                    )
                    break

    def visit_Dict(self, node: ast.Dict):
        """Validate literal dicts: key/value type restrictions and uniformity."""
        # ✅ Detect empty dict
        if len(node.keys) == 0:
            parent = getattr(node, "parent", None)
            if not isinstance(
                parent, (ast.Assign, ast.AnnAssign, ast.Call, ast.Return, ast.keyword)
            ):
                self.add_error(
                    node,
                    "Empty dict literal '{}' used as a standalone expression. "
                    "It must be assigned or annotated explicitly.",
                )
        ALLOWED_VALUE_TYPES = ("str", "int", "float", "bool")

        key_types = []
        val_types = []

        for key, val in zip(node.keys, node.values):
            # Key must be a constant string

            key_type = self.type_analyzer.get_node_type(key)
            value_type = self.type_analyzer.get_node_type(val)

            key_types.append(key_type)
            val_types.append(value_type)

            if key_type != "str":
                self.add_error(
                    node,
                    f"Dict keys must be of type str. Found: {key_type}",
                )
            if value_type not in ALLOWED_VALUE_TYPES:
                self.add_error(
                    node,
                    f"Dict values must be literal constants (int, str, float, bool). Found: {value_type}",
                )

        # Check uniformity of keys and values
        if key_types:
            first_key_type = key_types[0]
            for t in key_types[1:]:
                if t != first_key_type:
                    self.add_error(
                        node,
                        f"Dict keys must all be of the same type. Found both '{first_key_type}' and '{t}'.",
                    )
                    break

        if val_types:
            first_val_type = val_types[0]
            for t in val_types[1:]:
                if t != first_val_type:
                    self.add_error(
                        node,
                        f"Dict values must all be of the same type. Found both '{first_val_type}' and '{t}'.",
                    )
                    break

        # Continue walking
        self.generic_visit(node)

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

                # also check if the current platform is compatible
                available_platforms = self.dependency_resolver.get_available_platforms(
                    import_name
                )

                if available_platforms and available_platforms != "all":
                    list_available_platforms = available_platforms.split(",")

                    if self.platform not in list_available_platforms:
                        self.add_error(
                            node,
                            f"The module '{import_name}' is not available on {self.platform} due to hardware restrictions.",
                        )

        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        # Rule 1: from x import y is not allowed
        self.add_error(node, f"'from {node.module} import ...' is not allowed")
        self.generic_visit(node)

    """def _save_function_args(self, node):
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

        return"""

    def check_annotation_validity(self, annotation_type, node):
        """
        Validate a parsed annotation string.

        Rules:
          - Base Python types allowed: int, str, float, bool, list, dict
          - list must be 'list,<element>'
          - dict must be 'dict,<key>,<value>'
          - list element types allowed: int, bool, float, str
          - dict key must be str; value can be int, bool, float, str
        """

        if not annotation_type or not isinstance(annotation_type, str):
            return  # ignore empty or invalid input

        base_parts = annotation_type.split(",")
        base_type = base_parts[0]

        ALLOWED_BASE = {"int", "str", "float", "bool", "list", "dict"}
        ALLOWED_ELEM = {"int", "str", "float", "bool"}

        annotation_label = annotation_type

        if len(base_parts) == 1:
            annotation_label = annotation_type
        elif len(base_parts) == 2:
            annotation_label = f"{base_parts[0]}[{base_parts[1]}]"
        elif len(base_parts) == 3:
            annotation_label = f"{base_parts[0]}[{base_parts[1]}, {base_parts[2]}]"

        # --- Case 1: Base type is a core Python type ---
        if base_type in ALLOWED_BASE:
            # Simple scalar type (no extra commas)
            if base_type in {"int", "str", "float", "bool"}:
                if len(base_parts) > 1:
                    self.add_error(
                        node,
                        f"Annotation '{annotation_label}' is invalid — '{base_type}' should not have subtypes.",
                    )
                return

            # --- list ---
            if base_type == "list":
                if len(base_parts) != 2:
                    self.add_error(
                        node,
                        f"Annotation '{annotation_label}' is invalid — list must specify one subtype (e.g. 'list[int]').",
                    )
                    return

                subtype = base_parts[1]
                if subtype not in ALLOWED_ELEM:
                    self.add_error(
                        node,
                        f"Annotation '{annotation_label}' is invalid — list element type must be one of {ALLOWED_ELEM}.",
                    )
                return

            # --- dict ---
            if base_type == "dict":
                if len(base_parts) != 3:
                    self.add_error(
                        node,
                        f"Annotation '{annotation_label}' is invalid — dict must specify key and value (e.g. 'dict[str, int]').",
                    )
                    return

                key_type, val_type = base_parts[1], base_parts[2]
                if key_type != "str":
                    self.add_error(
                        node,
                        f"Annotation '{annotation_label}' is invalid — dict key type must be 'str'.",
                    )
                if val_type not in ALLOWED_ELEM:
                    self.add_error(
                        node,
                        f"Annotation '{annotation_label}' is invalid — dict value type must be one of {ALLOWED_ELEM}.",
                    )
                return

        # --- Case 2: Custom types (not in allowed base types) ---
        else:
            # Assume user-defined or imported type
            # No validation errors — acceptable as "custom type"
            print(f"hoo hoo haa haa got type {annotation_type}")

            is_class_valid = self.dependency_resolver.is_module_class(annotation_type)

            if not is_class_valid:
                closest_class_name = self.dependency_resolver.get_closest_class_name(
                    annotation_type
                )

                if closest_class_name:
                    self.add_error(
                        node,
                        f"{annotation_type} is neither imported nor defined anywhere. Did you mean {closest_class_name}?",
                    )

                else:
                    self.add_error(
                        node,
                        f"{annotation_type} is neither imported nor defined anywhere. Check this and try again.",
                    )
            return

    def _save_function_args(self, node):
        func_name = node.name
        return_type = None

        # Handle return type safely
        try:
            if node.returns:
                return_type = self.type_analyzer._extract_annotation(node.returns)
        except Exception as ex:
            self.add_error(
                node,
                f"Invalid return type annotation in function '{func_name}': {str(ex)}",
            )
            return_type = None

        saved_args = []

        # node.args.defaults gives default values for keyword-style args
        # alignment is from the *end* of node.args.args
        defaults = node.args.defaults
        kwarg_start_index = len(node.args.args) - len(defaults)

        for idx, arg in enumerate(node.args.args):
            arg_name = arg.arg
            is_kwarg = idx >= kwarg_start_index  # ✅ arg has a default value

            try:
                if arg.annotation is not None:
                    arg_type = self.type_analyzer._extract_annotation(arg.annotation)
                    self.check_annotation_validity(arg_type, node)
                else:
                    self.add_error(
                        arg,
                        f"Invalid type annotation for argument '{arg_name}' in function '{func_name}': Missing annotation",
                    )
                    arg_type = None
            except Exception as ex:
                self.add_error(
                    arg,
                    f"Invalid type annotation for argument '{arg_name}' in function '{func_name}': {str(ex)}",
                )
                arg_type = None

            saved_args.append(
                {
                    "name": arg_name,
                    "arg_type": arg_type,
                    "is_kwarg": is_kwarg,  # ✅ added flag
                }
            )

        # Save method metadata anyway so rest of linting works
        try:
            self.dependency_resolver._insert_method(
                func_name,
                None,
                self.module_name,
                "user",
                json.dumps(saved_args),
                return_type,
            )
        except Exception as ex:
            self.add_error(
                node, f"Internal error saving metadata for '{func_name}': {str(ex)}"
            )

        # finally save the arg types
        for arg in saved_args:
            print(
                f'saving arg {arg["name"]} of type {arg["arg_type"]} for scope {self.scope}'
            )
            self.dependency_resolver.insert_variable(
                arg["name"],
                arg["arg_type"],
                self.module_name,
                "user",
                scope=self.scope,
            )

        return

    def visit_FunctionDef(self, node):
        func_name = node.name

        # check current scope, if its not global, then function is defined
        # within function and not valid.

        if self.scope != "global":
            self.add_error(node, "Function within function not allowed.")
        if self.is_within_If or self.is_within_For or self.is_within_While:
            self.add_error(node, "Function cannot be defined within If/For/While.")

        self.scope = func_name

        if func_name in builtin_funcs or func_name == "range":
            self.add_error(
                node, f"{func_name} is a builtin func and cannot be overriden."
            )

        imported_global_methods = self.dependency_resolver.get_imported_global_methods(
            self.module_name
        )
        if func_name in imported_global_methods.keys():
            imported_from_module = imported_global_methods[func_name]
            self.add_error(
                node,
                f"{func_name} is imported from {imported_from_module}. Consider renaming this method.",
            )

        # Ensure annotation exists
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

        # Save function args before traversal
        self._save_function_args(node)

        # Track if function has an explicit return
        has_return = False

        # Visit body
        for stmt in node.body:
            if isinstance(stmt, ast.Return):
                has_return = True
            self.visit(stmt)

        # Post traversal checks
        annotated_return_type = self.dependency_resolver.get_module_call_return_type(
            self.module_name, func_name
        )

        # 1️⃣ No return at all but annotated type is not None
        if not has_return and annotated_return_type not in ("None", "NoneType", None):
            self.add_error(
                node,
                f"Function '{func_name}' is annotated as returning {annotated_return_type} but has no return statement.",
            )

        # 2️⃣ Has a return, but no annotation
        if has_return and (node.returns is None):
            self.add_error(
                node,
                f"Function '{func_name}' returns a value but has no return type annotation.",
            )

        # Reset scope
        self.scope = "global"

    def visit_Return(self, node):
        current_function = self.scope
        annotated_return_type = self.dependency_resolver.get_module_call_return_type(
            self.module_name, current_function
        )

        if node.value is None:
            actual_return_type = "None"
        else:
            actual_return_type = self.type_analyzer.get_node_type(node.value)

        if actual_return_type != annotated_return_type:
            self.add_error(
                node,
                f"Method returns {actual_return_type}, but it is annotated as {annotated_return_type}.",
            )

    def visit_If(self, node):
        self.is_within_If = True

        if self.scope == "global":
            self.add_error(node, "'if' can be only called within a function body.")

        if self.scope == "global":
            # in arduino, if only works within function/class body
            error_text = "'If' can only be called within function body."
            self.add_error(node, error_text)

        # visit the condition
        self.visit(node.test)

        # visit the body
        for stmt in node.body:
            self.visit(stmt)

        # also visit else/elif blocks if present
        for stmt in node.orelse:
            self.visit(stmt)

        self.is_within_If = False

    def visit_For(self, node):
        self.is_within_For = True

        if self.scope == "global":
            self.add_error(node, "'for' can be only called within a function body.")

        # cannot be called on global scope in arduino
        if self.scope == "global":
            self.add_error(node, "'for' can be only called within a function body.")

        loop_var_type = self.type_analyzer.get_node_type(node.iter)
        loop_type = loop_var_type.split(",")[0]
        loop_var = node.target
        iterable = node.iter

        if loop_type == "range":
            self.loop_variables[loop_var] = "int"
        elif loop_type == "list":
            element_type = loop_var_type.split(",")[1]
            print(f"saving loop var {loop_var.id} for {iterable}")
            self.loop_variables[loop_var.id] = element_type
        elif loop_type == "dict_items":
            # Extract key and value variables from the loop target
            if isinstance(loop_var, ast.Tuple) and len(loop_var.elts) == 2:
                key_var = loop_var.elts[0]
                val_var = loop_var.elts[1]
                _, key_type, value_type = loop_var_type.split(",")
                self.loop_variables[key_var.id] = key_type
                self.loop_variables[val_var.id] = value_type
            else:
                # Handle error case where loop target is not a tuple of two variables
                self.add_error(
                    node,
                    "dict_items iteration requires unpacking into key, value variables",
                )
        elif loop_type == "str":
            self.loop_variables[loop_var] = "str"

        if self.scope == "global":
            # in arduino, if only works within function/class body
            error_text = "'For' can only be called within function body."
            self.add_error(node, error_text)

        # visit the iterator expression and target
        self.visit(node.iter)
        # self.visit(node.target)

        for stmt in node.body:
            self.visit(stmt)

        # loop has ended so reset loop_variables
        self.loop_variables = {}

        self.is_within_For = False

    def visit_AnnAssign(self, node):
        """
        Handles annotated assignments like:
            x: list[int] = []
            y: dict[str, int] = {}
            z: int = 5

        Ensures annotated type matches the assigned type,
        except when the RHS is an empty list/dict with 'auto' subtype markers.
        """

        rhs_type = extract_annotation_type(node.annotation)
        is_lhs_name = isinstance(node.target, ast.Name)

        if not is_lhs_name:
            return  # Skip unpacking or complex targets

        lhs_name = self.type_analyzer.get_lhs_name(node.target)
        self.dependency_resolver.insert_variable(
            lhs_name, rhs_type, self.module_name, "user"
        )

        # Skip if there's no right-hand side (e.g., `x: int`)
        if node.value is None:
            return

        actual_rhs_type = self.type_analyzer.get_node_type(node.value)

        # Handle literal empty list/dict cases gracefully
        if isinstance(node.value, ast.List) and len(node.value.elts) == 0:
            actual_rhs_type = "list,auto"
        elif isinstance(node.value, ast.Dict) and len(node.value.keys) == 0:
            # If dict has annotation like dict[str, int], the auto subtype can remain
            # but should not trigger mismatch
            actual_rhs_type = "dict,auto"

        # Normalize for comparison
        def normalize(t: str):
            return [x.strip() for x in t.split(",") if x.strip()]

        expected_parts = normalize(rhs_type)
        actual_parts = normalize(actual_rhs_type)

        # Handle special rule: skip 'auto' for empty list/dict
        if "auto" in actual_parts:
            actual_parts = [x for x in actual_parts if x != "auto"]

        # For dicts, if annotation is dict[str, int] and actual is dict only, allow it
        if expected_parts and actual_parts:
            if expected_parts[0] in ("list", "dict") and actual_parts[0] in (
                "list",
                "dict",
            ):
                # If both are list/dict but lengths differ only because of auto placeholders, skip error
                if expected_parts[0] == actual_parts[0]:
                    pass  # same base type — fine
                else:
                    self.add_error(
                        node,
                        f"Type mismatch in annotated assignment for '{lhs_name}': "
                        f"expected '{rhs_type}', but got '{actual_rhs_type}'.",
                    )
                    return
            else:
                # Strict comparison for non-collection types
                if expected_parts != actual_parts:
                    self.add_error(
                        node,
                        f"Type mismatch in annotated assignment for '{lhs_name}': "
                        f"expected '{rhs_type}', but got '{actual_rhs_type}'.",
                    )
                    return

        self.visit(node.value)

    """def visit_Assign(self, node):
        lhs_name = self.type_analyzer.get_lhs_name(node.targets[0])

        is_lhs_function_name = self.dependency_resolver.get_method_metadata(lhs_name)
        if is_lhs_function_name:
            self.add_error(
                node,
                f"'{lhs_name}' is a an defined or imported method name. Please rename this variable.",
            )
        rhs_type = self.type_analyzer.get_node_type(node.value)

        self.dependency_resolver.insert_variable(
            lhs_name, rhs_type, self.module_name, "user"
        )

        self.visit(node.value)"""

    def visit_Assign(self, node):
        # Handle left-hand side safely — may be Name, Subscript, Attribute, etc.
        target = node.targets[0]
        is_lhs_name = isinstance(target, ast.Name)
        is_lhs_subscript = isinstance(target, ast.Subscript)
        rhs_type = self.type_analyzer.get_node_type(node.value)

        if rhs_type == "None":
            self.add_error(
                node,
                f"Invalid assignment: expressions of type 'void' cannot be assigned or used in any value context.",
            )

        if is_lhs_name:
            lhs_name = target.id

            is_lhs_function_name = self.dependency_resolver.get_method_metadata(
                lhs_name
            )

            variable_exists = self.dependency_resolver.variable_exists(lhs_name)
            if is_lhs_function_name:
                self.add_error(
                    node,
                    f"'{lhs_name}' is a defined or imported method name. Please rename this variable.",
                )

            # 🧩 New clause: Detect empty list or dict assignments
            if isinstance(node.value, ast.List) and len(node.value.elts) == 0:
                self.add_error(
                    node,
                    f"Empty list detected in assignment to '{lhs_name}'. "
                    "Empty lists must be initialized with an annotation, e.g.:\n"
                    f"# Example:\n{lhs_name}: list[int] = []",
                )

            elif isinstance(node.value, ast.Dict) and len(node.value.keys) == 0:
                self.add_error(
                    node,
                    f"Empty dict detected in assignment to '{lhs_name}'. "
                    "Empty dicts must be initialized with an annotation, e.g.:\n"
                    f"# Example:\n{lhs_name}: dict[str, int] = {{}}",
                )

            if not variable_exists:
                self.dependency_resolver.insert_variable(
                    lhs_name, rhs_type, self.module_name, "user"
                )

            if variable_exists:
                previous_init_type = self.dependency_resolver.get_variable_type(
                    lhs_name, self.scope
                )

                if previous_init_type != rhs_type:
                    self.add_error(
                        node,
                        f"Variable '{lhs_name}' was previously defined as type {previous_init_type}, but now you have assigned '{rhs_type}'. You can reassign previously initialized variable with same type, but you cannot reinitialize it as another type. Consider changing the variable name.",
                    )

        elif is_lhs_subscript:
            base = node.targets[0].value
            index = node.targets[0].slice

            base_type = self.type_analyzer.get_node_type(base)
            index_type = self.type_analyzer.get_node_type(index)

            base_type_split = base_type.split(",")

            if base_type_split[0] not in ("str", "dict", "int"):
                self.add_error(
                    node, f"You are calling subscript on non allowed type {base_type}"
                )

            else:
                if base_type_split[0] in ("str", "list") and index_type != "int":
                    self.add_error(
                        node,
                        f"Index for type {base_type} subscript can only be of type 'int'. You passed '{index_type}'",
                    )

                elif base_type_split[0] == "dict" and index_type != "str":
                    self.add_error(
                        node,
                        f"Index for 'dict' subscript can only be of type 'str'. You passed '{index_type}'",
                    )

                else:
                    if base_type_split[0] == "str" and rhs_type != "str":
                        self.add_error(
                            node,
                            f"Incompatibe assignment, expected 'str', you passed {rhs_type}",
                        )

                    elif base_type_split[0] == "list" and len(base_type_split) == 2:
                        if rhs_type != base_type_split[1]:
                            self.add_error(
                                node,
                                f"Incompatibe assignment, expected '{base_type_split[1]}', you passed {rhs_type}",
                            )

                    elif base_type_split[0] == "dict" and len(base_type_split) == 3:
                        if rhs_type != base_type_split[2]:
                            self.add_error(
                                node,
                                f"Incompatibe assignment, expected '{base_type_split[2]}', you passed {rhs_type}",
                            )

        self.visit(node.value)

    def _check_passed_method_args(
        self, call_args: list[dict], saved_args: list[dict], method_name: str, node
    ) -> None:
        """
        Validate whether passed arguments in a function call match the
        expected (saved) method signature.

        Each argument in `call_args` and `saved_args` is a dict:
            {
                "name": str | None,
                "arg_type": str | None,
                "is_kwarg": bool
            }

        Checks:
            1. Positional argument count and type match.
            2. Keyword argument type match (order ignored).
            3. Unexpected or missing kwargs.
        """
        errors = []

        # --- Separate positional and keyword arguments ---
        saved_pos = [a for a in saved_args if not a["is_kwarg"]]
        saved_kw = [a for a in saved_args if a["is_kwarg"]]
        call_pos = [a for a in call_args if not a["is_kwarg"]]
        call_kw = [a for a in call_args if a["is_kwarg"]]

        # -------------------------------------------------
        # ✅ Check 1: Positional argument count
        # -------------------------------------------------
        if len(call_pos) != len(saved_pos):
            errors.append(
                f"{method_name}() expects {len(saved_pos)} positional argument(s) "
                f"({', '.join(a['name'] or '<unnamed>' for a in saved_pos)}), "
                f"but {len(call_pos)} were passed."
            )
        else:
            # -------------------------------------------------
            # ✅ Check 2: Positional argument type matching
            # -------------------------------------------------
            for i, saved in enumerate(saved_pos):
                call = call_pos[i]
                expected_type = saved.get("arg_type")
                passed_type = call.get("arg_type")

                if expected_type != passed_type:
                    errors.append(
                        f"{method_name}(): positional argument #{i+1} "
                        f"({saved['name'] or '<unnamed>'}) expects type "
                        f"'{expected_type}', but got '{passed_type}'."
                    )

        # -------------------------------------------------
        # ✅ Check 3: Keyword argument handling
        # -------------------------------------------------
        saved_kw_map = {a["name"]: a for a in saved_kw if a["name"]}
        call_kw_map = {a["name"]: a for a in call_kw if a["name"]}

        # Check each passed kwarg
        for name, call_arg in call_kw_map.items():
            if name not in saved_kw_map:
                errors.append(
                    f"{method_name}() got an unexpected keyword argument '{name}'."
                )
                continue

            expected_type = saved_kw_map[name].get("arg_type")
            passed_type = call_arg.get("arg_type")

            if expected_type != passed_type:
                errors.append(
                    f"{method_name}(): keyword argument '{name}' expects type "
                    f"'{expected_type}', but got '{passed_type}'."
                )

        # No error if saved_kw exists but not passed — optional kwargs are fine.

        # -------------------------------------------------
        # 🚨 Record errors
        # -------------------------------------------------
        for error in errors:
            self.add_error(node, error)

    def visit_Call(self, node):
        # can only be called within function
        """if self.scope == "global":
        self.add_error(node, "Methods can be only called within a function body.")"""
        func = node.func
        call_args = []

        # --- Positional args ---
        for arg in node.args:
            arg_type = self.type_analyzer.get_node_type(arg)

            # Try to resolve loop variables if type missing
            if not arg_type and isinstance(arg, ast.Name):
                arg_type = self.loop_variables.get(arg.id, None)

            call_args.append({"name": None, "arg_type": arg_type, "is_kwarg": False})

            self.visit(arg)

        # --- Keyword args ---
        for kw in node.keywords:
            kw_name = kw.arg  # name in x=1
            kw_value = kw.value
            arg_type = self.type_analyzer.get_node_type(kw_value)

            if not arg_type and isinstance(kw_value, ast.Name):
                arg_type = self.loop_variables.get(kw_value.id, None)

            call_args.append({"name": kw_name, "arg_type": arg_type, "is_kwarg": True})

            self.visit(kw_value)

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

                    print(
                        f"method {method_name} is class {is_method_class} and is in module {module_name}"
                    )

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

                        if self.scope == "global":
                            self.add_error(
                                node,
                                "Methods can be only called within a function body.",
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
                    print(f"{base_name} is a variable.")
                    if self.scope == "global":
                        self.add_error(
                            node,
                            "Methods can be only called within a function body.",
                        )
                    variable_type = self.dependency_resolver.get_variable_type(
                        base_name, self.scope
                    )

                    print(
                        f"found {base_name} as type {variable_type} for scope {self.scope}."
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

                        print(
                            f"{base_name} has module of {variable_module_name} and variable_type {variable_type}"
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
            if self.scope == "global":
                self.add_error(
                    node,
                    "Methods can be only called within a function body.",
                )
            method_name = node.func.id

            if is_builtin_function(method_name):
                builtin_func_metadata = get_core_func_metadata(method_name)

                print(
                    f"[CORETYPE]: checking for {method_name}, {builtin_func_metadata}"
                )

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

    def visit_JoinedStr(self, node):
        print(f"⚡ NodeTransformer/Visitor visit_JoinedStr called!")
        for value in node.values:
            self.visit(value)
        return node

    def visit_FormattedValue(self, node):
        print(f"🔍 NodeTransformer/Visitor visit_FormattedValue called!")
        self.visit(node.value)
        return node

    def visit_Name(self, node):
        """
        Check if a bare function name is used illegally (not called, not passed as arg, not assigned).
        Only check right-hand side since LHS is likely being defined.
        """
        if isinstance(node.ctx, ast.Load):  # Right-hand side (being read)
            var_name = node.id

            is_variable_defined = self.dependency_resolver.variable_exists(var_name)
            is_function_defined = self.dependency_resolver.get_method_metadata(var_name)

            if not is_variable_defined and not is_function_defined:
                if self.is_within_For:
                    if var_name in self.loop_variables:
                        return

                self.add_error(
                    node, f"'{var_name}' is not defined anywhere. This could be a typo."
                )

            else:
                return

            # Skip Python builtins
            if var_name in dir(__builtins__):
                return

            # Check if this is a bare function name (not in a call, not in args, etc.)
            parent = getattr(node, "parent", None)

            # Allowed contexts: being called, passed as arg, or inside attribute
            if isinstance(parent, ast.Call):
                return  # Being called: f() or passed as arg: g(f)
            if isinstance(parent, ast.Attribute):
                attr_name = parent.attr  # This is 'var'
                obj_name = parent.value.id
                func_meta = self.dependency_resolver.get_method_metadata(attr_name)
                if func_meta:
                    self.add_error(
                        node,
                        f"Bare function name '{attr_name}' not allowed. "
                        f"Did you mean to call it with parentheses?",
                    )
                return

            if isinstance(parent, (ast.Tuple, ast.List, ast.Dict)):
                return  # Inside container

            # If we get here, it's a bare name. Check if it's a function.
            func_meta = self.dependency_resolver.get_method_metadata(var_name)
            if func_meta:
                self.add_error(
                    node,
                    f"Bare function name '{var_name}' not allowed. "
                    f"Did you mean to call it with parentheses?",
                )

        self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            if has_invalid_chars(node.value):
                self.add_error(node, "Special characters are not allowed.")


# ---- Auto-wrap all visit_* methods ----
for name, func in list(LintCode.__dict__.items()):
    if name.startswith("visit_") and callable(func):
        setattr(LintCode, name, safe_visit(func))


def main(code, sql_conn, platform, path_to_core_libs, module_name="main"):
    try:
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
        }

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
