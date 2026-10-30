"""Render a Song to notes, a text summary, and a Standard MIDI File."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Callable

import mido

from .pattern import Event, Pattern
from .song import Section, Song, Track, bar_beats
from .theory import (Chord, Key, chord_tone, lowest_at_or_above, parse_chord, resolve_key,
                     scale_degree, voice_chord)

CRASH = 49
DRUM_BARS = Fraction(1, 16)  # drum notes are one-shots: a 16th of a bar


class RenderError(ValueError):
    pass


@dataclass(frozen=True)
class Note:
    track: str
    start: float      # quarter-note beats from the start of the song
    duration: float   # beats
    pitch: int
    velocity: int


@dataclass
class SectionSpan:
    name: str
    start_bar: int                 # 0-based
    bars: int
    start_beat: Fraction
    start_seconds: float
    tempo: float
    key: Key
    meter: tuple[int, int]
    tempo_to: float | None         # gradual tempo change across the section
    chords_by_bar: list[list[str]]  # chord symbols starting in each bar
    chord_changes: list[tuple[Fraction, str]]  # (beat from song start, symbol)
    tracks: list[str]

    @property
    def beats(self) -> Fraction:
        return self.bars * bar_beats(self.meter)

    def tempo_steps(self) -> list[tuple[Fraction, Fraction, float]]:
        """(start beat, length, BPM) pieces of the section. A ramp (`tempo_to`) changes the
        tempo every quarter note and reaches the target on the last beat."""
        if self.tempo_to is None or self.tempo_to == self.tempo:
            return [(self.start_beat, self.beats, self.tempo)]
        steps = math.ceil(self.beats)
        out = []
        for i in range(steps):
            bpm = self.tempo + (self.tempo_to - self.tempo) * i / max(1, steps - 1)
            length = min(Fraction(1), self.beats - i)
            out.append((self.start_beat + i, length, bpm))
        return out

    @property
    def seconds(self) -> float:
        return sum(float(length) * 60 / bpm for _, length, bpm in self.tempo_steps())


@dataclass
class Rendering:
    song: Song
    notes: list[Note]
    sections: list[SectionSpan]
    total_beats: Fraction
    total_seconds: float


def render(song: Song, sections: list[str] | None = None) -> Rendering:
    """Render the song's form (or just the named sections, in the given order)."""
    order = sections if sections is not None else song.form
    if not order:
        raise RenderError("the song has no form: call song.arrange(...)")
    unknown = [name for name in order if name not in song.sections]
    if unknown:
        raise RenderError(f"unknown sections: {', '.join(unknown)} (have: {', '.join(song.sections)})")

    notes: list[Note] = []
    spans: list[SectionSpan] = []
    beat, bar, seconds = Fraction(0), 0, 0.0
    voicings: dict[str, list[int]] = {}  # last chord voicing per track, for voice leading

    for index, name in enumerate(order):
        sec = song.sections[name]
        key = section_key(song, sec)
        tempo = sec.tempo or song.tempo
        meter = sec.meter or song.meter
        bpb = bar_beats(meter)
        following = song.sections[order[index + 1]] if index + 1 < len(order) else None
        following_key = section_key(song, following) if following is not None else None
        chord_at = _chord_lookup(sec, key, following, following_key)
        changes = _chord_changes(sec, key)

        sec_notes: list[Note] = []
        for track_name, pattern in sec.parts.items():
            track = _track(song, track_name, sec)
            for ev in _section_events(sec, track_name, pattern):
                for pitch, velocity, length in _resolve(ev, track, key, chord_at, voicings, sec):
                    sec_notes.append(Note(track_name, float(beat + ev.begin * bpb),
                                          float(length * bpb), pitch, velocity))

        if song.crashes and sec.crash and index > 0 and "drums" in sec.parts:
            if not any(n.track == "drums" and n.pitch == CRASH and n.start == float(beat) for n in sec_notes):
                sec_notes.append(Note("drums", float(beat), float(DRUM_BARS * bpb), CRASH, 105))
        notes += _swing(song, sec_notes, meter, float(beat))

        span = SectionSpan(
            name, bar, sec.bars, beat, seconds, tempo, key, meter, sec.tempo_to,
            chords_by_bar=[[sym for t, sym in changes if math.floor(t) == b] for b in range(sec.bars)],
            chord_changes=[(beat + t * bpb, sym) for t, sym in changes],
            tracks=list(sec.parts),
        )
        spans.append(span)
        beat += span.beats
        bar += sec.bars
        seconds += span.seconds

    notes = _humanize(song, notes, spans)
    notes.sort(key=lambda n: (n.start, n.track, n.pitch))
    return Rendering(song, notes, spans, beat, seconds)


# ---------- per-section helpers ----------

