#Apple Gallery Showcase · Gallery display wall animation style

> Source of inspiration: Claude Design official website hero video + Apple product page "work wall" display
> Practical source: huashu-design releases hero v5
> Applicable scenarios: **Product release hero animation, skill demonstration, portfolio display** - any scene where "multiple high-quality outputs" need to be displayed at the same time and guide the audience's attention

---

## Trigger judgment: when to use this style

**Suitable**:
- There are more than 10 real outputs to be displayed on the same screen (PPT, App, webpage, infographic)
- The audience is a professional audience (developers, designers, product managers) and is sensitive to "texture"
- The temperament I hope to convey is "restrained, exhibition-style, high-end, and with a sense of space"
- The focus and overall situation need to exist at the same time (look at the details without losing the overall picture)

**Not suitable**:
- Single product focus (using frontend-design’s product hero template)
- Emotional/storytelling animation (using timeline narrative template)
- Small screen/vertical screen (tilted viewing angle will blur on small screens)

---

## Core Vision Token

```css
:root {
/* Light gallery palette */
  --bg:         # F5F5F7; /* Main canvas background — Apple official website gray */
  --bg-warm:    # FAF9F5; /* Warm off-white variant */
  --ink:        # 1D1D1F; /* Main text color */
  --ink-80:     #3A3A3D;
  --ink-60:     #545458;
  --muted:      # 86868B; /* Secondary text */
  --dim:        #C7C7CC;
  --hairline:   # E5E5EA; /* Card 1px border */
  --accent:     # D97757; /* Terracotta Orange — Claude brand */
  --accent-deep:#B85D3D;

  --serif-cn: "Noto Serif SC", "Songti SC", Georgia, serif;
  --serif-en: "Source Serif 4", "Tiempos Headline", Georgia, serif;
  --sans:     "Inter", -apple-system, "PingFang SC", system-ui;
  --mono:     "JetBrains Mono", "SF Mono", ui-monospace;
}
```

**Key Principles**:
1. **Never use a pure black base**. A black background will make the work look like a movie and not like "adoptable work product."
2. **Terracotta orange is the only hue accent**, all others are grayscale + white
3. **Three font stack** (serif English + serif Chinese + sans + mono) creates the temperament of a "publication" rather than an "Internet product"

---

## Core layout mode

### 1. Suspended card (the basic unit of the entire style)

```css
.gallery-card {
  background: #FFFFFF;
  border-radius: 14px;
padding: 6px; /* The padding is "framed paper" */
  border: 1px solid var(--hairline);
  box-shadow:
0 20px 60px -20px rgba(29, 29, 31, 0.12), /* Main shadow, soft and long */
0 6px 18px -6px rgba(29, 29, 31, 0.06); /* The second layer of low beam creates a floating feeling */
aspect-ratio: 16 / 9; /* Unify slide ratio */
  overflow: hidden;
}
.gallery-card img {
  width: 100%; height: 100%;
  object-fit: cover;
border-radius: 9px; /* Slightly smaller than the card's rounded corners, visual nesting */
}
```

**Negative teaching material**: Do not use edge tiles (no padding, no border, no shadow) - that is an expression of density in an information graphic, not an exhibition.

### 2. 3D tilted work wall

```css
.gallery-viewport {
  position: absolute; inset: 0;
  overflow: hidden;
perspective: 2400px; /* Deeper perspective, no exaggerated tilt */
  perspective-origin: 50% 45%;
}
.gallery-canvas {
width: 4320px; /* canvas = 2.25× viewport */
height: 2520px; /* Leave pan space */
  transform-origin: center center;
  transform: perspective(2400px)
rotateX(14deg) /* lean backward */
rotateY(-10deg) /* turn left */
rotateZ(-2deg); /* Slightly tilted, remove too regular */
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 40px;
  padding: 60px;
}
```

**Parameters sweet spot**:
- rotateX: 10-15deg (any more is like a VIP background board for a cocktail party)
- rotateY: ±8-12deg (left and right symmetry)
- rotateZ: ±2-3deg (human touch of "This is not done by a machine")
- Perspective: 2000-2800px (less than 2000 will be fisheye, greater than 3000 will be close to orthographic projection)

### 3. 2×2 four corners convergence (select scene)

