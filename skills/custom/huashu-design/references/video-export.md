# Video Export: HTML animation export to MP4/GIF

After the animated HTML is completed, users often wonder "Can the video be exported?" This guide gives the complete process.

## When to export

**Export timing**:
- The animation is completely run through and visually verified (Playwright screenshots confirm that the status at each time point is correct)
- The user has viewed it at least once in the browser, which means the effect is OK.
- **Don't** export before animation bugs are fixed - it's more expensive to fix after exporting to video

**Trigger words users may say**:
- "Can it be exported as a video?"
- "Convert to MP4"
- "Make it into GIF"
- 「60fps」

## Output specifications

By default, three formats are given at once for users to choose:

| Format | Specifications | Suitable scene | Typical size (30s) |
|---|---|---|---|
| MP4 25fps | 1920×1080 · H.264 · CRF 18 | Public account embed, video account, YouTube | 1-2 MB |
| MP4 60fps | 1920×1080 · minterpolate frame insertion · H.264 · CRF 18 | High frame rate display, B station, portfolio | 1.5-3 MB |
| GIF | 960×540 · 15fps · palette optimization | Twitter/X, README, Slack preview | 2-4 MB |

## Toolchain

Two scripts in `scripts/`:

### 1. `render-video.js` — HTML → MP4

Record a basic MP4 version at 25fps. Depends on global playwright.

```bash
NODE_PATH=$(npm root -g) node /path/to/claude-design/scripts/render-video.js <html file>
```

Optional parameters:
- `--duration=30` animation duration (seconds)
- `--width=1920 --height=1080` resolution
- `--trim=2.2` Number of seconds to trim from the beginning of the video (remove reload + font loading time)
- `--fontwait=1.5` Font loading waiting time (seconds), increase the font size when there is a large amount of fonts

Output: In the same directory as HTML, with the same name as `.mp4`.

### 2. `add-music.sh` — MP4 + BGM → MP4

Mix background music to silent MP4, select from the built-in BGM library by scene (mood), or bring your own audio. Automatically match duration and add fade-in and fade-out.

```bash
bash add-music.sh <input.mp4> [--mood=<name>] [--music=<path>] [--out=<path>]
```

**Built-in BGM library** (in `assets/bgm-<mood>.mp3`):

| `--mood=` | Style | Adaptation scene |
|-----------|------|---------|
| `tech` (default) | Apple Silicon / Apple conference, minimalist synthesizer + piano | Product release, AI tools, Skill promotion |
| `ad` | upbeat modern electronics with build + drop | social media advertising, product trailers, promotional videos |
| `educational` | Warm and bright, light guitar/electric piano, inviting | Popular science, tutorial introduction, course preview |
| `educational-alt` | Similar alternatives, try another one | Same as above |
| `tutorial` | lo-fi ambient sound, almost no sense of presence | software demonstration, programming tutorial, long demonstration |
| `tutorial-alt` | Similar alternative | Same as above |

**Behavior**:
- Music is cropped according to video duration
- 0.3s fade in + 1s fade out (avoid hard cuts)
- Video stream `-c:v copy` no re-encoding, audio AAC 192k
- `--music=<path>` has higher priority than `--mood` and can directly specify any external audio
- Passing the wrong mood name will list all available options and will not fail silently

**Typical pipeline** (three-piece animation export set + soundtrack):
```bash
node render-video.js animation.html                        # Record screen
bash convert-formats.sh animation.mp4                      # Derived 60fps + GIF
bash add-music.sh animation-60fps.mp4                      # Add default tech BGM
# Or for different scenarios:
bash add-music.sh tutorial-demo.mp4 --mood=tutorial
bash add-music.sh product-promo.mp4 --mood=ad --out=promo-final.mp4
```

### 3. `convert-formats.sh` — MP4 → 60fps MP4 + GIF

Generate 60fps versions and GIFs from existing MP4s.

```bash
bash /path/to/claude-design/scripts/convert-formats.sh <input.mp4> [gif_width] [--minterpolate]
```

Output (same directory as input):
- `<name>-60fps.mp4` — Use `fps=60` frame copy by default (wide compatibility); add `--minterpolate` to enable high-quality frame insertion
- `<name>.gif` — palette optimized GIF (default 960 width, can be changed)

**60fps mode selection**:

| Mode | Command | Compatibility | Usage Scenarios |
|---|---|---|---|
| Frame copy (default) | `convert-formats.sh in.mp4` | QuickTime/Safari/Chrome/VLC all-access | Universal delivery, upload platform, social media |
| minterpolate frame insertion | `convert-formats.sh in.mp4 --minterpolate` | macOS QuickTime/Safari may refuse to play | For display scenes such as Bilibili that require real frame insertion, the target player must be tested locally before delivery |

