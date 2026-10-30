# 12 — Bass

The bass connects **rhythm** (drums) and **harmony** (chords). It defines the chord's root
— the bass note largely decides how we hear a chord — and supplies the low-end weight.

## 12.1 The jobs of the bass

1. **Define the harmony** — usually plays the **root** on chord changes.
2. **Lock with the kick drum** — bass notes and kick hits coincide, creating one unified
   low-end rhythm.
3. **Drive the groove** — note length, rhythm and accents determine how "pushy" or "laid
   back" the song feels.
4. **Connect chords** — passing and approach notes lead smoothly into the next chord.

## 12.2 Register

- 4-string bass: E1 (41 Hz) to ~G3 in most playing; 5-string adds B0.
- Most pop/rock bass lines sit in **E1–E3**. The bass should generally be the **lowest**
  pitched instrument and stay below the chords' lowest note.
- Synth bass (808, Moog-style) may go lower (sub-bass 30–60 Hz) in modern pop/hip-hop.

## 12.3 Core bass patterns

Examples over a C chord, 16 steps per bar.

### Whole/half notes (roots)
```
C - - - - - - - - - - - - - - -        (one note per bar)
```
Ballads, intros, quiet verses. Maximum space.

### Driving 8ths ("pumping")
```
C . C . C . C . C . C . C . C .
```
The **rock and punk** default. Even, relentless 8ths on the root (U2, The Ramones,
Green Day, Foo Fighters). Energy depends on muting/attack.

### Root–fifth (country, rock'n'roll, folk)
```
C . . . G . . . C . . . G . . .        (G below or above C)
```

### Root–octave (disco, dance-pop)
```
C . C'. C . C'. C . C'. C . C'.        (octave jumps on the off-8ths)
```
Disco and funk-pop (Chic, Bee Gees-era disco, "I Will Survive"-style octave grooves).

### Kick-locked syncopation (pop, funk)
```
Kick:  x . . x . . x . x . . . . . x .
Bass:  C . . C . . C . C . . . . . E .   (last note = approach to next chord)
```

### Walking bass (blues, rockabilly, jazz)
Quarter notes outlining the chord with passing tones:
```
| C   E   G   A  | F   A   C   D  |    (C6 arpeggio walk / boogie)
| C   D   E   F♯ | G ...          |    (chromatic approach into G)
```

### Boogie-woogie / 12-bar riff
`1–3–5–6–♭7–6–5–3` per chord in shuffle — classic rock'n'roll ("Johnny B. Goode"-era).

### Pedal bass
Bass holds one note (often the tonic or dominant) while chords change above:
tension and drive (pre-choruses, intros, many U2 and post-punk tracks).

### Melodic / counter-melody bass
The bass plays its own melodic line (Paul McCartney, James Jamerson, Peter Hook) — uses
chord tones, scale runs, high register. More common in verses and bridges.

### Riff doubling
In riff rock and metal, the bass **doubles the guitar riff**, usually an octave lower.

### Synth-pop / modern pop
Sustained sub notes, sidechained to the kick ("pumping"), or sequenced 8ths/16ths
(arpeggiated, as in 80s synth-pop and synthwave).

## 12.4 Approach notes and fills

To lead into a new chord on the next downbeat, the bass often plays, on the last 8th or
16th of the bar:

- **Chromatic approach** — a semitone above or below the target (B → C, D♭ → C).
- **Scale approach** — a step from the scale (D → C).
- **Dominant approach** — the 5th of the target (G → C).
- **Walk-ups/walk-downs** — 3–4 notes stepping into the target
  (`G – A – B – C` into C, `E – D – C – B` into Am/B…).

Bass fills mirror drum fills: placed at phrase ends, larger at section transitions.

## 12.5 Bass and kick relationship

- **Same rhythm**: bass hits wherever the kick hits — the tightest, punchiest result
  (pop, rock, funk).
- **Complementary**: bass fills gaps between kick hits — busier, more melodic (Motown,
  reggae).
- In mixing, bass and kick share frequencies; producers use EQ separation and
  **sidechain compression** (bass ducks when the kick hits), especially in dance-pop.

## 12.6 Note length and articulation

Note duration is a huge part of the bass feel:

- **Staccato / muted** (short) — funk, punk, tight pop; leaves room for the kick.
- **Legato** (long, connected) — ballads, reggae, soul; full warm low end.
- **Palm-muted 8ths** — punk/pop-punk and post-punk.
- Ghost notes and slides add groove in funk/R&B.
- **Slap** (thumb) and **pop** (finger) — funk, 80s pop.

## 12.7 Dynamics across the song

| Section | Typical bass behaviour |
|---|---|
| Intro | Absent, or long root notes, or the riff |
| Verse | Sparse — roots on 1, long notes, or a small motif; leaves room for vocal |
| Pre-chorus | Pedal or rising line; 8ths start to build |
| Chorus | Driving 8ths or a strong kick-locked groove; louder, fuller, sometimes octave up |
| Bridge | Contrasting: half-time, melodic line, or drop out |
| Breakdown | Drop out entirely or a single sustained note |
| Final chorus | Busiest/fullest version |

Dropping the bass out for a bar or two and bringing it back on a downbeat is one of the
strongest energy tools in pop.

## 12.8 Style cheat sheet

| Style | Bass approach |
|---|---|
| Classic rock | Roots + fifths, 8ths, some riff doubling, blues-based fills |
| Punk / pop-punk | Fast root 8ths, follows guitar, picked |
| Pop | Kick-locked syncopation, sustained synth bass, minimal |
| Funk | 16th syncopation, ghost notes, slap/pop, emphasis on "the one" |
| Disco | Octave patterns, 8ths |
| Motown / soul | Melodic, chromatic approaches, syncopated (Jamerson) |
| Reggae | Deep, round, melodic, leaves beat 1 empty (one drop), lots of space |
| Blues / rockabilly | Walking, shuffle, boogie patterns |
| Metal | Doubles guitar riffs, distorted, follows double-kick |
| Ballad | Long roots, inversions creating descending lines |
| EDM-pop | Sub bass sidechained, offbeat ("donk") bass, rolling 16ths |

## For the pipeline

```python
def bass_bar(chord_root_pc, next_root_pc, kick_steps, style, octave=2):
    """Return list of (step, midi_note, length_steps, velocity) for one 16-step bar."""
    root = 12 * (octave + 1) + chord_root_pc          # e.g. C2 = 36
    notes = []
    if style == "rock_8ths":
        notes = [(s, root, 2, 100 if s % 4 == 0 else 85) for s in range(0, 16, 2)]
    elif style == "kick_locked":
        notes = [(s, root, 2, 100) for s in kick_steps]
    # Approach note into the next chord on the last 8th
    if next_root_pc is not None and next_root_pc != chord_root_pc:
        target = 12 * (octave + 1) + next_root_pc
        approach = target - 1 if target > root else target + 1   # chromatic
        notes = [n for n in notes if n[0] < 14] + [(14, approach, 2, 80)]
    return notes
```

- Inputs: chord per beat/bar, **kick pattern**, section energy, style.
- Outputs: notes in E1–E3, choose octave to minimise jumps between chords.
- Rules: root on chord-change downbeats (unless an inversion is specified, then the
  slash bass note); approach notes at chord changes with probability ∝ energy/style;
  note lengths by style (short for funk/punk, long for ballads).

## Exercises

1. Over C–G–Am–F, play: whole notes; 8ths; root–fifth; kick-locked syncopation.
2. Add chromatic approach notes into every chord change.
3. Play a 12-bar walking/boogie line in A with a shuffle.
