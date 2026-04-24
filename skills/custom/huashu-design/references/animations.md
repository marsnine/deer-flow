# Animations: Timeline animation engine

Read this when doing animation/motion design HTML. Principles, usage, typical patterns.

## Core mode: Stage + Sprite

Our animation system (`assets/animations.jsx`) provides a timeline-driven engine:

- **`<Stage>`**: The container of the entire animation, automatically provides auto-scale (fit viewport) + scrubber + play/pause/loop control
- **`<Sprite start end>`**: time slice. A Sprite is only displayed during the period from `start` to `end`. Internally, you can read your own local progress `t` (0→1) through `useSprite()` hook
- **`useTime()`**: Read the current global time (seconds)
- **`Easing.easeInOut` / `Easing.easeOut` / ...**: Easing function
- **`interpolate(t, from, to, easing?)`**: interpolate according to t

This model draws on the ideas of Remotion/After Effects, but is lightweight and has zero dependencies.

## Start

```html
<script type="text/babel" src="animations.jsx"></script>
<script type="text/babel">
  const { Stage, Sprite, useTime, useSprite, Easing, interpolate } = window.Animations;

  function Title() {
    const { t } = useSprite();  // Local progress 0→1
    const opacity = interpolate(t, [0, 1], [0, 1], Easing.easeOut);
    const y = interpolate(t, [0, 1], [40, 0], Easing.easeOut);
    return (
      <h1 style={{ 
        opacity, 
        transform: `translateY(${y}px)`,
        fontSize: 120,
        fontWeight: 900,
      }}>
        Hello.
      </h1>
    );
  }

  function Scene() {
    return (
<Stage duration={10}> {/* 10 seconds animation */}
        <Sprite start={0} end={3}>
          <Title />
        </Sprite>
        <Sprite start={2} end={5}>
          <SubTitle />
        </Sprite>
        {/* ... */}
      </Stage>
    );
  }

  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(<Scene />);
</script>
```

## Common animation modes

### 1. Fade In / Fade Out

```jsx
function FadeIn({ children }) {
  const { t } = useSprite();
  const opacity = interpolate(t, [0, 0.3], [0, 1], Easing.easeOut);
  return <div style={{ opacity }}>{children}</div>;
}
```

**Note range**: `[0, 0.3]` means that the fade-in is completed in the first 30% of the sprite, and opacity=1 is maintained thereafter.

### 2. Slide In

```jsx
function SlideIn({ children, from = 'left' }) {
  const { t } = useSprite();
  const progress = interpolate(t, [0, 0.4], [0, 1], Easing.easeOut);
  const offset = (1 - progress) * 100;
  const directions = {
    left: `translateX(-${offset}px)`,
    right: `translateX(${offset}px)`,
    top: `translateY(-${offset}px)`,
    bottom: `translateY(${offset}px)`,
  };
  return (
    <div style={{
      transform: directions[from],
      opacity: progress,
    }}>
      {children}
    </div>
  );
}
```

### 3. Verbatim typewriter

```jsx
function Typewriter({ text }) {
  const { t } = useSprite();
  const charCount = Math.floor(text.length * Math.min(t * 2, 1));
  return <span>{text.slice(0, charCount)}</span>;
}
```

### 4. Number counting

```jsx
function CountUp({ from = 0, to = 100, duration = 0.6 }) {
  const { t } = useSprite();
  const progress = interpolate(t, [0, duration], [0, 1], Easing.easeOut);
  const value = Math.floor(from + (to - from) * progress);
  return <span>{value.toLocaleString()}</span>;
}
```

### 5. Segmented explanation (typical teaching animation)

```jsx
function Scene() {
  return (
    <Stage duration={20}>
{/* Phase 1: Display problem */}
      <Sprite start={0} end={4}>
        <Problem />
      </Sprite>

{/* Phase 2: Show ideas */}
      <Sprite start={4} end={10}>
        <Approach />
      </Sprite>

{/* Phase 3: Display results */}
      <Sprite start={10} end={16}>
        <Result />
      </Sprite>

{/* Subtitles displayed throughout */}
      <Sprite start={0} end={20}>
        <Caption />
      </Sprite>
    </Stage>
  );
}
```

