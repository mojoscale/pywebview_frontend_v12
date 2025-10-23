"""
Robust completions module for PyWebView + Jedi.
- Accepts (code: str, line: int, column: int) where line/column are 0-based.
- Fast native-type completions for builtin types and variables assigned literals.
- Safe Jedi fallback for other completions.
"""

import sys
import threading
import time
from functools import wraps
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
import re
import traceback

# --------- Configuration ---------
# Max time for completions (seconds)
COMPLETION_TIMEOUT = 1.5
# Max number of Jedi completions we'll return
MAX_JEDI_COMPLETIONS = 200

# If running in a frozen app (Nuitka), base dir resolution:
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

CORE_STUBS_PATH = BASE_DIR / "transpiler" / "core_stubs"

# --------- Native types methods (your original list, kept concise) ---------
NATIVE_TYPES_METHODS = {
    "list": {
        "append": "Append object to the end of the list.",
        "clear": "Remove all items from list.",
        "copy": "Return a shallow copy of the list.",
        "count": "Return number of occurrences of value.",
        "extend": "Extend list by appending elements from the iterable.",
        "index": "Return first index of value.",
        "insert": "Insert object before index.",
        "pop": "Remove and return item at index (default last).",
        "remove": "Remove first occurrence of value.",
        "reverse": "Reverse *IN PLACE*.",
        "sort": "Sort the list in ascending order and return None.",
    },
    "str": {
        "capitalize": "Return a capitalized version of the string.",
        "casefold": "Return a version of the string suitable for caseless comparisons.",
        "center": "Return a centered string of length width.",
        "count": "Return the number of non-overlapping occurrences of substring.",
        "encode": "Encode the string using the codec registered for encoding.",
        "endswith": "Return True if the string ends with the specified suffix.",
        "find": "Return the lowest index in the string where substring is found.",
        "format": "Return a formatted version of the string.",
        "index": "Return the lowest index in the string where substring is found.",
        "isalnum": "Return True if all characters in the string are alphanumeric.",
        "isalpha": "Return True if all characters in the string are alphabetic.",
        "islower": "Return True if all cased characters in the string are lowercase.",
        "isupper": "Return True if all cased characters in the string are uppercase.",
        "join": "Return a string which is the concatenation of the strings.",
        "lower": "Return a copy of the string converted to lowercase.",
        "split": "Return a list of the substrings in the string.",
        "startswith": "Return True if the string starts with the specified prefix.",
        "strip": "Return a copy of the string with leading and trailing characters removed.",
        "upper": "Return a copy of the string converted to uppercase.",
    },
    "dict": {
        "clear": "Remove all items from the dictionary.",
        "copy": "Return a shallow copy of the dictionary.",
        "fromkeys": "Create a new dictionary with keys and values.",
        "get": "Return the value for key if key is in the dictionary.",
        "items": "Return a new view of the dictionary's items.",
        "keys": "Return a new view of the dictionary's keys.",
        "pop": "Remove specified key and return the corresponding value.",
        "popitem": "Remove and return a (key, value) pair from the dictionary.",
        "setdefault": "Return the value of the specified key.",
        "update": "Update the dictionary with the key/value pairs.",
        "values": "Return a new view of the dictionary's values.",
    },
    "set": {
        "add": "Add an element to the set.",
        "clear": "Remove all elements from the set.",
        "copy": "Return a shallow copy of the set.",
        "difference": "Return the difference of two or more sets.",
        "discard": "Remove an element from the set if it is a member.",
        "intersection": "Return the intersection of two sets.",
        "isdisjoint": "Return True if two sets have a null intersection.",
        "issubset": "Report whether another set contains this set.",
        "issuperset": "Report whether this set contains another set.",
        "pop": "Remove and return an arbitrary set element.",
        "remove": "Remove an element from the set.",
        "union": "Return the union of sets.",
        "update": "Update the set, adding elements from others.",
    },
    "tuple": {
        "count": "Return number of occurrences of value.",
        "index": "Return first index of value.",
    },
}


