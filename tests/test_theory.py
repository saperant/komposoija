import pytest

from komposoija.theory import (chord_tone, parse_chord, parse_key, parse_note, scale_degree,
                               voice_chord)

C = parse_key("C major")


@pytest.mark.parametrize("token, midi", [("c4", 60), ("a4", 69), ("e2", 40), ("f#2", 42), ("eb", 51), ("60", 60)])
def test_parse_note(token, midi):
    assert parse_note(token) == midi


@pytest.mark.parametrize("token, key, symbol", [
    ("I", "C", "C"), ("vi", "C", "Am"), ("V7", "C", "G7"), ("ii7", "C", "Dm7"), ("vii°", "C", "Bdim"),
    ("bVII", "C", "Bb"), ("bVI", "A minor", "F"), ("i", "A minor", "Am"), ("iv", "C", "Fm"),
    ("V/V", "C", "D"), ("V7/vi", "C", "E7"), ("IVadd9", "G", "Cadd9"), ("Isus4", "D", "Dsus4"),
    ("Am7", "G", "Am7"), ("D/F#", "G", "D/F#"), ("Bbmaj7", "F", "Bbmaj7"),
])
def test_parse_chord(token, key, symbol):
    k = parse_key(key)
    assert parse_chord(token, k).symbol(k) == symbol


def test_modes_and_signatures():
    assert parse_key("D mixolydian").midi_signature == "G"
    assert parse_key("E minor").midi_signature == "Em"
    assert parse_key("A dorian").midi_signature == "G"
    assert parse_key("F").prefers_flats


def test_chord_tones_and_scale_degrees():
    g7 = parse_chord("V7", C)
    assert [chord_tone(g7, i, 40) for i in range(5)] == [43, 47, 50, 53, 55]
    assert chord_tone(parse_chord("I", C), -1, 48) == 43          # fifth below the root
    assert chord_tone(parse_chord("D/F#", parse_key("G")), 0, 28) == 30  # slash bass
    assert [scale_degree(C, d, 60) for d in (0, 2, 4, 7, -1)] == [60, 64, 67, 72, 59]


def test_voice_leading_follows_docs_example():
    prev, out = None, []
    for numeral in ["I", "vi", "IV", "V"]:
        prev = voice_chord(parse_chord(numeral, C), 52, 76, prev)
        out.append(prev)
    assert out == [[60, 64, 67], [60, 64, 69], [60, 65, 69], [59, 62, 67]]


def test_power_and_open_voicings():
    assert voice_chord(parse_chord("I", parse_key("E")), 40, 64, style="power") == [40, 47, 52]
    v = voice_chord(parse_chord("I", C), 48, 84, style="open")
    assert len(v) == 3 and max(v) - min(v) > 12
