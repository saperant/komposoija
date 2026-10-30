"""Example song: shows the three stages of the composition flow.

Render:  komposoija render songs/example.py          (-> build/example.mid)
Live:    komposoija render songs/example.py --watch
"""

from komposoija import *

song = Song(title="Paper Lanterns", key="G major", tempo=116, swing=0.5)

# ---------------------------------------------------------------------------
# 1. STRUCTURE — sections derived from the lyrics (agent + human)
# ---------------------------------------------------------------------------

intro = song.section("intro", bars=4, energy=0.3)

verse = song.section("verse", bars=8, energy=0.4, lyrics="""
    We wrote our names on paper lanterns
    and let the river carry them away
    every light a little promise
    that we were never brave enough to say
""")

pre = song.section("pre", bars=4, energy=0.6, lyrics="""
    And the night keeps holding on
    holding on
""")

chorus = song.section("chorus", bars=8, energy=0.85, lyrics="""
    So light it up, light it up
    let it float above the water
    light it up, light it up
    we'll be shining even after
""")

bridge = song.section("bridge", bars=8, energy=0.55, lyrics="""
    When the last flame's gone
    I will still know where you are
""")

outro = song.section("outro", bars=4, energy=0.3)

song.arrange("intro verse pre chorus verse pre chorus bridge chorus chorus outro")

# ---------------------------------------------------------------------------
# 2. MOOD — key, tempo, progressions, groove presets
# ---------------------------------------------------------------------------

intro.chords = chords("<I IV vi IV>")
verse.chords = chords("<I V vi IV>")
pre.chords = chords("<IV V vi [IV V]>")      # faster harmonic rhythm in the last bar
chorus.chords = chords("<IV I V vi>")        # same four chords, new starting point
bridge.chords = chords("<vi IV I V vi IV bVII V>")  # borrowed bVII for colour
outro.chords = chords("<I IV I@2>")

intro.play(keys=comp.arp_broken, pad=comp.whole)
verse.play(drums=drums.sidestick, bass=bass.roots, keys=comp.halves)
pre.play(drums=drums.rock, bass=bass.eighths, keys=comp.quarters, pad=comp.whole)
chorus.play(drums=drums.rock_ride, bass=bass.driving, guitar=comp.power8,
            keys=comp.pop_strum, pad=comp.whole)
bridge.play(drums=drums.half_time, bass=bass.halves, keys=comp.arp_up, pad=comp.whole)
outro.play(keys=comp.whole, pad=comp.whole, bass=bass.roots)

# ---------------------------------------------------------------------------
# 3. DETAILS — fills, variations, hand-written parts
# ---------------------------------------------------------------------------

# Small fill every 4th bar of the verse, bigger fills into the next section.
verse.play(drums=drums.sidestick.last_of(4, fill(drums.sidestick, "one_beat")))
verse.fill(drums=fill(drums.sidestick, "two_beats"))
pre.fill(drums=fill(drums.rock, "build"), bass=ct("0*8").velocity("70 80 90 100 110 115 120 127"))
chorus.fill(drums=fill(drums.rock_ride, "full"))
bridge.fill(drums=fill(drums.half_time, "triplets"))

# A guitar hook answering the vocal at the end of every second chorus bar.
chorus.play(lead=n("<~ [~ ~ ~ [4 5]] ~ [7 ~ 5 4]>").legato(0.9).velocity(95))

# Second verse a bit busier than the first (energy rises on repeats).
verse2 = song.section("verse2", like=verse, energy=0.5)
verse2.play(bass=bass.syncopated, keys=comp.pop_strum.velocity(70))
song.arrange("intro verse pre chorus verse2 pre chorus bridge chorus chorus outro")
