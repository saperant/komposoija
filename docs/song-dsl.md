# Song DSL reference — backing tracks as code

A song is a Python file that builds a `Song` and assigns it to the variable `song`.
Parts are written in Strudel-style **mini-notation**; one cycle of a pattern is **one bar**.
`komposoija render` turns the file into a multi-track MIDI file, and optionally plays it or
renders WAV/MP3 audio.

## Setup

```bash
# System tools for audio (Ubuntu/Debian; on Fedora use dnf with the same package names)
sudo apt install fluidsynth fluid-soundfont-gm lame

# Python package (from the repository root)
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
```

MIDI rendering needs only Python and `mido`. FluidSynth and a General MIDI SoundFont are
needed for `--play`, `--wav` and `--mp3`; `lame` (or `ffmpeg`) for `--mp3`.

## Command line

```bash
komposoija render songs/example.py            # build/example.mid + summary
komposoija render songs/example.py --play     # ... and play it (Ctrl-C stops)
komposoija render songs/example.py -w --play  # live coding: replay on every save
komposoija render songs/example.py --mp3      # ... and build/example.mp3
komposoija render songs/example.py --sections chorus --play   # audition a part
komposoija render songs/example.py -w --play --from chorus.2:5  # replay from a place
komposoija show songs/example.py              # arrangement summary only
komposoija inspect songs/example.py           # the timeline and source map as JSON
```

| Option | Effect |
|---|---|
| `-o PATH` | MIDI output path (default `build/<song file name>.mid`; audio files go next to it) |
| `--sections a,b` | render these sections in this order instead of the form |
| `-w`, `--watch` | re-render whenever the file is saved; errors are printed and watching continues |
| `-p`, `--play` | play through FluidSynth; with `--watch`, playback restarts on each save |
| `--from PLACE` | with `--play`: start playing at a place (see below); the files written stay whole |
| `--wav [PATH]` | also write a WAV file |
| `--mp3 [PATH]` | also write an MP3 file (the intermediate WAV is removed unless `--wav` is given) |
| `--bitrate N` | MP3 bitrate in kbit/s (default 192) |
| `--gain G` | FluidSynth master gain (default 0.3, which leaves headroom for full choruses) |

`--sections` writes to the same default path as a full render, so give `-o` if you want to
keep both.

**Places** name a bar of the form: `chorus` (the first chorus), `chorus.2` (the second time
it is played), `chorus:5` (its bar 5), `chorus.2:5`, or a plain bar number of the song
(`33`). The summary's `@0:33` times and the bar numbers below are where they start.
`--play --from` writes the excerpt next to the MIDI file (`build/<song>.from.mid`): the
tempo, key, programs and notes held across the start are carried to its beginning.

`inspect` prints what editors and the myrcp companion read: the form with each bar's beat
and time, and which section each line of the file is about (a section's `song.section(...)`
call, the statements on its variable such as `verse.play(...)` and `verse.chords = ...`, and
on a lyric line the bar where that line starts: 4 lines in 8 bars start at bars 1, 3, 5
and 7). `-o PATH` also writes the MIDI file. A song that fails gives
`{"error", "traceback", "places"}` with the line in the song file, and exit status 1.

### In the myrcp workbench

