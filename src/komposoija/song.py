"""Song model: tracks (instruments), sections (with chords, lyrics and parts) and a form.

The model mirrors the composition flow:

    1. structure  song.section(...) with lyrics, song.arrange(...)
    2. mood       key, tempo, swing, chords per section, choice of presets
    3. details    per-section parts, fills, variants
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

from .notation import chords as chords_pattern
from .pattern import Pattern
from .styles import style_profile
from .theory import Key, is_relative_key, parse_key

GM_PROGRAMS: dict[str, int] = {
    "piano": 0, "bright_piano": 1, "epiano": 4, "clav": 7, "organ": 16, "rock_organ": 18,
    "nylon_guitar": 24, "acoustic_guitar": 25, "jazz_guitar": 26, "clean_guitar": 27,
    "muted_guitar": 28, "overdrive_guitar": 29, "distortion_guitar": 30,
    "acoustic_bass": 32, "finger_bass": 33, "pick_bass": 34, "fretless_bass": 35,
    "slap_bass": 36, "synth_bass": 38, "strings": 48, "slow_strings": 49, "synth_strings": 50,
    "choir": 52, "brass": 61, "sax": 65, "lead_square": 80, "lead_saw": 81, "pad_warm": 89,
    "pad_poly": 90, "pad_choir": 91,
    "drawbar_organ": 16, "perc_organ": 17, "harmonica": 22, "upright_bass": 32, "trumpet": 56,
    "trombone": 57, "muted_trumpet": 59, "alto_sax": 65, "tenor_sax": 66, "bari_sax": 67,
    "clavinet": 7, "vibraphone": 11, "guitar_harmonics": 31, "steel_drums": 114,
}


@dataclass
class Track:
    """An instrument: one MIDI track/channel. `register` bounds generated pitches."""
    name: str
    program: int | str = 0
    register: tuple[int, int] = (48, 72)
    is_drums: bool = False
    channel: int | None = None    # assigned automatically when None
    velocity: int = 90            # default velocity
    humanize_ms: float = 0.0      # random timing offset, +/- ms
    humanize_velocity: int = 0    # random velocity offset, +/-

    @property
    def program_number(self) -> int:
        if isinstance(self.program, int):
            return self.program
        if self.program not in GM_PROGRAMS:
            raise ValueError(f"unknown program {self.program!r}; use a GM number or one of {', '.join(GM_PROGRAMS)}")
        return GM_PROGRAMS[self.program]


def default_tracks() -> dict[str, Track]:
    return {t.name: t for t in [
        Track("drums", 0, (35, 81), is_drums=True, velocity=100),
        Track("bass", "finger_bass", (28, 52)),
        Track("keys", "piano", (52, 76), velocity=80),
        Track("guitar", "overdrive_guitar", (40, 64), velocity=90),
        Track("pad", "pad_warm", (55, 79), velocity=70),
        Track("lead", "lead_saw", (60, 84)),
    ]}


def parse_meter(text: str | tuple[int, int]) -> tuple[int, int]:
    """'7/8' -> (7, 8)."""
    if isinstance(text, tuple):
        num, den = text
    else:
        try:
            num, den = (int(x) for x in text.split("/"))
        except ValueError:
            raise ValueError(f"meter {text!r}: write it as 'beats/unit', e.g. '3/4' or '7/8'") from None
    if num < 1 or den not in (1, 2, 4, 8, 16, 32):
        raise ValueError(f"meter {num}/{den}: the unit must be 1, 2, 4, 8, 16 or 32")
    return num, den


def bar_beats(meter: tuple[int, int]) -> Fraction:
    """Length of a bar in quarter notes: 4/4 -> 4, 7/8 -> 7/2."""
    num, den = meter
    return Fraction(num * 4, den)


@dataclass
class Section:
    """A song section. `chords` is a pattern (one cycle = one bar) or mini-notation."""
    name: str
    bars: int
    chords: Pattern | str | None = None
    key: str | Key | None = None         # a key, or relative to the song key: "+1", "-2", "+3 minor"
    tempo: float | None = None
    tempo_to: float | None = None        # gradual change (rit./accel.) to this tempo by the last beat
    meter: str | tuple[int, int] | None = None   # time signature of this section, e.g. "7/8"
    lyrics: str | None = None
    energy: float | None = None          # 0..1, informational for now
    parts: dict[str, Pattern] = field(default_factory=dict)
    fills: dict[str, Pattern] = field(default_factory=dict)
    crash: bool = True                   # crash cymbal on beat 1 when the section starts
    notes: str | None = None             # free-form comments (for humans and agents)

    def __post_init__(self) -> None:
        if isinstance(self.chords, str):
            self.chords = chords_pattern(self.chords)
        if self.key is not None and not is_relative_key(self.key):
            self.key = parse_key(self.key)
        if isinstance(self.meter, str):
            self.meter = parse_meter(self.meter)
        if self.bars < 1:
            raise ValueError(f"section {self.name!r}: bars must be >= 1")

    def play(self, **parts: Pattern | None) -> "Section":
        """Set the pattern for one or more tracks; None removes a part."""
        for track, pat in parts.items():
            if pat is None:
                self.parts.pop(track, None)
            else:
                self.parts[track] = pat
        return self

    def fill(self, **parts: Pattern) -> "Section":
        """Patterns that replace a track's part in the section's last bar."""
        self.fills.update(parts)
        return self


class Song:
    def __init__(self, title: str = "Untitled", key: str = "C major", tempo: float = 120,
                 meter: str = "4/4", style: str = "pop_rock", swing: float | None = None,
                 swing_unit: int | None = None, seed: int = 0, crashes: bool | None = None):
        num, den = parse_meter(meter)
        self.title = title
        self.key = parse_key(key)
        self.tempo = tempo
        self.meter = (num, den)
        profile = style_profile(style)
        self.style = style
        self.swing = profile["swing"] if swing is None else swing  # 0.5 straight, ~0.66 triplet
        self.swing_unit = profile["swing_unit"] if swing_unit is None else swing_unit  # 8 or 16
        self.seed = seed
        self.crashes = profile["crashes"] if crashes is None else crashes  # crash on section starts
        self.tracks: dict[str, Track] = default_tracks()
        for name, settings in profile["tracks"].items():
            self.track(name, **settings)
        self.sections: dict[str, Section] = {}
        self.form: list[str] = []

    @property
    def beats_per_bar(self) -> Fraction:
        """Length of a bar in quarter notes."""
        return bar_beats(self.meter)

    def track(self, name: str, **settings: Any) -> Track:
        """Add a track, or change settings of an existing one."""
        if name in self.tracks:
            t = self.tracks[name]
            for k, v in settings.items():
                setattr(t, k, v)
        else:
            t = self.tracks[name] = Track(name, **settings)
        return t

    def section(self, name: str, bars: int | None = None, like: Section | str | None = None,
                **settings: Any) -> Section:
        """Create (and register) a section. `like=` copies another section as a variant."""
        if like is not None:
            base = self.sections[like] if isinstance(like, str) else like
            sec = copy.copy(base)
            sec.parts, sec.fills = dict(base.parts), dict(base.fills)
            sec.name = name
            if bars is not None:
                sec.bars = bars
            for k, v in settings.items():
                setattr(sec, k, v)
            sec.__post_init__()
        else:
            if bars is None:
                raise ValueError(f"section {name!r}: give bars= (or like=)")
            sec = Section(name, bars, **settings)
        self.sections[name] = sec
        return sec

    def arrange(self, *names: str) -> "Song":
        """Set the form: `song.arrange("intro verse chorus verse chorus outro")`."""
        form = [n for item in names for n in item.split()]
        missing = [n for n in form if n not in self.sections]
        if missing:
            raise ValueError(f"unknown sections in form: {', '.join(missing)}")
        self.form = form
        return self
