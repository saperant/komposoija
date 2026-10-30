from fractions import Fraction as F

import pytest

from komposoija import MiniNotationError, chords, ct, note, s


def onsets(pattern, begin=0, end=1, key="note"):
    return [(ev.begin, ev.end, ev.value.get(key)) for ev in pattern.query(begin, end)]


def test_sequence_divides_the_cycle():
    assert onsets(note("c3 d3 e3 f3")) == [
        (F(0), F(1, 4), 48), (F(1, 4), F(1, 2), 50), (F(1, 2), F(3, 4), 52), (F(3, 4), F(1), 53)]


def test_rests_and_subsequences():
    assert onsets(s("bd ~ [sd sd] -"), key="drum") == [
        (F(0), F(1, 4), 36), (F(1, 2), F(5, 8), 38), (F(5, 8), F(3, 4), 38)]


def test_alternation_advances_per_cycle_and_nests():
    got = [v for _, _, v in onsets(note("<c3 <e3 g3>>"), 0, 4)]
    assert got == [48, 52, 48, 55]


def test_alternation_weights_are_cycles():
    got = [ev.value["chord"] for ev in chords("<I IV@2 V>").query(0, 4)]
    assert got == ["I", "IV", "IV", "V"]


def test_fast_slow_replicate_weight():
    assert len(s("hh*8").query(0, 1)) == 8
    assert onsets(note("c3/2"), 0, 2) == [(F(0), F(2), 48)]
    assert [v for _, _, v in onsets(note("c3!3 e3"))] == [48, 48, 48, 52]
    assert onsets(note("c3@3 e3")) == [(F(0), F(3, 4), 48), (F(3, 4), F(1), 52)]
    assert [v for _, _, v in onsets(note("c3 ! e3"))] == [48, 48, 52]


def test_polyphony_with_comma():
    got = sorted(v for _, _, v in onsets(note("[c3, e3, g3]")))
    assert got == [48, 52, 55]


def test_euclid_is_bjorklund():
    starts = [ev.begin * 8 for ev in s("bd(3,8)").query(0, 1)]
    assert starts == [0, 3, 6]
    starts = [ev.begin * 8 for ev in s("bd(5,8)").query(0, 1)]
    assert starts == [0, 2, 3, 5, 6]


def test_degrade_is_deterministic():
    a = [ev.begin for ev in s("hh*16?").query(0, 4)]
    b = [ev.begin for ev in s("hh*16?").query(0, 4)]
    assert a == b and 0 < len(a) < 64


def test_slash_inside_atoms_vs_slow():
    assert [ev.value["chord"] for ev in chords("V/V C/E").query(0, 1)] == ["V/V", "C/E"]


def test_chord_tone_atoms():
    assert [ev.value for ev in ct("0 -1 a").query(0, 1)] == [{"ct": 0}, {"ct": -1}, {"approach": True}]


def test_patterned_controls_are_sampled_at_onsets():
    vel = [ev.value["velocity"] for ev in s("hh*4").velocity("[100 50]*2").query(0, 1)]
    assert vel == [100, 50, 100, 50]


@pytest.mark.parametrize("text", ["bd sx", "[bd sd", "bd ]", "bd(3,8"])
def test_errors_point_at_the_problem(text):
    with pytest.raises(MiniNotationError):
        s(text)


def test_invalid_chord_is_rejected_early():
    with pytest.raises(MiniNotationError, match="unknown chord suffix"):
        chords("I Vfoo")
