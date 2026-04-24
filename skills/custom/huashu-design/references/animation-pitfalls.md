# Animation Pitfalls: pitfalls and rules of HTML animation

The most common bugs when making animations and how to avoid them. Each rule is derived from a real failure case.

Reading this article before writing animation will save you a round of iterations.

## 1. Stacked layout - `position: relative` is the default requirement

**Pitfall**: A sentence-wrap element wraps 3 bracket-layers (`position: absolute`). Without setting `position: relative` for sentence-wrap, the result is that the absolute bracket uses `.canvas` as the coordinate system and floats 200px away from the bottom of the screen.

**rule**:
- Any container containing `position: absolute` child elements **must** explicitly `position: relative`
- Even if there is no need for "offset" visually, you must write `position: relative` as the coordinate system anchor point
- If you are writing `.parent { ... }` and there is `.child { position: absolute }` in its child elements, you will subconsciously add relative to parent

**Quick check**: For each occurrence of `position: absolute`, count up the ancestors and make sure the nearest positioned ancestor is the coordinate system you *want*.

## 2. Character trap - no reliance on rare Unicode

**Pitfall**: I want to use `␣` (U+2423 OPEN BOX) to visualize "space token". Noto Serif SC / Cormorant Garamond do not have this glyph, and are rendered as blank/tofu, which is completely invisible to the audience.

**rule**:
- **Every character appearing in the animation must exist in the font you selected**
- Blacklist of common rare characters: `␣ ␀ ␐ ␋ ␨ ↩ ⏎ ⌘ ⌥ ⌃ ⇧ ␦ ␖ ␛`
- To express metacharacters such as "space/carriage return/tab", use **CSS-constructed semantic box**:
  ```html
  <span class="space-key">Space</span>
  ```
  ```css
  .space-key {
    display: inline-flex;
    padding: 4px 14px;
    border: 1.5px solid var(--accent);
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.3em;
    letter-spacing: 0.2em;
    text-transform: uppercase;
  }
  ```
- Emoji also needs to be verified: some emoji will fallback into a gray box in fonts other than Noto Emoji. It is best to use `emoji` font-family or SVG

## 3. Data-driven Grid/Flex template

**Pitfall**: There are `const N = 6` tokens in the code, but the CSS is hard-coded `grid-template-columns: 80px repeat(5, 1fr)`. As a result, the sixth token has no column, and the entire matrix is ​​misaligned.

**rule**:
- When count comes from a JS array (`TOKENS.length`), the CSS template should also be data driven
- Option A: Inject from JS using CSS variables
  ```js
  el.style.setProperty('--cols', N);
  ```
  ```css
  .grid { grid-template-columns: 80px repeat(var(--cols), 1fr); }
  ```
- Option B: Use `grid-auto-flow: column` to let the browser automatically expand
- **Disable the combination of "fixed number + JS constant"**, CSS will not be updated synchronously if N is changed

## 4. Transition fault - scene switching must be continuous

**Pitfall**: Between zoom1 (13-19s) → zoom2 (19.2-23s), the main sentence has been hidden, zoom1 fade out (0.6s) + zoom2 fade in (0.6s) + stagger delay (0.2s+) = about 1 second of pure blank screen. The audience thought the animation was stuck.

**rule**:
- When switching scenes continuously, fade out and fade in must **cross-overlap**, instead of the previous one disappearing completely before starting the next one.
  ```js
  // Difference:
  if (t >= 19) hideZoom('zoom1');      // 19.0s out
  if (t >= 19.4) showZoom('zoom2');    // 19.4s in → 0.4s blank in the middle

  // good:
  if (t >= 18.6) hideZoom('zoom1');    // Start fade out 0.4s earlier
  if (t >= 18.6) showZoom('zoom2');    // Also fade in (cross-fade)
  ```
- Or use an "anchor element" (such as a main sentence) as a visual connection between scenes, which briefly echoes during zoom switching
- Calculate the duration of CSS transition clearly to avoid triggering the next transition before it ends

## 5. Pure Render principle - animation state should be seekable