def section_key(song: Song, sec: Section) -> Key:
    """The section's key: its own, one relative to the song key ("+1"), or the song key."""
    if sec.key is None:
        return song.key
    try:
        return resolve_key(sec.key, song.key)
    except ValueError as e:
        raise RenderError(f"section {sec.name!r}: {e}") from None


def _track(song: Song, name: str, sec: Section) -> Track:
    if name not in song.tracks:
        raise RenderError(f"section {sec.name!r} plays unknown track {name!r}; "
                          f"add it with song.track({name!r}, program=..., register=(lo, hi))")
    return song.tracks[name]


def _section_events(sec: Section, track: str, pattern: Pattern) -> list[Event]:
    events = pattern.query(0, sec.bars)
    fill = sec.fills.get(track)
    if fill is None:
        return events
    last = sec.bars - 1
    kept = [ev for ev in events if ev.begin < last]
    return kept + fill.query(last, sec.bars)


def _chord_lookup(sec: Section, key: Key, following: Section | None,
                  following_key: Key | None) -> Callable[[Fraction], Chord | None]:
    """Chord sounding at time t (in bars) of this section. From the section's end onward it
    is the first chord of the following section, so lines can lead into it."""
    cache: dict[tuple[str, Key], Chord] = {}

    def lookup(s: Section, k: Key, t: Fraction) -> Chord | None:
        value = s.chords.value_at(t) if s.chords is not None else None
        if value is None:
            return None
        token = value["chord"]
        if (token, k) not in cache:
            cache[token, k] = parse_chord(token, k)
        return cache[token, k]

    def chord_at(t: Fraction) -> Chord | None:
        if t >= sec.bars and following is not None:
            return lookup(following, following_key, Fraction(0))
        return lookup(sec, key, t)

    return chord_at


def _chord_changes(sec: Section, key: Key) -> list[tuple[Fraction, str]]:
    if sec.chords is None:
        return []
    out: list[tuple[Fraction, str]] = []
    for ev in sec.chords.query(0, sec.bars):
        sym = parse_chord(ev.value["chord"], key).symbol(key)
        if not out or out[-1][1] != sym or math.floor(ev.begin) != math.floor(out[-1][0]):
            out.append((ev.begin, sym))
    return out


def _resolve(ev: Event, track: Track, key: Key, chord_at: Callable[[Fraction], Chord | None],
             voicings: dict[str, list[int]], sec: Section) -> list[tuple[int, int, Fraction]]:
    """Turn one pattern event into (pitch, velocity, length-in-bars) tuples."""
    v = ev.value
    velocity = int(v.get("velocity", track.velocity))
    if velocity <= 0:
        return []
    length = ev.duration * Fraction(v.get("legato", 1)).limit_denominator(1000)
    shift = 12 * int(v.get("octave", 0)) + int(v.get("transpose", 0))
    lo, hi = track.register

    def need_chord(t: Fraction) -> Chord:
        chord = chord_at(t)
        if chord is None:
            raise RenderError(f"section {sec.name!r}, track {track.name!r}: no chord at bar "
                              f"{math.floor(t) + 1} (give the section chords=...)")
        return chord

    if "drum" in v:
        pitches = [v["drum"]]
        shift = 0
        length = min(length, DRUM_BARS)
    elif "note" in v:
        pitches = [v["note"]]
    elif "deg" in v:
        pitches = [scale_degree(key, v["deg"], lo)]
    elif "ct" in v:
        pitches = [chord_tone(need_chord(ev.begin), v["ct"], lo)]
    elif "approach" in v:
        target = chord_tone(chord_at(ev.end) or need_chord(ev.begin), 0, lo)
        pitches = [target - 1 if target - 1 >= lo else target + 1]
    elif "walk" in v:
        pitches = [_walk_note(ev, track, key, sec, chord_at, voicings, need_chord)]
    elif "strum" in v:
        voicing = voice_chord(need_chord(ev.begin), lo, hi, voicings.get(track.name),
                              str(v.get("voicing", "close")))
        voicings[track.name] = voicing
        pitches = voicing
    else:
        return []
    if v.get("power") and len(pitches) == 1:
        pitches = [pitches[0], pitches[0] + 7, pitches[0] + 12]
    return [(min(127, max(0, p + shift)), min(127, velocity), length) for p in pitches]


