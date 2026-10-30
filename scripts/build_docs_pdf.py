#!/usr/bin/env python3
"""Build a single, styled PDF (or HTML) from the Markdown files in docs/.

Pipeline: Markdown -> HTML (python-markdown + pygments) -> PDF (WeasyPrint).
Order: docs/README.md (as "About this guide"), numbered chapters, glossary, and
docs/song-dsl.md as an appendix.

Usage:
    python3 scripts/build_docs_pdf.py                 # -> build/music-theory.pdf
    python3 scripts/build_docs_pdf.py --html-only     # -> build/music-theory.html
    python3 scripts/build_docs_pdf.py -o out.pdf --paper letter
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import os
import re
import sys
import tempfile
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
STYLE = DOCS / "pdf" / "style.css"
DEFAULT_OUT = ROOT / "build" / "music-theory.pdf"

TITLE = "Music Theory for Pop &amp; Rock"
SUBTITLE = "Study material for an automatic song composition pipeline"

# Extra font directories to expose to fontconfig if they exist. Inside a
# toolbox/distrobox container the host's fonts live under /run/host.
EXTRA_FONT_DIRS = [Path("/run/host/usr/share/fonts"), Path.home() / ".local/share/fonts"]


def chapter_id(path: Path) -> str:
    m = re.match(r"(\d+)-", path.name)
    if m:
        return f"ch-{m.group(1)}"
    return "about" if path.name == "README.md" else path.stem


def ordered_sources() -> list[Path]:
    chapters = sorted(p for p in DOCS.glob("[0-9][0-9]-*.md"))
    files = [DOCS / "README.md", *chapters, DOCS / "glossary.md", DOCS / "song-dsl.md"]
    return [p for p in files if p.exists()]


def rewrite_links(body: str, ids: dict[str, str]) -> str:
    """Turn links to sibling .md files into links to the chapter anchors."""

    def repl(m: re.Match) -> str:
        target, frag = m.group(1), m.group(2) or ""
        if target not in ids:
            return m.group(0)
        anchor = frag[1:] if frag else ids[target]
        return f'href="#{anchor}"'

    return re.sub(r'href="([\w.-]+\.md)(#[\w-]+)?"', repl, body)


# Symbola's double accidentals are drawn at note-head size and sit low; use the usual
# typographic stand-ins instead.
ACCIDENTAL_SUBSTITUTES = {"\U0001D12B": "♭♭", "\U0001D12A": "×"}


def wrap_music_symbols(body: str) -> str:
    """Box clef glyphs (𝄞 𝄢): their outlines overhang their advance width in most fonts
    and would otherwise overlap neighbouring text. Replace 𝄫/𝄪 with ♭♭/×."""

    def repl(m: re.Match) -> str:
        ch = m.group(1)
        if ch in ACCIDENTAL_SUBSTITUTES:
            return f'<span class="accidental">{ACCIDENTAL_SUBSTITUTES[ch]}</span>'
        return f'<span class="music">{ch}</span>'

    return re.sub("([\U0001D100-\U0001D1FF])", repl, body)


def render_chapter(path: Path, ids: dict[str, str]) -> tuple[str, str, list[dict], str, str | None]:
    """Return (chapter id, HTML section, toc tokens, title, number) for one Markdown file."""
    cid = chapter_id(path)
    text = path.read_text(encoding="utf-8")

    # Split "# 07 — Chords and Harmony" into a number label and a title.
    first, _, rest = text.partition("\n")
    m = re.match(r"#\s+(?:(\d+)\s+—\s+)?(.*)", first)
    if cid == "about":
        number, title = None, "About this guide"
    else:
        number, title = (m.group(1), m.group(2)) if m else (None, path.stem)
    label = f'<span class="chapnum">Chapter {int(number)}</span>' if number else ""
    heading = f'<h1 id="{cid}">{label}<span class="chaptitle">{html.escape(title)}</span></h1>'

    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "codehilite", "toc", "sane_lists", "attr_list"],
        extension_configs={
            "codehilite": {"css_class": "hl", "guess_lang": False},
            # Prefix ids per chapter: every chapter has "For the pipeline" etc.
            "toc": {"slugify": lambda value, sep: f"{cid}-{slugify(value, sep)}"},
        },
    )
    body = wrap_music_symbols(rewrite_links(md.convert(rest), ids))
    section = f'<section class="chapter" id="sec-{cid}">\n{heading}\n{body}\n</section>'
    return cid, section, md.toc_tokens, title, number


def build_toc(entries: list[tuple[str, str, str | None, list[dict]]]) -> str:
    items = []
    for cid, title, number, tokens in entries:
        num = f'<span class="toc-num">{int(number)}</span>' if number else '<span class="toc-num"></span>'
        subs = "".join(
            f'<li><a href="#{t["id"]}">{t["name"]}</a></li>' for t in tokens if t["level"] == 2
        )
        items.append(
            f'<li class="toc-chapter"><a href="#{cid}">{num}{html.escape(title)}</a>'
            f'{f"<ul>{subs}</ul>" if subs else ""}</li>'
        )
    return f'<nav class="toc"><h1 class="toc-title">Contents</h1><ul>{"".join(items)}</ul></nav>'


def build_html(paper: str) -> str:
    sources = ordered_sources()
    ids = {p.name: chapter_id(p) for p in sources}
    sections, toc_entries = [], []
    for path in sources:
        cid, section, tokens, title, number = render_chapter(path, ids)
        sections.append(section)
        toc_entries.append((cid, title, number, tokens))

    css = STYLE.read_text(encoding="utf-8").replace("--paper--", paper)
    css += "\n" + HtmlFormatter(style="friendly").get_style_defs(".hl")
    today = dt.date.today().strftime("%B %Y")
    cover = (
        '<section class="cover">'
        f'<div class="cover-title">{TITLE}</div>'
        f'<div class="cover-subtitle">{SUBTITLE}</div>'
        f'<div class="cover-symbols">{"".join(f"<span>{wrap_music_symbols(c)}</span>" for c in "𝄞♯♭♮𝄢")}</div>'
        f'<div class="cover-date">{today}</div>'
        "</section>"
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{TITLE}</title><style>{css}</style></head><body>"
        f"{cover}{build_toc(toc_entries)}{''.join(sections)}</body></html>"
    )


def configure_fonts() -> None:
    """Make extra font dirs (e.g. host fonts in a toolbox) visible to fontconfig."""
    dirs = [d for d in EXTRA_FONT_DIRS if d.is_dir()]
    if not dirs or "FONTCONFIG_FILE" in os.environ:
        return
    conf = tempfile.NamedTemporaryFile("w", suffix=".conf", delete=False)
    conf.write(
        '<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig>'
        '<include ignore_missing="yes">/etc/fonts/fonts.conf</include>'
        + "".join(f"<dir>{d}</dir>" for d in dirs)
        + "</fontconfig>"
    )
    conf.close()
    os.environ["FONTCONFIG_FILE"] = conf.name


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", type=Path, help=f"output file (default: {DEFAULT_OUT.relative_to(ROOT)})")
    ap.add_argument("--paper", default="A4", help="CSS page size, e.g. A4 or letter (default: A4)")
    ap.add_argument("--html-only", action="store_true", help="write the intermediate HTML instead of a PDF")
    args = ap.parse_args()

    out = args.output or (DEFAULT_OUT.with_suffix(".html") if args.html_only else DEFAULT_OUT)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = build_html(args.paper)

    if args.html_only:
        out.write_text(doc, encoding="utf-8")
    else:
        configure_fonts()
        try:
            from weasyprint import HTML
        except ImportError:
            print("WeasyPrint is not installed: pip install -r requirements-docs.txt "
                  "(or use scripts/build-docs-pdf.sh)", file=sys.stderr)
            return 1
        HTML(string=doc, base_url=str(DOCS)).write_pdf(out)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
