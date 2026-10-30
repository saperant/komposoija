"""komposoija — backing tracks as code, rendered to MIDI.

A song file builds a `Song` with sections, chords and parts written in
Strudel-style mini-notation, then `komposoija render song.py` writes MIDI.
"""

from . import playback
from .mini import MiniNotationError, mini
from .genres import blues, funk, jazz, metal, reggae
from .notation import chords, ct, n, note, s, strum, walk
from .pattern import Pattern, cat, euclid, pure, sequence, silence, stack
from .presets import FILLS, bass, comp, drums, fill
from .render import Rendering, RenderError, render, summary, write_midi
from .song import Section, Song, Track
from .styles import STYLES

__all__ = [
    "Song", "Section", "Track",
    "s", "note", "n", "ct", "strum", "walk", "chords", "mini",
    "Pattern", "stack", "sequence", "cat", "euclid", "pure", "silence",
    "drums", "bass", "comp", "fill", "FILLS", "STYLES",
    "jazz", "blues", "funk", "reggae", "metal",
    "render", "summary", "write_midi", "playback", "Rendering", "RenderError", "MiniNotationError",
]
