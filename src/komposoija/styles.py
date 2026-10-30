"""Style profiles: instrument sounds, registers, feel and humanisation per genre.

`Song(style="jazz")` applies a profile; explicit `swing=`/`swing_unit=`/`crashes=`
arguments and later `song.track(...)` calls override it. See docs/14 and docs/16-20.
"""

from __future__ import annotations

from typing import Any

STYLES: dict[str, dict[str, Any]] = {
    "pop_rock": {
        "swing": 0.5, "swing_unit": 8, "crashes": True, "tracks": {},
    },
    "jazz": {
        # Medium-tempo swing; fast tunes are straighter (0.55-0.6), ballads looser.
        "swing": 0.64, "swing_unit": 8, "crashes": False,
        "tracks": {
            "drums": {"velocity": 80, "humanize_ms": 6, "humanize_velocity": 8},
            "bass": {"program": "acoustic_bass", "register": (28, 52), "humanize_ms": 5, "humanize_velocity": 6},
            "keys": {"program": "piano", "register": (50, 74), "velocity": 70, "humanize_ms": 8,
                     "humanize_velocity": 10},
            "guitar": {"program": "jazz_guitar", "register": (40, 64), "velocity": 70, "humanize_ms": 6},
            "lead": {"program": "tenor_sax", "register": (50, 79), "humanize_ms": 10, "humanize_velocity": 8},
            "horns": {"program": "trumpet", "register": (58, 82), "velocity": 85},
        },
    },
    "blues": {
        "swing": 0.66, "swing_unit": 8, "crashes": True,
        "tracks": {
            "drums": {"humanize_ms": 6, "humanize_velocity": 8},
            "bass": {"program": "finger_bass", "register": (28, 52), "humanize_ms": 5},
            "keys": {"program": "piano", "register": (52, 76), "velocity": 75, "humanize_ms": 6},
            "organ": {"program": "rock_organ", "register": (55, 79), "velocity": 70},
            "guitar": {"program": "overdrive_guitar", "register": (40, 64), "humanize_ms": 6},
            "lead": {"program": "harmonica", "register": (60, 84), "humanize_ms": 10},
        },
    },
    "funk": {
        # Tight 16th-note pocket with a touch of 16th swing.
        "swing": 0.54, "swing_unit": 16, "crashes": True,
        "tracks": {
            "drums": {"humanize_ms": 3, "humanize_velocity": 6},
            "bass": {"program": "finger_bass", "register": (28, 52), "humanize_ms": 3},
            "keys": {"program": "clav", "register": (55, 79), "velocity": 85},
            "guitar": {"program": "clean_guitar", "register": (55, 76), "velocity": 85, "humanize_ms": 3},
            "horns": {"program": "brass", "register": (58, 82), "velocity": 100},
        },
    },
    "reggae": {
        "swing": 0.56, "swing_unit": 8, "crashes": False,
        "tracks": {
            "drums": {"humanize_ms": 6, "humanize_velocity": 6},
            "bass": {"program": "finger_bass", "register": (28, 48), "velocity": 100, "humanize_ms": 5},
            "guitar": {"program": "clean_guitar", "register": (60, 79), "velocity": 80},
            "keys": {"program": "drawbar_organ", "register": (55, 76), "velocity": 70},
            "horns": {"program": "brass", "register": (58, 82), "velocity": 90},
        },
    },
    "metal": {
        "swing": 0.5, "swing_unit": 8, "crashes": True,
        "tracks": {
            # Register from D2 so drop-D riffs fit; power chords stack upward from there.
            "guitar": {"program": "distortion_guitar", "register": (38, 62), "velocity": 105},
            "guitar2": {"program": "distortion_guitar", "register": (38, 62), "velocity": 100},
            "bass": {"program": "pick_bass", "register": (26, 50), "velocity": 105},
            "lead": {"program": "overdrive_guitar", "register": (52, 88), "velocity": 100},
            "keys": {"program": "synth_strings", "register": (52, 76), "velocity": 70},
        },
    },
}


def style_profile(name: str) -> dict[str, Any]:
    if name not in STYLES:
        raise ValueError(f"unknown style {name!r}; known: {', '.join(STYLES)}")
    return STYLES[name]