**Pitfall**: Use `setTimeout` + `fireOnce(key, fn)` to trigger the animation state in a chain. There is no problem with normal playback, but when doing frame-by-frame recording/seek to any point in time, the previous setTimeout has been executed and you cannot "go back to the past".

**rule**:
- The `render(t)` function is ideally a **pure function**: outputs a unique DOM state given t
- If side effects (such as class switching) must be used, use `fired` set with explicit reset:
  ```js
  const fired = new Set();
  function fireOnce(key, fn) { if (!fired.has(key)) { fired.add(key); fn(); } }
function reset() { fired.clear(); /* Clear all .show class */ }
  ```
- Expose `window.__seek(t)` for Playwright / debugging use:
  ```js
  window.__seek = (t) => { reset(); render(t); };
  ```
- Animation-related setTimeout should not exceed >1 second, otherwise seek will be messed up when jumping back

## 6. Measure before font loading = error detection

**Pitfall**: As soon as the page is DOMContentLoaded, `charRect(idx)` is called to measure the bracket position. The font has not been loaded yet. The width of each character is the width of the fallback font, and the position is all wrong. Once the font is loaded (about 500ms later), the bracket's `left: Xpx` is still the old value and is permanently offset.

**rule**:
- Any layout code that relies on DOM measurements (`getBoundingClientRect`, `offsetWidth`) **must** be wrapped in `document.fonts.ready.then()`
  ```js
  document.fonts.ready.then(() => {
    requestAnimationFrame(() => {
      buildBrackets(...);  // At this point the font is ready and the measurement is accurate
      tick();              // Animation starts
    });
  });
  ```
- The additional `requestAnimationFrame` gives the browser one frame to submit the layout
- If using Google Fonts CDN, `<link rel="preconnect">` speeds up first load

## 7. Preparation for recording - reserve a grip for video export

**Pitfall**: Playwright `recordVideo` defaults to 25fps and starts recording when the context is created. The first 2 seconds of page loading and font loading are recorded. Delivered with the first 2 seconds of video blank/flashing white.

**rule**:
- Provide `render-video.js` tool processing: warmup navigate → reload restart animation → wait duration → ffmpeg trim head + convert to H.264 MP4
- Frame 0 of the animation is the complete initial state with the final layout in place (not blank or loading)
- Want 60fps? Use ffmpeg `minterpolate` post-processing, do not count on browser source frame rate
- Want a GIF? Two-stage palette (`palettegen` + `paletteuse`), can compress 30s 1080p animation to 3MB

See `video-export.md` for the complete script calling method.

## 8. Batch export - the tmp directory must have a PID to prevent concurrency conflicts

**Pitfall**: Use `render-video.js` to record 3 pieces of HTML in 3 processes in parallel. Because TMP_DIR is only named with `Date.now()`, 3 processes share the same tmp directory when started with milliseconds. The first process to complete cleans tmp, and the other two `ENOENT` when reading the directory, all crashed.

**rule**:
- Any temporary directory that may be shared by multiple processes must be named with **PID or a random suffix**:
  ```js
  const TMP_DIR = path.join(DIR, '.video-tmp-' + Date.now() + '-' + process.pid);
  ```
- If you really want to run multiple files in parallel, use shell's `&` + `wait` instead of forking in a node script
- When recording multiple HTML in batches, conservative approach: **Serial** operation (up to 2 can be parallelized, more than 3 can be queued honestly)

## 9. There is a progress bar/replay button in the screen recording - Chrome elements pollute the video

**Pitfall**: The animation HTML adds a `.progress` progress bar, a `.replay` replay button, and a `.counter` timestamp to facilitate human debugging and playback. When recorded as MP4 and delivered, these elements appear at the bottom of the video, as if the developer tools have been cut into it.

**rule**:
- The "chrome elements" for human use in HTML (progress bar / replay button / footer / masthead / counter / phase labels) are managed separately from the video content itself
- **Conventional class name** `.no-record`: Any element with this class, the screen recording script will be automatically hidden
- The script side (`render-video.js`) injects CSS by default to hide common chrome class names:
  ```
  .progress .counter .phases .replay .masthead .footer .no-record [data-role="chrome"]
  ```
