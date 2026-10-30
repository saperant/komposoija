"""Genre palettes: drums, bass, comping and progressions for jazz, blues, funk, reggae
and metal (docs/16-20). Use them with the matching style profile:

    song = Song(key="F major", tempo=160, style="jazz")
    head.chords = jazz.progressions.rhythm_a
    head.play(drums=jazz.drums.swing, bass=jazz.bass.walking, keys=jazz.comp.charleston)

All patterns are one bar per cycle. Unless a name says otherwise (`waltz` = 3/4,
`slow_12_8` = 12/8), they assume 4/4. Swing comes from the song (style profile),
so swung patterns are written in straight 8ths.
"""

from __future__ import annotations

from .notation import chords, ct, n, s, strum, walk
from .pattern import stack


class jazz:
    class drums:
        # Ride "ding, ding-a ding, ding-a" + hi-hat foot on 2 and 4 + feathered kick
        swing = stack(
            s("rd [rd rd] rd [rd rd]").velocity("85 [100 65] 85 [100 65]"),
            s("~ ph ~ ph").velocity(80),
            s("bd*4").velocity(35),
            s("~ [~ sd?0.6] ~ [~ sd?0.7]").velocity(50),     # sparse snare comping
        )
        two_feel = stack(s("rd [rd rd] rd [rd rd]").velocity("75 [90 55] 75 [90 55]"),
                         s("~ ph ~ ph").velocity(70), s("bd ~ bd ~").velocity(35))
        ballad = stack(s("rd [rd rd] rd [rd rd]").velocity("55 [65 40] 55 [65 40]"),
                       s("~ ph ~ ph").velocity(55))
        waltz = stack(s("rd [rd rd] rd").velocity("90 [70 55] 75"), s("~ ph ph").velocity(65),
                      s("bd ~ ~").velocity(40))                                        # 3/4
        bossa = stack(                                                                # straight 8ths
            s("hh*8").velocity("[70 50]*4"),
            s("<[rim ~ ~ rim ~ ~ rim ~] [~ ~ rim ~ ~ rim ~ ~]>").velocity(80),     # 2-bar clave
            s("[bd ~ ~ bd]*2").velocity(70),
        )
        trading_fill = s("[~ sd] [sd sd] [~ sd] [ht mt ft ~]").velocity("60 80 70 90")

    class bass:
        walking = walk("x*4").legato(0.95)
        two_feel = ct("0 2").octave("0 -1").legato(0.95)      # root, fifth below
        waltz = walk("x x x").legato(0.95)                       # 3/4
        bossa = ct("0@3 2 2@3 0").octave("0@3 -1 -1@3 0").legato(0.9)
        pedal = ct("0 ~ ~ [~ 0]").legato(0.9)

    class comp:
        charleston = strum("x ~ ~ x ~ ~ ~ ~").voicing("rootless").legato(0.8)   # beat 1 and the & of 2
        anticipation = strum("~ ~ ~ ~ ~ ~ ~ x").voicing("rootless").legato(2)   # push into the next bar
        sparse = strum("~ [~ x] ~ [x ~]").voicing("rootless").legato(0.7)
        freddie_green = strum("x*4").voicing("shell").velocity("[80 65]*2").legato(0.5)  # guitar
        whole = strum("x").voicing("rootless")
        waltz = strum("~ x x").voicing("rootless").legato(0.8)                           # 3/4
        bossa = strum("<[x ~ ~ x ~ ~ x ~] [~ ~ x ~ ~ x ~ ~]>").voicing("rootless").legato(0.8)

    class progressions:
        ii_v_i = chords("<ii7 V7 Imaj7 Imaj7>")
        ii_v_i_minor = chords("<iiø7 V7b9 i6 i6>")
        turnaround = chords("<[Imaj7 vi7] [ii7 V7]>")
        tritone_sub = chords("<ii7 bII7 Imaj7 Imaj7>")
        backdoor = chords("<iv7 bVII7 Imaj7 Imaj7>")
        rhythm_a = chords("<[Imaj7 VI7] [ii7 V7] [iii7 VI7] [ii7 V7] [Imaj7 I7] [IVmaj7 #iv°7] [Imaj7 VI7] [ii7 V7]>")
        rhythm_bridge = chords("<III7@2 VI7@2 II7@2 V7@2>")
        blues = chords("<I7 IV7 I7 [v7 I7] IV7 #iv°7 I7 VI7 ii7 V7 [I7 VI7] [ii7 V7]>")
        minor_blues = chords("<i7 i7 i7 i7 iv7 iv7 i7 i7 bVI7 V7 i7 [iiø7 V7]>")
        modal_aaba = chords("<i7@16 #i7@8 i7@8>")                  # 32 bars, Dorian vamps


