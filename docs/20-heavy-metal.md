# 20 — Heavy Metal

Heavy metal began around 1970 with Black Sabbath, building on the blues rock of Led Zeppelin
and Deep Purple. It has since split into many subgenres, but they share **distorted
guitars playing power chords and riffs**, **minor and modal harmony**, **driving or crushing
rhythms** with a powerful drum kit, and an aesthetic of **intensity**.

## 20.1 The guitar sound

- **High-gain distortion** compresses the sound and adds harmonics. That makes full triads
  muddy, so rhythm guitar uses **power chords** (root + fifth + octave, chapter 07) and single
  notes.
- **Palm muting**: the picking hand rests on the strings near the bridge, giving short, percussive
  "chugs". Alternating muted and open notes creates much of the rhythmic interest.
- **Down-tuning** for weight and lower riffs:

| Tuning | Lowest string | Typical use |
|---|---|---|
| E standard | E2 | classic metal, thrash |
| Drop D | D2 (others standard) | one-finger power chords, groove/nu-metal |
| D standard / C standard | D2 / C2 | doom, death, stoner |
| Drop C, B standard | C2, B1 | metalcore, death metal |
| 7-string (B), 8-string (F♯) | B1, F♯1 | djent, progressive |

- **Rhythm guitars are double-tracked** (two takes panned left and right); leads and harmonies
  sit in the middle.

## 20.2 Riffs

Metal songs are built from **riffs** — short, repeated, rhythmically distinctive figures, usually
on the low strings, doubled by the bass (chapter 09).

| Riff type | Description |
|---|---|
| **Pedal-point riff** | open low string (the tonic) alternating with fretted notes: E E F E E G E A♯ … |
| **Gallop** | 8th + two 16ths ("da-da-dum"), the NWOBHM drive (Iron Maiden) |
| **Chromatic riff** | stepwise half-step motion, including the ♭2 and tritone |
| **Power-chord riff** | chord shapes moving in parallel, often with rests and syncopation |
| **Tremolo-picked** | very fast repeated notes on a melodic line (black metal, thrash) |
| **Chug / breakdown riff** | palm-muted open-string rhythms synchronised with the kick (metalcore, djent) |

## 20.3 Harmony and scales

| Scale / mode | Characteristic | Sound |
|---|---|---|
| **Aeolian** (natural minor) | ♭6, ♭7 | the default; epic i–♭VI–♭VII |
| **Phrygian** | **♭2** | dark, heavy; the i–♭II (E5–F5) move |
| **Phrygian dominant** | ♭2 and major 3 | exotic, Middle-Eastern |
| **Harmonic minor** | raised 7 | neo-classical leads (Yngwie Malmsteen), V–i cadences |
| **Locrian** | ♭2 and **♭5** | unstable, extreme metal |
| **Chromatic / tritone** | the ♭5 ("diabolus in musica") | menace; Black Sabbath's title track |

Common progressions (in E minor): **i–♭VI–♭VII** (Em–C–D), **i–♭II** (Em–F), **i–♭VII–♭VI–V**
(Em–D–C–B), **i–♭VI–♭III–♭VII** (Em–C–G–D, power metal), and long pedal points with the
chords moving above.

**Twin-guitar harmony**: a melody doubled a diatonic **3rd** (or 6th) above, as in Thin Lizzy
and Iron Maiden.

## 20.4 Drums

| Pattern | Description | Where |
|---|---|---|
| **Rock/heavy beat** | backbeat with crash or ride 8ths | classic metal |
| **Thrash ("skank") beat** | kick on the beats, snare on every off-beat 8th | thrash, punk-metal |
| **Gallop** | kick in 8th + two 16ths under the riff | NWOBHM, power metal |
| **Double kick** | continuous 16ths (or triplets) on two kick pedals | choruses, power/death metal |
| **Blast beat** | very fast alternating (or unison) kick and snare with cymbal | death, black, grindcore |
| **Half-time / breakdown** | snare on 3, syncopated kick locked to the guitar chugs, china cymbal | metalcore, doom |

Cymbals are big (crash, china, splash); tom fills are frequent; drums are often sample-
reinforced so every kick is audible at high tempos.

## 20.5 Bass

The bass usually **doubles the guitar riff** (an octave lower, or the same octave), picked for
attack and often distorted. In NWOBHM the bass may drive the gallop alone (Steve Harris); in
progressive metal it can play independent lines.

## 20.6 Song structure

```
intro riff → verse riff (vocals) → pre-chorus → chorus → riff → verse → chorus →
solo section (often over a new riff) → breakdown / bridge → chorus or main riff → outro
```

- Songs are often **longer** (4–8 min) and introduce **new riffs** throughout, rather than
  repeating only verse and chorus.
- **Tempo and feel changes** between sections are common: double-time chorus, half-time
  breakdown, slow doom intro.
- The **guitar solo** is a feature section: fast scalar runs, sweep arpeggios, tapping,
  harmonised lines.

## 20.7 Subgenres

| Subgenre | Tempo | Features | Artists |
|---|---|---|---|
| Heavy metal / NWOBHM | 100–180 | gallops, twin leads, clean high vocals | Black Sabbath, Judas Priest, Iron Maiden |
| Thrash | 160–250 | thrash beat, fast palm-muted riffs | Metallica, Slayer, Megadeth |
| Doom | 50–90 | slow, down-tuned, heavy sustain | Black Sabbath, Candlemass |
| Power | 140–200 | double kick, major/minor anthems, keyboards | Helloween, Blind Guardian |
| Death | 100–250+ | down-tuned, blast beats, growled vocals, chromatic riffs | Death, Morbid Angel |
| Black | 150–250+ | tremolo picking, blast beats, raw production | Mayhem, Emperor |
| Progressive | varies | odd meters, long forms, virtuosity | Dream Theater, Opeth |
| Groove / nu-metal | 90–140 | syncopated mid-tempo chugs, drop tunings | Pantera, Korn |
| Metalcore / djent | 100–200 | breakdowns, 7/8-string chugs, polyrhythm | Killswitch Engage, Meshuggah |

## 20.8 In komposoija

```python
# style="metal": two distortion guitars from D2, pick bass
song = Song(title="...", key="E phrygian", tempo=168, style="metal")
riff = song.section("riff", bars=8, chords="<i>")
riff.play(drums=metal.drums.gallop, guitar=metal.riffs.gallop.power(),
          guitar2=metal.riffs.gallop.power(), bass=metal.riffs.gallop)
```

| Palette | Contents |
|---|---|
| `metal.drums` | `heavy double_kick gallop thrash blast breakdown doom` |
| `metal.bass` | `eighths sixteenths gallop breakdown sustained` |
| `metal.comp` | `chug16 chug8 gallop breakdown sustained tremolo` (power-chord rhythm guitar) |
| `metal.riffs` | `pedal gallop chromatic descending` (scale degrees of the song key) |
| `metal.progressions` | `aeolian phrygian descent epic doom` |

- Write riffs as scale degrees (`n(...)`) in a modal key such as `"E phrygian"`; `.power()`
  turns each note into a power chord; give the same pattern without `.power()` to the bass to
  double the riff.
- The metal style profile lowers the guitar register to D2 (drop-D riffs fit), adds `guitar2`
  for double-tracking, and uses a pick bass.
- A breakdown can halve the tempo with `tempo=` on the section. See `songs/metal_example.py`.

## Exercises

1. Write a pedal-point riff in E Phrygian and play it as single notes and as power chords.
2. Put the same riff over the thrash beat, the gallop and double kick; which suits a chorus?
3. Arrange an 8-bar breakdown whose kick pattern matches the guitar chugs exactly.