- Use Playwright's `addInitScript` injection (it will take effect before each navigate, and reload is also stable)
- Add the `--keep-chrome` flag when you want to see the original HTML (with chrome)

## 10. The animation repeats in the first few seconds of screen recording - Warmup frame leak

**Pitfall**: `render-video.js`’s old process `goto → wait fonts 1.5s → reload → wait duration`. Recording starts when the context is created. The animation in the warmup phase has been played for a while, and restarts from 0 after reload. As a result, the first few seconds of the video are "middle of animation + switching + animation starting from 0", which gives a strong sense of repetition.

**rule**:
- **Warmup and Record must use separate contexts**:
  - Warmup context (without `recordVideo` option): only responsible for loading url, waiting for fonts, and then close
  - Record context (with `recordVideo`): fresh state starts, animation starts recording from t=0
- ffmpeg `-ss trim` can only trim a little bit of Playwright's startup latency (~0.3s) and cannot be used to mask warmup frames; the source must be clean
- recording context off = webm file written to disk, this is a Playwright constraint
- Related code patterns:
  ```js
  // Phase 1: warmup (throwaway)
  const warmupCtx = await browser.newContext({ viewport });
  const warmupPage = await warmupCtx.newPage();
  await warmupPage.goto(url, { waitUntil: 'networkidle' });
  await warmupPage.waitForTimeout(1200);
  await warmupCtx.close();

  // Phase 2: record (fresh)
  const recordCtx = await browser.newContext({ viewport, recordVideo });
  const page = await recordCtx.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(DURATION * 1000);
  await page.close();
  await recordCtx.close();
  ```

## 11. Don’t draw “fake chrome” on the screen - the decorative version of player UI collides with real chrome

**Pitfall**: The `Stage` component is used for animation, and it already comes with scrubber + timecode + pause button (belongs to `.no-record` chrome, automatically hidden when exporting). I also drew a "magazine page number-like decorative progress bar" of "`00:60 ──── CLAUDE-DESIGN / ANATOMY`" at the bottom of the screen, which made me feel good about myself. **Result**: The user sees two progress bars - one for the Stage controller and one for the decoration I drew. Visually a complete crash and deemed a bug. "Why is there a progress bar in the video?"

**rule**:

- Stage already provides: scrubber + timecode + pause/replay button. **No more drawings on the screen** Progress indicators, current timecode, copyright strips, chapter counters - they either conflict with chrome or are filler slop (violating the "earn its place" principle).
- "Page sense", "magazine sense" and "base placement name strip", these **decorative demands** are high-frequency fillers automatically added by AI. Be alert to every occurrence – does it really convey an irreplaceable message? Or simply fill in the blanks?
- If you firmly believe that a certain bottom strip must exist (for example: the animation theme is about player UI), then it must be **narratively necessary** and **visually distinguishable** from the Stage scrubber (different position, different form, different tone).

**Element Attribution Test** (Each element drawn into the canvas must be able to answer):

| What does it belong to | Processing |
|------------|------|
| Narrative content of a certain scene | OK, keep it |
| Global chrome (for control/debugging) | Add `.no-record` class and hide it when exporting |
| **Neither belongs to any act nor chrome** | **Delete**. This is what has no owner and must be filler slop |

**Self-check (3 seconds before delivery)**: Take a screenshot of a static picture and ask yourself——

- Is there anything on the screen that "looks like the video player UI" (horizontal progress bar, timecode, control button appearance)?
- If so, would deleting it harm the narrative? Delete without loss.
- Does the same type of information (progress/time/signature) appear twice? Merged into chrome.

**Counter example**: `00:42 ───── PROJECT NAME` is drawn at the bottom, "CH 03 / 06" chapter count is drawn in the lower right corner of the screen, and version number "v0.3.1" is drawn on the edge of the screen - all are fake chrome fillers.

## 12. Blank before recording screen + Offset of starting point of screen recording —— `__ready` × tick × lastTick triple trap

