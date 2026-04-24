# Animation Best Practices · Forward animation design grammar

> Based on Anthropic’s three official product animations (Claude Design / Claude Code Desktop / Claude for Word)
> In-depth dismantling and extraction of "Anthropic-level" animation design rules.
>
> Used in conjunction with `animation-pitfalls.md` (pitfalls avoidance list) - this file is "**should be done**",
> pitfalls is "**Don't do this**", both are orthogonal and must be read.
>
> **Constraint Statement**: This document only contains **motion logic and expression style**, and **does not introduce any specific color values ​​of brand colors**.
> Color decision making §1.a Core asset agreement (extracted from brand spec) or "design direction consultant"
> (color schemes for each of the 20 philosophies). This reference discusses "**how to move**", not "**what color**".

---

## §0 · Who are you · Identity and taste

> Read this section before reading any of the technical rules that follow. Rules emerge from identities -
> Not the other way around.

### §0.1 Identity Anchor

**You are a motion designer who has studied Anthropic / Apple / Pentagram / Field.io motion files. **

When you animate, you're not adjusting CSS transitions - you're **simulating a physical world** with digital elements,
Let the audience's subconscious believe that "this is an object with weight, inertia, and overflow."

You don’t do PowerPoint-style animations. You don't do "fade in fade out" animations. The animation you made makes people believe the screen
It’s a space you can reach into**.

### §0.2 Core Beliefs (3 items)

1. **Animation is physics, not animation curves**
   `linear` is a number and `expoOut` is an object. You believe that the pixels on your screen deserve to be treated as "objects".
   Each easing choice is an answer to the physical question "How heavy is this element? What is the friction coefficient?"

2. **Time allocation is more important than curve shape**
   Slow-Fast-Boom-Stop is your breath. **Evenly-paced animation is a technical demonstration, and rhythmic animation is a narrative. **
   Slowing down at the right moment is more important than easing at the wrong moment.

3. **Being courteous to the audience is more difficult than showing off your skills**
   A 0.5 second pause before key results is a **technique**, not a compromise. **Allowing the human brain to have reaction time is the highest quality of an animator. **
   By default, AI will make an animation with no pauses and full information density - that's newbies. What you have to do is exercise restraint.

### §0.3 Taste standards · What is beauty

Here’s how you judge “good” and “great.” Each one has an **identification method** - when you see a candidate animation,
Use these questions to determine whether it's up to par, rather than mechanically comparing the 14 rules.

| Dimensions of beauty | Recognition methods (audience response) |
|---|---|
| **Physical weight** | At the end of the animation, the element "falls" steadily - it doesn't "stop" there. The audience subconsciously feels "this has weight" |
| **Courtesy to the audience** | There is a sensible pause (≥300ms) before the key information appears - the audience has time to "**see**" before continuing |
| **Blank** | The ending is abrupt stop + hold, not fade to black. The last frame is clear, certain, and decisive |
| **Restraint** | There is only one "120% exquisite" part in the whole film, and the other 80% is just right - **showing off skills everywhere is a sign of cheapness** |
| **Feel** | Arc (not straight line), irregular (not the mechanical rhythm of setInterval), breathing feeling |
| **Respect** | Show the tweaking process and bug fixes - **No hiding work, no "magic"**. AI is a collaborator, not a magician |

### §0.4 Self-examination · Audience first reaction method

After making an animation, what is the audience’s first reaction after watching it? ** – This is the only metric you want to optimize for.

| Audience Reaction | Rating | Diagnosis |
|---|---|---|
| "Looks pretty smooth" | good | Qualified but featureless, you are working on PowerPoint |
| "This animation is really smooth" | good+ | The technique is right, but not amazing |
| "This thing really looks like it's floating off the table" | great | You're getting a sense of physical weight |
| "It doesn't look like AI did it" | great+ | You've hit the Anthropic threshold |
| "I want to **take a screenshot** and send it to Moments" | great++ | You did it so that the audience can take the initiative to spread the word |