def _walk_note(ev: Event, track: Track, key: Key, sec: Section,
               chord_at: Callable[[Fraction], Chord | None], state: dict[str, list[int]],
               need_chord: Callable[[Fraction], Chord]) -> int:
    """One note of a walking bass line (docs/12, docs/16).

    First note of a chord: its root (or slash bass), nearest the previous note.
    Last note before the next chord: a chromatic approach to the next root, from the
    side the line is coming from. In between: chord tones (else scale steps) moving
    toward the next root by at most a 4th.
    """
    lo, hi = track.register
    hi = min(hi, lo + 19)                          # walk in the lower part of the register
    span = sec.chords.event_at(ev.begin) if sec.chords is not None else None
    chord = need_chord(ev.begin)
    nxt = chord_at(span.end) if span is not None else None
    nxt = nxt or chord
    prev = (state.get(f"walk:{track.name}") or [None])[0]

    def nearest(pc: int, ref: float) -> int:
        options = range(lowest_at_or_above(pc, lo), hi + 1, 12)
        return min(options, key=lambda p: abs(p - ref)) if options else lowest_at_or_above(pc, lo)

    ref = prev if prev is not None else lo + 7
    starts_chord = span is None or ev.begin == span.begin
    ends_chord = span is None or ev.end >= span.end
    if starts_chord:
        pitch = nearest(chord.bass if chord.bass is not None else chord.root, ref)
    elif ends_chord:
        target = nearest(nxt.root, ref)
        side = 1 if ref > target else -1
        pitch = target + side
        if not lo <= pitch <= hi or pitch == prev:
            pitch = target - side
    else:
        target = nearest(nxt.root, ref)
        direction = (1 if target > ref else -1) if target != ref else (1 if ref < (lo + hi) / 2 else -1)
        chord_pcs = set(chord.pcs)
        scale_pcs = {(key.tonic + i) % 12 for i in key.scale}

        def moves(pcs: set[int], max_step: int) -> list[int]:
            return [p for p in range(lo, hi + 1)
                    if p % 12 in pcs and 0 < (p - ref) * direction <= max_step and p != target]

        options = moves(chord_pcs, 5) or moves(scale_pcs | chord_pcs, 2) or \
            [p for p in range(lo, hi + 1) if p % 12 in chord_pcs and p != ref]
        pitch = min(options, key=lambda p: abs(p - ref))
    state[f"walk:{track.name}"] = [pitch]
    return pitch


# ---------- feel ----------

def _swing(song: Song, notes: list[Note], meter: tuple[int, int], origin: float = 0.0) -> list[Note]:
    """Delay every second 8th (or 16th). `origin` is where the section starts: the grid counts
    from there. Meters on an 8th/16th unit are not swung: 6/8 and 12/8 already have the
    triplet feel, and 5/8, 7/8 are played straight."""
    if abs(song.swing - 0.5) < 1e-9 or meter[1] >= 8:
        return notes
    unit = 0.5 if song.swing_unit == 8 else 0.25
    shift = (song.swing - 0.5) * 2 * unit
    out = []
    for n in notes:
        k = ((n.start - origin) % 1) / unit
        if abs(k - round(k)) < 1e-6 and round(k) % 2 == 1:
            n = Note(n.track, n.start + shift, n.duration, n.pitch, n.velocity)
        out.append(n)
    return out


def _humanize(song: Song, notes: list[Note], spans: list[SectionSpan]) -> list[Note]:
    out = []
    rngs: dict[str, random.Random] = {}
    for n in notes:
        t = song.tracks[n.track]
        if not t.humanize_ms and not t.humanize_velocity:
            out.append(n)
            continue
        rng = rngs.setdefault(n.track, random.Random(f"{song.seed}/{n.track}"))
        tempo = next((s.tempo for s in reversed(spans) if s.start_beat <= n.start), song.tempo)
        offset = rng.uniform(-t.humanize_ms, t.humanize_ms) / 1000 * tempo / 60
        velocity = n.velocity + rng.randint(-t.humanize_velocity, t.humanize_velocity)
        out.append(Note(n.track, max(0.0, n.start + offset), n.duration, n.pitch,
                        min(127, max(1, velocity))))
    return out


# ---------- output ----------

def summary(r: Rendering) -> str:
    """Human/agent-readable overview of the arrangement."""
    song = r.song
    num, den = song.meter

    def clock(sec: float) -> str:
        return f"{int(sec // 60)}:{int(sec % 60):02d}"

    lines = [
        f'"{song.title}" — {song.key.name}, {song.tempo:g} BPM, {num}/{den}'
        + (f", swing {song.swing:g}/{song.swing_unit}" if abs(song.swing - 0.5) > 1e-9 else ""),
        f"{sum(s.bars for s in r.sections)} bars, {clock(r.total_seconds)}, {len(r.notes)} notes",
        "",
    ]
    width = max(len(s.name) for s in r.sections)
    for i, s in enumerate(r.sections, 1):
        sec = song.sections[s.name]
        bars = " | ".join(" ".join(c) if c else "%" for c in s.chords_by_bar) or "(no chords)"
        extra = []
        if sec.key is not None:
            extra.append(f"key {s.key.name}")
        if sec.meter is not None:
            extra.append(f"{s.meter[0]}/{s.meter[1]}")
        if s.tempo_to is not None:
            extra.append(f"{s.tempo:g}→{s.tempo_to:g} BPM")
        elif sec.tempo is not None:
            extra.append(f"{s.tempo:g} BPM")
        if sec.fills:
            extra.append("fill: " + ", ".join(sec.fills))
        lines.append(f"{i:>2}. {s.name:<{width}}  {s.bars:>2} bars  @{clock(s.start_seconds)}  | {bars} |")
        lines.append(f"    {'':<{width}}  tracks: {', '.join(s.tracks) or '-'}"
                     + (f"  ({'; '.join(extra)})" if extra else ""))
        if sec.lyrics:
            first = next((ln.strip() for ln in sec.lyrics.strip().splitlines() if ln.strip()), "")
            lines.append(f"    {'':<{width}}  lyrics: {first}{' …' if sec.lyrics.strip().count(chr(10)) else ''}")
    return "\n".join(lines)


