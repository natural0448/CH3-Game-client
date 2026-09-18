"""Check the client-only file/document/index mapping and documented signatures."""
import ast
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".venv", "__pycache__", ".git", "docs"}


def client_files():
    """Enumerate only maintained client files, never the sibling server."""
    result = []
    for directory, folders, files in os.walk(ROOT):
        folders[:] = [name for name in folders if name not in EXCLUDED]
        for name in files:
            if name.endswith((".pyc", ".pyo", ".log")):
                continue
            result.append((Path(directory) / name).relative_to(ROOT))
    return sorted(result)


def signatures(tree, prefix=""):
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            yield from signatures(node, prefix + node.name + ".")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = prefix + node.name
            yield name + "(" + ast.unparse(node.args) + ")"
            yield from signatures(node, name + ".")


def main():
    routing = ROOT / "docs" / "client-routing"
    index = (routing / "README.md").read_text(encoding="utf-8")
    files = client_files()
    expected = {path.as_posix() + ".md" for path in files}
    actual = {path.relative_to(routing / "files").as_posix()
              for path in (routing / "files").rglob("*.md")}
    errors = ["missing: " + name for name in sorted(expected - actual)]
    errors += ["orphan: " + name for name in sorted(actual - expected)]
    for path in files:
        document = routing / "files" / (path.as_posix() + ".md")
        if not document.exists():
            continue
        if "files/" + path.as_posix() + ".md" not in index:
            errors.append("not indexed: " + path.as_posix())
        if path.suffix == ".py":
            contents = document.read_text(encoding="utf-8")
            tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
            for signature in signatures(tree):
                if signature not in contents:
                    errors.append("signature missing: " + path.as_posix() + ": " + signature)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"OK: {len(files)} client files, {len(actual)} paired documents; signatures and index match.")


if __name__ == "__main__":
    main()