Why is it changed to frame copy by default? The H.264 elementary stream output by minterpolate has a known compat bug - the problem of "macOS QuickTime cannot be opened" was encountered many times when minterpolate was used by default. See `animation-pitfalls.md` §14 for details.

`gif_width` parameters:
- 960 (default) - universal for social platforms
- 1280 - sharper but larger file size
- 600 - Twitter/X loaded first

## Complete process (standard recommendation)

After the user says "Export video":

```bash
cd <project directory>

# Assume $SKILL points to the root directory of this skill (replace it according to the installation location)

# 1. Record 25fps basic MP4
NODE_PATH=$(npm root -g) node "$SKILL/scripts/render-video.js" my-animation.html

# 2. Derive 60fps MP4 and GIF
bash "$SKILL/scripts/convert-formats.sh" my-animation.mp4

# Output list:
# my-animation.mp4         (25fps · 1-2 MB)
# my-animation-60fps.mp4   (60fps · 1.5-3 MB)
# my-animation.gif         (15fps · 2-4 MB)
```

## Technical details (for troubleshooting)

### Playwright recordVideo Pitfalls

- The frame rate is fixed at 25fps and cannot be directly recorded at 60fps (the upper limit of Chromium headless compositor)
- Recording starts when the context is created, you must use `trim` to trim the previous loading time
- The default webm format requires ffmpeg to be converted to H.264 MP4 for universal playback.

`render-video.js` has solved the above problems.

### ffmpeg minterpolate parameters

Current configuration: `minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1`

- `mi_mode=mci` — motion compensation interpolation
- `mc_mode=aobmc` — adaptive overlapped block motion compensation
- `me_mode=bidir` — Bidirectional motion estimation
- `vsbmc=1` — variable size block motion compensation

Works well with CSS **transform animation** (translate/scale/rotate).
May produce slight ghosting for **pure fade** - if user dislikes it, degenerate to simple frame copy:

```bash
ffmpeg -i input.mp4 -r 60 -c:v libx264 ... output.mp4
```

### Why does GIF palette need two stages?

GIF can only have 256 colors. The GIF in one pass will compress the full animation color to the 256-color universal palette, which will blur the delicate color combination of beige + orange.

Two stages:
1. `palettegen=stats_mode=diff` - scan the entire film first and generate the **optimal palette** for this animation
2. `paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle` - Using this palette encoding, rectangle diff only updates the changed area, greatly reducing the file size

Using `dither=bayer` for fade transitions is smoother than `none`, but the file size is larger.

## Pre-flight check (before export)

Self-test 30 seconds before export:

- [ ] HTML is completely run in the browser, no console errors
- [ ] Frame 0 of the animation is the complete initial state (not blank loading)
- [ ] The last frame of the animation is the stable ending state (not half-cut)
- [ ] Fonts/images/emoji are all rendered normally (refer to `animation-pitfalls.md`)
- [ ] Duration parameter matches the actual animation duration in HTML
- [ ] Stage detection in HTML `window.__recording` forces loop=false (handwritten Stage must be checked; use `assets/animations.jsx` to bring it)
- [ ] `fadeOut={0}` of the ending Sprite (the last frame of the video does not fade out)
- [ ] Contains "Created by Huashu-Design" watermark (only animation scenes must be added; third-party brand works add the "unofficial production ·" prefix. For details, see SKILL.md § "Skill Promotion Watermark")

## Instructions included with delivery

The standard description format given to the user after the export is completed:

```
**FULL DELIVERY**

| File | Format | Specifications | Size |
|---|---|---|---|
| foo.mp4 | MP4 | 1920×1080 · 25fps · H.264 | X MB |
| foo-60fps.mp4 | MP4 | 1920×1080 · 60fps (motion frame interpolation) · H.264 | X MB |
| foo.gif | GIF | 960×540 · 15fps · palette optimized | X MB |

**illustrate**
- 60fps uses minterpolate for motion estimation and frame interpolation, and the transform animation effect is good
- GIF is optimized with palette, and a 30s animation can be compressed to about 3MB.

Let me know if you want to change the size or frame rate.
```

## Common user additional requirements

| Users say | Coping |
|---|---|
| "Too big" | MP4: Increase CRF to 23-28; GIF: Reduce resolution to 600 or fps to 10 |
| "GIF is too blurry" | Increase `gif_width` to 1280; or it is recommended to use MP4 instead (WeChat Moments also supports it) |
| "Want vertical screen 9:16" | Change the HTML source `--width=1080 --height=1920` and re-record |
| "Add watermark" | ffmpeg adds `-vf "drawtext=..."` or `overlay=` a PNG |
| "Need transparent background" | MP4 does not support alpha; use WebM VP9 + alpha or APNG |
| "Be lossless" | CRF changed to 0 + preset veryslow (the file will be 10 times larger) |
