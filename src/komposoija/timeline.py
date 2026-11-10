"""Places in a rendered song: where each bar starts (in beats and seconds), and names
for places that a person can type, such as `chorus.2:5` (the second chorus, bar 5).

    chorus        the first chorus, from its first bar
    chorus.2      the second time the chorus is played
    chorus:5      bar 5 of the first chorus
    chorus.2:5    bar 5 of the second chorus
    33            bar 33 of the song

Bars and occurrences count from 1 in names, from 0 in the data.
"""

from __future__ import annotations

import bisect
import re
from dataclasses import dataclass
from fractions import Fraction

from .render import Rendering, RenderError
from .song import bar_beats


@dataclass(frozen=True)
class Bar:
    index: int        # 0-based in the song
    section: int      # index into Rendering.sections (one entry per time a section is played)
    bar: int          # 0-based in that section
    beat: Fraction    # quarter notes from the start of the song
    seconds: float


def seconds_at(r: Rendering, beat: Fraction | float) -> float:
    """The time at a beat of the song, following tempo changes and ramps."""
    beat = Fraction(beat)
    for span in r.sections:
        if beat < span.start_beat + span.beats or span is r.sections[-1]:
            seconds = span.start_seconds
            for start, length, bpm in span.tempo_steps():
                part = min(length, max(Fraction(0), beat - start))
                seconds += float(part) * 60 / bpm
            return seconds
    return 0.0


def bars(r: Rendering) -> list[Bar]:
    """Every bar of the song, in order."""
    out = []
    for i, span in enumerate(r.sections):
        bpb = bar_beats(span.meter)
        for b in range(span.bars):
            beat = span.start_beat + b * bpb
            out.append(Bar(span.start_bar + b, i, b, beat, seconds_at(r, beat)))
    return out


def bar_at(timeline: list[Bar], seconds: float) -> Bar | None:
    """The bar sounding at this time (None before the start or with no bars)."""
    if not timeline or seconds < timeline[0].seconds:
        return None
    return timeline[bisect.bisect_right([b.seconds for b in timeline], seconds) - 1]


def occurrence(r: Rendering, section: int) -> int:
    """Which time (1-based) the section at this index of the form is played."""
    name = r.sections[section].name
    return sum(1 for s in r.sections[: section + 1] if s.name == name)


def place_name(r: Rendering, section: int, bar: int = 0) -> str:
    """The name of a place: `chorus`, `chorus.2`, `chorus:5`, `chorus.2:5`."""
    name = r.sections[section].name
    n = occurrence(r, section)
    return name + (f".{n}" if n > 1 else "") + (f":{bar + 1}" if bar else "")


_PLACE = re.compile(r"^(?P<name>.+?)(?:\.(?P<n>\d+))?(?::(?P<bar>\d+))?$")


def find_place(r: Rendering, spec: str) -> Bar:
    """The bar a place names (see the module docstring)."""
    timeline = bars(r)
    spec = spec.strip()
    if spec.isdigit():
        n = int(spec)
        if not 1 <= n <= len(timeline):
            raise RenderError(f"bar {n}: the song has bars 1-{len(timeline)}")
        return timeline[n - 1]
    m = _PLACE.match(spec)
    names = {s.name for s in r.sections}
    if spec in names:  # a name that happens to contain '.' or ':'
        name, n, bar = spec, 1, 1
    elif m and m["name"] in names:
        name, n, bar = m["name"], int(m["n"] or 1), int(m["bar"] or 1)
    else:
        raise RenderError(f"{spec!r}: no such place; name a section in the form "
                          f"({', '.join(dict.fromkeys(s.name for s in r.sections))}), "
                          "e.g. chorus, chorus.2, chorus.2:5, or a bar number")
    played = [i for i, s in enumerate(r.sections) if s.name == name]
    if not 1 <= n <= len(played):
        raise RenderError(f"{spec!r}: {name} is played {len(played)} time(s)")
    section = played[n - 1]
    if not 1 <= bar <= r.sections[section].bars:
        raise RenderError(f"{spec!r}: {name} has {r.sections[section].bars} bars")
    return next(b for b in timeline if b.section == section and b.bar == bar - 1)
