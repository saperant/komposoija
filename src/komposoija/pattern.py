"""Time-based patterns in the spirit of Strudel/Tidal, specialised for MIDI output.

Time is measured in *cycles*; in a song one cycle is one bar. A pattern is a
function from a time span to the events whose **onset** lies inside that span.
Unlike Tidal, events are never cut into fragments at span boundaries: an event
keeps its full length, which is exactly what a MIDI note needs.

Event values are dicts of controls, e.g. ``{"drum": 36, "velocity": 100}``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Any, Callable, Iterator, Union

Time = Fraction
TimeLike = Union[int, float, Fraction]
Query = Callable[[Fraction, Fraction], list["Event"]]

# Tiny span used to sample "what is sounding at time t".
_EPSILON = Fraction(1, 1_000_000_000)


def to_time(x: TimeLike) -> Fraction:
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    return Fraction(x).limit_denominator(1_000_000)


def cycles_in(begin: Fraction, end: Fraction) -> Iterator[int]:
    """Integer cycles overlapping [begin, end)."""
    c = math.floor(begin)
    while c < end:
        yield c
        c += 1


def cycle_pos(t: Fraction) -> Fraction:
    """Position of t within its cycle, in [0, 1)."""
    return t - math.floor(t)


@dataclass(frozen=True)
class Event:
    begin: Fraction
    end: Fraction
    value: dict[str, Any]

    @property
    def duration(self) -> Fraction:
        return self.end - self.begin

    def shifted(self, offset: Fraction) -> "Event":
        return replace(self, begin=self.begin + offset, end=self.end + offset)


class Pattern:
    def __init__(self, query: Query):
        self._query = query

    # ---------- querying ----------

    def query(self, begin: TimeLike, end: TimeLike) -> list[Event]:
        """Events with onset in [begin, end), sorted by time."""
        b, e = to_time(begin), to_time(end)
        if e <= b:
            return []
        return sorted(self._query(b, e), key=lambda ev: (ev.begin, ev.end))

    def value_at(self, t: TimeLike, lookback: int = 64) -> dict[str, Any] | None:
        """Value of the latest-starting event sounding at time t (begin <= t < end), if any."""
        ev = self.event_at(t, lookback)
        return ev.value if ev else None

    def event_at(self, t: TimeLike, lookback: int = 64) -> Event | None:
        """The latest-starting event sounding at time t (begin <= t < end), if any."""
        t = to_time(t)
        # Widen the window only when needed. Anything a wider window adds starts earlier
        # than everything in the narrower one, so the first window with a hit has the answer.
        for back in (0, 1, 4, 16, lookback):
            window = self._query(math.floor(t) - back, t + _EPSILON)
            active = [ev for ev in window if ev.begin <= t < ev.end]
            if active:
                return max(active, key=lambda ev: ev.begin)
            if back >= lookback:
                break
        return None

    # ---------- time transformations ----------

    def fast(self, factor: TimeLike) -> "Pattern":
        f = to_time(factor)
        if f <= 0:
            return silence
        return Pattern(lambda b, e: [
            Event(ev.begin / f, ev.end / f, ev.value) for ev in self._query(b * f, e * f)
        ])

    def slow(self, factor: TimeLike) -> "Pattern":
        f = to_time(factor)
        return silence if f <= 0 else self.fast(1 / f)

    def compress(self, start: TimeLike, end: TimeLike) -> "Pattern":
        """Squeeze each cycle of this pattern into [start, end) of the cycle."""
        start, end = to_time(start), to_time(end)
        width = end - start
        if width <= 0:
            return silence

        def query(b: Fraction, e: Fraction) -> list[Event]:
            out = []
            for c in cycles_in(b, e):
                lo, hi = max(b, c + start), min(e, c + end)
                if hi <= lo:
                    continue
                inner_b = c + (lo - c - start) / width
                inner_e = c + (hi - c - start) / width
                for ev in self._query(inner_b, inner_e):
                    out.append(Event(c + start + (ev.begin - c) * width,
                                     c + start + (ev.end - c) * width, ev.value))
            return out

        return Pattern(query)

    def late(self, offset: TimeLike) -> "Pattern":
        """Shift later in time by offset cycles."""
        o = to_time(offset)
        return Pattern(lambda b, e: [ev.shifted(o) for ev in self._query(b - o, e - o)])

    def early(self, offset: TimeLike) -> "Pattern":
        return self.late(-to_time(offset))

    # ---------- per-cycle structure ----------

    def first_of(self, n: int, other: "Pattern | Callable[[Pattern], Pattern]") -> "Pattern":
        """Use `other` (a pattern, or a function of this pattern) on cycles 0, n, 2n, ..."""
        alt = other(self) if callable(other) and not isinstance(other, Pattern) else as_pattern(other)
        return per_cycle(lambda c: alt if c % n == 0 else self)

    every = first_of

    def last_of(self, n: int, other: "Pattern | Callable[[Pattern], Pattern]") -> "Pattern":
        """Use `other` on cycles n-1, 2n-1, ... — e.g. a drum fill every 4th bar."""
        alt = other(self) if callable(other) and not isinstance(other, Pattern) else as_pattern(other)
        return per_cycle(lambda c: alt if c % n == n - 1 else self)

    def end_with(self, other: "Pattern", portion: TimeLike) -> "Pattern":
        """Replace the last `portion` of every cycle with one cycle of `other`.

        `drums.end_with(s("sd*4"), "1/4")` keeps the groove for three beats of a 4/4
        bar and plays a 16th-note snare fill on beat 4.
        """
        p = to_time(Fraction(portion) if isinstance(portion, str) else portion)
        cut = 1 - p

        def head(b: Fraction, e: Fraction) -> list[Event]:
            out = []
            for ev in self._query(b, e):
                if cycle_pos(ev.begin) < cut:
                    limit = math.floor(ev.begin) + cut
                    out.append(replace(ev, end=min(ev.end, limit)))
            return out

        return stack(Pattern(head), as_pattern(other).compress(cut, 1))

    # ---------- values ----------

    def fmap(self, fn: Callable[[dict[str, Any]], dict[str, Any]]) -> "Pattern":
        return Pattern(lambda b, e: [replace(ev, value=fn(ev.value)) for ev in self._query(b, e)])

    def filter(self, pred: Callable[[Event], bool]) -> "Pattern":
        return Pattern(lambda b, e: [ev for ev in self._query(b, e) if pred(ev)])

    def set(self, **controls: Any) -> "Pattern":
        """Set controls. Each value is a constant, a mini-notation string or a pattern.

        Patterned values are sampled at each event's onset, so
        `.set(velocity="100 70")` accents the first half of every bar.
        """
        from .mini import mini  # local import: mini depends on this module

        resolved: dict[str, Any] = {}
        for name, v in controls.items():
            if isinstance(v, str) and name != "voicing":
                resolved[name] = mini(v, lambda tok: {"value": _number(tok)})
            else:
                resolved[name] = v

        def query(b: Fraction, e: Fraction) -> list[Event]:
            out = []
            for ev in self._query(b, e):
                value = dict(ev.value)
                for name, v in resolved.items():
                    if isinstance(v, Pattern):
                        sampled = v.value_at(ev.begin)
                        if sampled is None:
                            continue
                        value[name] = sampled.get("value")
                    else:
                        value[name] = v
                out.append(replace(ev, value=value))
            return out

        return Pattern(query)

    def velocity(self, v: Any) -> "Pattern":
        """MIDI velocity 1-127 (0 silences the event)."""
        return self.set(velocity=v)

    def legato(self, v: Any) -> "Pattern":
        """Note length as a fraction of the event's slot (1 = full, 0.5 = staccato)."""
        return self.set(legato=v)

    def octave(self, v: Any) -> "Pattern":
        """Shift pitched events by whole octaves."""
        return self.set(octave=v)

    def transpose(self, v: Any) -> "Pattern":
        """Shift pitched events by semitones."""
        return self.set(transpose=v)

    def voicing(self, style: str) -> "Pattern":
        """Chord voicing for `strum` patterns: "close" (default), "open" or "power"."""
        return self.set(voicing=style)

    def power(self) -> "Pattern":
        """Play single notes as power chords: note + fifth + octave (metal/rock riffs)."""
        return self.set(power=1)

    def degrade(self, probability: float = 0.5, seed: int = 0) -> "Pattern":
        """Drop events at random (deterministically for a given seed)."""

        def keep(ev: Event) -> bool:
            rng = random.Random(hash((seed, ev.begin.numerator, ev.begin.denominator)))
            return rng.random() >= probability

        return self.filter(keep)

    # ---------- operators ----------

    def __add__(self, other: "Pattern") -> "Pattern":
        return stack(self, other)

    def __repr__(self) -> str:
        events = self.query(0, 1)
        shown = ", ".join(f"{float(ev.begin):g}:{ev.value}" for ev in events[:8])
        more = " ..." if len(events) > 8 else ""
        return f"<Pattern cycle0=[{shown}{more}]>"


