"""Finding komposoija song files: Python files that import komposoija and make a Song."""

from __future__ import annotations

import os
import re
from pathlib import Path

SKIP_DIRS = {
    ".git", ".hg", ".venv", "venv", "env", "build", "dist", "__pycache__", "node_modules",
    ".tox", ".mypy_cache", ".pytest_cache", ".ruff_cache", "site-packages", "tests", "test",
}
_IMPORT = re.compile(r"^\s*(from\s+komposoija\b|import\s+komposoija\b)", re.MULTILINE)
_SONG = re.compile(r"\bSong\(")


def is_song(path: Path) -> bool:
    if path.suffix != ".py" or path.name.startswith("test_") or path.name == "conftest.py":
        return False
    try:
        with path.open(encoding="utf-8", errors="replace") as f:
            text = f.read(65536)
    except OSError:
        return False
    return bool(_IMPORT.search(text) and _SONG.search(text))


def find_songs(roots: list[Path], limit: int = 5000) -> list[Path]:
    """Song files under the roots (a root may be a file), sorted; the songs are not run."""
    found: list[Path] = []
    for root in roots:
        root = root.resolve()
        if root.is_file():
            if is_song(root):
                found.append(root)
            continue
        seen = 0
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
            for name in sorted(files):
                seen += 1
                if seen > limit:
                    break
                if name.endswith(".py") and is_song(p := Path(dirpath) / name):
                    found.append(p)
    return sorted(dict.fromkeys(found))


def relative(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path)