**The difference between great and good is not about technical correctness, but about taste judgment**. Technically correct + right taste = great.
Technically correct + tasteful = good. Technical errors = not getting started.

### §0.5 The relationship between identity and rules

The technical rules in §1-§8 below are the **implementation methods** of this set of identities in specific scenarios—not a list of independent rules.

- Encounter a scenario not covered by the rules → Return to §0, use **identity** to judge, don't guess blindly
- If there is a conflict between rules → go back to §0 and use the **criteria of taste** to decide which one is more important
- If you want to break a rule → first answer: "Which rule of §0.3 is in line with this?" If you can answer it, then break it; if you can't, don't break it.

good. Read on.

---

## Overview · Animation is a three-layer expansion of physics

The reason most AI-generated animations feel cheap is that they behave like “numbers” rather than “objects”.
Objects in the real world have mass, inertia, elasticity, and overflow. The source of the "high-end feel" of Anthropic's three films,
It lies in giving digital elements a set of movement rules in the physical world.

This set of rules has 3 levels:

1. **Narrative rhythm layer**: Slow-Fast-Boom-Stop time distribution
2. **Motion Curve Layer**: Expo Out/Overshoot/Spring, reject linear
3. **Expression language layer**: display process, mouse arc, logo deformation and closing

---

## 1. Narrative rhythm · Slow-Fast-Boom-Stop 5 paragraph structure

All three Anthropic films follow this structure without exception:

| Segment | Proportion | Rhythm | Function |
|---|---|---|---|
| **S1 Trigger** | ~15% | Slow | Give humans time to react and establish a sense of reality |
| **S2 Generation** | ~15% | Medium | Visually stunning point appears |
| **S3 Process** | ~40% | Fast | Demonstrate controllability/density/detail |
| **S4 Explosion** | ~20% | Boom | Zoom out/3D pop-out/Multi-panel pop-up |
| **S5 drop** | ~10% | Jing | Brand Logo + abrupt end |

**Specific duration mapping** (15 seconds animation as an example):
S1 triggers 2s · S2 generates 2s · S3 process 6s · S4 bursts 3s · S5 falls 2s

**Prohibited Things**:
- ❌ Even rhythm (same density of information per second) - audience fatigue
- ❌ Continuously high density - no peaks or memory points
- ❌ fade out (fade out to transparency) - should **stop**

**Self-check**: Use pen and paper to draw 5 thumbnails, each representing the climax of a paragraph. If there is not much difference between the 5 pictures,
It shows that the rhythm is not achieved.

---

## 2. Easing philosophy·Reject linear, embrace physics

All animations in Anthropic's three films use Bezier curves with "damping". Default cubic easeOut
(`1-(1-t)³`) **not sharp enough** - the start is not fast enough and the stop is not stable enough.

### Three core Easing (animations.jsx is built in)

```js
// 1. Expo Out · Quickly start slow braking (most commonly used, default main easing)
// Corresponding CSS: cubic-bezier(0.16, 1, 0.3, 1)
Easing.expoOut(t) // = t === 1 ? 1 : 1 - Math.pow(2, -10 * t)

// 2. Overshoot · Flexible toggle/button popup
// Corresponding CSS: cubic-bezier(0.34, 1.56, 0.64, 1)
Easing.overshoot(t)

// 3. Spring Physics · Geometry return to position, natural placement
Easing.spring(t)
```

### Usage mapping

| Scene | Which Easing to use |
|---|---|
| Card rise-in / Panel entry / Terminal fade / focus overlay | **`expoOut`** (main easing, most commonly used) |
| Toggle switch / button popup / emphasize interaction | `overshoot` |
| Preview geometry return / physical placement / UI element bounce | `spring` |
| Continuous motion (such as mouse trajectory interpolation) | `easeInOut` (preserve symmetry) |

### Counter-intuitive insights

The animation in most product videos is too fast and too hard. `linear` makes digital elements behave like machines, `easeOut` is the basic score,
`expoOut` is the technical root of "high-end sense" - it gives digital elements a sense of **physical world weight**.

