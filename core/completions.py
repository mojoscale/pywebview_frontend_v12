import sys
from pathlib import Path
from typing import List, Dict, Any, Set
import os
import signal
from functools import wraps
import threading
import time


# Timeout decorator to prevent freezing
def timeout(seconds=2):
    """Timeout decorator to prevent freezing."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    result[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)

            if thread.is_alive():
                raise TimeoutError(
                    f"Function {func.__name__} timed out after {seconds} seconds"
                )

            if isinstance(result[0], Exception):
                raise result[0]

            return result[0]

        return wrapper

    return decorator


# Setup Jedi environment IMMEDIATELY at module load
def _setup_jedi_environment():
    """Setup Jedi to work in packaged Nuitka environments using InterpreterEnvironment"""
    try:
        import jedi
        from jedi.api.environment import InterpreterEnvironment

        _patch_jedi_typeshed_paths()

        environment = InterpreterEnvironment()

        import jedi.api.environment as jedi_env

        original_get_default = jedi_env.get_default_environment
        jedi_env.get_default_environment = lambda: environment
        jedi_env._cached_default_environment = environment

        if hasattr(jedi_env, "get_default_project"):
            jedi_env._default_environment = environment

        print("[Jedi] Environment initialized with InterpreterEnvironment")
        return environment

    except ImportError as e:
        print(f"[Jedi] Failed to import required Jedi modules: {e}")
        return None
    except Exception as e:
        print(f"[Jedi] Error setting up environment: {e}")
        import traceback

        traceback.print_exc()
        return None


def _patch_jedi_typeshed_paths():
    """Patch Jedi's typeshed path detection to handle packaged environments"""
    try:
        from jedi.inference.gradual import typeshed

        original_get_typeshed_dirs = typeshed._get_typeshed_directories

        def patched_get_typeshed_directories(version_info):
            """Return typeshed directories, handling missing paths gracefully"""
            try:
                dirs = original_get_typeshed_dirs(version_info)
                valid_dirs = []
                for d in dirs:
                    try:
                        d_path = Path(str(d))
                        if d_path.exists():
                            valid_dirs.append(d)
                    except (TypeError, ValueError):
                        continue
                return valid_dirs
            except (FileNotFoundError, OSError):
                print("[Jedi] Typeshed directories not found, using fallback")
                return []

        typeshed._get_typeshed_directories = patched_get_typeshed_directories
        print("[Jedi] Typeshed path patching applied")

    except (ImportError, AttributeError) as e:
        print(f"[Jedi] Could not patch typeshed paths: {e}")


JEDI_ENVIRONMENT = _setup_jedi_environment()

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

CORE_STUBS_PATH = BASE_DIR / "transpiler" / "core_stubs"


