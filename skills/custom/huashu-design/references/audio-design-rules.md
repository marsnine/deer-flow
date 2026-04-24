# Audio Design Rules · huashu-design

> Audio application recipes for all animated demos. Used in conjunction with `sfx-library.md` (asset list).
> Practical training: huashu-design releases hero v1-v9 iteration · Gemini in-depth dismantling of Anthropic’s three official films · 8000+ A/B comparisons

---

## Core principles · Audio dual-track system (iron law)

Animation audio **must be designed independently in two layers**, not just one layer:

| Layer | Function | Time scale | Relationship with vision | Occupied frequency band |
|---|---|---|---|---|
| **SFX (beat layer)** | Mark each visual beat | 0.2-2 second bursts | **Strong Sync** (frame level alignment) | **High Frequency 800Hz+** |
| **BGM (atmospheric bottom)** | Emotional background, sound field | Continuous 20-60 seconds | Weak synchronization (paragraph level) | **Mid-low frequency <4kHz** |

**Animation that only does BGM is crippled** - the audience subconsciously perceives that "the painting is moving but there is no sound response", and this is the root of the cheap feeling.

---

## Gold Standard·Gold Ratio

These sets of values ​​are **engineering hard parameters** derived from the actual measurement of Anthropic's three official films + our own v9 final version. They can be applied directly:

### Volume
- **BGM Volume**: `0.40-0.50` (relative to full scale 1.0)
- **SFX Volume**: `1.00`
- **Loudness difference**: BGM is -6 to -8 dB **lower than SFX peak (it does not rely on the absolute loudness of SFX to stand out, but on the difference in loudness)
- **amix parameter**: `normalize=0` (never use normalize=1, it will flatten the dynamic range)

### Frequency band isolation (P1 hard optimization)
The secret of Anthropic is not "loud SFX volume", but **band layering**:

```bash
[bgm_raw]lowpass=f=4000[bgm]      # BGM limited to low-mid frequencies <4kHz
[sfx_raw]highpass=f=800[sfx]      # SFX pushed to mid and high frequencies of 800Hz+
[bgm][sfx]amix=inputs=2:duration=first:normalize=0[a]
```

Why: The human ear is most sensitive to the 2-5kHz range (i.e. the "presence frequency band"). If SFX is in this range and BGM covers the entire frequency range, **SFX will be covered by the high-frequency part of BGM**. Use highpass to push up SFX + lowpass to push down BGM. The two occupy one side of the spectrum, and the SFX clarity goes directly to the next level.

### Fade
- BGM input: `afade=in:st=0:d=0.3` (0.3s, avoid hard cuts)
- BGM out: `afade=out:st=N-1.5:d=1.5` (1.5s long tail, closing feeling)
- SFX comes with its own envelope, no additional fade is required

---

## SFX cue design rules

### Density (how many SFX per 10 seconds)
The measured SFX density of three Anthropic films has three levels:

| Movie | SFX per 10s | Product Character | Scene |
|---|---|---|---|
| Artifacts (ref-1) | **~9/10s** | Feature-dense, lots of information | Complex tool demonstrations |
| Code Desktop (ref-2) | **0** | Pure atmosphere, meditative feeling | Development tools focused state |
| Word (ref-3) | **~4/10s** | Balance, office rhythm | Productivity tools |

**Heuristics**:
- Product personality is calm/focused → SFX density is low (0-3 pieces/10s), BGM is the main focus
- The product has a lively personality/a lot of information → High SFX density (6-9 pieces/10s), SFX drives the rhythm
- **Don’t fill every visual beat** – White space is better than density. **Taking out 30-50% of cues will make the rest more dramatic**.

### Cue selection priority
Every visual beat doesn’t need to be paired with SFX. Choose according to this priority:

**P0 is required** (omitting it will be inconsistent):
- Typing (Terminal/Input)
- Click/select (user decision moment)
- Focus switching (visual protagonist shift)
- Logo reveal (brand closing)

**P1 recommended configuration**:
- Element entry/exit (modal/card)
- Completion/success feedback
- AI generation start/end
- Major transitions (scene switches)