class blues:
    class drums:
        shuffle = stack(s("hh*8").velocity("[90 60]*4"), s("~ sd ~ sd").velocity(105),
                        s("bd ~ bd ~").velocity(95))
        texas = stack(s("rd*8").velocity("[95 65]*4"),
                      s("[~ sd] [sd sd] [~ sd] [sd sd]").velocity("[~ 40] [110 40] [~ 40] [110 40]"),
                      s("bd ~ bd ~"))
        rock_blues = stack(s("hh*8").velocity("[90 65]*4"), s("~ sd ~ sd").velocity(110),
                           s("bd ~ [bd bd] ~"))
        slow_12_8 = stack(s("hh*12").velocity("[90 55 65]*4"),                               # 12/8
                          s("~ ~ ~ sd ~ ~ ~ ~ ~ sd ~ ~").velocity(100),
                          s("bd ~ ~ ~ ~ ~ bd ~ ~ ~ ~ [~ bd]").velocity(90))
        stop_time = s("[cr, bd] ~ ~ ~").velocity(115)             # hit on 1, then silence

    class bass:
        boogie = ct("0*8").transpose("[0 4 7 9 10 9 7 4]").legato(0.85)   # 1-3-5-6-b7-6-5-3
        boogie_low = ct("0*8").transpose("[0 0 4 4 7 7 9 9]").legato(0.85)  # 1 1 3 3 5 5 6 6
        shuffle_roots = ct("0*8").octave("[0 0 0 1]*2").legato(0.8)
        walking = walk("x*4").legato(0.95)
        slow_12_8 = ct("[0 ~ 0]*4").transpose("[0 ~ 0] [4 ~ 4] [7 ~ 7] [9 ~ 7]").legato(0.9)  # 12/8
        stop_time = ct("0 ~ ~ ~").legato(0.3)

    class comp:
        boogie_shuffle = stack(ct("0*8"), ct("2*8").transpose("[0 2]*4")).legato(0.8)  # 5th-6th rhythm guitar
        stabs = strum("~ x ~ x").legato(0.25)
        triplets_12_8 = strum("x*12").velocity("[85 55 65]*4").legato(0.8)                # 12/8 piano
        organ = strum("x").voicing("open")
        stop_time = strum("x ~ ~ ~").legato(0.3)

    class progressions:
        twelve_bar = chords("<I7 I7 I7 I7 IV7 IV7 I7 I7 V7 IV7 I7 V7>")
        quick_change = chords("<I7 IV7 I7 I7 IV7 IV7 I7 I7 V7 IV7 I7 V7>")
        minor = chords("<i7 i7 i7 i7 iv7 iv7 i7 i7 bVI7 V7 i7 V7>")
        eight_bar = chords("<I7 V7 IV7 IV7 I7 V7 I7 V7>")
        jazz = jazz.progressions.blues
        turnaround = chords("<[I7 IV7] [I7 V7]>")


