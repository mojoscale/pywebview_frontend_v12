import ast
import uuid
import sqlite3
import inspect
import json
from typing import get_args, get_origin
from pathlib import Path

import builtins
import types
import os


# move this to arg later
from core.utils import get_app_dir

ENV_PATH = Path(get_app_dir()) / ".env"
from dotenv import load_dotenv

load_dotenv(ENV_PATH)


LIST_ALLOWED_TYPES = [str, int, bool, float]
BUILTIN_TYPES = ["int", "str", "float", "bool", "list", "dict", "range"]

BUILTIN_FUNC_PREFIX = "py"

TOPLINE_INCLUDES = [
    "PyList",
    "PyString",
    "PyDict",
    "PyDictFromJsonSpecializations",
    "PyRange",
    "PyInt",
    "PyFloat",
    "PyMethods",
    "PyBool",
    "PyDictItems",
]


def is_builtin_function(name: str) -> bool:
    builtin_funcs = [
        name for name in dir(builtins) if callable(getattr(builtins, name))
    ]
    return name in builtin_funcs or name == "range"


def is_core_python_type(type_string):
    if not type_string:
        return False

    core_type = type_string.split(",")[0]

    if core_type in [
        "list",
        "str",
        "dict",
        "int",
        "float",
        "bool",
        "dict_items",
        "range",
    ]:
        return True

    return False


def get_builtin_function_return_type(method_name: str, args: list):
    if method_name == "abs":
        arg_type1 = args[0]
        print(f"abs called on arg type {arg_type1}")

        return arg_type1

    elif method_name in (
        "ascii",
        "bin",
        "chr",
        "format",
        "hex",
        "input",
        "oct",
        "repr",
        "str",
    ):
        return "str"

    elif method_name in ("int", "hash", "len", "id", "ord", "round"):
        return "int"

    elif method_name in ("all", "any", "bool", "callable", "hasattr"):
        return "bool"

    elif method_name == "range":
        return "range"

    elif method_name == "float":
        return "float"

    elif method_name == "divmod":
        return "list,int"

    elif method_name == "list":
        arg_type1 = args[0]
        if arg_type1 == "str":
            return "list,str"

    elif method_name in ("pow", "sorted"):
        arg_type1 = args[0]
        return arg_type1  # int if int is base or float if float is base

    elif method_name == "sum":
        arg_type1 = args[0]
        core_type = arg_type1.split(",")[0]
        if core_type == "list":
            return arg_type1.split(",")[1]  # return element type


def format_type_string(type_or_string):
    # Case 1: Input is a string like "str", "list[int]"
    if isinstance(type_or_string, str):
        try:
            # Convert string to actual type using eval in a safe context
            type_obj = eval(
                type_or_string,
                {"__builtins__": None},
                {
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                },
            )
        except Exception:
            return type_or_string  # fallback if string can't be parsed
    else:
        type_obj = type_or_string

    origin = get_origin(type_obj)
    args = get_args(type_obj)

    if origin is list and len(args) == 1:
        return f"list,{format_type_string(args[0])}"
    elif origin is dict and len(args) == 2:
        return f"dict,{format_type_string(args[0])},{format_type_string(args[1])}"
    elif origin is None:
        return type_obj.__name__ if hasattr(type_obj, "__name__") else str(type_obj)
    else:
        return str(type_obj)


def get_cpp_python_type(python_type, custom_type_str=False):
    if not python_type:
        return "auto"
    python_type_list = python_type.split(",")
    python_type = python_type_list[0]

    type_map = {
        "int": "int",
        "float": "float",
        "str": "PyString" if custom_type_str else "String",
        "bool": "PyBool",
        "range": "PyRange",
        "list": "PyList",
        "dict": "PyDict",
    }

    if len(python_type_list) == 1:
        try:
            return type_map[python_type]
        except:
            return python_type

    elif len(python_type_list) > 1:
        if python_type == "list":
            python_type_element = python_type_list[1]
        elif python_type == "dict":
            python_type_element = python_type_list[2]

        return f"{type_map[python_type]}<{type_map[python_type_element]}>"

    return "auto"


def get_python_builtin_class_method_type(class_name, method_name):
    print(f"trying to find method {method_name} for type {class_name}")
    class_name_split = class_name.split(",")
    core_class = class_name_split[0]

    if method_name == "contains":
        return "bool"

    if core_class == "list":
        element_type = class_name_split[1] if len(class_name_split) > 1 else "any"

        if method_name == "pop":
            return element_type
        elif method_name == "append":
            return "auto"
        elif method_name == "index":
            return "int"
        elif method_name in ("sort", "reverse", "clear", "remove", "extend", "insert"):
            return "auto"
        elif method_name == "copy":
            return class_name
        elif method_name == "count":
            return "int"

    elif core_class == "dict":
        key_type = class_name_split[1] if len(class_name_split) > 1 else "any"
        value_type = class_name_split[2] if len(class_name_split) > 2 else "any"

        if method_name == "keys":
            return f"list,{key_type}"
        elif method_name == "values":
            return f"list,{value_type}"
        elif method_name == "items":
            return f"dict_items,{key_type},{value_type}"
        elif method_name == "get":
            return value_type
        elif method_name == "pop":
            return value_type
        elif method_name == "popitem":
            return f"list,{key_type},{value_type}"
        elif method_name == "copy":
            return class_name
        elif method_name in ("clear", "update"):
            return "auto"

    elif core_class == "str":
        if method_name in ("capitalize", "lower", "replace", "strip", "title", "upper"):
            return "str"
        elif method_name in ("count", "find", "index", "rfind", "rindex"):
            return "int"
        elif method_name in (
            "encode",
            "join",
            "ljust",
            "rjust",
            "lstrip",
            "rstrip",
            "removeprefix",
            "removesuffix",
            "swapcase",
            "zfill",
            "format",
        ):
            return "str"
        elif method_name in (
            "endswith",
            "isalnum",
            "isalpha",
            "isdecimal",
            "isdigit",
            "islower",
            "isnumeric",
            "isspace",
            "istitle",
            "isupper",
            "startswith",
        ):
            return "bool"
        elif method_name in ("split", "rsplit", "splitlines"):
            return "list,str"

    elif core_class == "int":
        if method_name == "bit_length":
            return "int"
        elif method_name == "to_bytes":
            return "bytes"

    elif core_class == "float":
        if method_name == "is_integer":
            return "bool"

    elif core_class == "range":
        if method_name == "index":
            return "int"
        elif method_name == "count":
            return "int"

    elif core_class == "bool":
        if method_name in ("imag", "to_string", "to_bytes"):
            return "str"
        elif method_name == "get":
            return "bool"
        elif method_name == "toggle":
            return "auto"
        elif method_name in ("bit_length", "bit_count", "numerator", "denominator"):
            return "int"

    return "auto"


def extract_annotation_type(node):
    print(f"got node {node}")
    if isinstance(node, ast.Name):
        return node.id

    elif isinstance(node, ast.Constant):
        if node.value is None:
            return "None"

    elif isinstance(node, ast.Attribute):
        # Handle x.SomeClass → return "SomeClass"
        return node.attr

    elif isinstance(node, ast.Subscript):
        base = node.value
        sub = node.slice.value if hasattr(node.slice, "value") else node.slice

        # list[T]
        if (
            isinstance(base, (ast.Name, ast.Attribute))
            and getattr(base, "id", None) == "list"
            or getattr(base, "attr", None) == "list"
        ):
            return f"list,{extract_annotation_type(sub)}"

        # dict[K, V]
        if (
            isinstance(base, (ast.Name, ast.Attribute))
            and getattr(base, "id", None) == "dict"
            or getattr(base, "attr", None) == "dict"
        ):
            if isinstance(sub, ast.Tuple) and len(sub.elts) == 2:
                k = extract_annotation_type(sub.elts[0])
                v = extract_annotation_type(sub.elts[1])
                return f"dict,{k},{v}"

        # Callable[[arg1, arg2, ...], return_type]
        if (
            isinstance(base, (ast.Name, ast.Attribute))
            and getattr(base, "id", None) == "Callable"
            or getattr(base, "attr", None) == "Callable"
        ):
            if isinstance(sub, ast.Tuple) and len(sub.elts) == 2:
                args_node = sub.elts[0]
                return_node = sub.elts[1]

                if isinstance(args_node, ast.List):
                    args = [extract_annotation_type(arg) for arg in args_node.elts]
                else:
                    args = ["?"]

                return_type = extract_annotation_type(return_node)
                return f"callable,{','.join(args)}->{return_type}"

    raise ValueError("Unsupported annotation")


def _extract_chain(node: ast.Call):
    """
    Given an ast.Call node like x.foo().bar().baz(),
    returns a list of dicts from base to last call.

    Each dict has:
        - 'value': name of identifier / attribute / call
        - 'type': 'attr', 'call', or 'const'
        - 'args': only for calls
    """
    result = []
    current = node  # start from outermost Call

    while True:
        # Handle Call (like foo() or bar() or baz())
        if isinstance(current, ast.Call):
            func = current.func
            # Add this call node (name or attribute)
            if isinstance(func, ast.Name):
                result.append(
                    {
                        "value": func.id,
                        "type": "call",
                        "args": [a for a in current.args],
                    }
                )
                break

            elif isinstance(func, ast.Attribute):
                result.append(
                    {
                        "value": func.attr,
                        "type": "call",
                        "args": [a for a in current.args],
                    }
                )
                # keep walking down
                current = func.value
                continue

            else:
                # Fallback for rare cases (e.g. lambda() or subscript())
                result.append(
                    {
                        "value": ast.dump(func),
                        "type": type(func).__name__.lower(),
                        "args": [a for a in current.args],
                    }
                )
                break

        # Handle Attribute (like x.foo)
        elif isinstance(current, ast.Attribute):
            result.append({"value": current.attr, "type": "attr", "args": []})
            current = current.value
            continue

        # Handle Name (like x)
        elif isinstance(current, ast.Name):
            result.append(
                {
                    "value": current.id,
                    "type": "attr",  # base variable/object
                    "args": [],
                }
            )
            break

        # Handle constants like 123 or "hello"
        elif isinstance(current, ast.Constant):
            result.append({"value": repr(current.value), "type": "const", "args": []})
            break

        else:
            # unhandled type (e.g., Subscript, etc.)
            result.append(
                {
                    "value": ast.dump(current),
                    "type": type(current).__name__.lower(),
                    "args": [],
                }
            )
            break

    # reverse to get [x, foo, bar, baz]
    return list(reversed(result))