**P2 optional** (too many will cause confusion):
- hover / focus-in
- progress tick
- Decorative ambient

### Timestamp alignment accuracy
- **Same frame alignment** (0ms error): click/focus switch/Logo settled
- **1-2 frames** (-33ms): fast whoosh (gives the audience psychological expectations)
- **Post 1-2 frames** (+33ms): Object landing/impact (in line with real physics)

---

## BGM selection decision tree

huashu-design skill comes with 6 BGMs (`assets/bgm-*.mp3`):

```
What is an animated character?
├─ Product launch/tech demo → bgm-tech.mp3 (minimal synth + piano)
├─ Tutorial explanation / tool usage → bgm-tutorial.mp3 (warm, instructional)
├─ Educational learning / Principle explanation → bgm-educational.mp3 (curious, thoughtful)
├─ Marketing advertising / brand promotion → bgm-ad.mp3 (upbeat, promotional)
└─ Similar styles require variations → bgm-*-alt.mp3 (respective alternative versions)
```

### Scenes without BGM (worth considering)
Reference Anthropic Code Desktop (ref-2): **0 SFX + pure Lo-fi BGM** can also be very advanced.

**When to choose no BGM**:
- Animation duration <10s (BGM cannot be created)
- Product character is "focus/meditation"
- The scene itself has environmental sound/narration sound
- When SFX density is high (to avoid auditory overload)

---

## Scene recipe (out of the box)

### Formula A · Product release hero (same model as huashu-design v9)
```
Duration: 25 seconds
BGM: bgm-tech.mp3 · 45% · Frequency band <4kHz
SFX Density: ~6/10s

cue：
Terminal typing → type × 4 (interval 0.6s)
Enter → enter
Card aggregation → card × 4 (peak offset 0.2s)
Select → click
  Ripple   → whoosh
4 times focus → focus × ​​4
  Logo     → thud（1.5s）

Volume: BGM 0.45 / SFX 1.0 · amix normalize=0
```

### Recipe B · Tool function demonstration (refer to Anthropic Code Desktop)
```
Duration: 30-45 seconds
BGM：bgm-tutorial.mp3 · 50%
SFX density: 0-2 pieces/10s (very few)

Strategy: Let BGM + explain the voiceover driver, SFX only at the **decisive moment** (file save/command execution completed)
```

### Recipe C · AI Generation Demo
```
Duration: 15-20 seconds
BGM: bgm-tech.mp3 or no BGM
SFX density: ~8/10s (high density)

cue：
User input → type + enter
AI starts processing → magic/ai-process (1.2s loop)
Build complete → feedback/complete-done
Result rendering → magic/sparkle
  
Highlights: ai-process can cycle 2-3 times throughout the entire generation process
```

### Recipe D · Pure atmospheric long shot (refer to Artifacts)
```
Duration: 10-15 seconds
BGM: None
SFX: 3-5 well-designed cues individually

Strategy: Each SFX is the protagonist, there is no problem of BGM being "blended together".
Suitable for: single product slow-motion, close-up display
```

---

## ffmpeg synthesis template

### Template 1 · Single SFX overlay to video
```bash
ffmpeg -y -i video.mp4 -itsoffset 2.5 -i sfx.mp3 \
  -filter_complex "[0:a][1:a]amix=inputs=2:normalize=0[a]" \
  -map 0:v -map "[a]" output.mp4
```

### Template 2 · Multi-SFX timeline composition (aligned by cue time)
```bash
ffmpeg -y \
  -i sfx-type.mp3 -i sfx-enter.mp3 -i sfx-click.mp3 -i sfx-thud.mp3 \
  -filter_complex "\
[0:a]adelay=1100|1100[a0];\
[1:a]adelay=3200|3200[a1];\
[2:a]adelay=7000|7000[a2];\
[3:a]adelay=21800|21800[a3];\
[a0][a1][a2][a3]amix=inputs=4:duration=longest:normalize=0[mixed]" \
  -map "[mixed]" -t 25 sfx-track.mp3
```
**Key Parameters**:
- `adelay=N|N`: The front is the left channel delay (ms), and the back is the right channel. Write it twice to ensure stereo alignment.
- `normalize=0`: Preserve dynamic range, key!
- `-t 25`: truncate to the specified length

