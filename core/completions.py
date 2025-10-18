import sys
from pathlib import Path
from typing import List, Dict, Any
import os
import jedi


def fix_jedi_paths():
    """Fix Jedi paths for packaged applications"""
    if getattr(sys, "frozen", False):
        try:
            # Use InterpreterEnvironment which works entirely in-process
            from jedi.api.environment import InterpreterEnvironment

            # Create environment that uses current interpreter without external calls
            environment = InterpreterEnvironment()

            # Completely override the environment system
            import jedi.api.environment

            jedi.api.environment.get_default_environment = lambda: environment
            jedi.api.environment._cached_default_environment = environment

            # Also patch any other environment getters
            if hasattr(jedi, "Script"):
                original_init = jedi.Script.__init__

                def patched_init(self, code, *args, **kwargs):
                    kwargs["environment"] = environment
                    return original_init(self, code, *args, **kwargs)

                jedi.Script.__init__ = patched_init

        except Exception as e:
            print(f"Jedi environment setup warning: {e}")


# Call this at the start of your application
fix_jedi_paths()

# Setup paths for stubs
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

CORE_STUBS_PATH = BASE_DIR / "transpiler" / "core_stubs"


def get_completions(
    code: str, line: int, column: int, stub_path: str = None
) -> List[Dict[str, Any]]:
    """
    Get completions that work in both development and packaged Nuitka environments.
    """
    try:
        # Convert line and column to integers to handle string inputs
        line = int(line)
        column = int(column)

        if stub_path is None:
            stub_path = str(CORE_STUBS_PATH)

        stub_path = str(Path(stub_path).resolve())

        # Enhanced sys.path handling for packaged apps
        extended_sys_path = _get_extended_sys_path(stub_path)

        # Create project with proper environment detection
        project = _create_jedi_project(extended_sys_path)

        # Create script with error handling
        script = jedi.Script(code, path="script.py", project=project)
        completions = script.complete(
            line + 1, column
        )  # Jedi uses 1-based line numbers

        return [
            {
                "label": c.name,
                "kind": _map_completion_kind(c.type),
                "detail": c.description or c.name,
                "documentation": _get_docstring(c),
                "insertText": c.name,
            }
            for c in completions
        ]

    except Exception as e:
        print(f"Completion error: {e}")
        return []


def _get_extended_sys_path(stub_path: str) -> List[str]:
    """Get extended sys.path that works in packaged environments."""
    extended_sys_path = []

    # Add stub path first
    if stub_path not in sys.path:
        extended_sys_path.append(stub_path)

    # Add current sys.path
    extended_sys_path.extend(sys.path)

    # In packaged apps, we need to ensure essential paths are included
    if getattr(sys, "frozen", False):
        # Add the directory containing the executable
        exe_dir = str(Path(sys.executable).parent)
        if exe_dir not in extended_sys_path:
            extended_sys_path.insert(0, exe_dir)

        # Add lib directory if it exists
        lib_dir = str(Path(sys.executable).parent / "lib")
        if os.path.exists(lib_dir) and lib_dir not in extended_sys_path:
            extended_sys_path.insert(0, lib_dir)

    return extended_sys_path


def _create_jedi_project(extended_sys_path: List[str]):
    """Create Jedi project with proper configuration."""
    try:
        # Try with explicit sys_path first
        return jedi.Project(path=Path.cwd(), sys_path=extended_sys_path)
    except Exception as e:
        print(f"Project creation with sys_path failed: {e}")
        # Fallback to simple project
        return jedi.Project(path=Path.cwd())


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
    except:
        return ""


# Alternative implementation for Nuitka packaged apps
def get_completions_packaged(
    code: str, line: int, column: int, stub_path: str = None
) -> List[Dict[str, Any]]:
    """
    Alternative implementation specifically for Nuitka packaged apps.
    """
    try:
        # Convert line and column to integers
        line = int(line)
        column = int(column)

        if stub_path is None:
            stub_path = str(CORE_STUBS_PATH)

        # For packaged apps, we need to handle the environment differently
        import jedi

        # Set up environment paths
        environment = _setup_packaged_environment(stub_path)

        # Use Jedi with the custom environment
        script = jedi.Script(code, path="completion.py", environment=environment)

        completions = script.complete(
            line + 1, column
        )  # Jedi uses 1-based line numbers

        return [
            {
                "label": c.name,
                "kind": _map_completion_kind(c.type),
                "detail": getattr(c, "description", c.name),
                "documentation": _get_docstring(c),
                "insertText": c.name,
            }
            for c in completions
        ]

    except Exception as e:
        print(f"Packaged completion error: {e}")
        return []


def _setup_packaged_environment(stub_path: str):
    """Set up environment for packaged apps."""
    import jedi

    # Get the default environment
    environment = jedi.get_default_environment()

    # Add stub path to Python path
    if stub_path not in sys.path:
        sys.path.insert(0, stub_path)

    return environment


# Main function that auto-detects environment
def get_python_completions(
    code: str, line: int, column: int, stub_path: str = None
) -> List[Dict[str, Any]]:
    """
    Main completion function that works in both environments.
    """
    # Convert line and column to integers
    line = int(line)
    column = int(column)

    if getattr(sys, "frozen", False):
        # Use packaged version
        return get_completions_packaged(code, line, column, stub_path)
    else:
        # Use development version
        return get_completions(code, line, column, stub_path)


# Fallback for when Jedi completely fails
def get_completions_fallback(
    code: str, line: int, column: int, stub_path: str = None
) -> List[Dict[str, Any]]:
    """Simple fallback completions."""
    # Convert line and column to integers (though not used in fallback)
    line = int(line)
    column = int(column)

    # Basic Python keywords and builtins
    basics = [
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

    return [
        {
            "label": item,
            "kind": "keyword"
            if item
            in [
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
            else "function",
            "detail": "keyword"
            if item
            in [
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
            else "built-in",
            "documentation": f"Python {'keyword' if item in ['and', 'as', 'assert'] else 'built-in function'}",
            "insertText": item,
        }
        for item in basics
    ]


# Robust wrapper that tries multiple approaches
def get_completions_robust(
    code: str, line: int, column: int, stub_path: str = None
) -> List[Dict[str, Any]]:
    """
    Robust completion function that tries multiple approaches.
    """
    try:
        # Convert line and column to integers
        line = int(line)
        column = int(column)

        # First try the main approach
        completions = get_python_completions(code, line, column, stub_path)
        if completions:
            return completions

        # If main approach fails, try fallback
        return get_completions_fallback(code, line, column, stub_path)

    except Exception as e:
        print(f"Robust completion error: {e}")
        # Final fallback
        return get_completions_fallback(code, line, column, stub_path)
