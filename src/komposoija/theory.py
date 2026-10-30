"""Pitches, keys, chords and voicings (see docs/01, 04-07)."""

from __future__ import annotations

import re
from dataclasses import dataclass

NOTE_PC = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}
SHARP_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

MAJOR = (0, 2, 4, 5, 7, 9, 11)

SCALES: dict[str, tuple[int, ...]] = {
    "ionian": MAJOR,
    "dorian": (0, 2, 3, 5, 7, 9, 10),
    "phrygian": (0, 1, 3, 5, 7, 8, 10),
    "lydian": (0, 2, 4, 6, 7, 9, 11),
    "mixolydian": (0, 2, 4, 5, 7, 9, 10),
    "aeolian": (0, 2, 3, 5, 7, 8, 10),
    "locrian": (0, 1, 3, 5, 6, 8, 10),
    "harmonic_minor": (0, 2, 3, 5, 7, 8, 11),
    "melodic_minor": (0, 2, 3, 5, 7, 9, 11),
    "major_pentatonic": (0, 2, 4, 7, 9),
    "minor_pentatonic": (0, 3, 5, 7, 10),
    "blues": (0, 3, 5, 6, 7, 10),
}
SCALE_ALIASES = {"major": "ionian", "minor": "aeolian", "natural_minor": "aeolian"}

# Semitones from a mode's tonic down to the tonic of the major key with the same
# notes; used to pick a key signature (D mixolydian -> G major).
_MODE_TO_IONIAN = {"ionian": 0, "dorian": 2, "phrygian": 4, "lydian": 5,
                   "mixolydian": 7, "aeolian": 9, "locrian": 11}

# Key signatures accepted by MIDI/mido, by tonic pitch class.
_MAJOR_SIG = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
_MINOR_SIG = ["Cm", "C#m", "Dm", "Ebm", "Em", "Fm", "F#m", "Gm", "G#m", "Am", "Bbm", "Bm"]
_FLAT_MAJOR_KEYS = {5, 10, 3, 8, 1, 6}  # F Bb Eb Ab Db Gb


def parse_pc(name: str) -> int:
    """'C', 'F#', 'Bb', 'eb' -> pitch class."""
    m = re.fullmatch(r"([A-Ga-g])([#b]*)", name.strip())
    if not m:
        raise ValueError(f"not a note name: {name!r}")
    return (NOTE_PC[m.group(1).lower()] + m.group(2).count("#") - m.group(2).count("b")) % 12


def parse_note(token: str, default_octave: int = 3) -> int:
    """Note name with optional octave ('c3', 'F#2', 'eb') or MIDI number -> MIDI number.

    Middle C is c4 = 60. Without an octave, `default_octave` is used (3, like Strudel).
    """
    if re.fullmatch(r"\d+", token):
        n = int(token)
        if not 0 <= n <= 127:
            raise ValueError(f"MIDI note out of range: {n}")
        return n
    m = re.fullmatch(r"([A-Ga-g])([#b]*)(-?\d+)?", token)
    if not m:
        raise ValueError(f"not a note: {token!r} (use e.g. c3, f#2, eb4 or a MIDI number)")
    octave = int(m.group(3)) if m.group(3) is not None else default_octave
    n = 12 * (octave + 1) + NOTE_PC[m.group(1).lower()] + m.group(2).count("#") - m.group(2).count("b")
    if not 0 <= n <= 127:
        raise ValueError(f"note out of MIDI range: {token!r}")
    return n


def note_name(midi: int, flats: bool = False) -> str:
    names = FLAT_NAMES if flats else SHARP_NAMES
    return f"{names[midi % 12]}{midi // 12 - 1}"