class DependencyResolver:
    def __init__(self, commit_hash, sql_conn, platform, imported_modules=[]):
        self.current_id = "commit_" + commit_hash  # str(uuid.uuid4()).replace("-", "_")
        self.imported_modules = imported_modules
        self.conn = sql_conn
        self.platform = platform
        self.cursor = sql_conn.cursor()
        self.delete_all_tables()  # delete values from previous transpilation because they can cause issues.
        self._create_tables()
        self._save_modules()

    def _create_tables(self):
        query1 = f"""
        CREATE TABLE IF NOT EXISTS {self.current_id}_methods(
            module_name TEXT,
            class_name TEXT,
            method_name TEXT,
            args TEXT,
            module_type TEXT,
            return_type TEXT,
            use_as_is BOOL,
            translation TEXT,
            is_reference BOOL,
            construct_with_equal_to BOOL, 
            class_actual_type TEXT,
            pass_as TEXT, 
            is_eval BOOL
        )
        """

        query2 = f"""
        CREATE TABLE IF NOT EXISTS {self.current_id}_variables(
            variable_name TEXT,
            variable_type TEXT,
            module_name TEXT,
            module_type TEXT,
            scope TEXT
        )
        """

        query3 = f"""
        CREATE TABLE IF NOT EXISTS {self.current_id}_modules(
            module_name TEXT,
            module_type TEXT, 
            translated_name TEXT,
            dependencies TEXT, 
            include_internal_modules TEXT

        )
        """

        query4 = f"""
        CREATE TABLE IF NOT EXISTS {self.current_id}_imported_modules(

            main_module TEXT, 
            imported_module TEXT, 
            import_alias TEXT


        )
        """

        self.cursor.execute(query1)
        self.cursor.execute(query2)
        self.cursor.execute(query3)
        self.cursor.execute(query4)

        self.conn.commit()
        print("created tables")

    def delete_all_tables(self):
        tables_to_delete = [
            f"{self.current_id}_methods",
            f"{self.current_id}_variables",
            f"{self.current_id}_modules",
            f"{self.current_id}_imported_modules",
        ]

        for table in tables_to_delete:
            try:
                print(f"[DEBUG] Dropping table: {table}")
                self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
            except Exception as e:
                print(f"[ERROR] Failed to drop table {table}: {e}")

        self.conn.commit()
        print(f"[DEBUG] All tables for {self.current_id} deleted.")

    def get_imported_global_methods(self, current_module_name):
        methods_table = f"{self.current_id}_methods"

        query = f"""
        SELECT method_name, module_name
        FROM {methods_table}
        WHERE class_name IS NULL
          AND module_name <> ?
        """

        self.cursor.execute(query, (current_module_name,))
        rows = self.cursor.fetchall()

        # Convert to dictionary: {method_name: module_name}
        imported_methods = {
            method_name: module_name for method_name, module_name in rows
        }
        return imported_methods

    def get_method_metadata(self, method_name, module_name=None, class_name=None):
        methods_table = f"{self.current_id}_methods"

        # Deep dive prints - show all inputs clearly
        print(f"🔍 [get_method_metadata] START")
        print(
            f"   📋 Inputs: method_name='{method_name}', module_name='{module_name}', class_name='{class_name}'"
        )
        print(f"   🗃️  Table: {methods_table}")

        if module_name:
            if class_name:
                query = f"""
                SELECT method_name, return_type, args
                FROM {methods_table}
                WHERE method_name = ? AND module_name = ? AND class_name = ?
                """
                self.cursor.execute(query, (method_name, module_name, class_name))
                print(f"   🎯 Query Type: MODULE + CLASS")
                print(f"   📝 Query: {query}")
                print(
                    f"   🔢 Params: ('{method_name}', '{module_name}', '{class_name}')"
                )
            else:
                query = f"""
                SELECT method_name, return_type, args
                FROM {methods_table}
                WHERE method_name = ? AND module_name = ?
                """
                self.cursor.execute(query, (method_name, module_name))
                print(f"   🎯 Query Type: MODULE ONLY")
                print(f"   📝 Query: {query}")
                print(f"   🔢 Params: ('{method_name}', '{module_name}')")
        else:
            if class_name:
                query = f"""
                SELECT method_name, return_type, args
                FROM {methods_table}
                WHERE method_name = ? AND class_name = ?
                """
                self.cursor.execute(query, (method_name, class_name))
                print(f"   🎯 Query Type: CLASS ONLY")
                print(f"   📝 Query: {query}")
                print(f"   🔢 Params: ('{method_name}', '{class_name}')")
            else:
                query = f"""
                SELECT method_name, return_type, args
                FROM {methods_table}
                WHERE method_name = ?
                """
                self.cursor.execute(query, (method_name,))
                print(f"   🎯 Query Type: METHOD ONLY")
                print(f"   📝 Query: {query}")
                print(f"   🔢 Params: ('{method_name}',)")

        row = self.cursor.fetchone()
        print(f"   📊 Query Result: {row}")

        if row:
            method_name, return_type, args_json = row
            print(f"   ✅ Row Found:")
            print(f"      📛 Method: {method_name}")
            print(f"      🔄 Return Type: {return_type}")
            print(f"      📦 Args JSON: {args_json}")

            try:
                args = json.loads(args_json) if args_json else []
                print(f"      🎯 Parsed Args: {args}")
            except json.JSONDecodeError as e:
                print(f"      ❌ JSON Decode Error: {e}")
                args = []
                print(f"      🎯 Using empty args due to error")

            result = {
                "method_name": method_name,
                "return_type": return_type,
                "args": args,
            }
            print(f"   📤 Returning: {result}")
            print(f"🔍 [get_method_metadata] END - SUCCESS")
            return result

        print(f"   ❌ No row found for method '{method_name}'")
        print(f"🔍 [get_method_metadata] END - NOT FOUND")
        return None

    def get_print_method_for_class(self, class_name):
        methods_table = f"{self.current_id}_methods"

        query = f"""
        SELECT translation 
        FROM {methods_table} 
        WHERE class_name=? AND
              method_name=?
        """

        self.cursor.execute(
            query,
            (
                class_name,
                "__print__",
            ),
        )

        result = self.cursor.fetchone()

        if result:
            return result[0]

        return

    def get_method_is_eval(self, method_name, module_name):
        methods_table = f"{self.current_id}_methods"

        query = f"""
        SELECT is_eval
        FROM {methods_table} 
        WHERE method_name=? AND
              module_name=?
        """

        self.cursor.execute(
            query,
            (
                method_name,
                module_name,
            ),
        )

        result = self.cursor.fetchone()

        if result:
            return result[0]

        return False

    def get_method_args(self, module_name, method_name):
        methods_table = f"{self.current_id}_methods"

        query = f"""
        SELECT args
        FROM {methods_table} 
        WHERE module_name=? AND
              method_name=?
        """

        self.cursor.execute(
            query,
            (
                module_name,
                method_name,
            ),
        )

        result = self.cursor.fetchone()

        if result:
            res_str = result[0]
            return json.loads(res_str)

        return

    def is_setup_and_loop_present(self):
        table_name = f"{self.current_id}_methods"

        query = f"""
        SELECT DISTINCT method_name
        FROM {table_name}
        WHERE method_name IN ('setup', 'loop')
          AND module_name = 'main'
          AND class_name IS NULL
        """

        self.cursor.execute(query)
        result = self.cursor.fetchall()

        # More robust check
        method_names = {row[0] for row in result}
        return method_names == {"setup", "loop"}

    def get_class_pass_as(self, class_name):
        methods_table = f"{self.current_id}_methods"

        query = f"""
        SELECT pass_as
        FROM {methods_table} 
        WHERE class_name=?
        """

        self.cursor.execute(query, (class_name,))

        result = self.cursor.fetchone()

        if result:
            return result[0]

        return "reference"

    def get_closest_class_name(self, input_name, cutoff=0.5):
        """
        Return the class_name that most closely matches input_name
        from the current commit's _methods table.

        Args:
            input_name (str): Possibly misspelled class name.
            cutoff (float): Similarity threshold (0–1). Defaults to 0.5.

        Returns:
            str | None: Closest class name or None if no close match found.
        """
        import difflib

        table_name = f"{self.current_id}_methods"

        try:
            self.cursor.execute(
                f"SELECT DISTINCT class_name FROM {table_name} WHERE class_name IS NOT NULL"
            )
            class_names = [row[0] for row in self.cursor.fetchall() if row[0]]

            if not class_names:
                print("[DEBUG] No class names found in table.")
                return None

            matches = difflib.get_close_matches(
                input_name, class_names, n=1, cutoff=cutoff
            )
            if matches:
                print(
                    f"[DEBUG] Closest class name for '{input_name}' is '{matches[0]}'"
                )
                return matches[0]
            else:
                print(f"[DEBUG] No close match found for '{input_name}'")
                return None

        except Exception as e:
            print(f"[ERROR] Failed to find closest class name: {e}")
            return None

    def class_constructor_use_equal_to(self, class_name) -> bool:
        methods_table = f"{self.current_id}_methods"

        query = f"""
        SELECT construct_with_equal_to
        FROM {methods_table} 
        WHERE class_name=? AND
              method_name=?
        """

        self.cursor.execute(
            query,
            (
                class_name,
                "__init__",
            ),
        )

        result = self.cursor.fetchone()

        if result:
            return result[0]

        return

    def get_actual_class_type(self, class_name):
        methods_table = f"{self.current_id}_methods"

        query = f"""
        SELECT class_actual_type
        FROM {methods_table} 
        WHERE class_name=? AND
              method_name=?
        """

        self.cursor.execute(
            query,
            (
                class_name,
                "__init__",
            ),
        )

        result = self.cursor.fetchone()

        if result:
            return result[0]

        return

    def get_class_init_translation(self, class_name):
        methods_table = f"{self.current_id}_methods"

        query = f"""
        SELECT translation 
        FROM {methods_table} 
        WHERE class_name=? AND
              method_name=?
        """

        self.cursor.execute(
            query,
            (
                class_name,
                "__init__",
            ),
        )

        result = self.cursor.fetchone()

        if result:
            return result[0]

        return

    def is_class_init_reference(self, class_name):
        methods_table = f"{self.current_id}_methods"

        query = f"""
        SELECT is_reference 
        FROM {methods_table} 
        WHERE class_name=? AND
              method_name=?
        """

        self.cursor.execute(
            query,
            (
                class_name,
                "__init__",
            ),
        )

        result = self.cursor.fetchone()

        if result:
            return result[0]

        return

    def is_module_class(self, class_name, module_name=None) -> bool:
        methods_table = f"{self.current_id}_methods"

        if module_name:
            query = f"""

            SELECT class_name from 

            {methods_table}

            where class_name=?
            and module_name=?
            LIMIT 1
            """

            self.cursor.execute(
                query,
                (
                    class_name,
                    module_name,
                ),
            )

        else:
            query = f"""

            SELECT class_name from 

            {methods_table}

            where class_name=?
        
            LIMIT 1
            """

            self.cursor.execute(query, (class_name,))

        result = self.cursor.fetchone()

        if result:
            return True

        return False

    def get_global_function_return_type(self, method_name, current_module_name):
        methods_table = f"{self.current_id}_methods"

        query = f"""

        SELECT return_type from 

        {methods_table}

        where method_name=?
        and module_name=?
        LIMIT 1
        """

        self.cursor.execute(
            query,
            (
                method_name,
                current_module_name,
            ),
        )
        result = self.cursor.fetchone()

        if result:
            return result[0]

        return

    def insert_imported_module(self, main_module, imported_module, import_alias):
        data = {
            "main_module": main_module,
            "imported_module": imported_module,
            "import_alias": import_alias,
        }

        table_name = f"{self.current_id}_imported_modules"

        self._insert_dicts_to_table(table_name, [data])

    def get_module_call_return_type(self, module_name, method_name):
        methods_table = f"{self.current_id}_methods"
        query1 = f"""
        SELECT class_name from {methods_table}
        WHERE module_name = ? AND
              class_name = ?
        LIMIT 1
        """

        self.cursor.execute(
            query1,
            (
                module_name,
                method_name,
            ),
        )
        result = self.cursor.fetchone()

        if result:
            class_name = result[0]
            return class_name

        query2 = f"""
        SELECT return_type from {methods_table}
        WHERE module_name = ? AND
              method_name = ?
        LIMIT 1
        """

        self.cursor.execute(
            query2,
            (
                module_name,
                method_name,
            ),
        )
        result = self.cursor.fetchone()

        if result:
            return result[0]

        return "auto"

    def get_class_method_translation(
        self, method_name: str, class_name: str, module_name: str = None
    ) -> str | None:
        methods_table = f"{self.current_id}_methods"

        if module_name:
            query = f"""
                SELECT translation FROM {methods_table}
                WHERE method_name = '{method_name}'
                  AND class_name = '{class_name}'
                  AND module_name = '{module_name}'
            """
        else:
            query = f"""
                SELECT translation FROM {methods_table}
                WHERE method_name = '{method_name}'
                  AND class_name = '{class_name}'
            """

        self.cursor.execute(query)
        result = self.cursor.fetchone()

        if result:
            return result[0]
        return None

    def get_method_translation(self, method_name, module_name=None):
        methods_table = f"{self.current_id}_methods"
        print(f"[DEBUG] Looking up method translation:")
        print(f"        ├─ Method Name : {method_name}")
        print(f"        ├─ Module Name : {module_name}")
        print(f"        └─ Methods Table: {methods_table}")

        # 🔍 Print all available modules for this method or in general
        try:
            print(f"[DEBUG] Listing all modules with '{method_name}' in table:")
            self.cursor.execute(
                f"SELECT DISTINCT module_name FROM {methods_table} WHERE method_name=?",
                (method_name,),
            )
            modules = self.cursor.fetchall()
            if modules:
                for row in modules:
                    print(f"        └─ Found module: {row[0]}")
            else:
                print("        └─ No modules found with that method name.")
        except Exception as e:
            print(f"[ERROR] Could not list modules: {e}")

        if module_name:
            query = f"""
            SELECT translation
            FROM {methods_table}
            WHERE method_name=? 
                AND module_name=?
            """
            params = (method_name, module_name)
            print(f"[DEBUG] Executing SQL (with module): {query.strip()}")
            print(f"        Parameters: {params}")
            self.cursor.execute(query, params)
            result = self.cursor.fetchone()
        else:
            query = f"""
            SELECT translation
            FROM {methods_table}
            WHERE method_name=? 
            """
            params = (method_name,)
            print(f"[DEBUG] Executing SQL (no module): {query.strip()}")
            print(f"        Parameters: {params}")
            self.cursor.execute(query, params)
            result = self.cursor.fetchone()

        if result:
            print(f"[DEBUG] Found translation: {result}")
            return result[0]
        else:
            print(
                f"[DEBUG] No translation found for method '{method_name}' in table '{methods_table}'"
            )

            return

    def get_module_name_from_alias(self, main_module, alias):
        table_name = f"{self.current_id}_imported_modules"

        query = f"""
        SELECT imported_module 
        FROM {table_name} WHERE

        main_module=? AND
        import_alias=?
        """

        print(f"querying imported modules from {main_module} as {alias}")

        self.cursor.execute(
            query,
            (
                main_module,
                alias,
            ),
        )

        result = self.cursor.fetchone()
        print(f"got result {result}")

        if result:
            return result[0]

        return

    def _exec_get_variable_type_query(self, variable_name, scope):
        table_name = f"{self.current_id}_variables"
        query = f"""
        SELECT variable_type FROM 
        {table_name} WHERE 
        variable_name='{variable_name}' AND
        scope='{scope}'
        """

        self.cursor.execute(query)
        result = self.cursor.fetchone()

        if result:
            return result[0]

        return None

    def get_variable_type(self, variable_name, scope):
        print(f"checking type for {variable_name} in scope {scope}")
        if scope != "global":
            var_type = self._exec_get_variable_type_query(variable_name, scope)
            print(f"got type {var_type} for {variable_name} in scope {scope}")
            if var_type:
                return var_type

        # if not found in the provided scope
        # check global
        var_type = self._exec_get_variable_type_query(variable_name, "global")

        return var_type

    def get_variable_module_name(self, variable_name, scope):
        table_name = f"{self.current_id}_variables"
        query = f"""
        SELECT module_name FROM 
        {table_name} WHERE 
        variable_name='{variable_name}' AND
        scope='{scope}'
        """

        self.cursor.execute(query)
        result = self.cursor.fetchone()

        if result:
            return result[0]

        return None

    def get_class_method_return_type(self, class_name, method_name):
        table_name = f"{self.current_id}_methods"

        query = f"""
        SELECT return_type FROM

        {table_name} WHERE 
        class_name=? AND
        method_name=?
        """

        self.cursor.execute(
            query,
            (
                class_name,
                method_name,
            ),
        )
        result = self.cursor.fetchone()

        if result:
            return result[0]

        return "auto"

    def get_module_translation(self, module_name):
        table_name = f"{self.current_id}_modules"

        query = f"""
        SELECT translated_name FROM 

        {table_name} WHERE module_name=?
        LIMIT 1

        """

        self.cursor.execute(query, (module_name,))
        result = self.cursor.fetchone()

        if result:
            return result[0]

        else:
            return module_name

    def get_module_dependencies(self, module_name):
        table_name = f"{self.current_id}_modules"

        query = f"""
        SELECT dependencies FROM 

        {table_name} WHERE module_name=?
        LIMIT 1

        """

        self.cursor.execute(query, (module_name,))
        result = self.cursor.fetchone()

        if result:
            return result[0]

    def get_module_internal_includes(self, module_name):
        table_name = f"{self.current_id}_modules"

        query = f"""
        SELECT include_internal_modules FROM 

        {table_name} WHERE module_name=?
        LIMIT 1

        """

        self.cursor.execute(query, (module_name,))
        result = self.cursor.fetchone()

        if result:
            return result[0]

    def save_imported_module(self, main_module, imported_module, import_alias):
        data = {
            "main_module": main_module,
            "imported_module": imported_module,
            "import_alias": import_alias,
        }

        table_name = f"{self.current_id}_imported_modules"

        self._insert_dicts_to_table()

    def _insert_dicts_to_table(self, table_name, dict_list):
        # print(f"📥 Inserting into table: {table_name}")
        # print(f"📦 Incoming data: {dict_list}")

        # Get existing column names from the table
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = self.cursor.fetchall()
        table_columns = [col[1] for col in columns_info]

        # print(f"🧱 Table columns: {table_columns}")

        for data in dict_list:
            col_names = []
            values = []

            for col in table_columns:
                if col in data:
                    col_names.append(col)
                    values.append(data[col])
                else:
                    col_names.append(col)
                    values.append(None)

            placeholders = ",".join("?" for _ in col_names)
            column_str = ",".join(col_names)

            self.cursor.execute(
                f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})",
                values,
            )

        self.conn.commit()

    def _process_dunder_value(self, value):
        """
        Processes a string `value` that might represent a dictionary.
        If it is a JSON-like dict string, returns the value for `self.platform`.
        Otherwise, returns the original string.

        Args:
            value (str): The string to process.

        Returns:
            str: Value corresponding to `self.platform` if applicable, else the original string.
        """

        if isinstance(value, dict):
            return value[self.platform]

        return value

    def _get_dunder_value(self, ast_node, name):
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        try:
                            value = ast.literal_eval(node.value)
                            # print(f"[DEBUG] Found dunder '{name}' = {value!r}")
                            return self._process_dunder_value(value)
                        except Exception as e:
                            # print(f"[WARN] Could not evaluate value for '{name}': {e}")
                            return None
        # print(f"[DEBUG] Dunder '{name}' not found in AST node.")
        return None

    def _insert_module_info(
        self,
        module_name,
        translated_name,
        module_type,
        dependencies,
        include_internal_modules,
    ):
        data = {
            "module_name": module_name,
            "translated_name": translated_name,
            "module_type": module_type,
            "dependencies": dependencies,
            "include_internal_modules": include_internal_modules,
        }
        table = f"{self.current_id}_modules"
        self._insert_dicts_to_table(table, [data])
        return

    def _save_function(self, module, ast_node):
        method_name = ast_node.name
        # print(f"[DEBUG] Saving function: {method_name}")

        return_type = None

        print(f"saving method {method_name}")

        if ast_node.returns:
            return_type = extract_annotation_type(ast_node.returns)
            # print(f"[DEBUG] Return type: {return_type}")
        else:
            print("[DEBUG] No return type annotation found.")

        args = []

        for arg in ast_node.args.args:
            arg_name = arg.arg
            arg_type = (
                extract_annotation_type(arg.annotation) if arg.annotation else None
            )
            # print(f"[DEBUG] Positional arg: {arg_name}, type: {arg_type}")
            args.append({"name": arg_name, "arg_type": arg_type, "is_kwarg": False})

        for kwarg in ast_node.args.kwonlyargs:
            arg_name = kwarg.arg
            arg_type = (
                extract_annotation_type(kwarg.annotation) if kwarg.annotation else None
            )
            # print(f"[DEBUG] Keyword-only arg: {arg_name}, type: {arg_type}")
            args.append({"name": arg_name, "arg_type": arg_type, "is_kwarg": True})

        args_json = json.dumps(args)
        # print(f"[DEBUG] Args JSON: {args_json}")

        class_name = module["class_name"]
        module_name = module["name"]
        module_type = module["type"]

        use_as_is = True
        translation = None

        if module_type == "core":
            use_as_is = self._get_dunder_value(ast_node, "__use_as_is__")
            translation = self._get_dunder_value(ast_node, "__translation__")
            is_reference = self._get_dunder_value(ast_node, "__is_reference__") or False
            construct_with_equal_to = (
                self._get_dunder_value(ast_node, "__construct_with_equal_to__") or False
            )
            class_actual_type = self._get_dunder_value(
                ast_node, "__class_actual_type__"
            )
            pass_as = self._get_dunder_value(ast_node, "__pass_as__") or ""

            is_eval = self._get_dunder_value(ast_node, "__is_eval__") or False

            if use_as_is is None and translation is not None:
                use_as_is = False

        # print(f"[DEBUG] Inserting method: {method_name}, use_as_is: {use_as_is}")
        self._insert_method(
            method_name,
            class_name,
            module_name,
            module_type,
            args_json,
            return_type,
            use_as_is=use_as_is,
            is_reference=is_reference,
            translation=translation,
            class_actual_type=class_actual_type,
            pass_as=pass_as,
            construct_with_equal_to=construct_with_equal_to,
            is_eval=is_eval,
        )

        return

    def _insert_method(
        self,
        method_name,
        class_name,
        module_name,
        module_type,
        args,
        return_type,
        use_as_is=True,
        translation=None,
        is_reference=False,
        class_actual_type=None,
        pass_as=None,
        construct_with_equal_to=False,
        is_eval=False,
    ):
        table_name = f"{self.current_id}_methods"

        data = {
            "method_name": method_name,
            "class_name": class_name,
            "module_name": module_name,
            "module_type": module_type,
            "args": args,
            "return_type": return_type,
            "use_as_is": use_as_is,
            "translation": translation,
            "is_reference": is_reference,
            "class_actual_type": class_actual_type,
            "pass_as": pass_as,
            "construct_with_equal_to": construct_with_equal_to,
            "is_eval": is_eval,
        }

        self._insert_dicts_to_table(table_name, [data])
        return

    def _save_class(self, module, ast_node):
        for item in ast_node.body:
            if isinstance(item, ast.FunctionDef):
                self._save_function(module, item)

        return

    def insert_variable(
        self, variable_name, variable_type, module_name, module_type, scope="global"
    ):
        """

        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        args_dict = {arg: values[arg] for arg in args}"""
        table_name = f"{self.current_id}_variables"

        args_dict = {
            "variable_name": variable_name,
            "variable_type": variable_type,
            "module_name": module_name,
            "module_type": module_type,
            "scope": scope,
        }

        self._insert_dicts_to_table(table_name, [args_dict])
        return

    def _save_modules(self):
        for module in self.imported_modules:
            module_tree = module["module_tree"]
            module_type = module["type"]
            module_name = module["name"]
            module_alias = module["alias"]

            translated_name = self._get_dunder_value(module_tree, "__include_modules__")
            dependencies = self._get_dunder_value(module_tree, "__dependencies__")
            include_internal_modules = self._get_dunder_value(
                module_tree, "__include_internal_modules__"
            )

            self._insert_module_info(
                module_name,
                translated_name,
                module_type,
                dependencies,
                include_internal_modules,
            )

            for node in module_tree.body:
                if isinstance(node, ast.FunctionDef):
                    module["class_name"] = None
                    self._save_function(module, node)

                elif isinstance(node, ast.ClassDef):
                    module["class_name"] = node.name
                    self._save_class(module, node)

                elif (
                    isinstance(node, ast.AnnAssign)
                    and isinstance(node.target, ast.Name)
                    and module_type == "core"
                ):
                    variable_name = node.target.id
                    variable_type = ast.unparse(node.annotation)
                    module_import_line = module["line_num"]
                    occurence_line = node.lineno

                    self.insert_variable(
                        variable_name, variable_type, module_name, module_type
                    )

        return