# ---------- constructors ----------

silence = Pattern(lambda b, e: [])


def pure(value: dict[str, Any]) -> Pattern:
    """One event per cycle, filling the whole cycle."""
    return Pattern(lambda b, e: [
        Event(Fraction(c), Fraction(c + 1), dict(value)) for c in cycles_in(b, e) if c >= b
    ])


def as_pattern(x: Any) -> Pattern:
    if isinstance(x, Pattern):
        return x
    if x is None:
        return silence
    raise TypeError(f"expected a Pattern, got {type(x).__name__}: {x!r}")


def stack(*items: Pattern) -> Pattern:
    """Play patterns simultaneously."""
    pats = [as_pattern(p) for p in items]
    return Pattern(lambda b, e: [ev for p in pats for ev in p._query(b, e)])


def sequence(*items: Pattern, weights: list[TimeLike] | None = None) -> Pattern:
    """Fit all items into one cycle, one after another (Strudel `seq`/`fastcat`)."""
    pats = [as_pattern(p) for p in items]
    if not pats:
        return silence
    ws = [to_time(w) for w in (weights or [1] * len(pats))]
    total = sum(ws)
    parts, pos = [], Fraction(0)
    for p, w in zip(pats, ws):
        parts.append(p.compress(pos / total, (pos + w) / total))
        pos += w
    return stack(*parts)