---

## 3. Movement language · 8 common principles

### 3.1 The background color does not need to be pure black or pure white.

None of the three Anthropic films use `#FFFFFF` or `#000000` as the main background. **Neutral colors with color temperature**
(either warm or cold) has the material feel of "paper/canvas/desktop", which weakens the sense of machine.

**Specific color value decision** go to §1.a Core Asset Agreement (extracted from brand spec) or "Design Direction Consultant"
(Background schemes for each of the 20 philosophies). This reference does not give specific color values ​​- that is a **brand decision**, not a sports rule.

### 3.2 Easing is by no means linear

See §2.

### 3.3 Slow-Fast-Boom-Stop Narrative

See §1.

### 3.4 Show “process” rather than “magic results”

- Claude Design shows tweak parameters and dragging sliders (not one-click to generate perfect results)
- Claude Code shows code error + AI fix (not a success)
- Claude for Word shows the redline modification process of red deletion and green addition (not directly to the final draft)

**Common subtext**: Products are **collaborators, paired engineers, senior editors**—not one-click magicians.
This accurately attacks the pain points of "controllability" and "authenticity" among professional users.

**Anti-AI slop**: AI will do the "magic one-click success" animation by default (one-click generation → perfect result),
This is the universal common denominator. **Do it in reverse** - show the process, show tweaks, show bugs and fixes-
It is the source of brand recognition.

### 3.5 Manual drawing of mouse trajectory (arc + Perlin Noise)

The movement of a real mouse is not a straight line, but "starting acceleration → arc → deceleration correction → click".
The mouse trajectory of AI direct linear interpolation **has a subconscious feeling of repulsion**.

```js
// Quadratic Bezier curve interpolation (starting point → control point → end point)
function bezierQuadratic(p0, p1, p2, t) {
  const x = (1-t)*(1-t)*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0];
  const y = (1-t)*(1-t)*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1];
  return [x, y];
}

// Path: starting point → deviation from midpoint → end point (make an arc)
const path = [[100, 100], [targetX - 200, targetY + 80], [targetX, targetY]];

// Then superimpose a very small Perlin Noise (±2px) to create "hand shake"
const jitterX = (simpleNoise(t * 10) - 0.5) * 4;
const jitterY = (simpleNoise(t * 10 + 100) - 0.5) * 4;
```

### 3.6 Logo "Morph"

The logos of Anthropic's three films are not simply fade-in, but are transformed from the previous visual element.

**Common mode**: Count down 1-2 seconds to do Morph / Rotate / Converge, so that the entire narrative "collapses" at the brand point.

**Low cost implementation** (no real morph required):
Let the previous visual element "collapse" into a color block (scale → 0.1, translate toward the center),
The color blocks then "expand" into wordmarks. 150ms fast cut + motion blur for transition
（`filter: blur(6px)` → `0`）。

```js
<Sprite start={13} end={14}>
{/* Collapse: previous element scale 0.1, opacity maintained, filter blur increased */}
  const scale = interpolate(t, [0, 0.5], [1, 0.1], Easing.expoOut);
  const blur = interpolate(t, [0, 0.5], [0, 6]);
</Sprite>
<Sprite start={13.5} end={15}>
{/* Expansion: Logo scale 0.1 → 1 from the center of the color block, blur 6 → 0 */}
  const scale = interpolate(t, [0, 0.6], [0.1, 1], Easing.overshoot);
  const blur = interpolate(t, [0, 0.6], [6, 0]);
</Sprite>
```

### 3.7 Serif + Sans Serif Double Font

- **Branding/Narration**: serifs (with "academic/publication/tasteful")
- **UI/Code/Data**: Sans Serif + Monospace

**A single font is wrong**. Serifs give “class”, sans-serifs give “function”.

The specific font selection follows the brand spec (the Display / Body / Mono three stacks of brand-spec.md) or the design direction.
20 Philosophies of Consultants. This reference does not give specific fonts - that is a **branding decision**.

