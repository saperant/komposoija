"""Blues: 12-bar shuffle in A with AAB verses, stop-time, a harmonica solo and a
classic ending (docs/17)."""

from komposoija import *

song = Song(title="Long Way Home", key="A major", tempo=108, style="blues")

# 1. STRUCTURE — each verse is one 12-bar chorus; the lyric form is A A B
intro = song.section("intro", bars=4, chords="<V7 IV7 I7 V7>",
                     notes="intro from the V: the last four bars of the form")
verse = song.section("verse", bars=12, chords=blues.progressions.quick_change, lyrics="""
    Woke up this morning, the rain was on my door
    Woke up this morning, the rain was on my door
    I packed my bag, I can't stay here no more
""")
verse2 = song.section("verse2", like=verse, lyrics="""
    Train keeps on rolling, it don't know my name
    Train keeps on rolling, it don't know my name
    Every town I pass through looks about the same
""")
stop = song.section("stop", bars=4, chords="<I7>", lyrics="""
    Well I got a dollar, and a song to sing
""", notes="stop-time: band hits beat 1, the vocal fills the gap")
stop_rest = song.section("stop_rest", bars=8, chords="<IV7 IV7 I7 I7 V7 IV7 I7 V7>", lyrics="""
    Got a dollar and a song to sing
    That's all I'm carrying, that's everything
""")
solo = song.section("solo", like=verse)
ending = song.section("ending", bars=3, chords="<[I7 IV7] [I7 bII7] I7>")

song.arrange("intro verse verse2 solo stop stop_rest verse ending")

# 2. MOOD — shuffle groove (the style profile swings the 8ths), boogie bass and guitar
groove = dict(drums=blues.drums.shuffle, bass=blues.bass.boogie, guitar=blues.comp.boogie_shuffle,
              keys=blues.comp.stabs)
intro.play(**groove)
verse.play(**groove)
verse2.play(**groove, organ=blues.comp.organ)
stop_rest.play(**groove)
solo.play(drums=blues.drums.texas, bass=blues.bass.walking, guitar=blues.comp.boogie_shuffle,
          organ=blues.comp.organ)
stop.play(drums=blues.drums.stop_time, bass=blues.bass.stop_time, guitar=blues.comp.stop_time,
          keys=blues.comp.stop_time)

# 3. DETAILS — call-and-response harmonica answers, solo, fills and the ending
answers = ct("<~ ~ [~ ~ 2 3] [4 ~ 2 0] ~ ~ [~ ~ 2 3] [4 ~ 2 0] ~ ~ [3 2 1 0] [0 ~ ~ ~]>").transpose(
    "<0 0 [0 0 3 0] 0>").legato(0.8)                       # blue minor 3rd on the way up
for sec in (verse, verse2):
    sec.play(lead=answers)
solo.play(lead=ct("<[0 2 3 2] [4 ~ 3 2] [0 ~ ~ 3] [2 1 0 ~] [3 4 3 2] [1 ~ 0 ~] [2 3 4 3] [2 ~ 0 ~] "
                  "[4 ~ 3 2] [3 ~ 2 1] [0 2 4 2] [3 ~ ~ ~]>").transpose("[0 0 3 0]*2").legato(0.75)
          .velocity("[100 80 90 80]*2"))
intro.fill(drums=fill(blues.drums.shuffle, "two_beats"))
verse.fill(drums=fill(blues.drums.shuffle, "one_beat"))
ending.play(drums=blues.drums.shuffle, bass=ct("0 0 [~ 0] ~"), guitar=blues.comp.stabs, keys=strum("x"))
ending.fill(drums=s("[cr, bd] ~ ~ ~"), bass=ct("0"), guitar=strum("x"), keys=strum("x"))