## Easing function

Default easing curves:

| Easing | Features | Used in |
|--------|------|------|
| `linear` | Uniform speed | Rolling subtitles, continuous animation |
| `easeIn` | slow→fast | exit and disappear |
| `easeOut` | fast→slow | entry appears |
| `easeInOut` | Slow → Fast → Slow | Position change |
| **`expoOut`** ⭐ | **Exponential easing out** | **Anthropic level master easing** (physical weight) |
| **`overshoot`** ⭐ | **Elastic rebound** | **Toggle / Button popup / Emphasis on interaction** |
| `spring` | Spring | Interactive feedback, geometry return |
| `anticipation` | First reverse and then forward | Emphasis on action |

**Default primary easing uses `expoOut`** (not `easeOut`) - see `animation-best-practices.md` §2.
Use `expoOut` for entry, `easeIn` for exit, and `overshoot` for toggle - the basic rules of Anthropic-level animation.

## Pace and Duration Guidelines

### Micro-interaction (0.1-0.3 seconds)
- button hover
- Cardexpand
- Tooltip appears

### UI transition (0.3-0.8 seconds)
- Page switching
- Modal box appears
- List item added

### Narrative animation (2-10 seconds per segment)
- A phase of concept explanation
- Reveal of data charts
- scene transition

### The maximum length of a single narrative animation shall not exceed 10 seconds.
Human attention span is limited. Say one thing for 10 seconds, then switch to the next thing.

## Thinking order for designing animations

### 1. Content/story first, animation second

**Error**: First want to make fancy animation, and then insert the content into it
**Correct**: First think clearly about what message you want to convey, and then use animation to serve this message.

Animation is **signal**, not **decoration**. A fade-in emphasizes "This is very important, please take a look" - if everything fade-in, the signal will be invalid.

### 2. Write timeline by Scene

```
0:00 - 0:03 The problem fades in
0:03 - 0:06 Question zoom/expand (zoom+pan)
0:06 - 0:09 Solution appears (slide in from right)
0:09 - 0:12 Explanation of solution expansion (typewriter)
0:12 - 0:15 Results presentation (counter up + chart reveal)
0:15 - 0:18 Summarize a sentence (static, read for 3 seconds)
0:18 - 0:20 CTA or fade out
```

After writing the timeline, write the components.

### 3. Resources first

The pictures/icons/fonts to be used for the animation are prepared first. Don’t look for material in the middle of a painting – interrupt the flow.

## FAQ

**Animation lag**
→ Mainly layout thrashing. Use `transform` and `opacity`, do not touch `top`/`left`/`width`/`height`/`margin`. Browser GPU accelerated `transform`.

**The animation is too fast and cannot be seen clearly**
→ It takes 100-150ms for humans to read a Chinese character and 300-500ms for a word. If you use words to tell a story, give each sentence at least 3 seconds.

**The animation is too slow and the audience is bored**
→ Be dense with interesting visual variations. Static images will become boring if they last longer than 5 seconds.

**Multiple animations affect each other**
→ Use CSS `will-change: transform` to tell the browser in advance that this element will move to reduce reflow.

**Record to video**
→ Use skill’s own tool chain (one command to produce three formats): see `video-export.md`
- `scripts/render-video.js` — HTML → 25fps MP4（Playwright + ffmpeg）
- `scripts/convert-formats.sh` — 25fps MP4 → 60fps MP4 + optimized GIF
- Want more accurate frame rendering? Make render(t) a pure function, see `animation-pitfalls.md` Item 5

## Cooperation with video tools

What this skill does is **HTML animation** (running in the browser). If the final output is to be used as video material:

- **Short animation/concept demo**: Use the method here to make HTML animation → screen recording
- **Long video/narrative**: This skill focuses on HTML animation, and long videos use AI video generation skills or professional video software
- **motion graphics**: Professional After Effects/Motion Canvas is more suitable

## About Popmotion and other libraries

If you really need physical animation (spring, decay, keyframes with precise timing), our engine can't handle it, you can fallback to Popmotion:

```html
<script src="https://unpkg.com/popmotion@11.0.5/dist/popmotion.min.js"></script>
```

But **try our engine first**. It's enough in 90% of cases.