class funk:
    class drums:
        groove = stack(
            s("hh*16").velocity("[90 50 70 50]*4"),
            s("~ ~ ~ sd sd ~ ~ sd ~ sd ~ ~ sd ~ ~ sd").velocity("~ ~ ~ 35 110 ~ ~ 35 ~ 35 ~ ~ 110 ~ ~ 35"),
            s("bd ~ ~ bd ~ ~ ~ ~ ~ ~ bd ~ ~ bd ~ ~"),
        )
        the_one = stack(                                  # everything leans on beat 1
            s("hh*16").velocity("[95 45 70 45]*4"),
            s("~ ~ ~ ~ sd ~ ~ sd ~ sd ~ ~ sd ~ ~ ~").velocity("~ ~ ~ ~ 110 ~ ~ 40 ~ 40 ~ ~ 110 ~ ~ ~"),
            s("bd ~ ~ ~ ~ ~ ~ bd ~ ~ bd ~ ~ ~ ~ ~").velocity("120 ~ ~ ~ ~ ~ ~ 90 ~ ~ 100 ~ ~ ~ ~ ~"),
        )
        open_hat = stack(
            s("hh hh hh hh hh hh oh ~ hh hh hh hh hh hh oh ~").velocity("[90 50 70 50 90 50 95 ~]*2"),
            s("~ sd ~ sd").velocity(110),
            s("bd ~ ~ bd ~ ~ bd ~ ~ ~ bd ~ ~ ~ ~ ~"),
        )
        linear = s("bd hh sd hh hh bd hh sd bd hh sd hh hh bd hh sd").velocity(
            "110 60 110 50 70 95 50 40 100 60 110 50 70 95 50 40")       # one limb at a time

    class bass:
        syncopated = ct("0 ~ ~ 0 ~ ~ 2 ~ 0 ~ ~ 0 3 ~ 2 ~").legato(0.5)
        octave_pops = ct("0 ~ 0 ~ ~ 0 ~ ~ 0 ~ ~ 0 ~ ~ 0 ~").octave("0 ~ 1 ~ ~ 0 ~ ~ 1 ~ ~ 0 ~ ~ 1 ~") \
            .velocity("115 ~ 100 ~ ~ 90 ~ ~ 100 ~ ~ 90 ~ ~ 100 ~").legato(0.4)
        ghosts = ct("0 0 ~ 0 ~ 0 0 ~ 0 ~ 0 0 ~ 0 3 2").velocity(
            "115 35 ~ 90 ~ 35 100 ~ 90 ~ 35 100 ~ 90 95 85").legato(0.45)
        the_one = ct("0 ~ ~ ~ ~ ~ ~ 0 ~ ~ 0 ~ ~ ~ 3 2").velocity("125 ~ ~ ~ ~ ~ ~ 90 ~ ~ 95 ~ ~ ~ 85 90").legato(0.6)

    class comp:
        scratch = strum("x*16").velocity("[105 35 60 35]*4").legato(0.25)        # muted 16ths, accents
        chank = strum("[~ ~ x ~] [~ ~ ~ x] [~ ~ x ~] [~ x ~ ~]").legato(0.2)
        clav = strum("[x ~ x x] [~ x ~ x] [x ~ x x] [~ x x ~]").velocity(
            "[100 ~ 70 80] [~ 90 ~ 75] [100 ~ 70 80] [~ 90 80 ~]").legato(0.3)
        horn_hits = strum("~ ~ ~ ~ ~ ~ x ~ ~ ~ ~ ~ ~ x ~ ~").legato(0.3)
        horn_stab_one = strum("x ~ ~ ~").legato(0.25)

    class progressions:
        vamp = chords("I9")
        dorian_vamp = chords("<i7@3 IV9>")
        two_chord = chords("<I9 IV9>")
        bridge = chords("<IV9@2 V9@2>")
        minor_groove = chords("<i9 i9 bVII9 IV9>")


