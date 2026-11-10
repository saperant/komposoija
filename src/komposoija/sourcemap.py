"""Which section a line of a song file is about, read from its syntax (the file is not run).

    verse = song.section("verse", bars=8, lyrics=\"\"\"     -> verse
        We wrote our names on paper lanterns            -> verse, lyric line 1 of 4
        and let the river carry them away               -> verse, lyric line 2 of 4
    \"\"\")
    verse.chords = chords("<I V vi IV>")               -> verse (through the variable)
    verse.play(drums=drums.sidestick, ...)              -> verse
    verse2 = song.section("verse2", like=verse)         -> verse2

A lyric line stands for the bars its share of the section covers: with 4 lines in
8 bars, the second line starts at bar 3. `Region.lyric` is (line index, line count);
`lyric_bar` turns it into a bar once the section's length is known.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    first: int                          # 1-based lines, inclusive
    last: int
    section: str
    lyric: tuple[int, int] | None = None  # (0-based lyric line, number of lyric lines)

    def bar(self, bars: int) -> int:
        """The 0-based bar of a section of this many bars where the region starts."""
        return lyric_bar(self.lyric, bars)


def lyric_bar(lyric: tuple[int, int] | None, bars: int) -> int:
    if lyric is None:
        return 0
    k, n = lyric
    return min(bars - 1, k * bars // max(1, n))


def _str(node: ast.AST | None) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _subject(node: ast.AST) -> str | None:
    """The variable a statement works on: `verse` in verse.play(...).fill(...),
    verse.chords = ..., verse.parts["x"] = ...."""
    while True:
        if isinstance(node, ast.Call):
            node = node.func
        elif isinstance(node, (ast.Attribute, ast.Subscript)):
            node = node.value
        elif isinstance(node, ast.Name):
            return node.id
        else:
            return None


def _lyric_regions(node: ast.AST, section: str) -> list[Region]:
    """A region per non-empty line of a lyrics string literal."""
    text = _str(node)
    if text is None or node.lineno == node.end_lineno:
        return []
    lines = [(i, ln) for i, ln in enumerate(text.split("\n")) if ln.strip()]
    return [Region(node.lineno + i, node.lineno + i, section, (k, len(lines)))
            for k, (i, _) in enumerate(lines)]


def _section_call(node: ast.AST) -> ast.Call | None:
    """The `<song>.section("name", ...)` call in an expression, if any."""
    for sub in ast.walk(node):
        if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute)
                and sub.func.attr == "section"):
            return sub
    return None


def regions(source: str) -> list[Region]:
    """The regions of a song file's source, in order. Statements inside if/for/with
    blocks count too; functions and classes are not looked into."""
    out: list[Region] = []
    variables: dict[str, str] = {}

    def statement(stmt: ast.stmt) -> None:
        call = _section_call(stmt)
        name = None
        if call is not None:
            name = _str(call.args[0]) if call.args else None
            name = name or next((_str(k.value) for k in call.keywords if k.arg == "name"), None)
        if name is not None:
            out.append(Region(stmt.lineno, stmt.end_lineno or stmt.lineno, name))
            for k in call.keywords:
                if k.arg == "lyrics":
                    out.extend(_lyric_regions(k.value, name))
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        variables[target.id] = name
            return
        node = stmt.value if isinstance(stmt, ast.Expr) else stmt
        if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
            node = next((t for t in targets if not isinstance(t, ast.Name)), None)
        subject = _subject(node) if node is not None else None
        if subject in variables:
            section = variables[subject]
            out.append(Region(stmt.lineno, stmt.end_lineno or stmt.lineno, section))
            if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Attribute) and stmt.targets[0].attr == "lyrics"):
                out.extend(_lyric_regions(stmt.value, section))

    def block(body: list[ast.stmt]) -> None:
        for stmt in body:
            if isinstance(stmt, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                for part in ("body", "orelse", "finalbody"):
                    block(getattr(stmt, part, []))
                for handler in getattr(stmt, "handlers", []):
                    block(handler.body)
            elif not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                statement(stmt)

    block(ast.parse(source).body)
    return out


def region_at(found: list[Region], line: int) -> Region | None:
    """The narrowest region holding the line (a lyric line before its statement)."""
    holding = [r for r in found if r.first <= line <= r.last]
    return min(holding, key=lambda r: (r.last - r.first, r.lyric is None)) if holding else None