### 3.8 Focus switching = background weakening + foreground sharpening + Flash boot

Focus switching doesn't just reduce opacity. The complete recipe is:

```js
// Filter combinations for out-of-focus elements
tile.style.filter = `
  brightness(${1 - 0.5 * focusIntensity})
  saturate(${1 - 0.3 * focusIntensity})
  blur(${focusIntensity * 4}px)        // ← Key: Add blur to really "step back"
`;
tile.style.opacity = 0.4 + 0.6 * (1 - focusIntensity);

// After the focus is completed, do a 150ms Flash highlight at the focus position to guide your eyes back.
focusOverlay.animate([
  { background: 'rgba(255,255,255,0.3)' },
  { background: 'rgba(255,255,255,0)' }
], { duration: 150, easing: 'ease-out' });
```

**Why blur is necessary**: Only relying on opacity + brightness, elements outside the focus are still "sharp".
There is no visual "retreating to the background" effect. blur(4-8px) makes the non-focus really lose a layer of depth of field.

---

## 4. Specific sports skills (code snippets that can be copied directly)

### 4.1 FLIP / Shared Element Transition

The button "expands" into an input box, **not** the button disappears + a new panel appears. The core is **the same DOM element** in
A transition between two states, not a cross-fade between two elements.

```jsx
// Use Framer Motion layoutId
<motion.div layoutId="design-button">Design</motion.div>
// ↓ Same layoutId after clicking
<motion.div layoutId="design-button">
  <input placeholder="Describe your design..." />
</motion.div>
```

Native implementation reference https://aerotwist.com/blog/flip-your-animations/

### 4.2 "Breathing" expansion (width→height)

Panel expansion does not expand width and height at the same time, but:
- First 40% of time: just pull width (keep height small)
-Last 60% time:width maintains,supports height

This simulates the feeling of "expanding first, then filling in water" in the physical world.

```js
const widthT = interpolate(t, [0, 0.4], [0, 1], Easing.expoOut);
const heightT = interpolate(t, [0.3, 1], [0, 1], Easing.expoOut);
style.width = `${widthT * targetW}px`;
style.height = `${heightT * targetH}px`;
```

### 4.3 Staggered Fade-up（30ms stagger）

When table rows, card columns, and list items enter, **each element is delayed by 30ms**, and `translateY` ​​returns from 10px to 0.

```js
rows.forEach((row, i) => {
  const localT = Math.max(0, t - i * 0.03);  // 30ms stagger
  row.style.opacity = interpolate(localT, [0, 0.3], [0, 1], Easing.expoOut);
  row.style.transform = `translateY(${
    interpolate(localT, [0, 0.3], [10, 0], Easing.expoOut)
  }px)`;
});
```

### 4.4 Non-linear breathing · Hover 0.5s before key results

The machine executes quickly and coherently, but **hoveres for 0.5 seconds** before key results appear, giving the audience's brain time to react.

```jsx
// Typical scenario: AI is generated → hover for 0.5s → results appear
<Sprite start={8} end={8.5}>
{/* 0.5s pause - nothing moves, letting the audience stare at the loading status */}
  <LoadingState />
</Sprite>
<Sprite start={8.5} end={10}>
  <ResultAppear />
</Sprite>
```

**Counterexample**: After the AI ​​is generated, it immediately switches to the result seamlessly - the audience has no time to react and information is lost.

### 4.5 Chunk Reveal · Simulate token streaming

When AI generates text, don’t use `setInterval` to pop up single characters** (like old movie subtitles), use **chunk reveal**
——2-5 characters appear at a time with irregular intervals, simulating real token streaming output.

```js
// Divide into chunks instead of characters
const chunks = text.split(/(\s+|,\s*|\.\s*|;\s*)/);  // Cut by word + punctuation
let i = 0;
function reveal() {
  if (i >= chunks.length) return;
  element.textContent += chunks[i++];
  const delay = 40 + Math.random() * 80;  // Irregular 40-120ms
  setTimeout(reveal, delay);
}
reveal();
```