** Pitfalls (A · Leading blank) **: 60 seconds animation export to MP4, the first 2-3 seconds is a blank page. `ffmpeg --trim=0.3` cannot be trimmed.

** Pitfalls (B · Starting point offset, 2026-04-20 real accident)**: Export a 24-second video, and the user's perception is that "the first frame of the video does not start until 19 seconds." In fact, the animation starts recording at t=5, and then loops back to t=0 after recording at t=24, and then records for another 5 seconds to end - so the last 5 seconds of the video are the real beginning of the animation.

**Root cause** (two pits share a root cause):

Playwright `recordVideo` starts writing WebM from the moment of `newContext()`. At this time, Babel/React/font loading takes L seconds (2-6s). Screen recording scripts, etc. `window.__ready = true` is used as the anchor point of "animation starts from here" - it and animation `time = 0` must be strictly paired. There are two common mistakes:

| Wrong way | Symptoms |
|------|------|
| `__ready` is set in `useEffect` or synchronization setup phase (before the first frame of tick) | The screen recording script thinks that the animation has started, but in fact WebM is still recording a blank page → **Preceding blank** |
| Tick's `lastTick = performance.now()` is initialized at the top level of the **script** | Font loading L seconds are counted into the first frame `dt`, `time` jumps to L instantly → the entire screen recording lags by L seconds → **starting point offset** |

**✅ Correct and complete starter tick template** (handwritten animation must use this skeleton):

```js
// ━━━━━━ state ━━━━━━
let time = 0;
let playing = false;   // ❗ Not playing by default, wait until the font is ready before starting
let lastTick = null;   // ❗ sentinel——dt is forced to 0 at the first frame of tick (don’t use performance.now())
const fired = new Set();

// ━━━━━━ tick ━━━━━━
function tick(now) {
  if (lastTick === null) {
    lastTick = now;
    window.__ready = true;   // ✅ pair: "Screen recording starting point" and "Animation t=0" are in the same frame
    render(0);               // Render again to ensure the DOM is ready (the font is ready at this time)
    requestAnimationFrame(tick);
    return;
  }
  const dt = (now - lastTick) / 1000;   // dt starts to advance after the first frame
  lastTick = now;

  if (playing) {
    let t = time + dt;
    if (t >= DURATION) {
      t = window.__recording ? DURATION - 0.001 : 0;  // Do not loop when recording, leave 0.001s to retain the last frame
      if (!window.__recording) fired.clear();
    }
    time = t;
    render(time);
  }
  requestAnimationFrame(tick);
}

// ━━━━━━ boot ━━━━━━
// Don't rAF immediately at the top level - wait until the fonts are loaded before starting it
document.fonts.ready.then(() => {
  render(0);                 // First draw the initial screen (the font is ready)
  playing = true;
  requestAnimationFrame(tick);  // The first tick will be pair __ready + t=0
});

// ━━━━━━ seek interface (for render-video defensive correction)━━━━━━
window.__seek = (t) => { fired.clear(); time = t; lastTick = null; render(t); };
```

**Why this template works**:

| Link | Why is this necessary |
|------|-------------|
| `lastTick = null` + first frame `return` | Prevent the L seconds of "script loading to tick for first execution" from being counted into animation time |
| `playing = false` Default | During font loading, `tick` will not advance the time even if it is running, to avoid rendering misalignment |
| `__ready` is set in the first frame of tick | The screen recording script starts timing at this moment, and the corresponding picture is the real t=0 of the animation |
| Start tick only in `document.fonts.ready.then(...)` | Avoid font fallback width measurement and avoid font jump in the first frame |
| `window.__seek` exists | Let `render-video.js` be actively corrected - the second line of defense |

**Corresponding defense of screen recording script**:
1. `addInitScript` injects `window.__recording = true` (before page goto)
2. `waitForFunction(() => window.__ready === true)`, record the offset at this moment as ffmpeg trim
3. **Extra**: After `__ready`, actively `page.evaluate(() => window.__seek && window.__seek(0))` to force the possible time deviation of HTML to zero - this is the second line of defense to deal with HTML that does not strictly comply with the starter template.

