"""Jazz: a 32-bar AABA tune on rhythm changes, small-combo arrangement (docs/16).

Head in two-feel, then walking bass, a blowing chorus, trading fours, head out with a tag.
"""

from komposoija import *

song = Song(title="Blue Hour", key="Bb major", tempo=172, style="jazz")

# 1. STRUCTURE — head (AABA), solo chorus, trading, head out
intro = song.section("intro", bars=4, chords=jazz.progressions.turnaround)
a1 = song.section("A1", bars=8, chords=jazz.progressions.rhythm_a)
a2 = song.section("A2", bars=8, chords=jazz.progressions.rhythm_a)
bridge = song.section("bridge", bars=8, chords=jazz.progressions.rhythm_bridge)
a3 = song.section("A3", bars=8, chords=jazz.progressions.rhythm_a)
trade = song.section("trade", bars=8, chords=jazz.progressions.rhythm_a,
                     notes="trading fours: 4 bars sax, 4 bars drums")
tag = song.section("tag", bars=4, chords="<[iii7 VI7] [ii7 V7] Imaj7 Imaj7>")

# 2. MOOD — two-feel head, rootless piano comping, shell-voiced guitar
intro.play(keys=jazz.comp.whole, bass=jazz.bass.two_feel, drums=jazz.drums.two_feel)
head = dict(drums=jazz.drums.two_feel, bass=jazz.bass.two_feel, keys=jazz.comp.charleston)
a1.play(**head)
a2.play(**head)
bridge.play(drums=jazz.drums.swing, bass=jazz.bass.walking, keys=jazz.comp.sparse,
            guitar=jazz.comp.freddie_green)
a3.play(drums=jazz.drums.swing, bass=jazz.bass.walking, keys=jazz.comp.charleston,
        guitar=jazz.comp.freddie_green)

# 3. DETAILS — the head melody is written in chord tones so it fits every change
melody_a = ct("<[2 ~ 3 ~] [4 ~ 3 2] [1 ~ 2 ~] [3 ~ ~ ~] [2 1 0 ~] [1 ~ 2 3] [4 ~ 2 ~] [~ ~ ~ ~]>").legato(0.9)
melody_b = ct("<[3 ~ ~ 2] [1 ~ ~ ~] [3 ~ ~ 2] [1 ~ ~ ~] [2 ~ 3 ~] [4 ~ ~ ~] [3 2 1 ~] [0 ~ ~ ~]>").legato(0.9)
for sec in (a1, a2, a3):
    sec.play(lead=melody_a)
bridge.play(lead=melody_b)

solo = song.section("solo", like=a3)
solo.play(lead=ct("<[0 1 2 3] [4 3 2 1] [2 3 4 5] [6 ~ 4 ~] [5 4 3 2] [1 2 3 4] [3 ~ 1 ~] [0 ~ ~ ~]>")
          .legato(0.8).velocity("[95 70 85 70]*2"), keys=jazz.comp.sparse)
solo_b = song.section("solo_b", like=bridge)
solo_b.play(lead=ct("[0 2 1 3] [2 4 3 5]").legato(0.8).velocity("[95 70]*4"))

# Trading fours: sax for 4 bars, drums alone for 4 (bass and comping lay out)
trade.play(drums=jazz.drums.swing.last_of(8, jazz.drums.trading_fill), bass=jazz.bass.walking,
           keys=jazz.comp.sparse, lead=solo.parts["lead"])
for track in ("bass", "keys", "lead"):
    trade.parts[track] = trade.parts[track].filter(lambda ev: ev.begin % 8 < 4)

tag.play(drums=jazz.drums.swing, bass=jazz.bass.walking, keys=jazz.comp.whole, lead=ct("<~ ~ [2 ~ 1 ~] 0>"))
tag.fill(drums=fill(jazz.drums.swing, "[cr, bd] ~ ~ ~", beats=4), bass=ct("0"), keys=jazz.comp.whole)

song.arrange("intro A1 A2 bridge A3 solo solo solo_b solo trade A1 A2 bridge A3 tag")