@dataclass(frozen=True)
class Key:
    tonic: int  # pitch class
    mode: str   # key of SCALES

    @property
    def scale(self) -> tuple[int, ...]:
        return SCALES[self.mode]

    @property
    def prefers_flats(self) -> bool:
        ionian = (self.tonic - _MODE_TO_IONIAN.get(self.mode, 0)) % 12
        if self.mode in ("harmonic_minor", "melodic_minor"):
            ionian = (self.tonic + 3) % 12
        return ionian in _FLAT_MAJOR_KEYS

    def pc_name(self, pc: int) -> str:
        return (FLAT_NAMES if self.prefers_flats else SHARP_NAMES)[pc % 12]

    @property
    def name(self) -> str:
        mode = {"ionian": "major", "aeolian": "minor"}.get(self.mode, self.mode)
        return f"{self.pc_name(self.tonic)} {mode.replace('_', ' ')}"

    @property
    def midi_signature(self) -> str:
        """Key signature string for a MIDI key_signature event."""
        if self.mode in ("aeolian", "harmonic_minor", "melodic_minor"):
            return _MINOR_SIG[self.tonic]
        if self.mode in _MODE_TO_IONIAN:
            return _MAJOR_SIG[(self.tonic - _MODE_TO_IONIAN[self.mode]) % 12]
        return _MAJOR_SIG[self.tonic]

    def transpose(self, semitones: int) -> "Key":
        return Key((self.tonic + semitones) % 12, self.mode)


_RELATIVE_KEY_RE = re.compile(r"^\s*([+-]\d+)\s*(.*)$")


def is_relative_key(text: object) -> bool:
    """'+1', '-2', '+3 minor': a key given relative to the song key."""
    return isinstance(text, str) and _RELATIVE_KEY_RE.match(text) is not None


def resolve_key(text: str | Key, base: Key) -> Key:
    """Parse a key; '+n' / '-n' transposes `base` by n semitones (keeping its mode unless one
    follows, as in '+3 minor')."""
    if isinstance(text, str):
        m = _RELATIVE_KEY_RE.match(text)
        if m:
            shifted = base.transpose(int(m.group(1)))
            if not m.group(2).strip():
                return shifted
            return parse_key(f"{shifted.pc_name(shifted.tonic)} {m.group(2)}")
    return parse_key(text)


def parse_key(text: str | Key) -> Key:
    """'G major', 'E minor', 'D mixolydian', 'F# dorian', 'Bb' (= major)."""
    if isinstance(text, Key):
        return text
    parts = text.strip().split(None, 1)
    if not parts:
        raise ValueError("empty key")
    tonic = parse_pc(parts[0])
    mode = parts[1].strip().lower().replace(" ", "_") if len(parts) > 1 else "major"
    mode = SCALE_ALIASES.get(mode, mode)
    if mode not in SCALES:
        raise ValueError(f"unknown mode {mode!r}; known: {', '.join(sorted(SCALES) + sorted(SCALE_ALIASES))}")
    return Key(tonic, mode)


# ---------- chords ----------

# Chord-symbol suffix -> intervals. Also used to name Roman-numeral chords.
CHORD_SUFFIXES: dict[str, tuple[int, ...]] = {
    "": (0, 4, 7), "m": (0, 3, 7), "5": (0, 7),
    "dim": (0, 3, 6), "aug": (0, 4, 8), "+": (0, 4, 8),
    "sus2": (0, 2, 7), "sus4": (0, 5, 7), "sus": (0, 5, 7),
    "6": (0, 4, 7, 9), "m6": (0, 3, 7, 9),
    "7": (0, 4, 7, 10), "maj7": (0, 4, 7, 11), "m7": (0, 3, 7, 10), "mmaj7": (0, 3, 7, 11),
    "m7b5": (0, 3, 6, 10), "dim7": (0, 3, 6, 9), "7sus4": (0, 5, 7, 10),
    "add9": (0, 4, 7, 14), "madd9": (0, 3, 7, 14),
    "9": (0, 4, 7, 10, 14), "maj9": (0, 4, 7, 11, 14), "m9": (0, 3, 7, 10, 14),
    "11": (0, 7, 10, 14, 17), "m11": (0, 3, 7, 10, 14, 17), "13": (0, 4, 7, 10, 14, 21),
    # jazz: altered dominants, sixth-nine, sharp eleven, thirteenths
    "7b9": (0, 4, 7, 10, 13), "7#9": (0, 4, 7, 10, 15), "7#11": (0, 4, 7, 10, 18),
    "7b13": (0, 4, 7, 10, 20), "7alt": (0, 4, 10, 13, 15, 20), "7b5": (0, 4, 6, 10),
    "+7": (0, 4, 8, 10), "9sus4": (0, 5, 7, 10, 14), "69": (0, 4, 7, 9, 14), "m69": (0, 3, 7, 9, 14),
    "maj7#11": (0, 4, 7, 11, 18), "maj13": (0, 4, 7, 11, 14, 21), "m13": (0, 3, 7, 10, 14, 21),
}
_SUFFIX_ALIASES = {"min": "m", "M7": "maj7", "Δ": "maj7", "Δ7": "maj7", "ø": "m7b5", "ø7": "m7b5",
                   "°": "dim", "o": "dim", "°7": "dim7", "o7": "dim7", "min7": "m7", "-": "m", "-7": "m7",
                   "alt": "7alt", "aug7": "+7", "7+": "+7", "Δ9": "maj9", "m6/9": "m69"}
