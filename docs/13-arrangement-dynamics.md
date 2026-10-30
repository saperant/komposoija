# 13 — Arrangement and Dynamics

**Arrangement** = deciding *who plays what, when, and where in the frequency/pitch space*.
The same chords and melody can become a ballad or an arena anthem depending on
arrangement. For an automatic composer, arrangement is where most of the perceived quality
comes from.

## 13.1 Roles in a pop/rock arrangement

Think in **roles** rather than instruments:

| Role | Typical instruments | Register | Job |
|---|---|---|---|
| **Rhythm/foundation** | Drums, percussion | Full spectrum | Time, groove, energy |
| **Low end** | Bass guitar, synth bass, piano left hand | 40–250 Hz | Root, weight, groove |
| **Harmony bed (pad)** | Rhythm guitar, keys, synth pads, strings, organ | 200 Hz–3 kHz | Fill harmonic space, sustain |
| **Rhythmic harmony** | Strummed/chugging guitar, piano comping, plucks | Mid | Add rhythmic drive to harmony |
| **Lead/melody** | Lead vocal | Mid (most important range 1–4 kHz) | The song |
| **Counter-melody / fills** | Lead guitar, synth leads, horns, backing vocals | Mid–high | Answer the vocal in gaps |
| **Ear candy / FX** | Risers, reverse cymbals, vocal chops, sweeps | Any | Transitions, novelty |

Rule of thumb: **one thing in focus at a time**. Fills and counter-melodies go *between*
vocal phrases, never on top of them.

## 13.2 Frequency and register separation

- Each part should own a **register**: bass low, guitars/keys mid, vocal upper-mid,
  cymbals/percussion high.
- If two harmony instruments play together, voice them in **different octaves** or give
  them **different rhythms** (e.g. guitar strums 8ths, piano holds whole notes high).
- **Avoid low-register clutter**: below ~C3 use only root/fifth (bass handles the root).
- Doubling (guitar + synth on the same line, octave doubling) thickens without clutter.

## 13.3 Rhythmic layering

Assign different **rhythmic densities** to parts so they interlock:

```
Pad/organ:     whole notes          ────────────────
Piano:         quarter-note chords  ♩   ♩   ♩   ♩
Guitar:        8th-note strum       ♪♪♪♪♪♪♪♪
Hi-hat/shaker: 16ths                ♬♬♬♬♬♬♬♬
```

Syncopated parts (e.g. guitar on the "&"s, as in ska or reggae) leave the beat to the kick
and snare.

## 13.4 Dynamics

**Dynamics** = loudness and intensity, both literally (velocity/volume) and perceived
(density, register, brightness).

Classical dynamic marks (also used loosely in charts):

| Mark | Meaning | MIDI velocity (rough) |
|---|---|---|
| *pp* | pianissimo, very soft | 20–35 |
| *p* | piano, soft | 35–55 |
| *mp* | mezzo piano | 55–70 |
| *mf* | mezzo forte | 70–90 |
| *f* | forte, loud | 90–110 |
| *ff* | fortissimo | 110–127 |
| crescendo (<) | gradually louder | ramp up |
| decrescendo / diminuendo (>) | gradually softer | ramp down |
| *sfz* | sudden accent | spike |

In modern produced music, overall loudness is compressed, so **perceived energy** comes more
from **arrangement density** than from volume. The tools:

| To increase energy | To decrease energy |
|---|---|
| Add instruments/layers | Remove layers (strip to vocal + one instrument) |
| Busier subdivisions (8ths → 16ths) | Longer notes, more rests |
| Open voicings, higher register | Closed voicings, lower/middle register |
| Distortion, brighter tones | Clean, filtered (low-pass) tones |
| Crash/ride/open hats, tambourine | Side-stick, closed hats, no cymbals |
| Double-tracked vocals, harmonies, ad-libs | Single dry vocal |
| Faster harmonic rhythm | Static chord / pedal |
| Key change up | Drop to relative minor / sparse bridge |

## 13.5 Builds, drops and transitions