komposoija's user interface on [myrcp](https://github.com/saperant/myrcp)
(`pip install 'komposoija[ui]'`, then `komposoija-ui`; the plugin is
`src/komposoija/ui/plugins/komposoija`, run in komposoija's Python) lists the songs under
`$KOMPOSOIJA_SONGS` (else the working directory) and opens a song as a tab: the form as a
table with each section's bars, start and chords, a playhead while it plays, and render
errors in Problems at their line. Edit the file in a linked Vim or Neovim beside it:

- the editor's cursor sets the **start mark**: the section the line is about, on a lyric
  line the bar it starts;
- `space` (in the tab) or `F9` (anywhere, `Ctrl+\ F9` from a terminal tab) plays from the
  mark and stops; `Enter` on a row plays that section; `[` `]` move the mark a bar;
- every save renders again, and while playing the new version starts from the mark;
- while playing, the mark moving with the cursor restarts playback there (`f` toggles);
  `l` loops the section being played.

The printed summary shows key, tempo, length, and for every section its start time,
chords bar by bar (`%` = chord continues), tracks, fills and the first lyric line:

```
 4. chorus   8 bars  @0:33  | C | G | D | Em | C | G | D | Em |
            tracks: drums, bass, guitar, keys, pad, lead  (fill: drums)
            lyrics: So light it up, light it up …
```

Environment variables: `KOMPOSOIJA_SOUNDFONT=/path/to/file.sf2` selects a SoundFont
(default: the first that exists of `/usr/share/sounds/sf2/default-GM.sf2`,
`/usr/share/sounds/sf2/FluidR3_GM.sf2` and a few `/usr/share/soundfonts/` paths);
`KOMPOSOIJA_AUDIO_DRIVER` selects the FluidSynth audio driver for `--play` (default
`pulseaudio`, which PipeWire also provides).

## The flow, as code

A song file follows the composition flow in three blocks, so a human and an AI agent
can work through it stage by stage (see `songs/example.py` for a complete song):

```python
from komposoija import *

song = Song(title="...", key="G major", tempo=116)            # mood: key, tempo, swing

# 1. structure (from the lyrics)
verse  = song.section("verse",  bars=8, lyrics="""...""")
chorus = song.section("chorus", bars=8, lyrics="""...""")
song.arrange("intro verse chorus verse chorus bridge chorus outro")

# 2. mood: harmony and grooves
verse.chords  = chords("<I V vi IV>")
chorus.chords = chords("<IV I V vi>")
verse.play(drums=drums.sidestick, bass=bass.roots, keys=comp.halves)
chorus.play(drums=drums.rock_ride, bass=bass.driving, guitar=comp.power8)

# 3. details
verse.fill(drums=fill(drums.sidestick, "two_beats"))           # last bar of the section
chorus.play(lead=n("<~ [~ ~ ~ [4 5]] ~ [7 ~ 5 4]>"))           # hand-written hook
verse2 = song.section("verse2", like=verse)                     # variant of verse
verse2.play(bass=bass.syncopated)
```

## Mini-notation

| Syntax | Meaning | Example |
|---|---|---|
| `a b c` | sequence: items share the bar equally | `"bd sd bd sd"` = quarter notes |
| `[a b]` | subsequence inside one step | `"bd [sd sd]"` |
| `<a b>` | alternate: one item per bar | `"<I V vi IV>"` |
| `a, b` | simultaneous (inside `[]`/`<>` or top level) | `"bd*4, ~ sd ~ sd"` |
| `~` `-` | rest | `"bd ~ sd ~"` |
| `a*n` / `a/n` | faster / slower | `"hh*8"`, `"I/2"` (2 bars) |
| `a!n`, `a !` | replicate | `"0!7 a"` |
| `a@n` | weight (in `<>`: number of bars) | `"c3@3 e3"`, `"<I@2 IV V>"` |
| `a?` `a?0.3` | drop at random (deterministic) | `"hh*16?0.2"` |
| `a(k,n,r)` | Euclidean rhythm | `"bd(3,8)"` = tresillo |

Alternations restart at every occurrence of a section, so `"<I V vi IV>"` begins on `I` in
each verse. Syntax errors point at the offending character:

```
error: unknown drum 'sx'; known: bd, kick, ...
  bd sx
     ^
```

## Pattern constructors

| Function | Atoms | Pitch comes from |
|---|---|---|
| `s("bd sd hh")` | drum names: `bd sd rim cp hh ph oh rd rb cr china splash ht mt lt ft tb sh cb hc lc hb lb` (and long forms `kick snare clap ride crash tamb shaker cowbell`) or GM numbers | GM drum map |
| `note("c3 eb3 g3")` | note names (octave default 3, middle C = c4) or MIDI numbers | absolute |
| `n("0 2 4")` | 0-based scale degrees; negatives go down | section key; tonic placed at the bottom of the track register |
| `ct("0 1 2 a")` | chord tones: 0 root, 1 third, 2 fifth, 3 seventh…; past the chord size = next octave, negative = below; `a` = chromatic approach into the next chord's root | current chord; root placed at the bottom of the track register (slash chords: 0 = slash bass) |
| `strum("x ~ x x")` | any non-rest atom = whole-chord hit | current chord, voiced inside the register with smooth voice leading |
| `walk("x*4")` | any non-rest atom = one walking-bass note | generated: root on each chord change, chord tones/steps toward the next chord, chromatic approach on the last note before it (also into the next section) |
| `chords("<I V vi IV>")` | Roman numerals or chord symbols | section key |

The **register** only anchors where the root or tonic goes; higher chord tones and scale
degrees may rise above it (an arpeggio over a high root, say).

**Chords**: `I ii iii IV V vi vii°`, accidentals `bVII #iv°`, suffixes `7 maj7 6 9 add9 sus2 sus4
7sus4 5 + ° ø 11 13`, jazz suffixes `7b9 7#9 7#11 7b13 7alt 7b5 +7 9sus4 69 maj7#11 maj13`
(lower case: `m69 m13`; `ii7b5` = half-diminished), lower case = minor (`ii7` = m7), secondary dominants `V/V V7/vi`, or
symbols `Am7 D/F# Bbmaj7`. Numerals count from the **major** scale of the tonic (pop/rock
convention): in A minor write `i bIII iv v bVI bVII`. Chord names in the summary and the MIDI
file follow the numeral's own accidental (`bVII` in C is `Bb`), otherwise the key signature.

## Pattern methods

| Method | Effect |
|---|---|
| `.velocity(v)` | 1–127; constant or patterned (`"[100 70]*4"`); 0 silences |
| `.legato(x)` | note length as fraction of its step (patternable) |
| `.octave(n)` / `.transpose(st)` | shift pitched parts (patternable) |
| `.voicing(style)` | for `strum`: `"close"` (default), `"open"`, `"power"`, `"shell"` (root–3–7) or `"rootless"` (3–5–7–9, jazz piano) |
| `.power()` | play single notes (`n`, `note`, `ct`) as power chords: note + fifth + octave |
| `.fast(n)` `.slow(n)` | speed of the pattern |
| `.first_of(n, p)` (alias `.every`) `.last_of(n, p)` | use `p` (a pattern, or a function of the pattern) on the first/last bar of every n |
| `.end_with(p, portion)` | replace the end of every bar, e.g. `"1/4"` = last beat in 4/4 |
| `.degrade(prob, seed)` | random drops |
| `stack(a, b)` / `a + b` | layer patterns; `sequence(...)`, `cat(...)` as in Strudel |

Patterned controls are sampled at each note's start: `s("hh*8").velocity("[90 60]*4")`
alternates loud and soft eighths.

## Song, sections, tracks

- `Song(title, key, tempo, meter="4/4", style="pop_rock", swing=, swing_unit=, seed=0, crashes=)`
  - `key`: `"G major"`, `"E minor"`, `"D mixolydian"`, `"F# dorian"`, `"E phrygian"`, …
  - `style`: a style profile (below); `swing`, `swing_unit` and `crashes` default to the style's.
  - `swing`: 0.5 straight, ~0.6 light, 0.667 triplet shuffle; `swing_unit` 8 or 16. Ignored in
    meters counted in 8ths or 16ths: 6/8 and 12/8 already have the triplets in the bar, and
    5/8 or 7/8 are played straight.
  - `crashes`: crash cymbal on beat 1 of every section after the first that has drums.
- `song.section(name, bars, chords=, key=, tempo=, tempo_to=, meter=, lyrics=, energy=, crash=,
  notes=)` creates a section; `song.section(new_name, like=other, ...)` copies one as a variant.
  `key`, `tempo`, `tempo_to` and `meter` change the key, tempo and time signature for that
  section (see below).
- `section.chords = chords(...)` (or `chords="..."` at creation) sets the harmony.
- `section.play(track=pattern, ...)` sets parts (`None` removes one); `section.fill(track=pattern)`
  replaces that track in the section's last bar.
- `song.arrange("intro verse chorus ...")` sets the form; sections can repeat.

Default tracks:

| Track | Sound (GM) | Register (lowest anchor) |
|---|---|---|
| `drums` | standard kit, channel 10 | — |
| `bass` | finger bass | E1–E3 |
| `keys` | piano | E3–E5 |
| `guitar` | overdrive guitar | E2–E4 |
| `pad` | warm pad | G3–G5 |
| `lead` | saw lead | C4–C6 |

Add or change tracks with `song.track(name, program=..., register=(lo, hi), velocity=,
humanize_ms=, humanize_velocity=, channel=)`. `program` is a GM number or a name such as
`piano epiano clav organ drawbar_organ rock_organ clean_guitar jazz_guitar acoustic_guitar
overdrive_guitar distortion_guitar acoustic_bass finger_bass pick_bass slap_bass synth_bass
strings brass trumpet trombone alto_sax tenor_sax harmonica pad_warm lead_square`.

### Meter, key and tempo changes

Each section can have its own time signature, key and tempo. Anything not given comes from
the `Song`; the next section without its own setting returns to the song's.

```python
song = Song(key="E major", tempo=96)
verse = song.section("verse", bars=8, chords="<I vi IV V>")
waltz = song.section("interlude", bars=4, chords="<IV V>", meter="3/4")   # 3 beats per bar
riff = song.section("riff", bars=4, chords="<i>", meter="7/8", tempo=132)
last = song.section("last_chorus", like="chorus", key="+1")               # truck-driver's change
outro = song.section("outro", bars=4, chords="<IV I>", tempo=96, tempo_to=70)   # ritardando
```

- **`meter="3/4"`, `"6/8"`, `"7/8"`, `"5/4"`, …**: one cycle is still one bar, so a pattern
  fills the bar of the section's meter. `"x*7"` in 7/8 gives seven 8ths, and `s("bd hh hh")` in
  3/4 gives three quarters. The presets are written for 4/4, so in other meters use the
  patterns made for them (`jazz.*.waltz`, `blues.*.slow_12_8`) or write your own. For a 3/4 fill
  use `fill(groove, "one_beat", beats_per_bar=3)`. Swing follows the section's meter (see
  `swing` above).