# Native type method definitions
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
        "expandtabs": "Return a copy with tabs expanded to multiples of tabsize.",
        "find": "Return the lowest index in the string where substring is found.",
        "format": "Return a formatted version of the string.",
        "format_map": "Return a formatted version of the string using a mapping.",
        "index": "Return the lowest index in the string where substring is found.",
        "isalnum": "Return True if all characters in the string are alphanumeric.",
        "isalpha": "Return True if all characters in the string are alphabetic.",
        "isascii": "Return True if all characters in the string are ASCII.",
        "isdecimal": "Return True if the string is a decimal string.",
        "isdigit": "Return True if all characters in the string are digits.",
        "isidentifier": "Return True if the string is a valid Python identifier.",
        "islower": "Return True if all cased characters in the string are lowercase.",
        "isnumeric": "Return True if all characters in the string are numeric.",
        "isprintable": "Return True if all characters in the string are printable.",
        "isspace": "Return True if all characters in the string are whitespace.",
        "istitle": "Return True if the string is a titlecased string.",
        "isupper": "Return True if all cased characters in the string are uppercase.",
        "join": "Return a string which is the concatenation of the strings.",
        "ljust": "Return the string left justified in a string of length width.",
        "lower": "Return a copy of the string converted to lowercase.",
        "lstrip": "Return a copy of the string with leading characters removed.",
        "maketrans": "Return a translation table usable for str.translate().",
        "partition": "Partition the string into three parts using the separator.",
        "replace": "Return a copy with all occurrences of substring replaced.",
        "rfind": "Return the highest index in the string where substring is found.",
        "rindex": "Return the highest index in the string where substring is found.",
        "rjust": "Return the string right justified in a string of length width.",
        "rpartition": "Partition the string into three parts using the separator.",
        "rsplit": "Return a list of the substrings in the string.",
        "rstrip": "Return a copy of the string with trailing characters removed.",
        "split": "Return a list of the substrings in the string.",
        "splitlines": "Return a list of the lines in the string, breaking at newlines.",
        "startswith": "Return True if the string starts with the specified prefix.",
        "strip": "Return a copy of the string with leading and trailing characters removed.",
        "swapcase": "Return a copy of the string with uppercase characters converted to lowercase.",
        "title": "Return a titlecased version of the string.",
        "translate": "Replace each character mapped to itself.",
        "upper": "Return a copy of the string converted to uppercase.",
        "zfill": "Pad a numeric string with zeros on the left.",
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
        "difference_update": "Remove all elements from this set that are also in others.",
        "discard": "Remove an element from the set if it is a member.",
        "intersection": "Return the intersection of two sets.",
        "intersection_update": "Update the set, keeping only elements found in it and others.",
        "isdisjoint": "Return True if two sets have a null intersection.",
        "issubset": "Report whether another set contains this set.",
        "issuperset": "Report whether this set contains another set.",
        "pop": "Remove and return an arbitrary set element.",
        "remove": "Remove an element from the set.",
        "symmetric_difference": "Return the symmetric difference of two sets.",
        "symmetric_difference_update": "Update the set, keeping only elements found in either set.",
        "union": "Return the union of sets.",
        "update": "Update the set, adding elements from others.",
    },
    "tuple": {
        "count": "Return number of occurrences of value.",
        "index": "Return first index of value.",
    },
}


def _infer_native_type(code: str, line: int, column: int) -> str:
    """
    Infer if we're completing a native type method.
    Returns the type name ('list', 'str', 'dict', etc.) or None.
    """
    try:
        lines = code.split("\n")
        if line >= len(lines):
            return None

        current_line = lines[line]
        if column > 0:
            # Get the part before cursor
            before_cursor = current_line[:column]

            # Check if ends with dot (method completion)
            if not before_cursor.rstrip().endswith("."):
                return None

            # Remove the dot and get the identifier
            prefix = before_cursor.rstrip()[:-1]

            # Simple heuristic: look at variable assignments in the code
            for scan_line in lines[: line + 1]:
                # Match simple assignments like x = []
                if (
                    "= [" in scan_line
                    and scan_line.split("= [")[0].strip().split()[-1] in prefix
                ):
                    return "list"
                if (
                    "= {" in scan_line
                    and scan_line.split("= {")[0].strip().split()[-1] in prefix
                ):
                    return "dict"
                if "= '" in scan_line or '= "' in scan_line:
                    if scan_line.split("=")[0].strip().split()[-1] in prefix:
                        return "str"
                if (
                    "= (" in scan_line
                    and scan_line.split("= (")[0].strip().split()[-1] in prefix
                ):
                    return "tuple"

    except Exception:
        pass

    return None


def _map_completion_kind(jedi_type: str) -> str:
    """Map Jedi type to completion kind."""
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


def _get_docstring(completion) -> str:
    """Safely get docstring from completion."""
    try:
        docstring = completion.docstring()
        return docstring if docstring else ""
    except Exception:
        return ""