_NAME_FOR_INTERVALS = {}
for _suffix, _iv in CHORD_SUFFIXES.items():
    _NAME_FOR_INTERVALS.setdefault(_iv, _suffix)

# Roman numerals: suffixes for upper-case (major-based) and lower-case (minor-based) numerals.
_ROMAN_UPPER = {"": "", "5": "5", "6": "6", "7": "7", "maj7": "maj7", "M7": "maj7", "Δ": "maj7", "Δ7": "maj7",
                "9": "9", "maj9": "maj9", "add9": "add9", "sus2": "sus2", "sus4": "sus4", "sus": "sus4",
                "7sus4": "7sus4", "+": "aug", "aug": "aug", "11": "11", "13": "13",
                "7b9": "7b9", "7#9": "7#9", "7#11": "7#11", "7b13": "7b13", "7alt": "7alt", "alt": "7alt",
                "7b5": "7b5", "+7": "+7", "9sus4": "9sus4", "69": "69", "maj7#11": "maj7#11",
                "maj13": "maj13", "Δ9": "maj9"}
_ROMAN_LOWER = {"": "m", "7": "m7", "maj7": "mmaj7", "6": "m6", "9": "m9", "add9": "madd9", "11": "m11",
                "°": "dim", "o": "dim", "dim": "dim", "°7": "dim7", "o7": "dim7", "dim7": "dim7",
                "ø": "m7b5", "ø7": "m7b5", "m7b5": "m7b5", "7b5": "m7b5", "69": "m69", "13": "m13"}
_NUMERALS = {"I": 0, "II": 1, "III": 2, "IV": 3, "V": 4, "VI": 5, "VII": 6}
_ROMAN_RE = re.compile(r"([#b]*)(VII|VI|IV|V|III|II|I|vii|vi|iv|v|iii|ii|i)(.*)")


@dataclass(frozen=True)
class Chord:
    root: int                    # pitch class
    intervals: tuple[int, ...]   # from the root, ascending
    bass: int | None = None      # pitch class of a slash bass, if any
    label: str = ""              # as written, e.g. "V7/vi" or "Am7"
    flats: bool | None = None    # spelling hint from the source (bVII -> Bb); None = follow key

    @property
    def pcs(self) -> list[int]:
        return [(self.root + i) % 12 for i in self.intervals]

    @property
    def suffix(self) -> str:
        return _NAME_FOR_INTERVALS.get(self.intervals, "?")

    def symbol(self, key: Key | None = None) -> str:
        """Absolute chord symbol, e.g. 'Em7' or 'D/F#'."""
        if self.flats is not None:
            names = FLAT_NAMES if self.flats else SHARP_NAMES
            name = lambda pc: names[pc]  # noqa: E731
        else:
            name = key.pc_name if key else (lambda pc: SHARP_NAMES[pc])
        s = name(self.root) + self.suffix
        return s + (f"/{name(self.bass)}" if self.bass is not None else "")