- **`key=`**: a key (`"A minor"`, `"D dorian"`) or a change relative to the song key: `"+1"` and
  `"+2"` (the final-chorus lift), `"-2"`, or `"+3 minor"` (new tonic and mode). Roman numerals
  are read in the section's key. Lines that lead into the next section (walking bass, `a`
  approach notes) target the next section's key.
- **`tempo=`** jumps to a new tempo at the start of the section, for example a half-time
  breakdown. **`tempo_to=`** changes the tempo gradually across the section, one step per
  quarter note, and reaches the target on the last beat: a ritardando when it is slower, an
  accelerando when it is faster. The ramp starts from `tempo` if it is given, otherwise from the
  song's tempo.
- Tempo is always in **quarter notes per minute** (the MIDI convention), also in 6/8 and 7/8.
  For 6/8 at 60 dotted quarters per minute, write `tempo=90`.
- Changes happen only at section boundaries. For a key change part-way through, such as a
  pivot chord into the new key, end the section on the pivot and start a new one in the new
  key. Chord symbols (`"D7"`) also work in any key.
- The summary shows each change after the section's tracks, for example
  `(7/8; 132 BPM)`, `(key F major)` or `(96→70 BPM)`. The MIDI file has a `time_signature`,
  `key_signature` and `set_tempo` event at each change, so notation programs show the new
  bar lengths and key signatures.

