import inspect
import runpy
from pathlib import Path

import pytest

from komposoija import (Pattern, Song, blues, chords, ct, funk, jazz, metal, n, reggae, render,
                        walk)
from komposoija.theory import parse_chord, parse_key, voice_chord

SONGS = sorted((Path(__file__).parent.parent / "songs").glob("*.py"))
GENRES = [jazz, blues, funk, reggae, metal]


def genre_patterns():
    for genre in GENRES:
        for group_name, group in vars(genre).items():
            if inspect.isclass(group):
                for name, pat in vars(group).items():
                    if isinstance(pat, Pattern):
                        yield f"{genre.__name__}.{group_name}.{name}", pat


@pytest.mark.parametrize("name, pattern", list(genre_patterns()), ids=lambda x: x if isinstance(x, str) else "")
def test_genre_pattern_has_events(name, pattern):
    assert pattern.query(0, 4), name


@pytest.mark.parametrize("path", SONGS, ids=lambda p: p.stem)
def test_song_files_render(path):
    song = runpy.run_path(str(path))["song"]
    r = render(song)
    assert r.notes and r.total_seconds > 30


# ---------- style profiles ----------

def test_style_profile_sets_instruments_and_feel():
    song = Song(style="jazz")
    assert song.swing == 0.64 and not song.crashes
    assert song.tracks["bass"].program == "acoustic_bass"
    assert "horns" in song.tracks


def test_explicit_arguments_override_the_style():
    song = Song(style="blues", swing=0.5, crashes=False)
    assert song.swing == 0.5 and song.crashes is False


def test_unknown_style():
    with pytest.raises(ValueError, match="unknown style"):
        Song(style="polka")


# ---------- jazz harmony ----------

@pytest.mark.parametrize("token, symbol", [
    ("V7b9", "G7b9"), ("V7alt", "G7alt"), ("iiø7", "Dm7b5"), ("bII7", "Db7"), ("#iv°7", "F#dim7"),
    ("I69", "C69"), ("IVmaj7#11", "Fmaj7#11"), ("V13", "G13"), ("ii9", "Dm9"), ("V9sus4", "G9sus4"),
])
def test_jazz_chord_symbols(token, symbol):
    c = parse_key("C")
    assert parse_chord(token, c).symbol(c) == symbol


def test_rootless_ii_v_i_voice_leads():
    f = parse_key("F")
    prev, out = None, []
    for numeral in ("ii7", "V7", "Imaj7"):
        prev = voice_chord(parse_chord(numeral, f), 50, 72, prev, "rootless")
        out.append(prev)
    # Gm7: A Bb D F -> C7: G Bb D E -> Fmaj7: G A C E (3rds and 7ths move by step)
    assert out == [[57, 58, 62, 65], [55, 58, 62, 64], [55, 57, 60, 64]]


def test_shell_voicing_is_root_third_seventh():
    g7 = voice_chord(parse_chord("V7", parse_key("C")), 40, 64, style="shell")
    assert sorted(p % 12 for p in g7) == [5, 7, 11]   # F, G, B


def test_walking_bass_roots_and_chromatic_approaches():
    song = Song(key="F major", style="jazz")
    song.section("a", bars=4, chords="<[ii7 V7] Imaj7 [vi7 II7] [ii7 V7]>").play(bass=walk("x*4"))
    song.section("b", bars=1, chords="I7").play(bass=walk("x*4"))
    song.arrange("a b")
    r = render(song)
    bass = [n_ for n_ in r.notes if n_.track == "bass"]
    roots = {0: 7, 2: 0, 4: 5, 8: 2, 10: 7, 12: 7, 14: 0, 16: 5}       # beat -> root pitch class
    for beat, pc in roots.items():
        assert round(bass[beat].pitch) % 12 == pc
    # the note before every chord change is a semitone from the next root
    for beat, pc in roots.items():
        if beat:
            assert (bass[beat - 1].pitch - bass[beat].pitch) in (-1, 1)
    assert all(28 <= b.pitch <= 47 for b in bass)


# ---------- metal, blues meters ----------

def test_power_turns_notes_into_power_chords():
    song = Song(key="E phrygian", style="metal")
    song.section("r", bars=1).play(guitar=n("0 1").power())
    song.arrange("r")
    pitches = sorted(n_.pitch for n_ in render(song).notes)
    assert pitches == [40, 41, 47, 48, 52, 53]   # E5 and F5 power chords


def test_compound_meter_is_not_swung():
    song = Song(meter="12/8", style="blues", tempo=60)
    song.section("slow", bars=1, chords="I7").play(drums=blues.drums.slow_12_8)
    song.arrange("slow")
    r = render(song)
    hats = sorted(x.start for x in r.notes if x.pitch == 42)
    # 12 even eighths in a 6-beat bar (humanised by a few ms; a swing shift would be 0.16 beats)
    assert hats == pytest.approx([i * 0.5 for i in range(12)], abs=0.01)
    assert r.total_beats == 6


def test_lines_lead_into_the_next_section():
    song = Song(key="C")
    song.section("a", bars=1, chords="I").play(bass=ct("0 ~ ~ a"))
    song.section("b", bars=1, chords="IV").play(bass=ct("0"))
    song.arrange("a b")
    bass = [x.pitch for x in render(song).notes if x.track == "bass"]
    assert bass[1] in (bass[2] - 1, bass[2] + 1) and bass[2] % 12 == 5   # approach to F