class TranslatedExpr:
    """Wrapper to keep translated code and its inferred type for chained calls."""

    def __init__(self, code: str, type_: str = "auto"):
        self.code = code
        self.type = type_

    def __str__(self):
        return self.code


class TypeAnalyzer:
    def __init__(
        self,
        dependency_resolver: DependencyResolver,
        current_module_name: str,
        get_scope,
        get_is_inside_loop,
        get_loop_vars,
    ):
        self.dependency_resolver = dependency_resolver
        self.scope = "global"
        self.current_module_name = current_module_name
        self.loop_variables = {}
        self.is_inside_loop = False
        self.get_scope = get_scope
        self.get_is_inside_loop = get_is_inside_loop
        self.get_loop_vars = get_loop_vars

    def _call_type_analyzer(self, call_chain: dict, node):
        prev_type = None
        prev_statement = None
        print(f"processing call chain {call_chain}")

        for called_entity in call_chain:
            called_entity_type = called_entity["type"]
            called_entity_value = called_entity["value"]
            if not prev_type:
                if called_entity_type == "const":
                    # basically a call like [1, 2, 3].split()
                    prev_statement = self.visit(called_entity_value)
                    prev_type = self.type_analyzer.get_node_type(called_entity_value)

                elif called_entity_type == "attr":
                    # this is a call like x.foo()

                    # attr can be an imported module
                    module_name = self.dependency_resolver.get_module_name_from_alias(
                        self.current_module_name, called_entity_value
                    )

                    print(f"found module {module_name}")

                    if module_name:
                        # this is an imported module
                        prev_type = "module"
                        prev_statement = module_name

                    else:
                        # this is a variable
                        prev_statement = called_entity_value
                        prev_type = self.dependency_resolver.get_variable_type(
                            called_entity_value, self.scope
                        )

                elif called_entity_type == "call":
                    # this is a global function.
                    method_name = called_entity_value
                    args = called_entity["args"]

                    args_type = [self.get_node_type(arg) for arg in node.args]
                    if is_builtin_function(method_name):
                        translated_method_name = f"{BUILTIN_FUNC_PREFIX}_{method_name}"

                        prev_statement = None
                        prev_type = get_builtin_function_return_type(
                            method_name, args_type
                        )

                    else:
                        # this is a global function that user defined in current module.
                        # call it as is.

                        prev_statement = None
                        prev_type = (
                            self.dependency_resolver.get_global_function_return_type(
                                method_name, self.current_module_name
                            )
                        )

            else:
                if called_entity_type == "attr":
                    # not expected yet because core classes do not expose variables
                    # TBD
                    pass
                elif called_entity_type == "call":
                    method_name = called_entity_value
                    args = called_entity["args"]

                    if prev_type == "module":
                        # example
                        # import lib as l
                        # l.foo()
                        # currently going over foo.
                        print(f"visited args are {args}")
                        module_name = prev_statement

                        is_module_class = self.dependency_resolver.is_module_class(
                            method_name, module_name=prev_statement
                        )

                        if is_module_class:
                            # current function is actually a class initialization
                            # l.SomeClass(*args)
                            called_entity_translation = (
                                self.dependency_resolver.get_class_init_translation(
                                    method_name
                                )
                            )
                            # need to add a dummy arg at position to simulate self in class init
                            args.insert(0, "dummy")

                            prev_type = method_name  # this is class name itself
                            prev_statement = (
                                f"{called_entity_translation.format(*args)}"
                            )

                        else:
                            called_entity_return_type = (
                                self.dependency_resolver.get_module_call_return_type(
                                    prev_statement, method_name
                                )
                            )

                            prev_type = called_entity_return_type

                    else:
                        if prev_type in BUILTIN_TYPES:
                            cpp_type = get_cpp_python_type(
                                transformed_core_type, custom_type_str=True
                            )

                            prev_type = get_python_builtin_class_method_type(
                                prev_type, method_name
                            )

                        else:
                            # here prev_type is class name, prev_statement is class instance
                            # and entity called is the class method

                            called_entity_type = (
                                self.dependency_resolver.get_class_method_return_type(
                                    prev_type, method_name
                                )
                            )

                            prev_type = called_entity_type

        return prev_type

    def get_node_type(self, node, prev_translated_expr=None):
        self.scope = self.get_scope()
        self.is_inside_loop = self.get_is_inside_loop()
        self.loop_variables = self.get_loop_vars()
        if isinstance(node, ast.Constant):
            return type(node.value).__name__

        elif isinstance(node, ast.List):
            element_type = self._get_list_element_type(node.elts)
            return f"list,{element_type}"

        elif isinstance(node, ast.Name):
            # check scope
            # if inside function, check args first
            var_name = node.id
            if self.is_inside_loop:
                if var_name in self.loop_variables.keys():
                    return self.loop_variables[var_name]

            return self.dependency_resolver.get_variable_type(var_name, self.scope)

        elif isinstance(node, ast.Compare):
            # Comparisons always result in boolean
            return "bool"

        elif isinstance(node, ast.BoolOp):
            # and/or returns boolean
            return "bool"

        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            if isinstance(node.operand, ast.Constant):
                return type(-node.operand.value).__name__

        elif isinstance(node, ast.JoinedStr):
            return "str"

        elif isinstance(node, ast.Dict):
            keys = node.keys
            values = node.values

            for k, v in zip(keys, values):
                if not (isinstance(k, ast.Constant) and isinstance(v, ast.Constant)):
                    json_parts.append("/* unsupported */")
                    continue

                k_val = k.value
                v_val = v.value

                return f"dict,{type(k_val).__name__},{type(v_val).__name__}"

        elif isinstance(node, ast.Call):
            call_chain = _extract_chain(node)
            return self._call_type_analyzer(call_chain, node)

        elif isinstance(node, ast.Subscript):
            value = node.value

            value_type = self.get_node_type(value)

            value_type_split = value_type.split(",")
            core_type = value_type_split[0]

            if core_type == "str":
                # return str
                return "str"

            elif core_type == "list":
                element_type = value_type_split[1]
                if isinstance(node.slice, ast.Constant):
                    # user has called an index list[i]
                    # return self.dependency_resolver.get_list_element_type(value.id, self.scope)
                    # return self._get_list_element_type(value.elts)
                    if isinstance(value, ast.Name):
                        # this is a defined variable
                        return element_type
                        # return self.dependency_resolver.get_list_element_type(value.id, self.scope)
                    elif isinstance(value, ast.List):
                        return self._get_list_element_type(value.elts)
                else:
                    # this is slize
                    # list[i:j]
                    return value_type

            elif value_type == "dict":
                dict_info = self.dependency_resolver.get_dict_key_value_type(
                    value.id, self.scope
                )

                return dict_info["value_type"]

        elif isinstance(node, ast.BinOp):
            print("starting type extraction")
            left_type = self.get_node_type(node.left)
            right_type = self.get_node_type(node.right)

            print(f"left type is {left_type} and right type is {right_type}")

            if not left_type or not right_type:
                raise TypeError(f"BinaryOp missing operand types: {ast.dump(node)}")

            left_parts = left_type.split(",")
            right_parts = right_type.split(",")

            left_base = left_parts[0]
            right_base = right_parts[0]

            op = node.op

            # STR + STR → STR
            if left_base == right_base == "str":
                if isinstance(op, ast.Add):
                    return "str"
                raise TypeError(f"Unsupported binary op for str: {type(op).__name__}")

            # LIST + LIST → LIST,<element_type>
            if left_base == right_base == "list":
                if isinstance(op, ast.Add):
                    # Must also match element type
                    if left_parts[1:] == right_parts[1:]:
                        return left_type
                    else:
                        raise TypeError(
                            f"List element type mismatch: {left_type} + {right_type}"
                        )
                raise TypeError(f"Unsupported binary op for list: {type(op).__name__}")

            # DICT — not supported
            if "dict" in (left_base, right_base):
                raise TypeError(
                    f"Binary operations on dicts are not supported: {ast.dump(node)}"
                )

            # BOOL + BOOL
            if left_base == right_base == "bool":
                if isinstance(op, (ast.And, ast.Or, ast.BitAnd, ast.BitOr, ast.BitXor)):
                    return "bool"
                elif isinstance(op, (ast.Add, ast.Sub)):
                    return "int"
                else:
                    raise TypeError(
                        f"Unsupported binary op for bool: {type(op).__name__}"
                    )

            # INT/FLOAT logic
            allowed_numeric = {"int", "float"}
            if left_base in allowed_numeric and right_base in allowed_numeric:
                return "float" if "float" in (left_base, right_base) else "int"

            raise TypeError(
                f"Unsupported binary operation between {left_type} and {right_type}: {ast.dump(node)}"
            )

    def _get_list_element_type(self, elements):
        for elt in elements:
            if not isinstance(elt, ast.Constant):
                raise NotImplementedError(
                    f"Only flat constant lists are supported. Found: {type(elt).__name__}"
                )

            py_val = elt.value

            if type(py_val) not in LIST_ALLOWED_TYPES:
                raise NotImplementedError(
                    f"Unsupported constant type in list: {type(py_val).__name__}"
                )

            return type(py_val).__name__

        return "auto"

    def _extract_annotation(self, node):
        """Extract only the final type name(s) from an annotation node."""

        if node is None:
            return None

        # Simple names like int, str, float
        if isinstance(node, ast.Name):
            return node.id

        # Qualified attributes like a.SomeType or x.y.Type -> return only final part
        elif isinstance(node, ast.Attribute):
            return node.attr

        # Subscripted types: e.g. List[int], Dict[str, a.Type]
        elif isinstance(node, ast.Subscript):
            # Get the main type (e.g. "List" or "Dict")
            base = self._extract_annotation(node.value)

            # Handle slice difference between Python <3.9 and >=3.9
            sub = node.slice.value if hasattr(node.slice, "value") else node.slice

            # Get inner types recursively
            if isinstance(sub, ast.Tuple):
                inner = [self._extract_annotation(elt) for elt in sub.elts]
            else:
                inner = [self._extract_annotation(sub)]

            # Combine all relevant type names
            return ",".join([base] + inner)

        # Handle None, Optional[None], etc.
        elif isinstance(node, ast.Constant) and node.value is None:
            return "None"

        # Handle string literal annotations (PEP 563)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value

        # If nothing matches, raise to catch unsupported structures
        raise ValueError(f"Unsupported annotation node: {ast.dump(node)}")


