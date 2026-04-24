# Gallery Ripple + Multi-Focus · Scene arrangement philosophy

> A reusable visual arrangement structure extracted from huashu-design hero animation v9 (25 seconds, 8 scenes).
> It’s not about the animation production line, it’s about **what scenario is this arrangement “right”**?
> Practical reference: [demos/hero-animation-v9.mp4](../demos/hero-animation-v9.mp4) · [https://www.huasheng.ai/huashu-design-hero/](https://www.huasheng.ai/huashu-design-hero/)

## One sentence first

> **When you have 20+ homogeneous visual materials and the scene needs to "express a sense of scale and depth", give priority to the arrangement of Gallery Ripple + Multi-Focus instead of stacked layouts. **

General SaaS feature animations, product launches, skill promotions, series portfolio displays - as long as the amount of materials is sufficient and the style is consistent, this structure can almost be effective.

---

## What exactly does this technique express?

It's not "show material" - it's about telling a narrative through **two rhythm changes**:

**First beat · Ripple expansion (~1.5s)**: 48 cards spread out from the center to the surroundings, and the audience was shocked by the "quantity" - "Oh, this thing has so much output."

**Second shot · Multi-Focus (~8s, 4 loops)**: While the camera is in slow pan, dim + desaturate the background 4 times, and zoom in on a certain card individually to the center of the screen - the audience switches from "quantity impact" to "quality gaze", with a stable rhythm of 1.7s each time.

**Core Narrative Structure**: **Scale (Ripple) → Gaze (Focus × ​​4) → Fade (Walloff)**. The combination of these three beats expresses "Breadth × Depth" - not only can it do a lot, but each one is worth stopping to look at.

Compare the counterexample:

| Practice | Audience Perception |
|------|---------|
| 48 cards statically arranged (without Ripple) | Good-looking but no narrative, like a grid screenshot |
| Fast cut one by one (without Gallery context) | Like slideshow, loses "sense of scale" |
| Only Ripple but no Focus | Shocked but no one will remember any specific one |
| **Ripple + Focus × ​​4 (this recipe)** | **First shocked by the quantity, then stared at the quality, and finally faded away calmly - a complete emotional arc** |

---

## Preconditions (all must be met)

This arrangement is not a panacea. The following four items are indispensable:

1. **Material size ≥ 20 pictures, preferably 30+**
   Less than 20 Ripples will appear "empty" - each of the 48 grids is moving to give a sense of density. v9 uses 48 cells × 32 pictures (cyclic filling).

2. **The visual style of the material is consistent**
   All are 16:9 slide previews / all are app screenshots / all are cover designs - the aspect ratio, color tone, and layout are like a "set". Mix and match will make the Gallery look like a clipboard.

3. **The material still has readable information after being individually enlarged**
   Focus enlarges a certain card to a width of 960px. If the original image is blurry or the information is thin after enlarging, the Focus shot will be useless. Reverse verification: Can you pick 4 out of 48 pictures as the "most representative" ones? If you can't pick it out, it means the quality of the material is uneven.

4. **The scene itself is landscape or square, not vertical screen**
   Gallery's 3D tilt (`rotateX(14deg) rotateY(-10deg)`) requires a sense of horizontal extension, and a vertical screen will make the tilt effect look narrow and awkward.

**Backup path for missing conditions**:

| What is missing | Why is it degenerating |
|-------|-----------|
| Material < 20 pictures | Switch to "3-5 pictures side by side static display + focus one by one" |
| Inconsistent style | Switch to keynote-style of "cover + 3 chapter images" |
| Information is sparse | Use "data-driven dashboard" or "golden sentences + big characters" instead |
| Vertical screen scene | Use "vertical scroll + sticky cards" instead |

---

## Technical formula (v9 actual parameters)

### 4-Layer structure

```
viewport (1920×1080, perspective: 2400px)
└─ canvas (4320×2520, super large overflow) → 3D tilt + pan
      └─ 8×6 grid = 48 cards (gap 40px, padding 60px)
          └─ img (16:9, border-radius 9px)
      └─ focus-overlay (absolute center, z-index 40)
          └─ img (matches selected slide)
```

**Key**: The canvas is 2.25 times larger than the viewport, so that the pan can have the feeling of "peeping into a larger world".

### Ripple expansion (distance delay algorithm)

```js
// Entry time of each card = distance from center × 0.8s delay
const col = i % 8, row = Math.floor(i / 8);
const dc = col - 3.5, dr = row - 2.5;       // offset to center
const dist = Math.hypot(dc, dr);
const maxDist = Math.hypot(3.5, 2.5);
const delay = (dist / maxDist) * 0.8;       // 0 → 0.8s
const localT = Math.max(0, (t - rippleStart - delay) / 0.7);
const opacity = expoOut(Math.min(1, localT));
```

**Core Parameters**:
- Total duration 1.7s (`T.s3_ripple: [8.3, 10.0]`)
- Maximum delay 0.8s (the center comes out earliest, the corners come out latest)
- The entry time for each card is 0.7s
- Easing: `expoOut` (explosion, not smoothness)

**Things to do at the same time**: canvas scale from 1.25 → 0.94 (zoom out to reveal) - to match the synchronous zoom out feeling that appears.

### Multi-Focus (4 beats)

```js
T.focuses = [
  { start: 11.0, end: 12.7, idx: 2  },  // 1.7s
  { start: 13.3, end: 15.0, idx: 3  },  // 1.7s
  { start: 15.6, end: 17.3, idx: 10 },  // 1.7s
  { start: 17.9, end: 19.6, idx: 16 },  // 1.7s
];
```

**Rhythm Rule**: Each focus is 1.7s, with a 0.6s breather interval. Total 8s (11.0–19.6s).

**Inside each focus**:
- In ramp: 0.4s（`expoOut`）
- Hold: middle 0.9s (`focusIntensity = 1`)
- Out ramp: 0.4s（`easeOut`）

**Background changes (this is key)**:

```js
if (focusIntensity > 0) {
  const dimOp = entryOp * (1 - 0.6 * focusIntensity);  // dim to 40%
  const brt = 1 - 0.32 * focusIntensity;                // brightness 68%
  const sat = 1 - 0.35 * focusIntensity;                // saturate 65%
  card.style.filter = `brightness(${brt}) saturate(${sat})`;
}
```

**Not just opacity – desaturate + darken at the same time**. This makes the color of the foreground overlay "pop out" instead of just "brightening" it.

**Focus overlay size animation**:
- From 400×225 (entry) → 960×540 (hold state)
- There are 3 layers of shadow + 3px accent color outline ring on the periphery, giving a "framed feeling"

### Pan (a sense of continuity makes stillness less boring)

```js
const panT = Math.max(0, t - 8.6);
const panX = Math.sin(panT * 0.12) * 220 - panT * 8;
const panY = Math.cos(panT * 0.09) * 120 - panT * 5;
```

- Sine wave + linear drift double-layer motion - not a pure cycle, the position is different at each moment
- Different X/Y frequencies (0.12 vs 0.09) to avoid visual "regular loops"
- clamp at ±900/500px to prevent drifting out

**Why not use pure linear pan**: Pure linear viewers will "predict" where they will be in the next second; sine + drift makes every second new, and 3D tilt will produce a "slight seasickness" (the good kind), and the attention will be captured.

---

## 5 reusable patterns (distilled from v6→v9 iteration)

### 1. **expoOut is used as the main easing, not cubicOut**

`easeOut = 1 - (1-t)³` (smooth) vs `expoOut = 1 - 2^(-10t)` (rapid convergence after explosion).

**Reason for selection**: The first 30% of expoOut quickly reaches 90%, which is more like physical damping and conforms to the intuition of "heavy things falling to the ground". Especially suitable for:
- Card entry (sense of weight)
- Ripple diffusion (shock wave)
- Brand floats (sense of settling)

**When to still use cubicOut**: focus out ramp, symmetrical micro-motion effect.

### 2. **Paper base color + terracotta orange accent (Anthropic origin)**

```css
--bg: # F7F4EE; /* warm paper */
--ink: # 1D1D1F; /* almost black */
--accent: # D97757; /* Terracotta Orange */
--hairline: # E4DED2; /* warm lines */
```

**Why**: Warm background colors still have a "breathing" feel after GIF compression, unlike pure white which will look "screeny". Terracotta orange serves as the only accent throughout the terminal prompt, dir-card selection, cursor, brand hyphen, and focus ring—all visual anchors are connected by this single color.

**V5 Lesson**: Added noise overlay to simulate "paper texture", and as a result, the GIF frame compression was completely useless (each frame is different). v6 was changed to "only use background color + warm shadow", retaining 90% of the paper feel and reducing the GIF size by 60%.

### 3. **Two levels of Shadow simulation depth, no need for true 3D**

```css
.gallery-card.depth-near { box-shadow: 0 32px 80px -22px rgba(60,40,20,0.22), ... }
.gallery-card.depth-far  { box-shadow: 0 14px 40px -16px rgba(60,40,20,0.10), ... }
```

Use `sin(i × 1.7) + cos(i × 0.73)` deterministic algorithm to assign near/mid/far three-level shadow to each card - **Visually there is a "three-dimensional stacking" feeling, but the transform of each frame is completely unchanged, and the GPU consumption is 0**.

**The cost of true 3D**: Each card is `translateZ` alone, and the GPU is calculating 48 transform + shadow blur every frame. I tried v4 and Playwright struggled to record 25fps. The difference in visual effect between the two shadow levels of v6 is <5%, but the cost difference is 10 times.

### 4. **Font weight changes (font-variation-settings) are more cinematic than font size changes**

```js
const wght = 100 + (700 - 100) * morphP;  // 100 → 700 over 0.9s
wordmark.style.fontVariationSettings = `"wght" ${wght.toFixed(0)}`;
```

The Brand wordmark uses a 0.9s gradient from Thin → Bold, and is fine-tuned with letter-spacing (-0.045 → -0.048em).

**Why it’s better than zooming in and out**:
- Zoom in and out. The audience has seen too much and their expectations are solidified.
- The word weight change is "inner sense of fullness", like a balloon being blown up, rather than "being pushed closer"
- variable fonts is a feature that was only popularized in 2020+, and the audience subconsciously feels "modern"

**Restrictions**: Must use fonts that support variable font (Inter/Roboto Flex/Recursive, etc.). Ordinary static fonts can only be mimicked (there will be a jump when switching between several fixed weights).

### 5. **Corner Brand Low Intensity Continuous Signature**

There is a small logo of `HUASHU · DESIGN` in the upper left corner of the Gallery stage, 16% opacity color value, 12px font size, and wide font spacing.

**Why add this**:
- After the Ripple outbreak, viewers are prone to "losing focus" and forgetting what they are watching. Lightly mark the upper left corner to help anchor.
- More advanced than a full-screen large logo - branding people know that the brand signature does not need to be shouted
- Leave a signal of attribution even when the GIF is screenshot shared

**Rules**: Appear only in the middle (the picture is busy), close the opening (the terminal is not covered), and close the ending (the brand reveal is the protagonist).

---

## Counterexample: When not to use this arrangement

**❌ Product demonstration (to show functions)**: Gallery makes every picture pass by in a flash, and the audience cannot remember any function. Use "single screen focus + tooltip annotation" instead.

**❌ Data-driven content**: Audiences want to read numbers, and Gallery’s fast pace doesn’t give them time. Use "data chart + item-by-item reveal" instead.

**❌ Story Narrative**: Gallery is a "parallel" structure, and the story requires "cause and effect". Use keynote chapter switching instead.

**❌ Only 3-5 images**: Ripple is not dense enough and looks like a "patch". Use "static arrangement + highlight one by one" instead.

**❌ Vertical screen (9:16)**: 3D tilt needs to be extended horizontally. The vertical screen will make the tilt feel "crooked" instead of "expanded".

---

## How to judge whether your task is suitable for this arrangement?

Three-step quick check:

**Step 1 · Number of Materials**: Count how many similar visual materials you have. < 15 → stop; 15-25 → make up; 25+ → use directly.

**Step 2 · Consistency test**: Place 4 random materials side by side. Does it look like a "set"? Unlike → Unify the style first and then do it, or change the plan.

**Step 3 · Narrative Matching**: Do you want to express "Breadth × Depth" (Quantity × Quality)? Or "process", "function" and "story"? If it’s not the former, don’t be too rigid.

All three steps are yes, just fork v6 HTML, change the `SLIDE_FILES` array and timeline to reuse it. The color palette is changed to `--bg / --accent / --ink`, and the overall skin is changed but not the bones.

---

## Related Reference

- Complete technical process: [references/animations.md](animations.md) · [references/animation-best-practices.md](animation-best-practices.md)
- Animation export pipeline: [references/video-export.md](video-export.md)
- Audio configuration (BGM + SFX dual track): [references/audio-design-rules.md](audio-design-rules.md)
- Horizontal reference for Apple gallery style: [references/apple-gallery-showcase.md](apple-gallery-showcase.md)
- Source HTML (v6 + audio integrated version): `www.huasheng.ai/huashu-design-hero/index.html`
