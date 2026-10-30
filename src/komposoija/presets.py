"""Ready-made grooves, bass lines and comping patterns (see docs/11-13).

Pick presets in the "mood" step, then refine them or replace them with your own
patterns in the "details" step. All patterns are one bar of 4/4 per cycle.
"""

from __future__ import annotations

from fractions import Fraction

from .notation import ct, n, s, strum
from .pattern import Pattern, stack


class drums:
    rock = stack(s("hh*8").velocity("[90 65]*4"), s("~ sd ~ sd").velocity(110), s("bd ~ [bd bd] ~"))
    rock_ride = stack(s("rd*8").velocity("[95 70]*4"), s("~ sd ~ sd").velocity(115), s("bd ~ [bd bd] ~"))
    rock16 = stack(s("hh*16").velocity("[90 55 75 55]*4"), s("~ sd ~ sd").velocity(110),
                   s("bd ~ ~ bd ~ ~ bd ~ bd ~ ~ ~ ~ ~ bd ~"))
    four_floor = stack(s("[hh oh]*4").velocity("[70 85]*4"), s("~ sd ~ sd").velocity(105), s("bd*4"))
    half_time = stack(s("hh*8").velocity("[85 60]*4"), s("~ ~ sd ~").velocity(115),
                      s("bd ~ ~ ~ ~ ~ bd ~ ~ ~ ~ ~ ~ ~ ~ ~"))
    punk = stack(s("hh*8").velocity(100), s("[~ sd]*4").velocity(110), s("bd*4"))
    shuffle = stack(s("[hh ~ hh]*4").velocity("[85 ~ 60]*4"), s("~ sd ~ sd").velocity(105), s("bd ~ bd ~"))
    funk = stack(
        s("hh*16").velocity("[85 50 70 50]*4"),
        s("~ ~ ~ sd sd ~ ~ sd ~ sd ~ ~ sd ~ ~ sd").velocity("~ ~ ~ 35 110 ~ ~ 35 ~ 35 ~ ~ 110 ~ ~ 35"),
        s("bd ~ ~ bd ~ ~ ~ ~ ~ ~ bd ~ ~ bd ~ ~"),
    )
    motown = stack(s("hh*8").velocity(70), s("~ [sd, tb] ~ [sd, tb]").velocity(105), s("bd ~ bd ~"))
    one_drop = stack(s("hh*8").velocity("[75 55]*4"), s("~ ~ rim ~").velocity(100), s("~ ~ bd ~"))
    ballad = stack(s("hh*8").velocity("[65 45]*4"), s("~ rim ~ rim").velocity(85), s("bd ~ [~ bd] ~").velocity(90))
    sidestick = stack(s("hh*8").velocity("[70 50]*4"), s("~ rim ~ rim").velocity(90), s("bd ~ bd ~").velocity(90))
    toms = stack(s("[ft ~ ft ft]*2").velocity(95), s("~ sd ~ sd").velocity(105), s("bd*4"))


# Fill bodies, keyed by name: (mini-notation, beats at the end of the bar).
FILLS: dict[str, tuple[str, int]] = {
    "one_beat": ("sd sd mt ft", 1),
    "two_beats": ("sd sd sd sd mt mt ft ft", 2),
    "full": ("sd sd sd sd ht ht ht ht mt mt mt mt ft ft ft ft", 4),
    "build": ("[sd sd] [sd sd] [sd sd sd sd] [sd sd sd sd]", 4),
    "triplets": ("[sd sd sd] [ht ht ht] [mt mt mt] [ft ft ft]", 4),
    "stop": ("~", 1),
}


def fill(groove: Pattern, kind: str = "one_beat", beats: float | None = None,
         beats_per_bar: int = 4) -> Pattern:
    """`groove` with its last beats replaced by a fill.

    `kind` is a name from FILLS or a drum mini-notation string (then give `beats`):
        fill(drums.rock, "two_beats")
        fill(drums.rock, "sd ~ sd [cr, bd]", beats=1)
    """
    if kind in FILLS:
        text, default_beats = FILLS[kind]
    else:
        text, default_beats = kind, 1
    b = beats if beats is not None else default_beats
    body = s(text)
    if kind == "build":
        body = body.velocity("70 85 100 115")
    return groove.end_with(body, Fraction(b).limit_denominator(64) / beats_per_bar)


class bass:
    roots = ct("0")
    halves = ct("0 0")
    quarters = ct("0*4")
    eighths = ct("0*8").velocity("[100 80]*4").legato(0.9)
    driving = ct("0!7 a").velocity("[100 80]*4").legato(0.9)         # 8ths + approach note
    root_fifth = ct("0 ~ 2 ~").octave("0 0 -1 0")                    # root, fifth below
    octaves = ct("0*8").octave("[0 1]*4").legato(0.7)                # disco
    kick_locked = ct("0 ~ ~ 0 ~ ~ 0 ~ 0 ~ ~ ~ ~ ~ 0 ~").legato(0.9)   # matches drums.rock16
    walking = ct("0 1 2 a")                                          # quarters, approach on 4
    boogie = ct("0*8").transpose("[0 4 7 9 10 9 7 4]")               # 1-3-5-6-b7-6-5-3
    pedal = n("0*8").legato(0.9)                                     # tonic pedal
    syncopated = ct("0 ~ ~ 0 ~ ~ 0 ~").legato(0.8)                   # tresillo 3+3+2


class comp:
    whole = strum("x")
    halves = strum("x x")
    quarters = strum("x*4").legato(0.9)
    eighths = strum("x*8").velocity("[90 70]*4").legato(0.9)
    pop_strum = strum("x ~ x x ~ x x x").velocity("100 ~ 80 75 ~ 85 80 75")   # D-DU-UDU
    offbeat = strum("[~ x]*4").legato(0.5)                                    # reggae/ska skank
    stabs = strum("~ x ~ x").legato(0.3)
    power_whole = strum("x").voicing("power")
    power8 = strum("x*8").voicing("power").velocity("[100 85]*4").legato(0.8)
    arp_up = ct("0 1 2 3 4 3 2 1").legato(1.5)
    arp_broken = ct("0 2 1 2 0 2 1 2").legato(1.5)
