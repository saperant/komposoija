"""komposoija's user interface on the myrcp workbench (https://github.com/saperant/myrcp):
this directory is a myrcp product (product.toml, plugins/komposoija), started by the
`komposoija-ui` command. Needs the `ui` extra: pip install 'komposoija[ui]'."""

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT = Path(__file__).resolve().parent


def main() -> None:
    try:
        from myrcp.launch import run_product
    except ImportError:
        print("komposoija-ui needs myrcp: pip install 'komposoija[ui]'", file=sys.stderr)
        raise SystemExit(1) from None
    run_product(PRODUCT)