```css
.grid22 {
  display: grid;
  grid-template-columns: repeat(2, 800px);
  gap: 56px 64px;
  align-items: start;
}
```

Each card slides + fade in from the corresponding corner (tl/tr/bl/br) to the center. The corresponding `cornerEntry` vector:

```js
const cornerEntry = {
  tl: { dx: -700, dy: -500 },
  tr: { dx:  700, dy: -500 },
  bl: { dx: -700, dy:  500 },
  br: { dx:  700, dy:  500 },
};
```

---

## Five core animation modes

### Mode A · Four corners convergence (0.8-1.2s)

Four elements slide in from the four corners of the viewport, while scaling 0.85→1.0, corresponding to ease-out. An opening suitable for "showing multiple options".

```js
const inP = easeOut(clampLerp(t, start, end));
card.style.transform = `translate3d(${(1-inP)*ce.dx}px, ${(1-inP)*ce.dy}px, 0) scale(${0.85 + 0.15*inP})`;
card.style.opacity = inP;
```

### Mode B · Select to zoom in + other slide out (0.8s)

The selected card is enlarged 1.0→1.28, and other cards fade out + blur + float back to the four corners:

```js
// selected
card.style.transform = `translate3d(${cellDx*outP}px, ${cellDy*outP}px, 0) scale(${1 + 0.28*easeOut(zoomP)})`;
// Not selected
card.style.opacity = 1 - outP;
card.style.filter = `blur(${outP * 1.5}px)`;
```

**Key**: The unselected items need to be blurred, not purely faded. blur simulates depth of field and visually "pushes out" the selected object.

### Mode C · Ripple ripple expansion (1.7s)

From the center outward, according to the distance delay, each card fades in sequence + shrinks from 1.25x to 0.94x ("zoom out"):

```js
const col = i % COLS, row = Math.floor(i / COLS);
const dc = col - (COLS-1)/2, dr = row - (ROWS-1)/2;
const dist = Math.sqrt(dc*dc + dr*dr);
const delay = (dist / maxDist) * 0.8;
const localT = Math.max(0, (t - rippleStart - delay) / 0.7);
card.style.opacity = easeOut(Math.min(1, localT));

// At the same time, the overall scale 1.25→0.94
const galleryScale = 1.25 - 0.31 * easeOut(rippleProgress);
```

### Mode D · Sinusoidal Pan (continuous drift)

Use a combination of sine wave + linear drift to avoid the cyclical feeling of "having a starting point and ending point" like marquee:

```js
const panX = Math.sin(panT * 0.12) * 220 - panT * 8;    // Lateral left drift
const panY = Math.cos(panT * 0.09) * 120 - panT * 5;    // vertical drift
const clampedX = Math.max(-900, Math.min(900, panX));   // Prevent exposure
```

**parameter**:
- Sine period `0.09-0.15 rad/s` (slow, one swing in about 30-50 seconds)
- Linear drift `5-8 px/s` (slower than a viewer’s blink)
- Amplitude `120-220 px` (big enough to feel, small enough not to feel dizzy)

### Mode E · Focus Overlay (focus switching)

**Key Design**: The focus overlay is a **flat element** (not tilted) that floats above the tilted canvas. The selected slide is scaled from the tile position (about 400×225) to the center of the screen (960×540). The background canvas does not tilt but darkens to 45%:

```js
// Focus overlay (flat, centered)
focusOverlay.style.width = (startW + (endW - startW) * focusIntensity) + 'px';
focusOverlay.style.height = (startH + (endH - startH) * focusIntensity) + 'px';
focusOverlay.style.opacity = focusIntensity;

// The background card is darkened but still visible (key! Don’t mask it 100%)
card.style.opacity = entryOp * (1 - 0.55 * focusIntensity);   // 1 → 0.45
card.style.filter = `brightness(${1 - 0.3 * focusIntensity})`;
```

**Iron Law of Clarity**:
- The `<img>` of Focus overlay must be directly connected to the original image in `src`, **Do not reuse the compressed thumbnail in the gallery**
- Preload all original images into the `new Image()[]` array in advance
- Overlay's own `width/height` is calculated on a frame-by-frame basis, and the browser resamples the original image for each frame

---

## Timeline architecture (reusable skeleton)