# --------- Utility: timeout decorator that returns a sentinel on timeout ---------
def timeout(seconds: float):
    """Timeout decorator returns None on timeout (does not raise)."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result_container = {"result": None, "exception": None}
            finished = threading.Event()

            def target():
                try:
                    result_container["result"] = func(*args, **kwargs)
                except Exception as e:
                    result_container["exception"] = e
                finally:
                    finished.set()

            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            if not finished.wait(seconds):
                # timed out
                return None
            if result_container["exception"]:
                # propagate exception to caller as None result so host app doesn't crash;
                # caller should check for None and handle gracefully.
                # We print traceback for debugging.
                print("[completions] Error in threaded operation:")
                traceback.print_exception(
                    type(result_container["exception"]),
                    result_container["exception"],
                    result_container["exception"].__traceback__,
                )
                return None
            return result_container["result"]

        return wrapper

    return decorator


# --------- Helpers to build LSP-like completion dicts ---------
def make_completion_item(
    label: str,
    kind: str,
    detail: str = "",
    documentation: str = "",
    insert_text: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "label": label,
        "kind": kind,
        "detail": detail or label,
        "documentation": documentation or "",
        "insertText": insert_text if insert_text is not None else label,
    }


# --------- Infer identifier before dot (works with partial attribute) ---------
IDENT_BEFORE_DOT_RE = re.compile(
    r"([A-Za-z_][\w]*)\.\w*$"
)  # captures name right before the last dot in the context
IDENT_EXACT_DOT_RE = re.compile(r"([A-Za-z_][\w]*)\.$")  # ends with dot


def _identifier_before_dot(line_text_up_to_cursor: str) -> Optional[str]:
    """
    Return the identifier directly left of the most-recent dot before the cursor.
    Simple and robust approach.
    """
    if not line_text_up_to_cursor:
        return None

    # Find the last dot position
    last_dot_pos = line_text_up_to_cursor.rfind(".")
    if last_dot_pos == -1:
        return None

    # Get text before the last dot
    text_before_dot = line_text_up_to_cursor[:last_dot_pos]

    # Extract the last contiguous identifier from the end
    # This handles cases like "obj.method().attribute" by taking "method" from "obj.method()"
    ident_match = re.search(r"([A-Za-z_][\w]*)\s*$", text_before_dot)
    if ident_match:
        return ident_match.group(1)

    return None


# --------- Try to infer native type from simple assignments earlier in the code ---------
ASSIGN_RE = re.compile(r"^([A-Za-z_][\w]*)\s*=\s*(.+)$")


def _infer_type_from_assignments(
    code_lines: List[str], target_var: str
) -> Optional[str]:
    """
    Scan earlier lines for assignments like `x = []`, `d = {}`, `s = '...'`, `t = (...)`, `x = dict()`, etc.
    Returns one of 'list', 'dict', 'set', 'tuple', 'str', or None.
    """
    # scan top-to-bottom to prefer newer assignments (later lines shadow earlier ones)
    for line in reversed(code_lines):
        if not line or line.strip().startswith("#"):
            continue
        m = ASSIGN_RE.match(line.strip())
        if not m:
            continue
        var, value = m.group(1), m.group(2).strip()
        if var != target_var:
            continue
        # quick literals detection
        if value.startswith("["):
            return "list"
        if value.startswith("{"):
            # {} is dict; {1,2} could be set but we assume dict for {} specifically.
            if value == "{}":
                return "dict"
            # if contains ':' it's dict literal
            if ":" in value:
                return "dict"
            # otherwise if set-like with commas and no colons -> 'set' but ambiguous
            # We'll assume set if it looks like {1,2} (contains digits or commas but no colon)
            if re.search(r"\d|'", value) and ":" not in value:
                # heuristics
                return "set"
            return "dict"
        if value.startswith("("):
            return "tuple"
        if value.startswith(("'", '"')):
            return "str"
        # constructor calls
        if re.match(r"list\s*\(", value):
            return "list"
        if re.match(r"dict\s*\(", value):
            return "dict"
        if re.match(r"set\s*\(", value):
            return "set"
        if re.match(r"tuple\s*\(", value):
            return "tuple"
        if re.match(r"str\s*\(", value):
            return "str"
    return None


# --------- Native completions generator (filters by partial suffix) ---------
def get_native_type_completions(
    native_type: str, existing: Set[str] = None, partial: str = ""
) -> List[Dict[str, Any]]:
    if existing is None:
        existing = set()
    methods = NATIVE_TYPES_METHODS.get(native_type.lower(), {})
    results = []
    partial = (partial or "").lower()
    for name, doc in methods.items():
        if name in existing:
            continue
        if partial and not name.lower().startswith(partial):
            continue
        results.append(
            make_completion_item(
                name,
                "method",
                detail=f"{native_type}.{name}",
                documentation=doc,
                insert_text=name,
            )
        )
    return results


# --------- Jedi setup (safe) ---------
def _setup_jedi_environment_once():
    """
    Try to create a safe InterpreterEnvironment for Jedi.
    Return a tuple (environment, error_message_or_None).
    """
    try:
        import jedi
        from jedi.api.environment import InterpreterEnvironment

        # best-effort patch typeshed to avoid missing path crashes
        try:
            from jedi.inference.gradual import typeshed

            orig = getattr(typeshed, "_get_typeshed_directories", None)
            if orig:

                def patched(v):
                    try:
                        dirs = orig(v)
                    except Exception:
                        return []
                    valid = []
                    for d in dirs:
                        try:
                            p = Path(str(d))
                            if p.exists():
                                valid.append(d)
                        except Exception:
                            continue
                    return valid

                typeshed._get_typeshed_directories = patched
        except Exception:
            # non-fatal
            pass

        env = InterpreterEnvironment()
        return env, None
    except Exception as e:
        return None, str(e)


_JEDI_ENV_CACHE = None
_JEDI_ENV_ERROR = None


def _get_jedi_environment():
    global _JEDI_ENV_CACHE, _JEDI_ENV_ERROR
    if _JEDI_ENV_CACHE is None and _JEDI_ENV_ERROR is None:
        env, err = _setup_jedi_environment_once()
        _JEDI_ENV_CACHE = env
        _JEDI_ENV_ERROR = err
    return _JEDI_ENV_CACHE, _JEDI_ENV_ERROR


def _create_jedi_script(code: str, stub_path: Optional[str] = None):
    try:
        import jedi

        env, env_err = _get_jedi_environment()
        if env_err:
            raise ImportError(f"Jedi environment error: {env_err}")
        # Add stubs path if available and exists
        added = []
        if stub_path:
            sp = str(Path(stub_path).resolve())
            if sp not in sys.path:
                try:
                    sys.path.insert(0, sp)
                    added.append(sp)
                except Exception:
                    pass
        elif CORE_STUBS_PATH.exists():
            sp = str(CORE_STUBS_PATH.resolve())
            if sp not in sys.path:
                try:
                    sys.path.insert(0, sp)
                    added.append(sp)
                except Exception:
                    pass

        # Create project with added sys path to improve completions
        project = None
        try:
            project = jedi.Project(path=Path.cwd(), added_sys_path=added)
        except Exception:
            # fallback: simple script without project
            project = None

        # Jedi expects 1-based line numbers later on; we'll convert when calling .complete
        script = jedi.Script(code, path="script.py", project=project, environment=env)
        return script
    except Exception as e:
        print("[completions] Jedi script creation failed:", e)
        return None


# --------- Map jedi types to simpler kinds ---------
def _map_completion_kind(jedi_type: str) -> str:
    type_map = {
        "class": "class",
        "function": "function",
        "method": "method",
        "module": "module",
        "instance": "variable",
        "statement": "variable",
        "param": "variable",
        "property": "property",
    }
    return type_map.get(jedi_type, "variable")


def _get_docstring_safe(c):
    try:
        return c.docstring() or ""
    except Exception:
        return ""


# --------- Public API: get_completions (unified, robust) ---------
@timeout(COMPLETION_TIMEOUT)
def get_python_completions(
    code: str, line: int, column: int, stub_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Unified completions API.
    - code: full document text
    - line, column: 0-based cursor position
    - returns list of completion items (dict)
    """
    try:
        # defensive normalization
        if code is None:
            return []
        try:
            line = int(line)
            column = int(column)
        except Exception:
            return []

        lines = code.splitlines()
        # ensure line is in bounds
        if line < 0:
            line = 0

        # If line index is past last line, use last line
        if line >= len(lines):
            # allow completion at virtual end of file
            current_line = lines[-1] if lines else ""
            # but set column to end
            column = len(current_line)
            line = len(lines) - 1 if lines else 0
        else:
            current_line = lines[line]

        # clamp column
        if column < 0:
            column = 0
        if column > len(current_line):
            column = len(current_line)

        context_up_to_cursor = current_line[:column]

        # 1) Try quick native-type detection: identifier before dot
        identifier = _identifier_before_dot(context_up_to_cursor)
        partial_after_dot = ""
        # extract partial token after dot (if any)
        # e.g. "dict.ite" -> partial_after_dot = "ite"
        partial_match = re.search(r"\.([\w]*)$", context_up_to_cursor)
        if partial_match:
            partial_after_dot = partial_match.group(1) or ""

        if identifier:
            # If identifier is a builtin type name
            lower_id = identifier.lower()
            if lower_id in NATIVE_TYPES_METHODS:
                # return native completions directly filtered by partial
                items = get_native_type_completions(
                    lower_id, existing=set(), partial=partial_after_dot
                )
                # If we have results, return early (fast path)
                if items:
                    return items

            # If identifier is a variable, try infer type from assignments
            inferred = _infer_type_from_assignments(lines[: line + 1], identifier)
            if inferred:
                items = get_native_type_completions(
                    inferred, existing=set(), partial=partial_after_dot
                )
                if items:
                    return items

        # 2) If not native or native returned nothing, fallback to Jedi (safe)
        script = _create_jedi_script(code, stub_path)
        if script is None:
            # last-resort fallback: small keyword list
            return _get_basic_fallback_items(partial_after_dot)

        # jedi expects 1-based line numbers
        jedi_line = line + 1
        try:
            completions = script.complete(jedi_line, column) or []
        except Exception as e:
            print("[completions] Jedi .complete() failed:", e)
            completions = []

        result = []
        for c in completions[:MAX_JEDI_COMPLETIONS]:
            try:
                result.append(
                    make_completion_item(
                        label=c.name,
                        kind=_map_completion_kind(c.type),
                        detail=(c.description or c.name),
                        documentation=_get_docstring_safe(c),
                        insert_text=c.name,
                    )
                )
            except Exception:
                continue

        if not result:
            return _get_basic_fallback_items(partial_after_dot)

        return result

    except Exception as e:
        print("[completions] Unexpected error:", e)
        traceback.print_exc()
        return []