### 4.6 Anticipation → Action → Follow-through

3 of Disney’s 12 Principles. Anthropic is used very explicitly:

- **Anticipation** (preparatory): There is a small reverse movement before the action starts (the button shrinks slightly and then pops up)
- **Action**: the main action itself
- **Follow-through** (Follow): There is a lingering after the action (the card bounces slightly after it is placed)

```js
// The complete three paragraphs of card admission
const anticip = interpolate(t, [0, 0.2], [1, 0.95], Easing.easeIn);     // preparation
const action  = interpolate(t, [0.2, 0.7], [0.95, 1.05], Easing.expoOut); // initiative
const settle  = interpolate(t, [0.7, 1], [1.05, 1], Easing.spring);       // rebound
// Final scale = three-stage product or piecewise application
```

**Counterexample**: Only Action without Anticipation + Follow-through animation, like "PowerPoint animation".

### 4.7 3D Perspective + translateZ layering

If you want the temperament of "tilted 3D + floating card", add perspective to the container and give different translateZ to individual elements:

```css
.stage-wrap {
  perspective: 2400px;
perspective-origin: 50% 30%; /* slightly overhead view */
}
.card-grid {
  transform-style: preserve-3d;
transform: rotateX(8deg) rotateY(-4deg); /* golden ratio */
}
.card:nth-child(3n) { transform: translateZ(30px); }
.card:nth-child(5n) { transform: translateZ(-20px); }
.card:nth-child(7n) { transform: translateZ(60px); }
```

**Why rotateX 8° / rotateY -4° is the golden ratio**:
- Greater than 10° → The element distortion is too strong and looks like "falling down"
- Less than 5° → like "cross-cut" instead of "perspective"
- The asymmetric ratio of 8° × -4° simulates the natural angle of "the camera is looking down at the upper left corner of the desktop"

### 4.8 Oblique Pan·Move XY simultaneously

The camera movement is not purely up and down or purely left and right, but **moves XY at the same time** to simulate diagonal movement:

```js
const panX = Math.sin(flowT * 0.22) * 40;
const panY = Math.sin(flowT * 0.35) * 30;
stage.style.transform = `
  translate(-50%, -50%)
  rotateX(8deg) rotateY(-4deg)
  translate3d(${panX}px, ${panY}px, 0)
`;
```

**Key**: X and Y have different frequencies (0.22 vs 0.35) to avoid Lissajous cycle regularization.

---

## 5. Scene recipe (three narrative templates)

The three videos in the reference material correspond to three product personalities. **Choose a product that works best for you**, don’t mix and match.

### Recipe A · Apple Keynote Dramatic (Claude Design Class)

**Suitable**: Large version releases, hero animations, and visually stunning priority
**Rhythm**: Slow-Fast-Boom-Stop strong arc
**Easing**: Full `expoOut` + a small amount of `overshoot`
**SFX Density**: High (~0.4/s), SFX pitch adjusted to BGM scale
**BGM**: IDM / minimalist technology electronics, calm + precision
**Closing**: The camera zooms out → drop → Logo deformation → ethereal single tone → abruptly stop

### Recipe B · One-shot tool style (Claude Code type)

**Suitable**: developer tools, productivity apps, flow scenarios
**Rhythm**: Continuous and stable flow, no obvious peaks
**Easing**: `spring` physics + `expoOut`
**SFX Density**: **0** (Purely relies on BGM to drive the editing rhythm)
**BGM**：Lo-fi Hip-hop / Boom-bap，85-90 BPM
**Core skills**: Key UI actions are based on BGM kick/snare transients - "**Music rhythm is interactive sound effects**"

### Recipe C · Office Efficiency Narrative (Claude for Word class)

