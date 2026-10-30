"""Pattern constructors: mini-notation strings -> patterns of musical events.

    s("bd ~ sd ~")         drum hits by name (GM drum map)
    note("c3 e3 g3")       absolute pitches
    n("0 2 4 7")           scale degrees of the section's key (0 = tonic)
    ct("0 2 0 [~ a]")      chord tones of the current chord (0 = root, 1 = 3rd, 2 = 5th);
                           `a` is a chromatic approach note into the next chord's root
    strum("x ~ x x")       whole-chord hits, voiced in the track's register
    walk("x*4")            walking bass: root on each chord change, steps toward the next
                           chord, chromatic approach on the last note before it
    chords("<I V vi IV>")  the harmony of a section (Roman numerals or symbols)
"""

from __future__ import annotations

import re

from .mini import mini
from .pattern import Pattern
from .theory import Key, parse_chord, parse_note

GM_DRUMS: dict[str, int] = {
    "bd": 36, "kick": 36, "bd2": 35,
    "sd": 38, "snare": 38, "sd2": 40, "rim": 37, "rs": 37, "cp": 39, "clap": 39,
    "hh": 42, "ch": 42, "ph": 44, "oh": 46,
    "rd": 51, "ride": 51, "rb": 53, "cr": 49, "crash": 49, "cr2": 57, "china": 52, "splash": 55,
    "ht": 50, "mt": 47, "lt": 45, "ft": 43, "ft2": 41,
    "tb": 54, "tamb": 54, "sh": 70, "shaker": 70, "cb": 56, "cowbell": 56,
    "hc": 62, "lc": 64, "hb": 60, "lb": 61,  # congas, bongos
}


def _drum(token: str) -> dict:
    if re.fullmatch(r"\d+", token):
        return {"drum": int(token)}
    if token not in GM_DRUMS:
        raise ValueError(f"unknown drum {token!r}; known: {', '.join(GM_DRUMS)}")
    return {"drum": GM_DRUMS[token]}


def _int(kind: str):
    def convert(token: str) -> dict:
        try:
            return {kind: int(token)}
        except ValueError:
            raise ValueError(f"expected an integer, got {token!r}") from None
    return convert


def _chord_tone(token: str) -> dict:
    if token == "a":
        return {"approach": True}
    return _int("ct")(token)


_VALIDATION_KEY = Key(0, "ionian")


def _chord(token: str) -> dict:
    parse_chord(token, _VALIDATION_KEY)  # validate now; resolve against the real key later
    return {"chord": token}


def s(text: str) -> Pattern:
    """Drum pattern: `s("bd*4, ~ sd ~ sd, hh*8")`."""
    return mini(text, _drum)


def note(text: str) -> Pattern:
    """Absolute notes: `note("e2 ~ g2 a2")` (octave defaults to 3)."""
    return mini(text, lambda tok: {"note": parse_note(tok)})


def n(text: str) -> Pattern:
    """Scale degrees of the current key, 0-based: `n("0 1 2 4")`."""
    return mini(text, _int("deg"))


def ct(text: str) -> Pattern:
    """Chord tones of the current chord: `ct("0*8")` = root eighths; `a` = approach note."""
    return mini(text, _chord_tone)


def strum(text: str) -> Pattern:
    """Whole-chord hits; any non-rest atom is a hit: `strum("x ~ x [~ x]")`."""
    return mini(text, lambda tok: {"strum": True})


def walk(text: str = "x*4") -> Pattern:
    """Walking bass line; any non-rest atom is a note: `walk("x*4")` = quarter notes."""
    return mini(text, lambda tok: {"walk": True})


def chords(text: str) -> Pattern:
    """Chord progression, usually one chord per bar: `chords("<I V vi IV>")`."""
    return mini(text, _chord)