# --------- Basic fallback keyword/builtin completions (used when Jedi unavailable) ---------
def _get_basic_fallback_items(partial: str = "") -> List[Dict[str, Any]]:
    keywords = [
        "and",
        "as",
        "assert",
        "break",
        "class",
        "continue",
        "def",
        "del",
        "elif",
        "else",
        "except",
        "False",
        "finally",
        "for",
        "from",
        "global",
        "if",
        "import",
        "in",
        "is",
        "lambda",
        "None",
        "nonlocal",
        "not",
        "or",
        "pass",
        "raise",
        "return",
        "True",
        "try",
        "while",
        "with",
        "yield",
    ]
    builtins = [
        "abs",
        "all",
        "any",
        "bin",
        "bool",
        "bytes",
        "chr",
        "dict",
        "dir",
        "enumerate",
        "filter",
        "float",
        "format",
        "help",
        "int",
        "len",
        "list",
        "map",
        "max",
        "min",
        "open",
        "ord",
        "pow",
        "print",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "sorted",
        "str",
        "sum",
        "tuple",
        "type",
        "zip",
    ]
    items = []
    partial = (partial or "").lower()
    for w in keywords:
        if partial and not w.startswith(partial):
            continue
        items.append(
            make_completion_item(
                w,
                "keyword",
                detail="Python keyword",
                documentation="Python keyword",
                insert_text=w,
            )
        )
    for b in builtins:
        if partial and not b.startswith(partial):
            continue
        items.append(
            make_completion_item(
                b,
                "function",
                detail="built-in",
                documentation="Built-in function or type",
                insert_text=b,
            )
        )
    return items