def write_midi(r: Rendering, path: str | Path, ticks_per_beat: int = 480) -> Path:
    song = r.song
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mid = mido.MidiFile(type=1, ticks_per_beat=ticks_per_beat)

    def tick(beats: float | Fraction) -> int:
        return max(0, round(float(beats) * ticks_per_beat))

    # Conductor track: tempo, meter, key, section markers and chord symbols.
    meta: list[tuple[int, int, mido.MetaMessage]] = [
        (0, 0, mido.MetaMessage("track_name", name=song.title)),
    ]
    tempo = key = meter = None
    for s in r.sections:
        t = tick(s.start_beat)
        if s.meter != meter:
            meta.append((t, 0, mido.MetaMessage("time_signature", numerator=s.meter[0],
                                                denominator=s.meter[1])))
            meter = s.meter
        for start, _, bpm in s.tempo_steps():
            if bpm != tempo:
                meta.append((tick(start), 1, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))))
                tempo = bpm
        if s.key != key:
            meta.append((t, 1, mido.MetaMessage("key_signature", key=s.key.midi_signature)))
            key = s.key
        meta.append((t, 2, mido.MetaMessage("marker", text=s.name)))
        for beat, sym in s.chord_changes:
            meta.append((tick(beat), 3, mido.MetaMessage("text", text=sym)))
    mid.tracks.append(_to_track(meta))

    channels = _assign_channels(song)
    by_track: dict[str, list[Note]] = {}
    for n in r.notes:
        by_track.setdefault(n.track, []).append(n)
    for name, track in song.tracks.items():
        if name not in by_track:
            continue
        ch = channels[name]
        msgs: list[tuple[int, int, mido.Message | mido.MetaMessage]] = [
            (0, 0, mido.MetaMessage("track_name", name=name)),
            (0, 1, mido.Message("program_change", channel=ch, program=track.program_number)),
        ]
        for start, end, n in _without_overlaps(by_track[name], tick):
            msgs.append((start, 3, mido.Message("note_on", channel=ch, note=n.pitch, velocity=n.velocity)))
            msgs.append((end, 2, mido.Message("note_off", channel=ch, note=n.pitch, velocity=0)))
        mid.tracks.append(_to_track(msgs))

    mid.save(path)
    return path


def _assign_channels(song: Song) -> dict[str, int]:
    channels: dict[str, int] = {}
    free = [c for c in range(16) if c != 9]
    for name, t in song.tracks.items():
        if t.is_drums:
            channels[name] = 9
        elif t.channel is not None:
            channels[name] = t.channel
    taken = set(channels.values())
    free = [c for c in free if c not in taken]
    for name in song.tracks:
        if name not in channels:
            if not free:
                raise RenderError("more than 15 melodic tracks: set Track.channel to share channels")
            channels[name] = free.pop(0)
    return channels


def _without_overlaps(notes: list[Note], tick: Callable[[float], int]) -> list[tuple[int, int, Note]]:
    """Ticks per note, cutting a note short when the same pitch starts again before it ends."""
    out = []
    by_pitch: dict[int, list[Note]] = {}
    for n in notes:
        by_pitch.setdefault(n.pitch, []).append(n)
    for group in by_pitch.values():
        group.sort(key=lambda n: n.start)
        for i, n in enumerate(group):
            start, end = tick(n.start), tick(n.start + n.duration)
            if i + 1 < len(group):
                end = min(end, tick(group[i + 1].start))
            if end > start:
                out.append((start, end, n))
    return out


def _to_track(events: list[tuple[int, int, mido.Message | mido.MetaMessage]]) -> mido.MidiTrack:
    track = mido.MidiTrack()
    now = 0
    for t, _, msg in sorted(events, key=lambda e: (e[0], e[1])):
        track.append(msg.copy(time=t - now))
        now = t
    return track