```js
const T = {
  DURATION: 25.0,
  s1_in: [0.0, 0.8],    s1_type: [1.0, 3.2],  s1_out: [3.5, 4.0],
  s2_in: [3.9, 5.1],    s2_hold: [5.1, 7.0],  s2_out: [7.0, 7.8],
  s3_hold: [7.8, 8.3],  s3_ripple: [8.3, 10.0],
  panStart: 8.6,
  focuses: [
    { start: 11.0, end: 12.7, idx: 2  },
    { start: 13.3, end: 15.0, idx: 3  },
    { start: 15.6, end: 17.3, idx: 10 },
    { start: 17.9, end: 19.6, idx: 16 },
  ],
  s4_walloff: [21.1, 21.8], s4_in: [21.8, 22.7], s4_hold: [23.7, 25.0],
};

// core easing
const easeOut = t => 1 - Math.pow(1 - t, 3);
const easeInOut = t => t < 0.5 ? 4*t*t*t : 1 - Math.pow(-2*t+2, 3)/2;
function lerp(time, start, end, fromV, toV, easing) {
  if (time <= start) return fromV;
  if (time >= end) return toV;
  let p = (time - start) / (end - start);
  if (easing) p = easing(p);
  return fromV + (toV - fromV) * p;
}

// A single render(t) function reads timestamps and writes all elements
function render(t) { /* ... */ }
requestAnimationFrame(function tick(now) {
  const t = ((now - startMs) / 1000) % T.DURATION;
  render(t);
  requestAnimationFrame(tick);
});
```

**The essence of the architecture**: **All states are derived from timestamp t**, there is no state machine and no setTimeout. so:
- Play to any time `window.__setTime(12.3)` and jump immediately (convenient for playwright to capture frame by frame)
- Loops naturally seamless (t mod DURATION)
- Can freeze any frame when debugging

---

## Texture details (easily overlooked but fatal)

### 1. SVG noise texture

Light-colored bottoms are most afraid of "peace". Overlay a very weak layer of fractalNoise:

```html
<style>
.stage::before {
  content: '';
  position: absolute; inset: 0;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.078  0 0 0 0 0.078  0 0 0 0 0.074  0 0 0 0.035 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
  opacity: 0.5;
  pointer-events: none;
  z-index: 30;
}
</style>
```

There seems to be no difference, you will know it is there after you remove it.

### 2. Corner Brand Identity

```html
<div class="corner-brand">
  <div class="mark"></div>
  <div>HUASHU · DESIGN</div>
</div>
```

```css
.corner-brand {
  position: absolute; top: 48px; left: 72px;
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--muted);
}
```

It is only displayed in the work wall scene and fades in and out. Like an art museum exhibition label.

### 3. Brand closing wordmark

```css
.brand-wordmark {
  font-family: var(--sans);
  font-size: 148px;
  font-weight: 700;
letter-spacing: -0.045em; /* Negative kerning is the key, making words compact into logos */
}
.brand-wordmark .accent {
  color: var(--accent);
font-weight: 500; /* The accent characters are thinner and have a visual difference */
}
```

`letter-spacing: -0.045em` is the standard practice for large text on Apple product pages.

---

## Common failure modes

| Symptoms | Causes | Solutions |
|---|---|---|
| Looks like PPT template | Cards without shadow / hairline | Add two layers of box-shadow + 1px border |
| Cheap tilt feeling | Only use rotateY without adding rotateZ | Add ±2-3deg rotateZ to break the neatness |
| Pan feels "stuck" | Use setTimeout or CSS keyframes loop | Use rAF + sin/cos continuous function |
| The characters cannot be seen clearly when Focusing | Low score image that reuses gallery tiles | Independent overlay + original image src direct connection |
| Background space | Solid color `#F5F5F7` | Overlay SVG fractalNoise 0.5 opacity |
| The font is too "Internet" | Only Inter | Add Serif (one for Chinese and English) + mono three stacks |

---

## Quote

- Complete implementation sample: `/Users/alchain/Documents/writing/01-public account writing/project/2026.04-huashu-design release/pictures/hero-animation-v5.html`
- Original inspiration: claude.ai/design hero video
- Reference aesthetic: Apple product page, Dribbble shot collection page

When encountering the animation requirement of "many pieces of high-quality output to be displayed", just copy the skeleton from this file, change the content + adjust the timing.