**Suitable**: Enterprise software, documents/forms/calendars, professional sense is preferred
**Rhythm**: Multiple scene hard cuts + Dolly In/Out
**Easing**: `overshoot` (toggle) + `expoOut` (panel)
**SFX Density**: Medium (~0.3/s), UI click is the main one
**BGM**: Jazzy Instrumental, minor, BPM 90-95
**Core Highlights**: A certain scene must have a "full film highlight" - 3D pop-out / floating out of the plane

---

## 6. Counterexample · Doing this is AI slop

| Anti-pattern | Why it's wrong | What to do |
|---|---|---|
| `transition: all 0.3s ease` | `ease` is a relative of linear, all elements move at the same speed | Use `expoOut` + stagger to divide elements |
| All entries have `opacity 0→1` | No sense of direction of movement | With `translateY 10→0` + Anticipation |
| Logo fades in | No sense of narrative closure | Morph / Converge / Collapse-Expand |
| Mouse moves in a straight line | Subconscious machine feeling | Bezier arc + Perlin Noise |
| Typing words pop out (setInterval) | Like old movie subtitles | Chunk Reveal, random intervals |
| No hover for key results | No reaction time for the audience | 0.5s hover before the result |
| Focus switching only changes opacity | Non-focused elements are still sharp | opacity + brightness + **blur** |
| Pure black base / pure white base | Cyber ​​sense / reflective fatigue | Neutral color with color temperature (brand spec) |
| All animations equally fast | No pacing | Slow-Fast-Boom-Stop |
| Fade out ending | No sense of decision | Stop suddenly (hold the last frame) |

---

## 7. Self-check checklist (60 seconds before animation delivery)

- [ ] The narrative structure is Slow-Fast-Boom-Stop, not evenly paced?
- [ ] Default easing is `expoOut`, not `easeOut` or `linear`?
- [ ] Toggle / button popup using `overshoot`?
- [ ] Is there a 30ms stagger for card/list entries?
- [ ] 0.5s hover before key result?
- [ ] Use Chunk Reveal when typing, not setInterval single words?
- [ ] Added blur (not just opacity) to focus switching?
- [ ] Logo is Morph, not fade-in?
- [ ] The background color is not pure black/pure white (with color temperature)?
- [ ] Text with serif + sans-serif hierarchy?
- [ ] The ending ends abruptly, not a diminution?
- [ ] (If you have a mouse) Is the mouse trajectory an arc, not a straight line?
- [ ] SFX density consistent with product characteristics (see recipes A/B/C)?
- [ ] There is a 6-8dB loudness difference between BGM and SFX? (See `audio-design-rules.md`)

---

## 8. Relationship with other references

| reference | positioning | relationship |
|---|---|---|
| `animation-pitfalls.md` | Technical pitfalls to avoid (16 items) | "**Don't do this**" · The reverse side of this document |
| `animations.md` | Stage/Sprite engine usage | Basics of animation **how to write** |
| `audio-design-rules.md` | Dual-track audio rules | Rules for animation **audio** |
| `sfx-library.md` | List of 37 SFX | Sound Effects **Library** |
| `apple-gallery-showcase.md` | Apple gallery display style | Features on a specific sports style |
| **This document** | Forward motion design grammar | "**This should be done**" |

**Calling order**:
1. First look at the four position questions in Step 3 of the SKILL.md workflow (determining narrative roles and visual temperature)
2. After selecting the direction, read this document to determine the **movement language** (recipe A/B/C)
3. Refer to `animations.md` and `animation-pitfalls.md` when writing code
4. When exporting video, use `audio-design-rules.md` + `sfx-library.md`

---

## Appendix · Source of material for this document

- Anthropic official animation dismantling: `Reference Animation/BEST-PRACTICES.md` in the Uncle Hua project directory
- Anthropic Audio Teardown: Same directory `AUDIO-BEST-PRACTICES.md`
- 3 reference videos: `ref-{1,2,3}.mp4` + corresponding to `gemini-ref-*.md` / `audio-ref-*.md`
- **Strict filtering**: This reference does not include any specific brand color values, font names, or product names.
  Color/font decisions go §1.a Core Asset Protocol or 20 Design Philosophies.