def _safe_get_completions(script, line: int, column: int):
    """Safely get completions with additional error handling."""
    try:
        completions = script.complete(line, column)
        return completions
    except (AttributeError, KeyError, TypeError) as e:
        print(f"[Jedi] Safe completion fallback for native type: {e}")
        return []
    except Exception as e:
        print(f"[Jedi] Unexpected error in safe completion: {e}")
        return []


def _create_safe_jedi_script(code: str, stub_path: str = None):
    """Create Jedi script with safe configuration."""
    try:
        import jedi
        from jedi.api.environment import InterpreterEnvironment

        if stub_path is None:
            stub_path = str(CORE_STUBS_PATH)
        else:
            stub_path = str(Path(stub_path).resolve())

        if stub_path not in sys.path:
            sys.path.insert(0, stub_path)

        environment = InterpreterEnvironment()

        project = jedi.Project(
            path=Path.cwd(),
            added_sys_path=[stub_path] if stub_path else [],
            safe=True,
        )

        script = jedi.Script(
            code, path="script.py", project=project, environment=environment
        )

        return script

    except Exception as e:
        print(f"[Jedi] Error creating script: {e}")
        return None


@timeout(2)
def get_python_completions(
    code: str, line: int, column: int, stub_path: str = None
) -> List[Dict[str, Any]]:
    """
    Get Python completions using Jedi with InterpreterEnvironment.
    Works in both development and Nuitka packaged environments.
    """
    try:
        line = int(line) + 1
        column = int(column)

        script = _create_safe_jedi_script(code, stub_path)
        if script is None:
            return []

        completions = _safe_get_completions(script, line, column)

        if not completions:
            return []

        result = []
        for c in completions:
            try:
                result.append(
                    {
                        "label": c.name,
                        "kind": _map_completion_kind(c.type),
                        "detail": c.description or c.name,
                        "documentation": _get_docstring(c),
                        "insertText": c.name,
                    }
                )
            except Exception as e:
                print(
                    f"[Jedi] Error processing completion '{c.name if hasattr(c, 'name') else 'unknown'}': {e}"
                )
                continue

        return result

    except TimeoutError as e:
        print(f"[Jedi] Completion timeout: {e}")
        return []
    except ImportError as e:
        print(f"[Jedi] Import error: {e}")
        return []
    except Exception as e:
        print(f"[Jedi] Completion error: {type(e).__name__}: {e}")
        return []


def get_native_type_completions(
    native_type: str, existing: Set[str] = None
) -> List[Dict[str, Any]]:
    """
    Get completions for native types (list, str, dict, set, tuple).
    Supplements or replaces Jedi results.
    """
    if existing is None:
        existing = set()

    methods = NATIVE_TYPES_METHODS.get(native_type.lower(), {})
    result = []

    for method_name, documentation in methods.items():
        # Avoid duplicates with Jedi results
        if method_name not in existing:
            result.append(
                {
                    "label": method_name,
                    "kind": "method",
                    "detail": f"{native_type}.{method_name}",
                    "documentation": documentation,
                    "insertText": method_name,
                }
            )

    return result


def get_completions_fallback(
    code: str, line: int, column: int, stub_path: str = None
) -> List[Dict[str, Any]]:
    """
    Enhanced fallback completions when Jedi fails.
    Returns Python keywords, built-in functions, and context-aware suggestions.
    """
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

    context_suggestions = _analyze_context(code, line, column)

    all_items = keywords + builtins + context_suggestions

    result = []
    for item in all_items:
        if item in keywords:
            kind = "keyword"
            detail = "Python keyword"
        elif item in builtins:
            kind = "function"
            detail = "built-in function"
        else:
            kind = "variable"
            detail = "suggestion"

        result.append(
            {
                "label": item,
                "kind": kind,
                "detail": detail,
                "documentation": f"Python {detail}",
                "insertText": item,
            }
        )

    return result


