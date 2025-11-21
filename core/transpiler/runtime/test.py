import os
import sys

if len(sys.argv) < 2:
    print("Usage: python dump_tree.py <folder>")
    sys.exit(1)

ROOT = os.path.abspath(sys.argv[1])

if not os.path.exists(ROOT):
    print(f"Folder does not exist: {ROOT}")
    sys.exit(1)

for root, dirs, files in os.walk(ROOT):
    level = root.replace(ROOT, "").count(os.sep)
    indent = " " * 4 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = " " * 4 * (level + 1)
    for f in files:
        print(f"{subindent}{f}")