**Verification method**: After exporting MP4
```bash
ffmpeg -i video.mp4 -ss 0 -vframes 1 frame-0.png
ffmpeg -i video.mp4 -ss $DURATION-0.1 -vframes 1 frame-end.png
```
The first frame must be the initial state of the animation t=0 (not the middle, not black), and the last frame must be the final state of the animation (not a certain moment in the second loop).

**Reference implementation**: The Stage component of `assets/animations.jsx` and `scripts/render-video.js` have been implemented according to this protocol. Handwritten HTML must be set with a starter tick template - each line is to prevent specific bugs.

## 13. Disable loop during recording - `window.__recording` signal

**Pitfall**: Animation Stage defaults to `loop=true` (it is convenient to see the effect in the browser). `render-video.js` will wait 300ms for buffering after recording duration seconds before stopping. This 300ms will allow Stage to enter the next cycle. When ffmpeg `-t DURATION` is intercepted, the last 0.5-1s falls into the next loop - the end of the video suddenly returns to the first frame (Scene 1), and the audience thinks that there is a bug in the video.

**Root Cause**: There is no "I'm recording" handshake between the recording script and the HTML. HTML doesn't know that it is being recorded, and still cycles through the browser interaction scene.

**rule**:

1. **Recording script**: Inject `window.__recording = true` in `addInitScript` (before page goto):
   ```js
   await recordCtx.addInitScript(() => { window.__recording = true; });
   ```

2. **Stage component**: Recognize this signal and force loop=false:
   ```js
   const effectiveLoop = (typeof window !== 'undefined' && window.__recording) ? false : loop;
   // ...
   if (next >= duration) return effectiveLoop ? 0 : duration - 0.001;
   // ↑ Leave 0.001 to prevent Sprite end=duration from being turned off
   ```

3. **FadeOut of the ending Sprite**: `fadeOut={0}` should be set in the recording scene, otherwise the video will fade to transparent/dark at the end - the user expects to stop at the clear last frame, not fade out. When handwriting HTML, it is recommended to use `fadeOut={0}` at the end of the sprite.

**Reference implementation**: `assets/animations.jsx` and Stage / `scripts/render-video.js` have built-in handshake. The handwriting stage must implement `__recording` detection - otherwise the recording will fall into this trap.

**Verification**: After exporting MP4, run `ffmpeg -ss 19.8 -i video.mp4 -frames:v 1 end.png` and check whether the countdown 0.2 seconds is still the expected last frame and there is no sudden switch to another scene.

## 14. 60fps video uses frame copy by default - minterpolate has poor compatibility

**Fault**: The 60fps MP4 generated by `convert-formats.sh` using `minterpolate=fps=60:mi_mode=mci...` cannot be opened in some versions of macOS QuickTime / Safari (it goes black or refuses to be played). VLC/Chrome can open it.

**Root Cause**: The H.264 elementary stream output by minterpolate contains SEI/SPS fields that some players have trouble parsing.

**rule**:

- Default 60fps with simple `fps=60` filter (frame copy), wide compatibility (QuickTime/Safari/Chrome/VLC can be turned on)
- High-quality frame insertion is explicitly enabled with the `--minterpolate` flag - but it must be tested locally on the target player before delivery
- The value of the 60fps tag is **algorithm recognition of the upload platform** (the 60fps tag on Bilibili/YouTube will be pushed first), and the actual perceived smoothness is slightly improved for CSS animations.
- Add `-profile:v high -level 4.0` to improve H.264 universal compatibility

**`convert-formats.sh` has been changed to compatibility mode by default**. If you need high quality interpolation, add the `--minterpolate` flag:
```bash
bash convert-formats.sh input.mp4 --minterpolate
```

## 15. CORS trap for `file://` + external `.jsx` - single file delivery must be inline engine

**Pitfall**: Use the `<script type="text/babel" src="animations.jsx"></script>` external loading engine in animated HTML. Double-click to open the local machine (`file://` protocol) → Babel Standalone uses XHR to pull `.jsx` → Chrome reports `Cross origin requests are only supported for protocol schemes: http, https, chrome, chrome-extension...` → The whole page is black, no `pageerror` is reported, only console error is reported, which is easy to be misdiagnosed as "the animation is not triggered".