### Template 3 · Video + SFX track + BGM (with band isolation)
```bash
ffmpeg -y -i video.mp4 -i sfx-track.mp3 -i bgm.mp3 \
  -filter_complex "\
[2:a]atrim=0:25,afade=in:st=0:d=0.3,afade=out:st=23.5:d=1.5,\
     lowpass=f=4000,volume=0.45[bgm];\
[1:a]highpass=f=800,volume=1.0[sfx];\
[bgm][sfx]amix=inputs=2:duration=first:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k final.mp4
```

---

## FAILURE MODE QUICK CHECK

| Symptoms | Root Cause | Fix |
|---|---|---|
| SFX cannot be heard | BGM high frequency part is covered | Add `lowpass=f=4000` for BGM + `highpass=f=800` for SFX |
| The sound effect is too loud and harsh | SFX absolute volume is too high | SFX volume is reduced to 0.7, while reducing BGM to 0.3, maintaining the difference |
| Rhythm conflict between BGM and SFX | Wrong choice of BGM (music with strong beat used) | Replaced with ambient/minimal synth BGM |
| BGM suddenly cuts off at the end of animation | Did not fade out | `afade=out:st=N-1.5:d=1.5` |
| SFX overlap into a blur | Cues are too dense + each SFX duration is too long | SFX duration is controlled within 0.5s, cue interval ≥ 0.2s |
| Official account mp4 has no sound | Official accounts sometimes mute auto-play | Don’t worry, there will be sound when the user clicks on it; gif has no sound |

---

## Linkage with vision (advanced)

### SFX sound should match the visual style
- Warm beige/paper-like visual → SFX uses **woody/soft** sounds (Morse, paper snap, soft click)
- Cool black technology vision → SFX uses **metal/digital** sounds (beep, pulse, glitch)
- Hand-drawn/childlike visuals → SFX uses **cartoon/exaggerated** sounds (boing, pop, zap)

Our current `apple-gallery-showcase.md` has a warm beige base color → paired with `keyboard/type.mp3` (mechanical) + `container/card-snap.mp3` (soft) + `impact/logo-reveal-v2.mp3` (cinematic bass)

### SFX can guide visual rhythm
Advanced tip: **Design the SFX timeline first, then adjust the visual animation to align the SFX** (not the other way around).
Because each cue in SFX is a "clock tick", the visual animation will be very stable when it adapts to the rhythm of SFX - on the contrary, if SFX pursues the visual, it will often feel inconsistent if it does not match ±1 frame.

---

## Quality Checklist (Self-inspection before publishing)

- [ ] Loudness difference: SFX peak - BGM peak = -6 to -8 dB?
- [ ] Band: BGM lowpass 4kHz + SFX highpass 800Hz?
- [ ] amix normalize=0 (preserve dynamic range)?
- [ ] BGM fade-in 0.3s + fade-out 1.5s？
- [ ] Is the number of SFX appropriate (choose density according to scene character)?
- [ ] Each SFX and visual beat aligned within the same frame (±1 frame)?
- [ ] Logo reveal sound effect is long enough (recommended 1.5s)?
- [ ] Listen again with BGM off: are the SFX rhythmic enough on their own?
- [ ] Turn off SFX and listen again: Are there any emotional ups and downs with the BGM alone?

Either layer of the two should be self-consistent when listened to alone. If it only sounds good if you add two layers, it means it’s not done well.

---

## refer to

- SFX asset list: `sfx-library.md`
- Visual style reference: `apple-gallery-showcase.md`
- In-depth audio analysis of three Anthropic films: `/Users/alchain/Documents/writing/01-public account writing/project/2026.04-huashu-design release/reference animation/AUDIO-BEST-PRACTICES.md`
- huashu-design v9 practical case: `/Users/alchain/Documents/writing/01-public account writing/project/2026.04-huashu-design release/pictures/hero-animation-v9-final.mp4`