def _analyze_context(code: str, line: int, column: int) -> List[str]:
    """Analyze code context to provide better fallback suggestions."""
    suggestions = []

    try:
        lines = code.split("\n")
        if line < len(lines):
            current_line = lines[line]

            if column > 0 and current_line[:column].rstrip().endswith("."):
                prefix = current_line[:column].rstrip()[:-1]

                if any(name in prefix for name in ["list", "arr", "array", "items"]):
                    suggestions.extend(list(NATIVE_TYPES_METHODS["list"].keys()))
                elif any(name in prefix for name in ["str", "string", "text", "msg"]):
                    suggestions.extend(list(NATIVE_TYPES_METHODS["str"].keys()))
                elif any(name in prefix for name in ["dict", "dictionary", "map"]):
                    suggestions.extend(list(NATIVE_TYPES_METHODS["dict"].keys()))
                elif any(name in prefix for name in ["file", "f", "fp"]):
                    suggestions.extend(
                        [
                            "read",
                            "readline",
                            "readlines",
                            "write",
                            "writelines",
                            "seek",
                            "tell",
                            "close",
                            "flush",
                        ]
                    )

    except Exception:
        pass

    return suggestions


def get_completions_robust(
    code: str, line: int, column: int, stub_path: str = None
) -> List[Dict[str, Any]]:
    """
    Robust completion function that intelligently handles native types.
    This is the recommended entry point for your application.
    """
    try:
        line = int(line)
        column = int(column)

        # Check if we're completing a native type
        native_type = _infer_native_type(code, line, column)

        # Try Jedi first
        completions = get_python_completions(code, line, column, stub_path)
        existing_labels = {c["label"] for c in completions}

        # Supplement with native type methods
        if native_type and native_type in NATIVE_TYPES_METHODS:
            print(f"[Completions] Detected native type: {native_type}")
            native_completions = get_native_type_completions(
                native_type, existing_labels
            )
            completions.extend(native_completions)
            print(
                f"[Completions] Total: {len(completions)} (Jedi: {len(completions) - len(native_completions)}, Native: {len(native_completions)})"
            )
            return completions

        # If Jedi returned results, use them
        if completions:
            print(f"[Completions] Returned {len(completions)} completions from Jedi")
            return completions

        # Fall back to basic completions
        print("[Completions] Using enhanced fallback")
        return get_completions_fallback(code, line, column, stub_path)

    except TimeoutError as e:
        print(f"[Completions] Timeout: {e}")
        return get_completions_fallback(code, line, column, stub_path)
    except Exception as e:
        print(f"[Completions] Error: {e}")
        return get_completions_fallback(code, line, column, stub_path)


def debug_completion_context(code: str, line: int, column: int):
    """Debug function to understand completion context."""
    print(f"\n=== Completion Debug ===")
    print(f"Line: {line}, Column: {column}")
    lines = code.split("\n")
    if line < len(lines):
        current_line = lines[line]
        print(f"Current line: '{current_line}'")
        if column <= len(current_line):
            context = current_line[:column]
            print(f"Context: '{context}'")
            print(f"Ends with dot: {context.rstrip().endswith('.')}")
            detected_type = _infer_native_type(code, line, column)
            print(f"Detected type: {detected_type}")
    print("======================\n")


def test_completions():
    """Test completions with various scenarios."""
    test_cases = [
        ("x = [1, 2, 3]\nx.", 1, 2),  # List completion
        ("s = 'hello'\ns.", 1, 2),  # String completion
        ("d = {}\nd.", 1, 2),  # Dict completion
        ("t = (1, 2)\nt.", 1, 2),  # Tuple completion
    ]

    for code, line, column in test_cases:
        print(f"\nTesting: {code!r} at line {line}, column {column}")
        debug_completion_context(code, line, column)
        try:
            completions = get_completions_robust(code, line, column)
            print(f"Found {len(completions)} completions")
            for comp in completions[:10]:
                print(
                    f"  - {comp['label']} ({comp['kind']}): {comp['documentation'][:50]}"
                )
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    test_completions()
