# 19 — Reggae

Reggae developed in Jamaica in the late 1960s out of **ska** and **rocksteady**, which in turn
grew from mento, American R&B and jazz. Bob Marley & the Wailers made it global in the 1970s.
Its essentials are the **off-beat skank**, a **drum feel that drops the downbeat**, a heavy,
melodic **bass that leads**, simple harmony, and a laid-back, spacious groove.

## 19.1 From ska to dancehall

| Style | Period | Tempo | Features |
|---|---|---|---|
| **Ska** | early 1960s | fast (≈ 110–140 BPM, often felt in 2) | guitar/piano on every off-beat 8th, walking bass, horn sections (The Skatalites) |
| **Rocksteady** | 1966–68 | slower | bass becomes melodic and prominent, sweeter vocal harmony (Alton Ellis) |
| **Reggae / roots** | late 1960s–70s | ≈ 60–90 BPM | one drop, skank on 2 & 4, bass-led riddims, conscious lyrics (Bob Marley, Burning Spear, Toots & the Maytals) |
| **Dub** | 1970s | as reggae | remixes: drums and bass foregrounded, instruments dropped in and out, echo and reverb (King Tubby, Lee "Scratch" Perry) |
| **Rockers / steppers** | mid–late 1970s | as reggae | driving kick patterns (Sly & Robbie) |
| **Dancehall** | 1980s– | faster, digital | drum machines, sparse riddims, deejay vocals |
| **2 Tone (UK ska revival)** | late 1970s | fast | punk energy + ska (The Specials, Madness) |

## 19.2 Counting reggae

Reggae is usually counted **slowly in 4** (≈ 60–90 BPM). In that count:

- the guitar **skank** falls on **beats 2 and 4**;
- in the **one drop**, the kick and snare (or rim) land together on **beat 3** and beat 1 is
  left empty;
- the hi-hat plays 8ths (often lightly swung) or a shuffling triplet figure.

Ska is counted faster, and the same off-beat chops fall on the **"&" of every beat**. When
writing reggae, pick one counting and stay consistent; komposoija's reggae presets use the slow
count (skank on 2 and 4).

## 19.3 Drums: one drop, rockers, steppers

| Pattern | Kick | Snare / rim | Feel |
|---|---|---|---|
| **One drop** (Carlton Barrett) | beat 3 only | cross-stick on 3 | spacious, hypnotic; beat 1 "dropped" |
| **Rockers** (Sly Dunbar) | beats 1 and 3 | rim on 3 | more drive |
| **Steppers** | every beat (four-on-the-floor) | rim on 3 | marching, militant, dub and UK roots |
| **Ska** | 1 and 3 | backbeat 2 & 4 | fast, off-beat hi-hats |

Fills are short and placed late in the bar (often snare 16ths/triplets leading into beat 1 of
the next phrase). Drum timing tends to sit slightly **behind the beat**.

## 19.4 Bass: the lead instrument

- The bass is the loudest instrument in the mix and carries the song's identity. An
  instrumental backing (drums + bass, plus skank) is a **riddim**, often reused for many songs.
- Lines are **melodic**, repeat every 1–2 bars, use chord tones and scale steps, and leave
  **space** — in a one drop the bassist often avoids beat 1 too.
- Tone: deep and round, short sustain, little treble.
- Players: Aston "Family Man" Barrett, Robbie Shakespeare.

## 19.5 Guitar, keys and horns

- **Skank**: a short, muted chord chop on 2 and 4 (in the slow count), usually a small
  high-register voicing; the "double skank" chops twice (16ths) on the off-beat.
- **Organ bubble**: a rhythmic organ figure that fills the 8ths/16ths around the skank, giving
  the groove its rolling motion.
- **Piano** often doubles the skank; **melodica** (Augustus Pablo) and **horns** play short
  melodic answers.
- A second guitar may double the bass line an octave up (muted single notes).

## 19.6 Harmony and form

- One- and two-chord vamps: **I–IV**, **I–V**, **i–iv**, **i–♭VII**; minor keys are common.
- Rocksteady borrowed R&B progressions such as **I–vi–IV–V**.
- Forms are verse–chorus, frequently with a long instrumental or **dub** section in which
  instruments drop in and out over the riddim.
- **Dub techniques** as arrangement tools: mute everything except drums and bass, let an
  instrument play only one bar in four, throw a chord into echo, return with the full band.

## 19.7 Listening

Bob Marley & the Wailers, Toots & the Maytals, Burning Spear, Peter Tosh, Jimmy Cliff,
The Skatalites, Lee "Scratch" Perry, King Tubby, Sly & Robbie, Steel Pulse, The Specials.

## 19.8 In komposoija

```python
song = Song(title="...", key="G major", tempo=74, style="reggae")
verse = song.section("verse", bars=8, chords=reggae.progressions.two_chord)
verse.play(drums=reggae.drums.one_drop, bass=reggae.bass.melodic,
           guitar=reggae.comp.skank, keys=reggae.comp.bubble)
```

| Palette | Contents |
|---|---|
| `reggae.drums` | `one_drop rockers steppers ska fill` |
| `reggae.bass` | `one_drop rockers steppers melodic ska_walk` |
| `reggae.comp` | `skank double_skank ska_skank bubble horn_line` |
| `reggae.progressions` | `two_chord roots minor_vamp minor_bvii rocksteady` |

The reggae style profile uses a deep bass register (E1–C3), a high clean guitar for the
skank, an organ on `keys`, light 8th swing and no automatic crashes. A dub section is just
a section with fewer parts — or parts filtered by time, as in `songs/reggae_example.py`.

## Exercises

1. Program the same bass line over one drop, rockers and steppers drums; describe the change.
2. Write a two-bar riddim (drums + bass) and build a verse and chorus on it without changing it.
3. Arrange an 8-bar dub break in which the skank plays only in bars 3–4 and 7–8.
