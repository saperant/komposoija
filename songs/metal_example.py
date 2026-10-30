"""Heavy metal: Phrygian riffs in E, gallops, double kick, a solo and a breakdown (docs/20)."""

from komposoija import *

song = Song(title="Iron Tide", key="E phrygian", tempo=168, style="metal")

# 1. STRUCTURE — riff-driven: the riffs come first, vocals ride on top
intro = song.section("intro", bars=4, chords=metal.progressions.doom)
riff = song.section("riff", bars=8, chords="<i>")
verse = song.section("verse", bars=8, chords=metal.progressions.phrygian, lyrics="""
    Black water rising, the harbour lights are gone
    Iron in the tide, and the tide goes on
""")
chorus = song.section("chorus", bars=8, chords=metal.progressions.epic, lyrics="""
    Iron tide, iron tide
    Nowhere left to hide
""")
solo = song.section("solo", bars=8, chords=metal.progressions.aeolian)
breakdown = song.section("breakdown", bars=8, chords="<i>", tempo=84,
                         notes="half the tempo for weight; china on quarters")
outro = song.section("outro", bars=4, chords="<i i bII i>")

song.arrange("intro riff verse chorus riff verse chorus solo breakdown riff outro")

# 2. MOOD — power chords everywhere; bass doubles the riffs
intro.play(drums=metal.drums.doom, guitar=metal.comp.sustained, bass=metal.bass.sustained,
           keys=strum("x"))
riff.play(drums=metal.drums.gallop, guitar=metal.riffs.gallop.power(), guitar2=metal.riffs.gallop.power(),
          bass=metal.riffs.gallop)
verse.play(drums=metal.drums.thrash, guitar=metal.comp.chug16, guitar2=metal.riffs.pedal,
           bass=metal.bass.sixteenths)
chorus.play(drums=metal.drums.double_kick, guitar=metal.comp.chug8, guitar2=metal.comp.sustained,
            bass=metal.bass.eighths, keys=strum("x"))
solo.play(drums=metal.drums.heavy, guitar=metal.comp.chug8, bass=metal.bass.eighths)
breakdown.play(drums=metal.drums.breakdown, guitar=metal.comp.breakdown, guitar2=metal.comp.breakdown,
               bass=metal.bass.breakdown)
outro.play(drums=metal.drums.doom, guitar=metal.comp.sustained, bass=metal.bass.sustained)

# 3. DETAILS — a scale-degree solo with tremolo bursts, fills into every chorus
solo.play(lead=n("<[7 8 9 8] [7 ~ 5 4] [5 6 7 9] [10 ~ 9 7] [8 7 5 4] [5 ~ 4 2] [4 5 7 8] [7*4 ~]>")
          .legato(0.8).velocity("[110 85 100 85]*2"))
verse.fill(drums=fill(metal.drums.thrash, "full"))
riff.fill(drums=fill(metal.drums.gallop, "[sd sd sd sd] [ht ht mt mt] [ft ft ft ft] [cr, bd]", beats=4))
outro.fill(drums=s("[cr, bd] ~ ~ ~"), guitar=metal.comp.sustained, bass=metal.bass.sustained)