### Style profiles

`Song(style=...)` sets instruments, registers, feel and humanisation for a genre. Later
`song.track(...)` calls and explicit `swing=`/`crashes=` arguments override it.

| Style | Feel | Instruments and registers |
|---|---|---|
| `pop_rock` (default) | straight | the default tracks above |
| `jazz` | swing 0.64 (8ths), no auto crashes | acoustic bass, piano D3–D5, jazz guitar, tenor sax `lead`, trumpet `horns`; humanised |
| `blues` | shuffle 0.66 (8ths) | finger bass, piano, `organ` track, overdrive guitar, harmonica `lead` |
| `funk` | 16th swing 0.54 | clav on `keys`, clean guitar G3–E5, brass `horns`; tight timing |
| `reggae` | light swing 0.56, no auto crashes | deep bass E1–C3, high clean guitar for the skank, drawbar organ on `keys`, `horns` |
| `metal` | straight | two distortion guitars (`guitar`, `guitar2`) from D2, pick bass from D1, overdrive `lead` |

## Presets (mood palette)

Presets come from docs chapters 11–13; every one is an ordinary pattern you can modify
(`drums.rock.velocity(80)`) or combine.

- `drums.`: `rock rock_ride rock16 four_floor half_time punk shuffle funk motown one_drop ballad
  sidestick toms`
