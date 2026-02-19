from __future__ import annotations

import argparse
import ast
import shutil
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Iterable, List

DEFAULT_EXTENSIONS = [
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".c", ".cpp", ".h", ".hpp",
    ".go", ".php", ".css", ".html", ".htm"
]

EXCLUDED_DIRS = {
    "vendor",
    "node_modules",
    ".git",
    "venv",
    "__pycache__",
    "storage",
    "bootstrap",
    "dist",
    "build",
    ".next",
    "out",
    "coverage"
}

def remove_comments_safely(content: str, suffix: str) -> str:
    result = []
    i = 0
    length = len(content)

    in_string = False
    string_char = ""
    in_block_comment = False
    in_line_comment = False

    while i < length:
        char = content[i]
        next_char = content[i + 1] if i + 1 < length else ""

        if in_line_comment:
            if char == "\n":
                in_line_comment = False
                result.append(char)
            i += 1
            continue

        if in_block_comment:
            if char == "*" and next_char == "/":
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        if in_string:
            result.append(char)
            if char == string_char and content[i - 1] != "\\":
                in_string = False
            i += 1
            continue

        if char in {"'", '"', "`"}:
            in_string = True
            string_char = char
            result.append(char)
            i += 1
            continue

        if suffix == ".py" and char == "#":
            in_line_comment = True
            i += 1
            continue

        if suffix in {".js", ".ts", ".jsx", ".tsx",
                      ".java", ".c", ".cpp", ".h",
                      ".hpp", ".go", ".php"}:
            if char == "/" and next_char == "/":
                in_line_comment = True
                i += 2
                continue
            if char == "/" and next_char == "*":
                in_block_comment = True
                i += 2
                continue

        if suffix == ".css":
            if char == "/" and next_char == "*":
                in_block_comment = True
                i += 2
                continue

        if suffix in {".html", ".htm"}:
            if content[i:i+4] == "<!--":
                end = content.find("-->", i + 4)
                if end != -1:
                    i = end + 3
                    continue

        result.append(char)
        i += 1

    return "".join(result)

def validate_syntax(file_path: Path, content: str) -> bool:
    suffix = file_path.suffix.lower()

    try:
        if suffix == ".py":
            ast.parse(content)
            return True

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content.encode("utf-8"))
            tmp_path = Path(tmp.name)

        if suffix in {".js", ".ts"}:
            result = subprocess.run(
                ["node", "--check", str(tmp_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return result.returncode == 0

        if suffix == ".php":
            result = subprocess.run(
                ["php", "-l", str(tmp_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return result.returncode == 0

        if suffix in {".c", ".cpp"}:
            result = subprocess.run(
                ["gcc", "-fsyntax-only", str(tmp_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return result.returncode == 0

        return True

    except Exception:
        return False

def process_file(file_path: Path, backup: bool, validate: bool, dry_run: bool) -> str:
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        cleaned = remove_comments_safely(content, file_path.suffix.lower())

        if validate and not validate_syntax(file_path, cleaned):
            return f"[SKIPPED - INVALID SYNTAX] {file_path}"

        if dry_run:
            return f"[DRY RUN] {file_path}"

        if backup:
            shutil.copy(file_path, file_path.with_suffix(file_path.suffix + ".bak"))

        file_path.write_text(cleaned, encoding="utf-8")
        return f"[OK] {file_path}"

    except Exception as e:
        return f"[ERROR] {file_path} - {e}"


def iter_files(root: Path, extensions: Iterable[str]) -> List[Path]:
    files: List[Path] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in extensions:
            continue

        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue

        files.append(path)

    return files

def main() -> None:
    parser = argparse.ArgumentParser(description="Enterprise Comment Remover")
    parser.add_argument("--path", required=True)
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--extensions", nargs="+", default=DEFAULT_EXTENSIONS)
    parser.add_argument("--workers", type=int, default=4)

    args = parser.parse_args()
    root = Path(args.path)

    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")

    files = iter_files(root, args.extensions)

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        results = executor.map(
            process_file,
            files,
            [args.backup] * len(files),
            [args.validate] * len(files),
            [args.dry_run] * len(files),
        )

        for r in results:
            print(r)

    print(f"\nDone. {len(files)} file(s) processed.")


if __name__ == "__main__":
    main()