# --------- Convenience debug function (prints context) ---------
def debug_completion_context(code: str, line: int, column: int):
    try:
        lines = code.splitlines()
        print("=== Completion Debug ===")
        print(f"Cursor (0-based): line={line}, column={column}")
        if 0 <= line < len(lines):
            current = lines[line]
            print("Current line:", repr(current))
            ctx = current[:column]
            print("Context up to cursor:", repr(ctx))
            print("Identifier before dot:", _identifier_before_dot(ctx))
            pm = re.search(r"\.([\w]*)$", ctx)
            print("Partial after dot:", pm.group(1) if pm else "")
        else:
            print("Line out of range. Total lines:", len(lines))
        print("========================")
    except Exception:
        pass


# --------- Small test harness ---------
def _test():
    tests = [
        ("x = [1,2,3]\nx.", 1, 2),
        ("s = 'hello'\ns.", 1, 2),
        ("d = {}\nd.", 1, 2),
        ("t = (1,2)\nt.", 1, 2),
        ("dict.it", 0, len("dict.it")),  # partial builtin
        ("mydict = {}\nmydict.it", 1, len("mydict.it")),
        (
            "unknown_obj.",
            0,
            len("unknown_obj."),
        ),  # should fallback to keywords / jedi (maybe empty)
    ]
    for code, l, c in tests:
        print("\n--- Test:", repr(code), "cursor", l, c)
        debug_completion_context(code, l, c)
        comps = get_completions(code, l, c)
        if comps is None:
            print("Timed out or error -> None returned")
            continue
        print("Found", len(comps), "completions (top 10):")
        for item in comps[:10]:
            print(f" - {item['label']} ({item['kind']}) : {item.get('detail','')}")


if __name__ == "__main__":
    _test()
