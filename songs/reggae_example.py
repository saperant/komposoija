"""Reggae: one-drop verses, rockers chorus, a dub breakdown and steppers outro (docs/19)."""

from komposoija import *

song = Song(title="Sunday Riddim", key="G major", tempo=74, style="reggae")

# 1. STRUCTURE
intro = song.section("intro", bars=4, chords=reggae.progressions.two_chord)
verse = song.section("verse", bars=8, chords=reggae.progressions.two_chord, lyrics="""
    Sunday morning, sun upon the hill
    Every little thing is standing still
""")
chorus = song.section("chorus", bars=8, chords=reggae.progressions.rocksteady, lyrics="""
    Let it roll, let it roll
    Let the rhythm take control
""")
dub = song.section("dub", bars=8, chords=reggae.progressions.two_chord,
                   notes="dub breakdown: instruments drop in and out, riddim carries it")
outro = song.section("outro", bars=8, chords=reggae.progressions.rocksteady)

song.arrange("intro verse chorus verse chorus dub chorus outro")

# 2. MOOD — riddim section first (drums + bass), skank and organ bubble on top
intro.play(drums=reggae.drums.one_drop, guitar=reggae.comp.skank, keys=reggae.comp.bubble)
verse.play(drums=reggae.drums.one_drop, bass=reggae.bass.melodic, guitar=reggae.comp.skank,
           keys=reggae.comp.bubble)
chorus.play(drums=reggae.drums.rockers, bass=reggae.bass.rockers, guitar=reggae.comp.double_skank,
            keys=reggae.comp.bubble, horns=reggae.comp.horn_line)
outro.play(drums=reggae.drums.steppers, bass=reggae.bass.steppers, guitar=reggae.comp.skank,
           keys=reggae.comp.bubble, horns=reggae.comp.horn_line)

# 3. DETAILS — dub: bass and drums, the skank only in bars 3-4 and 7-8
dub.play(drums=reggae.drums.one_drop, bass=reggae.bass.melodic,
         guitar=reggae.comp.skank.filter(lambda ev: ev.begin % 4 >= 2))
for sec in (verse, chorus):
    sec.fill(drums=fill(reggae.drums.one_drop, "~ ~ ~ [sd sd sd ~]", beats=4))