def parse_chord(token: str, key: Key) -> Chord:
    """A Roman numeral relative to `key` ('I', 'vi7', 'bVII', 'V7/vi') or a chord symbol
    ('Am7', 'F#m', 'Bb/D').

    Roman numerals are measured from the *major* scale of the key's tonic, the usual
    pop/rock convention: in A minor write i, bIII, iv, v, bVI, bVII.
    """
    if re.match(r"[A-G]", token):
        return _parse_symbol(token)
    if "/" in token:
        head, target = token.split("/", 1)
        target_chord = parse_chord(target, key)
        inner = parse_chord(head, Key(target_chord.root, "major"))
        return Chord(inner.root, inner.intervals, label=token)
    m = _ROMAN_RE.fullmatch(token)
    if not m:
        raise ValueError(f"not a chord: {token!r} (use Roman numerals like I, vi, bVII, V7 or symbols like Am7)")
    acc, numeral, suffix = m.groups()
    table = _ROMAN_UPPER if numeral.isupper() else _ROMAN_LOWER
    if suffix not in table:
        raise ValueError(f"unknown chord suffix {suffix!r} in {token!r}; known: {', '.join(repr(s) for s in table)}")
    root = (key.tonic + MAJOR[_NUMERALS[numeral.upper()]] + acc.count("#") - acc.count("b")) % 12
    flats = True if "b" in acc else False if "#" in acc else None
    return Chord(root, CHORD_SUFFIXES[table[suffix]], label=token, flats=flats)


def _parse_symbol(token: str) -> Chord:
    m = re.fullmatch(r"([A-G][#b]?)([^/]*)(?:/([A-G][#b]?))?", token)
    if not m:
        raise ValueError(f"not a chord symbol: {token!r}")
    root, suffix, bass = m.groups()
    suffix = _SUFFIX_ALIASES.get(suffix, suffix)
    if suffix not in CHORD_SUFFIXES:
        raise ValueError(f"unknown chord quality {suffix!r} in {token!r}; known: {', '.join(repr(s) for s in CHORD_SUFFIXES)}")
    flats = True if "b" in root else False if "#" in root else None
    return Chord(parse_pc(root), CHORD_SUFFIXES[suffix], parse_pc(bass) if bass else None, token, flats)


# ---------- placing pitches in a register ----------

def lowest_at_or_above(pc: int, lo: int) -> int:
    """Lowest MIDI note with pitch class `pc` that is >= lo."""
    return lo + (pc - lo) % 12