class ArduinoTranspiler(ast.NodeVisitor):
    def __init__(
        self,
        current_module_name: str,
        tree: ast.Module,
        dependency_resolver: DependencyResolver,
        monitor_speed: int,
    ):
        self.tree = tree
        self.current_module_name = current_module_name
        self.dependency_resolver = dependency_resolver
        self.scope = "global"
        self.output = []
        self.added_imports = []
        self.is_inside_loop = False
        self.loop_variables = {}
        self.monitor_speed = monitor_speed
        self.dependencies = []
        self.has_transpiled = False
        self.type_analyzer = TypeAnalyzer(
            dependency_resolver=self.dependency_resolver,
            current_module_name=self.current_module_name,
            get_scope=lambda: self.scope,
            get_is_inside_loop=lambda: self.is_inside_loop,
            get_loop_vars=lambda: self.loop_variables,
        )

    """def visit(self, node, prev_translated_expr=None):
        
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        # Call the real visitor method, passing along context if it accepts it
        try:
            return visitor(node, prev_translated_expr=prev_translated_expr)
        except TypeError:
            # Visitor doesn’t accept translated_expr → call normally
            return visitor(node)"""

    def transpile(self) -> str:
        # tree = ast.parse(self.code)
        transpiled_code = self.visit(self.tree)

        topline_includes = self.get_topline_includes()
        has_transpiled = True

        return "\n".join([topline_includes, transpiled_code])

    def get_dependencies(self):
        if self.has_transpiled:
            return self.dependencies

        self.visit(self.tree)

        return self.dependencies

    def get_topline_includes(self):
        op = "\n".join(f'#include "{module}.h"' for module in TOPLINE_INCLUDES)

        return op

    def visit_Module(self, node):
        lines = []
        for stmt in node.body:
            line = self.visit(stmt)
            if line:  # ✅
                if isinstance(
                    stmt,
                    (
                        ast.Assign,
                        ast.Expr,
                        ast.Return,
                        ast.Call,
                        ast.Compare,
                        ast.BinOp,
                    ),
                ):
                    if not line.strip().endswith(";"):
                        line += ";"
                lines.append(line)

        if lines:
            return "\n".join(lines)

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Name(self, node):
        return f"{node.id}"

    def visit_Num(self, node):
        return str(node.n)

    def visit_Attribute(self, node):
        return f"{self.visit(node.value)}.{node.attr}"

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)

        if operand is None:
            raise Exception(f"Unsupported operand in UnaryOp: {ast.dump(node)}")

        if isinstance(node.op, ast.USub):
            return f"-({operand})"
        elif isinstance(node.op, ast.UAdd):
            return f"+({operand})"
        elif isinstance(node.op, ast.Not):
            return f"!({operand})"
        elif isinstance(node.op, ast.Invert):
            return f"~({operand})"
        else:
            raise Exception(f"Unsupported unary operator: {ast.dump(node.op)}")

    def _operator_to_str(self, op):
        if isinstance(op, ast.Eq):
            return "=="
        elif isinstance(op, ast.NotEq):
            return "!="
        elif isinstance(op, ast.Lt):
            return "<"
        elif isinstance(op, ast.LtE):
            return "<="
        elif isinstance(op, ast.Gt):
            return ">"
        elif isinstance(op, ast.GtE):
            return ">="
        elif isinstance(op, ast.Is):
            return "=="
        elif isinstance(op, ast.IsNot):
            return "!="
        elif isinstance(op, ast.In):
            return "in"
        elif isinstance(op, ast.NotIn):
            return "not in"
        else:
            raise NotImplementedError(f"Unknown comparison operator: {op}")

    def visit_Compare(self, node):
        # Visit the left side
        left = self.visit(node.left)

        # Build each comparison
        comparisons = []
        for op, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)

            if isinstance(op, (ast.In, ast.NotIn)):
                right_side_type = self.type_analyzer.get_node_type(comparator)

                if isinstance(op, ast.In):
                    if right_side_type in ["list", "dict"]:
                        return f"{right}.contains({left})"

                    elif right_side_type == "str":
                        return f"PyString({right}).contains({left})"

                elif isinstance(op, ast.NotIn):
                    if right_side_type in ["list", "dict"]:
                        return f"!{right}.contains({left})"

                    elif right_side_type == "str":
                        return f"!PyString({right}).contains({left})"

            op_str = self._operator_to_str(op)

            comparisons.append(f"{op_str} {right}")

        # Join left with the comparisons
        result = f"{left} " + " ".join(comparisons)
        return result

    def visit_If(self, node: ast.If):
        result = []

        # Render the if condition
        condition = self.visit(node.test)
        result.append(f"if ({condition}) {{")

        for stmt in node.body:
            line = self.visit(stmt)
            if line:
                result.append(f"    {line};")

        result.append("}")

        # Handle elif and else
        orelse = node.orelse
        while len(orelse) == 1 and isinstance(orelse[0], ast.If):
            # Handle `elif`
            elif_node = orelse[0]
            condition = self.visit(elif_node.test)
            result.append(f"else if ({condition}) {{")
            for stmt in elif_node.body:
                line = self.visit(stmt)
                if line:
                    result.append(f"    {line};")
            result.append("}")
            orelse = elif_node.orelse

        # Final else
        if orelse:
            result.append("else {")
            for stmt in orelse:
                line = self.visit(stmt)
                if line:
                    result.append(f"    {line};")
            result.append("}")

        return "\n".join(result)

    def visit_For(self, node):
        self.is_inside_loop = True
        loop_var_type = self.type_analyzer.get_node_type(node.iter)
        loop_type = loop_var_type.split(",")[0]
        print(f"loop type is {loop_type}")
        result = []
        loop_var = self.visit(node.target)
        iterable = self.visit(node.iter)

        if loop_type == "range":
            self.loop_variables[loop_var] = "int"
            result.append("{")
            result.append(f"    PyRange __range_obj = PyRange({iterable});")
            result.append(f"    while (__range_obj.has_next()) {{")
            result.append(f"        int {loop_var} = __range_obj.next();")
            for stmt in node.body:
                body_line = self.visit(stmt)
                if body_line:
                    result.append(f"        {body_line};")
            result.append("    }")
            result.append("}")

        elif loop_type == "list":
            element_type = loop_var_type.split(",")[1]
            self.loop_variables[loop_var] = element_type
            element_type_cpp = get_cpp_python_type(element_type)
            result.append("{")
            result.append(
                f"    PyList<{element_type_cpp}> __list_obj = PyList<{element_type_cpp}>({iterable});"
            )
            result.append(f"    for (int __i = 0; __i < __list_obj.size(); ++__i) {{")
            result.append(f"        {element_type_cpp} {loop_var} = __list_obj[__i];")
            for stmt in node.body:
                body_line = self.visit(stmt)
                if body_line:
                    result.append(f"        {body_line};")
            result.append("    }")
            result.append("}")

        elif loop_type == "dict_items":
            try:
                _, key_type, value_type = loop_var_type.split(",")
            except ValueError:
                raise TranspilerError(
                    f"Invalid dict_items type format: {loop_var_type}"
                )

            if key_type != "str":
                raise TranspilerError(
                    "Only 'str' keys supported for dict_items iteration."
                )

            key_cpp = "String"
            val_cpp = get_cpp_python_type(value_type)

            if isinstance(node.target, ast.Tuple) and len(node.target.elts) == 2:
                key_var = self.visit(node.target.elts[0])
                val_var = self.visit(node.target.elts[1])
            else:
                raise TranspilerError(
                    "dict_items must unpack to two variables (key, value)"
                )

            self.loop_variables[key_var] = key_type
            self.loop_variables[val_var] = value_type

            # Get the dictionary expression (e.g. from `a.items()` → extract `a`)
            dict_expr = iterable  # fallback to full expression
            if isinstance(node.iter, ast.Call) and isinstance(
                node.iter.func, ast.Attribute
            ):
                if node.iter.func.attr == "items":
                    dict_expr = self.visit(
                        node.iter.func.value
                    )  # e.g. `a` from `a.items()`

            result.append("{")
            result.append(
                f"    PyDictItems<{val_cpp}> __dict_items_obj = {dict_expr}.items();"
            )
            result.append(
                f"    for (int __i = 0; __i < __dict_items_obj.size(); ++__i) {{"
            )
            result.append(f"        String {key_var} = __dict_items_obj.key_at(__i);")
            result.append(
                f"        {val_cpp} {val_var} = __dict_items_obj.value_at(__i);"
            )

            for stmt in node.body:
                body_line = self.visit(stmt)
                if body_line:
                    result.append(f"        {body_line};")

            result.append("    }")
            result.append("}")

        elif loop_type == "str":
            self.loop_variables[loop_var] = "str"
            temp_name = "__str_obj"  # You can make this auto-generated if needed
            result.append("{")
            result.append(f"    PyString {temp_name} = PyString({iterable});")
            result.append(f"    for (int __i = 0; __i < {temp_name}.len(); ++__i) {{")
            result.append(f"        String {loop_var} = String({temp_name}[__i]);")

            for stmt in node.body:
                body_line = self.visit(stmt)
                if body_line:
                    result.append(f"        {body_line};")

            result.append("    }")
            result.append("}")

        self.loop_variables = {}
        self.is_inside_loop = False

        return "\n".join(result)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        op = node.op
        if isinstance(op, ast.Add):
            operator = "+"
        elif isinstance(op, ast.Sub):
            operator = "-"
        elif isinstance(op, ast.Mult):
            operator = "*"
        elif isinstance(op, ast.Div):
            operator = "/"
        elif isinstance(op, ast.FloorDiv):
            operator = "/"  # Note: C++ doesn't have Python-style //
        elif isinstance(op, ast.Mod):
            operator = "%"
        elif isinstance(op, ast.Pow):
            return f"pow({left}, {right})"  # Use C++ std::pow
        elif isinstance(op, ast.LShift):
            operator = "<<"
        elif isinstance(op, ast.RShift):
            operator = ">>"
        elif isinstance(op, ast.BitOr):
            operator = "|"
        elif isinstance(op, ast.BitXor):
            operator = "^"
        elif isinstance(op, ast.BitAnd):
            operator = "&"
        else:
            raise NotImplementedError(f"Unsupported binary operator: {ast.dump(op)}")
        return f"({left} {operator} {right})"

    def visit_Dict(self, node):
        keys = node.keys
        values = node.values
        json_parts = []
        inferred_type = None

        for k, v in zip(keys, values):
            if not (isinstance(k, ast.Constant) and isinstance(v, ast.Constant)):
                json_parts.append("/* unsupported */")
                continue

            k_val = k.value
            v_val = v.value

            # stringify key with JSON-style quotes (do NOT escape here)
            key_str = f'"{k_val}"' if isinstance(k_val, str) else f'"{str(k_val)}"'

            if isinstance(v_val, bool):
                inferred_type = get_cpp_python_type("bool")
                value_str = "true" if v_val else "false"

            elif isinstance(v_val, int):
                inferred_type = get_cpp_python_type("int")
                value_str = str(v_val)

            elif isinstance(v_val, float):
                inferred_type = get_cpp_python_type("float")
                value_str = str(v_val)

            elif isinstance(v_val, str):
                inferred_type = get_cpp_python_type("str")
                escaped_val = v_val.replace(
                    '"', '\\"'
                )  # only escape internal quotes in string values
                value_str = f'"{escaped_val}"'

            else:
                value_str = "/* unsupported */"

            json_parts.append(f"{key_str}: {value_str}")

        json_str = "{ " + ", ".join(json_parts) + " }"
        c_string_literal = json_str.replace(
            '"', '\\"'
        )  # just escape for outer C++ string

        if not inferred_type:
            inferred_type = "auto"

        return f'PyDict<{inferred_type}>("{c_string_literal}")'

    def visit_Import(self, node):
        imports = list()
        internal_imports = list()
        for alias in node.names:
            alias_name = alias.name
            imported_as = alias.asname
            self.dependency_resolver.insert_imported_module(
                self.current_module_name, alias_name, imported_as
            )
            print(f"inserted {alias_name} imported as {imported_as}")
            translated_modules = self.dependency_resolver.get_module_translation(
                alias_name
            )
            dependencies = self.dependency_resolver.get_module_dependencies(alias_name)

            include_internal_modules = (
                self.dependency_resolver.get_module_internal_includes(alias_name)
            )
            print(f"translated modules are {translated_modules}")
            print(f"dependencies are {dependencies}")
            print(f"internal modules are {include_internal_modules}")

            if dependencies:
                for dependency in dependencies.split(","):
                    self.dependencies.append(dependency)

            if translated_modules:
                translated_modules_split = translated_modules.split(",")
                for module in translated_modules_split:
                    # translated_code += f"#include {module}.h" + "\n"
                    imports.append(module)

            if include_internal_modules:
                for internal_module in include_internal_modules.split(","):
                    internal_imports.append(internal_module)

        translated_code = ""

        for i in set(imports):
            if i not in self.added_imports:
                translated_code += f"#include <{i}.h>" + "\n"
                self.added_imports.append(i)

        for i in set(internal_imports):
            translated_code += f'#include "{i}.h"' + "\n"

        return translated_code

    def visit_Call(self, node):
        call_chain = _extract_chain(node)

        analyzed_call = self._call_analyzer(call_chain, node)

        return analyzed_call["translation"]

    def _call_analyzer(self, call_chain: dict, node):
        prev_type = None
        prev_statement = None
        print(f"processing call chain {call_chain}")

        for called_entity in call_chain:
            called_entity_type = called_entity["type"]
            called_entity_value = called_entity["value"]
            if not prev_type:
                if called_entity_type == "const":
                    # basically a call like [1, 2, 3].split()
                    prev_statement = self.visit(called_entity_value)
                    prev_type = self.type_analyzer.get_node_type(called_entity_value)

                elif called_entity_type == "attr":
                    # this is a call like x.foo()

                    # attr can be an imported module
                    module_name = self.dependency_resolver.get_module_name_from_alias(
                        self.current_module_name, called_entity_value
                    )

                    print(f"found module {module_name}")

                    if module_name:
                        # this is an imported module
                        prev_type = "module"
                        prev_statement = module_name

                    else:
                        # this is a variable
                        prev_statement = called_entity_value
                        prev_type = self.dependency_resolver.get_variable_type(
                            called_entity_value, self.scope
                        )

                elif called_entity_type == "call":
                    # this is a global function.
                    method_name = called_entity_value
                    args = called_entity["args"]
                    args = self._visit_function_args(args)
                    args_type = [
                        self.type_analyzer.get_node_type(arg) for arg in node.args
                    ]
                    if is_builtin_function(method_name):
                        translated_method_name = f"{BUILTIN_FUNC_PREFIX}_{method_name}"

                        prev_statement = f"{translated_method_name}({','.join(args)})"
                        prev_type = get_builtin_function_return_type(
                            method_name, args_type
                        )

                    else:
                        # this is a global function that user defined in current module.
                        # call it as is.
                        process_joined_args = self._process_func_args(
                            self.current_module_name, method_name, args
                        )
                        prev_statement = f"{method_name}({process_joined_args})"
                        prev_type = (
                            self.dependency_resolver.get_global_function_return_type(
                                method_name, self.current_module_name
                            )
                        )

            else:
                if called_entity_type == "attr":
                    # not expected yet because core classes do not expose variables
                    # TBD
                    pass
                elif called_entity_type == "call":
                    method_name = called_entity_value
                    args = called_entity["args"]
                    args = self._visit_function_args(args)

                    if prev_type == "module":
                        # example
                        # import lib as l
                        # l.foo()
                        # currently going over foo.
                        print(f"visited args are {args}")
                        module_name = prev_statement

                        is_module_class = self.dependency_resolver.is_module_class(
                            method_name, module_name=prev_statement
                        )

                        if is_module_class:
                            # current function is actually a class initialization
                            # l.SomeClass(*args)
                            called_entity_translation = (
                                self.dependency_resolver.get_class_init_translation(
                                    method_name
                                )
                            )
                            # need to add a dummy arg at position to simulate self in class init
                            args.insert(0, "dummy")

                            args = self._process_func_args(
                                module_name, "__init__", ",".join(args)
                            )

                            print(
                                f"doing translation for {method_name} module {prev_statement} and args are {args}"
                            )

                            prev_type = method_name  # this is class name itself
                            prev_statement = (
                                f"{called_entity_translation.format(*args)}"
                            )

                        else:
                            args = self._process_func_args(
                                module_name, method_name, ",".join(args)
                            )
                            called_entity_translation = (
                                self.dependency_resolver.get_method_translation(
                                    method_name, module_name=module_name
                                )
                            )
                            called_entity_return_type = (
                                self.dependency_resolver.get_module_call_return_type(
                                    prev_statement, method_name
                                )
                            )

                            prev_type = called_entity_return_type
                            prev_statement = called_entity_translation.format(*args)

                    else:
                        if prev_type in BUILTIN_TYPES:
                            cpp_type = get_cpp_python_type(
                                transformed_core_type, custom_type_str=True
                            )
                            if prev_type == "str" and method_name == "isspace":
                                prev_statement = (
                                    f"{prev_statement}.py{method_name}({args})"
                                )
                            else:
                                prev_statement = f"{prev_statement}.method_name({args})"

                            prev_type = get_python_builtin_class_method_type(
                                prev_type, method_name
                            )

                        else:
                            # here prev_type is class name, prev_statement is class instance
                            # and entity called is the class method
                            print(
                                f"evaluation for {prev_statement}, {prev_type} and current {method_name}, args are {args}"
                            )

                            called_entity_translation = (
                                self.dependency_resolver.get_class_method_translation(
                                    method_name, prev_type
                                )
                            )

                            called_entity_type = (
                                self.dependency_resolver.get_class_method_return_type(
                                    prev_type, method_name
                                )
                            )

                            args.insert(0, prev_statement)

                            prev_type = called_entity_type
                            prev_statement = called_entity_translation.format(*args)

        return {"translation": prev_statement, "type": prev_type}

    def _visit_function_args(self, args: list):
        visited_args = []

        for arg in args:
            visited_arg = self.visit(arg)
            visited_args.append(visited_arg)

        return visited_args

    """def visit_Call(self, node, prev_translated_expr: TranslatedExpr):
        positional_args = []

        print(f"args are {node.args}")
        for arg in node.args:
            result = self.visit(arg)
            if result is None:
                print(f"[ERROR] visit_Call: unsupported argument: {ast.dump(arg)}")
                result = "None"
            positional_args.append(result)

        joined_args = ",".join(positional_args)

        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr

            if isinstance(node.func.value, ast.Name):
                base_name = node.func.value.id
                print(
                    f"[DEBUG] Attribute Call on base '{base_name}' with method '{method_name}'"
                )

                module_name = self.dependency_resolver.get_module_name_from_alias(
                    self.current_module_name, base_name
                )
                print(
                    f"[DEBUG] Resolved module alias: {module_name} for base name {base_name}"
                )

                if module_name:
                    translated_func = self.dependency_resolver.get_method_translation(
                        method_name, module_name=module_name
                    )
                    translated_type = (
                        self.dependency_resolver.get_module_call_return_type(
                            method_name, module_name
                        )
                    )
                    print(
                        f"[DEBUG] Translated function: {translated_func}, Return type: {translated_type}"
                    )
                    if self.dependency_resolver.is_module_class(
                        method_name, module_name=module_name
                    ):
                        # return f"{{{joined_args}}}"
                        # this is class initialization
                        # the method is actually a class
                        class_name = method_name
                        class_init = (
                            self.dependency_resolver.get_class_init_translation(
                                class_name
                            )
                        )
                        positional_args.insert(0, "dummy")
                        print(f"class init is {class_init}")
                        return class_init.format(*positional_args)

                    if translated_func:
                        # this is module function.
                        # check if the translation need to be eval

                        is_translation_eval = (
                            self.dependency_resolver.get_method_is_eval(
                                method_name, module_name
                            )
                        )

                        if is_translation_eval == True:
                            raw_args = []
                            for arg in node.args:
                                raw_args.append(arg.value)
                            print("this need eval")
                            print(f"evaluating {translated_func.format(*raw_args)}")
                            return f'"{eval(translated_func.format(*raw_args))}"'

                        return translated_func.format(*positional_args)
                    else:
                        print(
                            f"[WARN] No translation found for {module_name}.{method_name}"
                        )
                        return f"{method_name}({joined_args})"
                else:
                    variable_type = self.dependency_resolver.get_variable_type(
                        base_name, self.scope
                    )
                    variable_module_name = (
                        self.dependency_resolver.get_variable_module_name(
                            base_name, self.scope
                        )
                    )

                    variable_type_split = "auto"

                    if variable_type:
                        variable_type_split = variable_type.split(",")

                    core_type = variable_type_split[0]

                    print(f"[DEBUG] Variable '{base_name}' type: {variable_type}")

                    if core_type in ("list", "dict"):
                        return f"{base_name}.{method_name}({joined_args})"
                    elif core_type in ("str", "bool", "int", "float"):
                        cpp_type = get_cpp_python_type(
                            variable_type, custom_type_str=True
                        )

                        if core_type == "str" and method_name == "isspace":
                            return f"{cpp_type}({base_name}).py{method_name}({joined_args})"

                        return f"{cpp_type}({base_name}).{method_name}({joined_args})"

                    # this is an internal class method.
                    # check for its translation
                    print(
                        f"checking translation for class {variable_type} method {method_name} and module is {variable_module_name}"
                    )
                    # translated_class_method = self.dependency_resolver.get_class_method_translation(method_name, variable_type, module_name=variable_module_name)
                    translated_class_method = (
                        self.dependency_resolver.get_class_method_translation(
                            method_name, variable_type
                        )
                    )
                    print(f"translation is {translated_class_method}")

                    if translated_class_method:
                        positional_args.insert(
                            0, base_name
                        )  # this is to pass self as an argument
                        print(
                            f"translation is {translated_class_method} and args are {positional_args}"
                        )
                        return translated_class_method.format(*positional_args)

                    return f"{base_name}.{method_name}({joined_args})"

            elif isinstance(node.func.value, ast.Call):
                print(
                    f"[DEBUG] Method call on result of another call: {ast.dump(node.func.value)}"
                )
                transformed_func = self.visit(
                    node.func.value, prev_translated_expr=prev_translated_expr
                )
                transformed_type = self.type_analyzer.get_node_type(
                    node.func.value, prev_translated_expr=prev_translated_expr
                )
                transformed_core_type = transformed_type.split(",")[0]

                if transformed_core_type in BUILTIN_TYPES:
                    cpp_type = get_cpp_python_type(
                        transformed_core_type, custom_type_str=True
                    )

                    if transformed_core_type == "str" and method_name == "isspace":
                        return f"{cpp_type}({transformed_func}).py{method_name}({joined_args})"

                    return (
                        f"{cpp_type}({transformed_func}).{method_name}({joined_args})"
                    )
                else:
                    return f"{transformed_func}.{method_name}({joined_args})"

            elif isinstance(node.func.value, ast.Constant):
                transformed_func = self.visit(node.func.value)
                transformed_type = self.type_analyzer.get_node_type(node.func.value)
                cpp_type = get_cpp_python_type(transformed_type, custom_type_str=True)

                print(
                    f"[DEBUG] Constant call: type={transformed_type}, func={transformed_func}"
                )

                if transformed_type == "str" and method_name == "isspace":
                    return (
                        f"{cpp_type}({transformed_func}).py{method_name}({joined_args})"
                    )

                return f"{cpp_type}({transformed_func}).{method_name}({joined_args})"

        elif isinstance(node.func, ast.Name):
            method_name = node.func.id
            print(f"[DEBUG] Direct function call: {method_name}")

            if is_builtin_function(method_name):
                translated_method_name = f"{BUILTIN_FUNC_PREFIX}_{method_name}"
                print(f"[DEBUG] Translated built-in function: {translated_method_name}")
                return f"{translated_method_name}({joined_args})"

            # this is a global function that user defined in current module.
            # call it as is.
            process_joined_args = self._process_func_args(
                self.current_module_name, method_name, joined_args
            )
            return f"{method_name}({process_joined_args})"

        print(f"[WARN] visit_Call fell through! Node: {ast.dump(node)}")"""

    def _process_func_args(self, module_name, method_name, joined_args):
        print(f"processing for {module_name} and method {method_name}")
        stored_args = self.dependency_resolver.get_method_args(module_name, method_name)

        arg_list = joined_args.split(",")

        for i in range(len(stored_args)):
            arg = stored_args[i]
            print(f"proceeing arg is {arg}")
            arg_type = arg["arg_type"]

            if arg and not is_core_python_type(arg_type):
                arg_pass_as = self.dependency_resolver.get_class_pass_as(arg_type)

                if arg_pass_as == "pointer":
                    arg_list[i] = f"*{arg_list[i]}"

                elif arg_pass_as == "reference":
                    arg_list[i] = f"&{arg_list[i]}"
                else:
                    arg_list[i] = f"{arg_list[i]}"

        return arg_list

    def visit_FunctionDef(self, node):
        func_name = node.name
        self.scope = func_name

        # Step 1: Determine return type
        return_type = None
        if node.returns:
            return_type = self.type_analyzer._extract_annotation(node.returns)

        return_cpp_type = get_cpp_python_type(return_type) or "void"
        if (
            return_cpp_type == "auto"
            or not return_cpp_type
            or return_cpp_type == "None"
        ):
            return_cpp_type = "void"

        # Step 2: Process arguments
        cpp_args = []
        save_args = []
        for arg in node.args.args:
            arg_name = arg.arg
            arg_type = self.type_analyzer._extract_annotation(arg.annotation)
            cpp_base_type = get_cpp_python_type(arg_type)

            if cpp_base_type in {"int", "float", "bool", "str", "String"}:
                cpp_type = f"{cpp_base_type}"
            else:
                pass_as = self.dependency_resolver.get_class_pass_as(arg_type)

                if pass_as == "pointer":
                    cpp_type = f"{cpp_base_type}*"
                else:
                    cpp_type = f"{cpp_base_type}&"

            cpp_args.append(f"{cpp_type} {arg_name}")

            self.dependency_resolver.insert_variable(
                arg_name, arg_type, self.current_module_name, "user", scope=self.scope
            )

            save_args.append({"arg_name": arg_name, "arg_type": arg_type})

        args_str = ", ".join(cpp_args)

        # Step 3: Generate body
        body_lines = []
        if func_name == "setup":
            body_lines.append(f"    Serial.begin({self.monitor_speed});")

        for stmt in node.body:
            print(f"visiting statement {stmt}")
            stmt_line = self.visit(stmt)
            if stmt_line:
                if isinstance(
                    stmt,
                    (
                        ast.Assign,
                        ast.Expr,
                        ast.Return,
                        ast.Call,
                        ast.Compare,
                        ast.BinOp,
                    ),
                ):
                    if not stmt_line.strip().endswith(";"):
                        stmt_line += ";"
                body_lines.append(f"    {stmt_line}")

        body_str = "\n".join(body_lines)

        # Step 4: Combine full function
        function_str = f"{return_cpp_type} {func_name}({args_str}) {{\n{body_str}\n}}"

        self.dependency_resolver._insert_method(
            func_name,
            None,
            self.current_module_name,
            "user",
            json.dumps(save_args),
            return_type,
        )

        self.scope = "global"
        return function_str

    def visit_Return(self, node):
        if node.value is None:
            return "return"
        return f"return {self.visit(node.value)}"

    def visit_AugAssign(self, node):
        line_code = ast.unparse(node)

        return f"{line_code}"

    def visit_Subscript(self, node):
        value_code = self.visit(node.value)
        value_type = self.type_analyzer.get_node_type(node.value)

        # --- Case 1: Standard Index like mylist[2] ---
        if isinstance(node.slice, ast.Constant):
            index_code = self.visit(node.slice)

            # Extract core type from list,str,dict,...
            if value_type.startswith("list"):
                # list,int,bool,float,str
                parts = value_type.split(",")
                elem_type = parts[1] if len(parts) > 1 else "auto"
                cpp_elem_type = get_cpp_python_type(elem_type)

                # If it's a literal list like [1,2,3][0]
                if isinstance(node.value, ast.List):
                    return f"PyList<{cpp_elem_type}>::from({{{', '.join(self.visit(e) for e in node.value.elts)}}})[{index_code}]"

                # Otherwise, variable/expression list
                return f"{value_code}[{index_code}]"

            elif value_type.startswith("dict"):
                # dict,str,int,...
                parts = value_type.split(",")
                val_type = parts[2] if len(parts) > 2 else "auto"
                cpp_val_type = get_cpp_python_type(val_type)
                return f"({value_code}).get({index_code})"

            elif value_type == "str":
                return f"PyString({value_code})[{index_code}]"

            else:
                # Fallback for unsupported types
                return f"{value_code}[{index_code}]"

        # --- Case 2: Slice like mylist[1:3] ---
        elif isinstance(node.slice, ast.Slice):
            lower = self.visit(node.slice.lower) if node.slice.lower else "0"
            upper = (
                self.visit(node.slice.upper)
                if node.slice.upper
                else f"{value_code}.size()"
            )

            if node.slice.step:
                raise NotImplementedError("Slicing with step is not supported yet.")

            if value_type.startswith("list") or value_type.startswith("PyList"):
                return f"{value_code}.slice({lower}, {upper})"
            elif value_type == "str":
                return f"PyString({value_code}).slice({lower}, {upper})"
            else:
                raise NotImplementedError(
                    f"Subscript slice not supported for type: {value_type}"
                )

        # --- Fallback (should rarely happen) ---
        return f"{value_code}[UNKNOWN]"

    def visit_While(self, node: ast.While):
        result = []

        condition = self.visit(node.test)
        result.append(f"while ({condition}) {{")

        for stmt in node.body:
            line = self.visit(stmt)
            if line:
                result.append(f"    {line};")

        result.append("}")

        # Python's while-else is rare; handle if needed
        if node.orelse:
            result.append("// else clause from Python's while-else:")
            result.append("if (/* no break detected */) {")
            for stmt in node.orelse:
                line = self.visit(stmt)
                if line:
                    result.append(f"    {line};")
            result.append("}")

        return "\n".join(result)

    def visit_JoinedStr(self, node: ast.JoinedStr):
        print("doing joined str")
        parts = []
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                self.visit(value.value)  # for type inference side effects
                expr_code = self.visit(value.value)
                expr_type = self.type_analyzer.get_node_type(value.value)
                expr_core_type = expr_type.split(",")[0]

                if expr_core_type == "str":
                    parts.append(expr_code)
                elif expr_core_type in ("int", "float"):
                    parts.append(f"String({expr_code})")
                elif expr_core_type in ("bool"):
                    parts.append(f"PyBool({expr_code}).to_string()")
                elif expr_core_type in ("list", "dict"):
                    parts.append(f"({expr_code}).to_string()")
                else:
                    # this is a custom class type
                    print_method = self.dependency_resolver.get_print_method_for_class(
                        expr_core_type
                    )

                    if print_method:
                        print(f"expr code is {expr_code}")
                        print(f"print method is {print_method}")
                        parts.append(print_method.format(expr_code))

                    else:
                        parts.append(f"{expr_core_type} instance")

            elif isinstance(value, ast.Constant):
                const_str = str(value.value).replace('"', '\\"')
                parts.append(f'"{const_str}"')

            elif isinstance(value, ast.Str):  # For Python < 3.8
                const_str = value.s.replace('"', '\\"')
                parts.append(f'"{const_str}"')

            else:
                raise NotImplementedError(
                    f"Unsupported f-string part: {ast.dump(value)}"
                )

        return f'concat_all({{{", ".join(parts)}}})'

    def _get_node_type(self, node):
        if isinstance(node, ast.Constant):
            return type(node.value).__name__

        elif isinstance(node, ast.List):
            element_type = self.type_analyzer._get_list_element_type(node.elts)
            return f"list,{element_type}"

        elif isinstance(node, ast.Name):
            # check scope
            # if inside function, check args first
            var_name = node.id
            if self.is_inside_loop:
                if var_name in self.loop_variables.keys():
                    return self.loop_variables[var_name]

            return self.dependency_resolver.get_variable_type(var_name, self.scope)

        elif isinstance(node, ast.Compare):
            # Comparisons always result in boolean
            return "bool"

        elif isinstance(node, ast.BoolOp):
            # and/or returns boolean
            return "bool"

        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            if isinstance(node.operand, ast.Constant):
                return type(-node.operand.value).__name__

        elif isinstance(node, ast.JoinedStr):
            return "str"

        elif isinstance(node, ast.Dict):
            keys = node.keys
            values = node.values

            for k, v in zip(keys, values):
                if not (isinstance(k, ast.Constant) and isinstance(v, ast.Constant)):
                    json_parts.append("/* unsupported */")
                    continue

                k_val = k.value
                v_val = v.value

                return f"dict,{type(k_val).__name__},{type(v_val).__name__}"

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                # Case: direct call like foo() or MyClass()
                method_name = node.func.id
                args_type = [self.type_analyzer.get_node_type(arg) for arg in node.args]

                if is_builtin_function(method_name):
                    return get_builtin_function_return_type(method_name, args_type)

                # Check if it's a class defined in the current module or imports
                if self.dependency_resolver.is_module_class(method_name):
                    return method_name  # class constructor

                # Otherwise it's a global function — resolve return type
                return self.dependency_resolver.get_global_function_return_type(
                    method_name, self.current_module_name
                )

            elif isinstance(node.func, ast.Attribute):
                method_name = node.func.attr
                base = node.func.value

                # Case 1: base is a function call (e.g., get_obj().foo())
                if isinstance(base, ast.Call):
                    base_type = self.type_analyzer.get_node_type(base).split(",")[0]
                    if base_type in BUILTIN_TYPES:
                        return get_python_builtin_class_method_type(
                            base_type, method_name
                        )
                    else:
                        return self.dependency_resolver.get_class_method_return_type(
                            base_type, method_name
                        )

                # Case 2: base is a Name (e.g., abc.foo())
                elif isinstance(base, ast.Name):
                    base_name = base.id

                    # Subcase 2a: base is an imported module
                    print(f"getting module name for alias {base_name}")
                    module_name = self.dependency_resolver.get_module_name_from_alias(
                        self.current_module_name, base_name
                    )
                    print(f"got module name {module_name}")
                    if module_name:
                        # 👇 This is the missing piece
                        # Check if the attribute is a class inside the imported module
                        print(f"checking if the method is a class")
                        print(f"checking {method_name} in {module_name}")
                        if self.dependency_resolver.is_module_class(
                            method_name, module_name=module_name
                        ):
                            return method_name  # class constructor call

                        # Otherwise it's a function in that module
                        return_type = (
                            self.dependency_resolver.get_module_call_return_type(
                                module_name, method_name
                            )
                        )
                        print(f"git return type {return_type} for {method_name}")

                        return return_type

                    # Subcase 2b: base is a variable → get its type
                    variable_type = self.dependency_resolver.get_variable_type(
                        base_name, self.scope
                    )
                    core_type = variable_type.split(",")[0]

                    if core_type in BUILTIN_TYPES:
                        return get_python_builtin_class_method_type(
                            core_type, method_name
                        )
                    else:
                        return self.dependency_resolver.get_class_method_return_type(
                            core_type, method_name
                        )

                # Case 3: base is a constant like "hello".upper()
                elif isinstance(base, ast.Constant):
                    const_type = self.type_analyzer.get_node_type(base)
                    return get_python_builtin_class_method_type(const_type, method_name)

                # Fallback
                else:
                    raise NotImplementedError(
                        f"Unsupported attribute base: {ast.dump(base)}"
                    )

        elif isinstance(node, ast.Subscript):
            value = node.value

            value_type = self.type_analyzer.get_node_type(value)

            value_type_split = value_type.split(",")
            core_type = value_type_split[0]

            if core_type == "str":
                # return str
                return "str"

            elif core_type == "list":
                element_type = value_type_split[1]
                if isinstance(node.slice, ast.Constant):
                    # user has called an index list[i]
                    # return self.dependency_resolver.get_list_element_type(value.id, self.scope)
                    # return self._get_list_element_type(value.elts)
                    if isinstance(value, ast.Name):
                        # this is a defined variable
                        return element_type
                        # return self.dependency_resolver.get_list_element_type(value.id, self.scope)
                    elif isinstance(value, ast.List):
                        return self._get_list_element_type(value.elts)
                else:
                    # this is slize
                    # list[i:j]
                    return value_type

            elif value_type == "dict":
                dict_info = self.dependency_resolver.get_dict_key_value_type(
                    value.id, self.scope
                )

                return dict_info["value_type"]

        elif isinstance(node, ast.BinOp):
            print("starting type extraction")
            left_type = self.type_analyzer.get_node_type(node.left)
            right_type = self.type_analyzer.get_node_type(node.right)

            print(f"left type is {left_type} and right type is {right_type}")

            if not left_type or not right_type:
                raise TypeError(f"BinaryOp missing operand types: {ast.dump(node)}")

            left_parts = left_type.split(",")
            right_parts = right_type.split(",")

            left_base = left_parts[0]
            right_base = right_parts[0]

            op = node.op

            # STR + STR → STR
            if left_base == right_base == "str":
                if isinstance(op, ast.Add):
                    return "str"
                raise TypeError(f"Unsupported binary op for str: {type(op).__name__}")

            # LIST + LIST → LIST,<element_type>
            if left_base == right_base == "list":
                if isinstance(op, ast.Add):
                    # Must also match element type
                    if left_parts[1:] == right_parts[1:]:
                        return left_type
                    else:
                        raise TypeError(
                            f"List element type mismatch: {left_type} + {right_type}"
                        )
                raise TypeError(f"Unsupported binary op for list: {type(op).__name__}")

            # DICT — not supported
            if "dict" in (left_base, right_base):
                raise TypeError(
                    f"Binary operations on dicts are not supported: {ast.dump(node)}"
                )

            # BOOL + BOOL
            if left_base == right_base == "bool":
                if isinstance(op, (ast.And, ast.Or, ast.BitAnd, ast.BitOr, ast.BitXor)):
                    return "bool"
                elif isinstance(op, (ast.Add, ast.Sub)):
                    return "int"
                else:
                    raise TypeError(
                        f"Unsupported binary op for bool: {type(op).__name__}"
                    )

            # INT/FLOAT logic
            allowed_numeric = {"int", "float"}
            if left_base in allowed_numeric and right_base in allowed_numeric:
                return "float" if "float" in (left_base, right_base) else "int"

            raise TypeError(
                f"Unsupported binary operation between {left_type} and {right_type}: {ast.dump(node)}"
            )

    def visit_Constant(self, node):
        value = node.value

        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'String("{escaped}")'
        return str(value)

    def _get_list_element_type(self, elements):
        for elt in elements:
            if not isinstance(elt, ast.Constant):
                raise NotImplementedError(
                    f"Only flat constant lists are supported. Found: {type(elt).__name__}"
                )

            py_val = elt.value

            if type(py_val) not in LIST_ALLOWED_TYPES:
                raise NotImplementedError(
                    f"Unsupported constant type in list: {type(py_val).__name__}"
                )

            return type(py_val).__name__

        return "auto"

    def visit_List(self, node):
        elements = node.elts
        element_exprs = [self.visit(elt) for elt in elements]

        # Infer element type from first element or fallback
        # py_element_type = self._get_list_element_type(elements)
        py_element_type = self.type_analyzer._get_list_element_type(elements)
        element_type = get_cpp_python_type(py_element_type) or "auto"

        arr_values = ", ".join(element_exprs)

        return f"PyList<{element_type}>::from({{{arr_values}}})"

    def is_constructor_call(self, node) -> bool:
        """
        Determine if the AST node represents a constructor-style call like `WiFiClient()` or `wifi.WebServer()`.
        Logs reasons why a node is or is not considered a constructor call.
        """
        if not isinstance(node, ast.Call):
            print("🚫 Node is not a function call.")
            return False

        # Case 1: Direct constructor like WiFiClient()
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            print(f"🔍 Found function call: {func_name}()")

            if is_builtin_function(func_name):
                print(
                    f"⚠️ {func_name} is a built-in function. Not treating as constructor."
                )
                return False

            if self.dependency_resolver.is_module_class(func_name):
                print(f"✅ {func_name} is a known class. Treating as constructor.")
                return True

            print(
                f"❓ {func_name} is not a built-in and not found in module class list. Not treating as constructor."
            )
            return False

        # Case 2: Attribute constructor like wifi.WebServer()
        elif isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value, ast.Name
        ):
            base = node.func.value
            method_name = node.func.attr
            base_name = base.id

            print(
                f"🔍 Found attribute-style constructor call: {base_name}.{method_name}()"
            )

            module_name = self.dependency_resolver.get_module_name_from_alias(
                self.current_module_name, base_name
            )
            print(f"📦 Alias {base_name} maps to module {module_name}")

            if module_name and self.dependency_resolver.is_module_class(
                method_name, module_name=module_name
            ):
                print(
                    f"✅ {method_name} is a class in module {module_name}. Treating as constructor."
                )
                return True
            else:
                print(
                    f"❌ {method_name} is not recognized as a class in module {module_name}."
                )
                return False

        print("🚫 Node.func is not a simple name or recognizable attribute-based call.")
        return False

    def visit_Assign(self, node):
        lhs_name = node.targets[0].id
        rhs_converted = self.visit(node.value)
        print(f"rhs converted is {rhs_converted}")
        print(f"node value is {node.value}")

        rhs_type = self.type_analyzer.get_node_type(node.value)
        print(f"var {lhs_name} is declared {rhs_type}")

        is_python_type = is_core_python_type(rhs_type)

        cpp_type = get_cpp_python_type(rhs_type)

        self.dependency_resolver.insert_variable(
            lhs_name, rhs_type, self.current_module_name, "user"
        )

        if is_python_type or cpp_type == "auto":
            return f"{cpp_type} {lhs_name} = {rhs_converted}"

        if self.is_constructor_call(node.value):
            class_name = node.value.func.attr
            is_reference = self.dependency_resolver.is_class_init_reference(class_name)
            construct_with_equal_to = (
                self.dependency_resolver.class_constructor_use_equal_to(class_name)
            )
            actual_cpp_type = self.dependency_resolver.get_actual_class_type(class_name)
            pass_as = self.dependency_resolver.get_class_pass_as(class_name)

            if actual_cpp_type:
                cpp_type = actual_cpp_type
            if is_reference:
                cpp_type = f"{cpp_type}&"

            elif pass_as == "pointer":
                cpp_type = f"{cpp_type}*"
            elif pass_as == "reference":
                cpp_type = f"{cpp_type}&"

            if construct_with_equal_to:
                return f"{cpp_type} {lhs_name} = {rhs_converted}"

            else:
                return f"{cpp_type} {lhs_name}{rhs_converted}"

        if not is_python_type:
            pass_as = self.dependency_resolver.get_class_pass_as(rhs_type)

            if pass_as == "pointer":
                cpp_type = f"{cpp_type}*"
            elif pass_as == "reference":
                cpp_type = f"{cpp_type}&"

        return f"{cpp_type} {lhs_name} = {rhs_converted}"