- **Build (riser)**: gradually add elements, accelerate drum subdivisions (snare roll),
  raise a filter cutoff, rising pitch FX, pedal bass. Typically over the pre-chorus,
  4–8 bars.
- **Drop / hit**: the arrival at the chorus downbeat — crash, full kick and bass, all
  layers in.
- **Dropout**: remove everything (or keep only vocal) for the last half-bar or beat before
  the chorus — the silence makes the downbeat hit harder.
- **Reverse cymbal / swell** leading into a downbeat.
- **Pickup**: vocal or instrument starts before the bar line of the new section.
- **Filter sweep**: low-pass the mix in the build, open it on the drop (dance-pop).

## 13.6 Typical arrangement per section (pop-rock)

| Section | Drums | Bass | Guitars/keys | Vocals | Extras |
|---|---|---|---|---|---|
| Intro | None / light / riff with full band | Roots or riff | Riff or arpeggio | — | Hook teaser |
| Verse 1 | Light groove, closed hat or side-stick | Sparse, roots | One instrument, clean/muted | Lead, single | — |
| Pre-chorus | Build, tom pattern or snare roll | Pedal or rising 8ths | Add pad / sustained chords | Rising melody | Riser |
| Chorus | Full groove, crash, open hats/ride | Driving 8ths | Full strums/power chords, keys | Doubled + harmonies | Tambourine, synths |
| Verse 2 | Slightly fuller than V1 | Busier than V1 | + a counter line | Lead + occasional harmony | — |
| Bridge | Half-time or drop out | Melodic or out | New texture | Different melody | Strings/synth pad |
| Breakdown | Minimal / none | Out | Single instrument | Intimate vocal | — |
| Final chorus | Biggest | Biggest | Everything + octave-up parts | Ad-libs, choir | Key change? |
| Outro | Fade, or final hit + ring out | Root | Riff/hook | Tag line | — |

## 13.7 Instrument-specific idioms (quick)

- **Rhythm guitar**: strumming patterns (D-DU-UDU), palm-muted 8ths, power chords on
  distortion, arpeggios on clean, chord "stabs" (funk/ska), "chugs" (metal).
- **Lead guitar**: riffs, fills between vocal lines, solos (pentatonic/blues), harmonised
  thirds (Thin Lizzy, Iron Maiden).
- **Piano**: block chords on quarters (pop ballad), broken chords/arpeggios, left hand
  octaves + right hand chords, rock'n'roll triplets.
- **Organ (Hammond)**: sustained pads, swells, gospel stabs.
- **Synth**: pads (sustained), arps (16th arpeggios), plucks, leads, bass.
- **Strings**: long-note pads, rising lines in builds, staccato rhythmic figures.
- **Backing vocals**: harmonies a 3rd/6th above or below, "oohs/aahs" pads,
  call-and-response.
- **Horns**: stabs on accents, unison riffs (soul, funk, ska).

## For the pipeline

- Define an **instrument roster** per style with roles, register windows and density
  options.
- For each section, an **energy value (0–1)** selects:
  - which instruments are active (thresholds per instrument),
  - pattern variants (sparse/medium/busy),
  - velocity offsets,
  - whether transition events (fill, riser, dropout) happen at the section end.

```python
ACTIVATION = {          # instrument: minimum energy to play
    "drums": 0.25, "bass": 0.3, "rhythm_guitar": 0.35, "keys_pad": 0.5,
    "lead_guitar_fills": 0.6, "tambourine": 0.75, "backing_vocals": 0.7,
    "strings": 0.8,
}
def active_instruments(energy: float) -> list[str]:
    return [i for i, thr in ACTIVATION.items() if energy >= thr]
```

- Run an **arrangement checker**: no two parts in the same register with the same rhythm
  (unless intentional doubling), bass is lowest, nothing masks the vocal range during vocal
  phrases.

## Exercises

1. Take a 4-chord loop and make three arrangements: intimate, mid, full.
2. Program a 4-bar pre-chorus build into a chorus with a half-bar dropout.
3. Listen to a pop hit and write down when each instrument enters and leaves.