class reggae:
    class drums:
        one_drop = stack(s("hh*8").velocity("[75 55]*4"), s("~ ~ rim ~").velocity(105),
                         s("~ ~ bd ~").velocity(110))                       # kick + rim only on 3
        rockers = stack(s("hh*8").velocity("[75 55]*4"), s("~ ~ rim ~").velocity(100),
                        s("bd ~ bd ~").velocity(105))                       # kick on 1 and 3
        steppers = stack(s("hh*8").velocity("[70 55]*4"), s("~ ~ rim ~").velocity(100),
                         s("bd*4").velocity(105))                           # kick on every beat
        ska = stack(s("hh*8").velocity("[55 90]*4"), s("~ sd ~ sd").velocity(100), s("bd ~ bd ~"))
        fill = s("~ ~ ~ [sd sd sd ~]").velocity(90)

    class bass:
        one_drop = ct("~ 0 [~ 0] [2 1]").legato(0.9)        # leaves beat 1 open
        rockers = ct("0 ~ [~ 0] [2 0]").legato(0.9)
        steppers = ct("0*4").legato(0.85)
        melodic = ct("<[0 ~ [~ 1] 2] [3 ~ [2 1] ~]>").legato(0.9)   # 2-bar riddim line
        ska_walk = walk("x*4").legato(0.8)

    class comp:
        skank = strum("~ x ~ x").legato(0.25)                  # guitar on 2 and 4
        double_skank = strum("~ [x x] ~ [x x]").legato(0.2)
        ska_skank = strum("[~ x]*4").legato(0.3)               # off-beat 8ths (fast ska)
        bubble = strum("[~ x] [x x] [~ x] [x x]").velocity("[~ 85] [55 75] [~ 85] [55 75]").legato(0.4)
        horn_line = n("<[~ 4 ~ 2] [4 ~ ~ ~]>").legato(0.8)    # scale degrees: a simple answer phrase

    class progressions:
        two_chord = chords("<I IV>")
        roots = chords("<I IV V IV>")
        minor_vamp = chords("<i iv>")
        minor_bvii = chords("<i bVII>")
        rocksteady = chords("<I vi IV V>")


class metal:
    class drums:
        heavy = stack(s("rd*8").velocity("[105 80]*4"), s("~ sd ~ sd").velocity(122),
                      s("bd ~ [bd bd] ~").velocity(115))
        double_kick = stack(s("cr*4").velocity(95), s("~ sd ~ sd").velocity(122),
                            s("bd*16").velocity("[115 95]*8"))
        gallop = stack(s("cr*4").velocity(90), s("~ sd ~ sd").velocity(120),
                       s("[bd ~ bd bd]*4").velocity(110))
        thrash = stack(s("hh*8").velocity(105), s("[~ sd]*4").velocity(118), s("[bd ~]*4").velocity(112))
        blast = stack(s("[bd sd]*8").velocity(115), s("cr*8").velocity(85))
        breakdown = stack(s("china*4").velocity(105), s("~ ~ sd ~").velocity(125),
                          s("bd ~ ~ bd ~ ~ bd ~ ~ ~ bd ~ ~ bd ~ ~").velocity(118))
        doom = stack(s("rd*4").velocity(85), s("~ ~ sd ~").velocity(122), s("bd ~ ~ ~ ~ ~ bd ~").velocity(115))

    class bass:
        eighths = ct("0*8").legato(0.85)
        sixteenths = ct("0*16").legato(0.8)
        gallop = ct("[0 ~ 0 0]*4").legato(0.7)
        breakdown = ct("0 ~ ~ 0 ~ ~ 0 ~ ~ ~ 0 ~ ~ 0 ~ ~").legato(0.7)
        sustained = ct("0").legato(1)

    class comp:   # rhythm guitar; all power chords
        chug16 = strum("x*16").voicing("power").velocity("[115 85 100 85]*4").legato(0.45)
        chug8 = strum("x*8").voicing("power").velocity("[115 95]*4").legato(0.55)
        gallop = strum("[x ~ x x]*4").voicing("power").legato(0.5)
        breakdown = strum("x ~ ~ x ~ ~ x ~ ~ ~ x ~ ~ x ~ ~").voicing("power").legato(0.6)
        sustained = strum("x").voicing("power")
        tremolo = ct("0*16").octave(1).legato(0.9)

    class riffs:  # scale degrees of the song key (e.g. "E phrygian"); add .power() for chords
        pedal = n("0 0 1 0 0 2 0 [3 2]").legato(0.6)                    # open-string pedal riff
        gallop = n("[0 ~ 0 0] [0 ~ 0 0] [5 ~ 5 5] [4 ~ 4 4]").legato(0.6)
        chromatic = ct("0*8").transpose("0 0 1 0 0 3 0 6").legato(0.6)  # root, b2, b3, tritone
        descending = n("<[0 ~ 0 6] [5 ~ 4 ~]>").legato(0.8)

    class progressions:
        aeolian = chords("<i bVI bVII i>")
        phrygian = chords("<i bII>")
        descent = chords("<i bVII bVI V>")
        epic = chords("<i bVI bIII bVII>")
        doom = chords("<i i bII bII>")
