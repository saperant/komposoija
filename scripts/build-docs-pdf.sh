#!/usr/bin/env bash
# Build build/music-theory.pdf from docs/*.md.
# Creates a private virtualenv (.venv-docs) with the Python dependencies on first run.
# Any arguments are passed to build_docs_pdf.py (e.g. --paper letter, --html-only, -o file).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
venv="$root/.venv-docs"
reqs="$root/requirements-docs.txt"

if [[ ! -x "$venv/bin/python" ]]; then
    echo "Creating $venv ..."
    python3 -m venv "$venv"
fi

# Reinstall only when the requirements file changes.
stamp="$venv/.requirements.sha"
want="$(sha256sum "$reqs" | cut -d' ' -f1)"
if [[ ! -f "$stamp" || "$(cat "$stamp")" != "$want" ]]; then
    "$venv/bin/pip" install --quiet --upgrade pip
    "$venv/bin/pip" install --quiet -r "$reqs"
    echo "$want" > "$stamp"
fi

exec "$venv/bin/python" "$root/scripts/build_docs_pdf.py" "$@"