def chord_tone(chord: Chord, index: int, lo: int) -> int:
    """Chord tone by index (0 = root, 1 = 3rd, 2 = 5th, 3 = 7th...), root placed at or
    above `lo`. Indices past the chord size continue an octave up; negative ones go down.
    For a slash chord (D/F#) index 0 is the slash bass note."""
    if index == 0 and chord.bass is not None:
        return lowest_at_or_above(chord.bass, lo)
    n = len(chord.intervals)
    root = lowest_at_or_above(chord.root, lo)
    return root + chord.intervals[index % n] + 12 * (index // n)


def scale_degree(key: Key, degree: int, lo: int) -> int:
    """0-based scale degree of the key (0 = tonic), tonic placed at or above `lo`."""
    scale = key.scale
    n = len(scale)
    return lowest_at_or_above(key.tonic, lo) + scale[degree % n] + 12 * (degree // n)


def _close_candidates(pcs: list[int], lo: int, hi: int) -> list[list[int]]:
    """Every rotation of `pcs` stacked in close position (each note the next one up)
    with all notes inside [lo, hi]."""
    out = []
    for k in range(len(pcs)):
        order = pcs[k:] + pcs[:k]
        for start in range(lo, hi + 1):
            if start % 12 != order[0]:
                continue
            notes = [start]
            for pc in order[1:]:
                notes.append(notes[-1] + ((pc - notes[-1]) % 12 or 12))
            if notes[-1] <= hi:
                out.append(notes)
    return out


def _nearest(candidates: list[list[int]], previous: list[int] | None, lo: int, hi: int) -> list[int]:
    """The candidate closest to the previous voicing, or to the middle of the register."""
    if previous:
        def cost(v: list[int]) -> float:
            return sum(min(abs(n - p) for p in previous) for n in v) + sum(
                min(abs(p - n) for n in v) for p in previous)
    else:
        centre = (lo + hi) / 2

        def cost(v: list[int]) -> float:
            return abs(sum(v) / len(v) - centre)
    return min(candidates, key=cost)


def _guide_tones(chord: Chord) -> tuple[int, int]:
    """(third, seventh) intervals; sus chords use the 4th/2nd, chords without a 7th the 6th or 5th."""
    iv = [i % 12 for i in chord.intervals]
    third = next((i for i in iv if i in (3, 4)), next((i for i in iv if i in (5, 2)), 4))
    seventh = next((i for i in iv if i in (10, 11)), next((i for i in iv if i == 9), 7))
    return third, seventh


def _rootless_pcs(chord: Chord) -> list[int]:
    """3rd, 5th (or its alteration/13th), 7th (or 6th) and 9th, as pitch classes from the root."""
    iv = chord.intervals
    third, seventh = _guide_tones(chord)
    if seventh == 7:  # triad: use the 6th as the "seventh" colour
        seventh = 9
    upper = [i - 12 for i in iv if i > 12]
    ninth = next((i for i in upper if i in (1, 2, 3)), 2)   # b9/9/#9 if written, else natural 9
    if 21 in iv:
        fifth = 9            # 13th replaces the 5th
    elif 20 in iv:
        fifth = 8            # b13
    elif 18 in iv:
        fifth = 6            # #11
    else:
        fifth = next((i for i in iv if i in (6, 7, 8)), 7)
    return list(dict.fromkeys(pc for pc in (third, fifth, seventh, ninth)))


def voice_chord(chord: Chord, lo: int, hi: int, previous: list[int] | None = None,
                style: str = "close") -> list[int]:
    """Voice a chord inside [lo, hi].

    close:    all inversions in close position that fit; picks the one nearest the
              previous voicing (smooth voice leading) or the middle of the register.
    open:     close voicing with the second-highest note dropped an octave.
    power:    root, fifth, octave (rock/metal guitar).
    shell:    root + 3rd + 7th, or root + 7th + 3rd above (jazz guitar, piano left hand).
    rootless: 3rd, 5th/13th, 7th and 9th in close position, no root (jazz piano; the bass
              has the root). Voice-led like close.
    A slash bass is added below close/open voicings when it fits in the register.
    """
    if style == "power":
        root = lowest_at_or_above(chord.root, lo)
        return [n for n in (root, root + 7, root + 12) if n <= hi] or [root]

    if style == "shell":
        third, seventh = _guide_tones(chord)
        candidates = []
        root = lowest_at_or_above(chord.root, lo)
        while root + max(third, seventh) <= hi:
            for shape in ([root, root + third, root + seventh], [root, root + seventh, root + third + 12]):
                if shape[-1] <= hi and sorted(shape) == shape:
                    candidates.append(shape)
            root += 12
        if not candidates:
            root = lowest_at_or_above(chord.root, lo)
            candidates = [[root, root + third, root + seventh]]
        return _nearest(candidates, previous, lo, hi)

    if style == "rootless":
        pcs = [(chord.root + i) % 12 for i in _rootless_pcs(chord)]
        candidates = _close_candidates(pcs, lo, hi) or _close_candidates(pcs, lo, hi + 12)
        return _nearest(candidates, previous, lo, hi)

    if style not in ("close", "open"):
        raise ValueError(f"unknown voicing {style!r}; use close, open, power, shell or rootless")
    pcs = list(dict.fromkeys(chord.pcs))  # unique, root first
    candidates = _close_candidates(pcs, lo, hi)
    if not candidates:  # register too narrow: fall back to the lowest root position
        root = lowest_at_or_above(chord.root, lo)
        candidates = [[root + i for i in chord.intervals]]
    best = _nearest(candidates, previous, lo, hi)
    if style == "open" and len(best) >= 3:
        dropped = best[-2] - 12
        best = sorted([dropped] + best[:-2] + best[-1:]) if dropped >= lo else best
    if chord.bass is not None:
        bass = lowest_at_or_above(chord.bass, lo)
        if bass < best[0]:
            best = [bass] + best
    return best