- `fill(groove, kind)`: kinds `one_beat two_beats full build triplets stop`, or your own drum
  string with `beats=`: `fill(drums.rock, "sd ~ sd [cr, bd]", beats=1)`
- `bass.`: `roots halves quarters eighths driving root_fifth octaves kick_locked walking boogie
  pedal syncopated`
- `comp.`: `whole halves quarters eighths pop_strum offbeat stabs power_whole power8 arp_up
  arp_broken`

### Genre palettes

Each genre has `drums`, `bass`, `comp` and `progressions` (metal also `riffs`), explained in
the genre chapters. Use them together with the matching style profile.

| Genre | Chapter | Example song | Highlights |
|---|---|---|---|
| `jazz` | [16](16-jazz.md) | `songs/jazz_example.py` | swing ride, `walk()` bass, rootless/shell comping, rhythm changes, jazz blues |
| `blues` | [17](17-blues.md) | `songs/blues_example.py` | shuffle, Texas shuffle, 12/8 slow blues, boogie bass, 5th–6th guitar, stop-time, 12-bar forms |
| `funk` | [18](18-funk.md) | `songs/funk_example.py` | the one, ghost notes, linear drums, slap octaves, chicken scratch, clav, horn hits, vamps |
| `reggae` | [19](19-reggae.md) | `songs/reggae_example.py` | one drop, rockers, steppers, skank, organ bubble, riddim bass |
| `metal` | [20](20-heavy-metal.md) | `songs/metal_example.py` | gallop, double kick, blast, breakdown, palm-muted chugs, Phrygian riffs with `.power()` |

```python
song = Song(key="F major", tempo=160, style="jazz")
head = song.section("head", bars=8, chords=jazz.progressions.rhythm_a)
head.play(drums=jazz.drums.swing, bass=jazz.bass.walking, keys=jazz.comp.charleston)
```

Patterns whose names say so are for other meters: `jazz.*.waltz` (3/4) and
`blues.*.slow_12_8` (12/8).

## Output

**MIDI**: type-1 file at 480 ticks per quarter note. A conductor track carries tempo, meter,
key signature, a **marker** per section and a **text** event per chord change; then one track
per instrument with its GM program. Repeated notes of the same pitch never overlap. MuseScore and
other notation programs can import it for scores; any SoundFont player can play it.

**Audio**: FluidSynth renders the MIDI with the SoundFont at 44.1 kHz; `--mp3` encodes with
`lame` and writes the song title into the ID3 tag.

## Troubleshooting

| Message | Fix |
|---|---|
| `no chord at bar N` | the section has `ct`/`strum` parts but no `chords` |
| `plays unknown track 'x'` | add it with `song.track("x", program=..., register=(lo, hi))` |
| `fluidsynth not found` / `no General MIDI SoundFont found` | install the packages above or set `KOMPOSOIJA_SOUNDFONT` |
| no sound with `--play` | try `KOMPOSOIJA_AUDIO_DRIVER=pipewire` or `alsa` |
| `'x': no such place` | `--from` takes a section of the form, `name.N`, `name:BAR` or a bar number |
| choruses distort | lower `--gain` |