def parse_external_python_file(filepath):
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"{filepath} does not exist")

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    tree = ast.parse(code, filename=str(filepath))
    return tree


def extract_imported_modules_from_tree(tree, path_to_core_libs, input_files={}):
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name  # 'x.y.z'
                module_path = os.path.join(*module_name.split(".")) + ".py"

                if module_path in input_files:
                    print(f"🔗 Found internal import: {module_name}")
                    continue

                core_lib_path = os.path.join(path_to_core_libs, module_path)
                print(f"🧩 Trying core module: {module_name} at {core_lib_path}")
                try:
                    module = {
                        "name": module_name,
                        "alias": alias.asname,
                        "type": "core",
                        "module_tree": parse_external_python_file(core_lib_path),
                        "line_num": node.lineno,
                    }
                    modules.append(module)
                except Exception as core_err:
                    print(f"⚠️ Failed to load core module {module_name}: {core_err}")

    return modules


def main(
    commit_hash,
    sql_conn,
    input_files: dict,
    path_to_core_libs,
    platform,
    monitor_speed=115200,
):
    """
    input_files: {"file_name.py": "<py code>"}
    """
    try:
        print(f"🧠 [transpiler_main] called with {len(input_files)} file(s)")
        print(f"📦 core_lib path: {path_to_core_libs}")
        print(f"📄 files: {list(input_files.keys())}")

        input_trees = {}
        output = {}
        transpiled_code = {}
        dependencies = set()
        modules = []

        for k, v in input_files.items():
            print(f"\n🧾 Parsing file: {k}")
            try:
                tree = ast.parse(v)
                input_trees[k] = tree
            except Exception as parse_err:
                print(f"❌ Failed to parse {k}: {parse_err}")
                raise

            extracted_modules = extract_imported_modules_from_tree(
                tree, path_to_core_libs, input_files=input_files
            )
            modules += extracted_modules

        print(f"\n📚 Found {len(modules)} external/core modules")
        dr = DependencyResolver(
            commit_hash, sql_conn, platform, imported_modules=modules
        )
        print(f"🧮 Current transpilation ID: {dr.current_id}")

        for key, tree in input_trees.items():
            print(f"\n🛠️ Transpiling {key}")
            try:
                at = ArduinoTranspiler(key, tree, dr, monitor_speed)
                transpiled_code[key] = at.transpile()
                module_dependencies = at.get_dependencies()

                for dependency in module_dependencies:
                    dependencies.add(dependency)
                print(f"✅ {key} transpiled successfully")
            except Exception as transpile_err:
                print(f"❌ Transpilation failed for {key}: {transpile_err}")
                raise

        output["code"] = transpiled_code
        output["dependencies"] = list(dependencies)
        print(f"\n✅ Transpilation complete. Files: {list(transpiled_code.keys())}")
        # dr.delete_all_tables()
        return output

    except Exception as e:
        print(f"\n❌ [FATAL] transpiler_main crashed: {e}")
        import traceback

        traceback.print_exc()
        raise
