from pathlib import Path

IGNORE = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".streamlit",
    ".vscode",
    ".idea",
    "build",
    "dist",
    ".DS_Store"
}

IGNORE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".log",
    ".tmp"
}


def print_tree(path, prefix=""):
    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))

    items = [
        item for item in items
        if item.name not in IGNORE
        and item.suffix not in IGNORE_EXTENSIONS
    ]

    for index, item in enumerate(items):
        connector = "└── " if index == len(items)-1 else "├── "
        print(prefix + connector + item.name)

        if item.is_dir():
            extension = "    " if index == len(items)-1 else "│   "
            print_tree(item, prefix + extension)


print(Path(".").resolve().name)
print_tree(Path("."))