def cat(*items: Pattern) -> Pattern:
    """One item per cycle, in turn (Strudel `cat`/`slowcat`, mini-notation `<a b>`).

    Each item keeps its own cycle count, so nested alternations advance only
    when their turn comes: `<a <b c>>` plays a b a c.
    """
    pats = [as_pattern(p) for p in items]
    n = len(pats)
    if n == 0:
        return silence

    def query(b: Fraction, e: Fraction) -> list[Event]:
        out = []
        for c in cycles_in(b, e):
            lo, hi = max(b, Fraction(c)), min(e, Fraction(c + 1))
            offset = Fraction(c - c // n)
            out.extend(ev.shifted(offset) for ev in pats[c % n]._query(lo - offset, hi - offset))
        return out

    return Pattern(query)


def per_cycle(choose: Callable[[int], Pattern]) -> Pattern:
    """Pick a pattern for each cycle."""

    def query(b: Fraction, e: Fraction) -> list[Event]:
        out = []
        for c in cycles_in(b, e):
            out.extend(choose(c)._query(max(b, Fraction(c)), min(e, Fraction(c + 1))))
        return out

    return Pattern(query)


def bjorklund(k: int, n: int) -> list[bool]:
    """Euclidean rhythm: k onsets spread as evenly as possible over n steps."""
    if n <= 0:
        return []
    if k <= 0:
        return [False] * n
    if k >= n:
        return [True] * n
    a: list[list[bool]] = [[True] for _ in range(k)]
    b: list[list[bool]] = [[False] for _ in range(n - k)]
    while len(b) > 1:
        m = min(len(a), len(b))
        a, b = [a[i] + b[i] for i in range(m)], (a[m:] if len(a) > m else b[m:])
    return [step for group in a + b for step in group]


def euclid(p: Pattern, k: int, n: int, rotation: int = 0) -> Pattern:
    steps = bjorklund(k, n)
    if rotation:
        r = rotation % n
        steps = steps[r:] + steps[:r]
    return sequence(*[p if on else silence for on in steps])


def _number(token: str) -> float | int:
    try:
        return int(token)
    except ValueError:
        try:
            return float(Fraction(token))
        except ValueError:
            raise ValueError(f"expected a number, got {token!r}") from None
