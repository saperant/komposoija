"""Funk: a one-chord Dorian vamp built from interlocking parts, a bridge, a breakdown
and horn hits (docs/18)."""

from komposoija import *

song = Song(title="Tight Squeeze", key="E dorian", tempo=104, style="funk")

# 1. STRUCTURE — vamp sections, a bridge for contrast, a breakdown before the last vamp
intro = song.section("intro", bars=4, chords="<i7>")
vamp = song.section("vamp", bars=8, chords=funk.progressions.dorian_vamp, lyrics="""
    Hold it right there, don't you move
    Got to keep it tight, got to keep the groove
""")
bridge = song.section("bridge", bars=8, chords="<IV9 IV9 V9 V9 IV9 IV9 [bVII9 V9] V9>")
breakdown = song.section("breakdown", bars=8, chords="<i7>", notes="drums and bass only, then guitar returns")
hits = song.section("hits", bars=2, chords="<i7>")
vamp2 = song.section("vamp2", like=vamp)

song.arrange("intro vamp vamp bridge vamp2 breakdown vamp2 vamp2 hits")

# 2. MOOD — every instrument plays a small, syncopated part that locks with the others
intro.play(drums=funk.drums.the_one, guitar=funk.comp.scratch)
vamp.play(drums=funk.drums.groove, bass=funk.bass.ghosts, guitar=funk.comp.scratch, keys=funk.comp.clav)
vamp2.play(drums=funk.drums.open_hat, bass=funk.bass.octave_pops, guitar=funk.comp.chank,
           keys=funk.comp.clav, horns=funk.comp.horn_hits)
bridge.play(drums=funk.drums.the_one, bass=funk.bass.the_one, guitar=funk.comp.chank,
            horns=strum("x ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ [~ x] ~").legato(0.3))
breakdown.play(drums=funk.drums.linear, bass=funk.bass.syncopated)

# 3. DETAILS — guitar returns halfway through the breakdown; unison hits to end
breakdown.play(guitar=funk.comp.scratch.filter(lambda ev: ev.begin >= 4))
hits.play(drums=s("<[[cr, bd] ~ ~ [~ ~ sd ~]] [[cr, bd] ~ ~ ~]>").velocity(120),
          bass=ct("<[0 ~ ~ [~ ~ 3 ~]] [0 ~ ~ ~]>").legato(0.4),
          horns=strum("<[x ~ ~ [~ ~ x ~]] [x ~ ~ ~]>").legato(0.3),
          guitar=strum("<[x ~ ~ [~ ~ x ~]] [x ~ ~ ~]>").legato(0.3))
vamp.fill(drums=fill(funk.drums.groove, "[sd ~ sd sd] [~ sd ~ [cr, bd]]", beats=2))
bridge.fill(drums=fill(funk.drums.the_one, "build"))