Enabling the HTTP server may not be a solution - when the local machine has a global proxy, `localhost` will also use the proxy and return 502 / Connection failed.

**rule**:

- **Single file delivery (double click to open ready-to-use HTML)** → `animations.jsx` must be **inline** within the `<script type="text/babel">...</script>` tag, do not use `src="animations.jsx"`
- **Multi-file project (starting from HTTP server demo)** → Can be loaded externally, but clearly specify the `python3 -m http.server 8000` command when delivering it
- Judgment criteria: Is it delivered to the user "HTML file" or "project directory with server"? The former uses inline
- Stage component/animations.jsx often 200+ lines - pasting into HTML `<script>` blocks is perfectly acceptable, don’t be afraid of the size

**Minimal Authentication**: Double-click the HTML you generated, **Do not** open it through any server. It will only pass if the Stage displays the first frame of the animation normally.

## 16. Invert color context across scenes - do not hard-code colors for elements within the scene

** Pitfall **: When doing multi-scene animation, `ChapterLabel` / `SceneNumber` / `Watermark` and other elements appear across scenes, so write `color: '#1A1A1A'` (dark text) in the component. The light background of the first 4 scenes is OK, and the "05" and watermark disappear directly when the fifth black background scene is reached - no error is reported, no inspection is triggered, and key information is invisible.

**rule**:

- **In-screen elements reused across multiple scenes** (chapter label/scene number/timecode/watermark/copyright strip) **Hard-coded color values ​​are prohibited**
- Use one of three methods instead:
  1. **`currentColor` inheritance**: The element only writes `color: currentColor`, and the parent scene container sets `color: calculated value`
  2. **invert prop**: The component accepts `<ChapterLabel invert />` to manually switch the depth.
  3. **Automatic calculation based on background color**: `color: contrast-color(var(--scene-bg))` (CSS 4 new API, or JS judgment)
- Use Playwright to extract the representative frames of each scene before delivery, and check whether the "cross-scene elements" are all visible to the human eye.

The hiddenness of this pit is that there is no bug alarm**. Only the human eye or OCR can detect it.

## Quick self-check checklist (5 seconds before starting work)

- [ ] Every parent element with `position: absolute` has `position: relative`?
- [ ] Do the special characters in the animation (`␣` `⌘` `emoji`) exist in the font?
- [ ] Is the count of Grid/Flex template consistent with the length of JS data?
- [ ] Cross-fade between scene switches, no >0.3s of pure whitespace?
- [ ] DOM measurement code packaged in `document.fonts.ready.then()`?
- [ ] Is `render(t)` pure, or has an explicit reset mechanism?
- [ ] Frame 0 is the complete initial state, not blank?
- [ ] There is no "pseudo-chrome" decoration in the screen (progress bar/timecode/bottom deployment bar collides with Stage scrubber)?
- [ ] Animation tick first frame synchronization set `window.__ready = true`? (Using animations.jsx comes with it; handwriting HTML and adding it yourself)
- [ ] Stage detection `window.__recording` forces loop=false? (Handwritten HTML must be added)
- [ ] Set the `fadeOut` of the ending Sprite to 0 (stop the clear frame at the end of the video)?
- [ ] 60fps MP4 uses frame copy mode by default (compatibility), only add `--minterpolate` for high-quality frame insertion?
- [ ] Is the 0th frame + last frame verified after exporting the initial/final state of the animation?
- [ ] Involving specific brands (Stripe/Anthropic/Lovart/...): Have you completed the "Brand Asset Agreement" (SKILL.md §1.a five steps)? Have you written `brand-spec.md`?
- [ ] Single-file delivered HTML: `animations.jsx` is inline, not `src="..."`? (external .jsx under file:// will cause a CORS black screen)
- [ ] No hard-coded colors for elements that appear across scenes (chapter tags/watermarks/scene numbers)? Visible under every scene background?
