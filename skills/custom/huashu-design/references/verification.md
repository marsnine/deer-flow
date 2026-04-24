# Verification: Output verification process

Some design-agent native environments (such as Claude.ai Artifacts) have built-in `fork_verifier_agent` to start subagent checking with iframe screenshots. Most agent environments (Claude Code / Codex / Cursor / Trae / etc.) do not have this built-in capability - you can cover the same verification scenarios manually with Playwright.

## Verification list

Each time you generate HTML, follow this checklist:

### 1. Browser rendering check (required)

The most basic: **Can HTML be opened**? On macOS:

```bash
open -a "Google Chrome" "/path/to/your/design.html"
```

Or take a screenshot with Playwright (next section).

### 2. Console error checking

The most common problem in HTML files is a white screen caused by JS errors. Run it again with Playwright:

```bash
python ~/.claude/skills/claude-design/scripts/verify.py path/to/design.html
```

This script will:
1. Open HTML with headless chromium
2. Save the screenshot to the project directory
3. Capture console errors
4. Report status

See `scripts/verify.py` for details.

### 3. Multi-viewport inspection

If it is a responsive design, capture multiple viewports:

```bash
python verify.py design.html --viewports 1920x1080,1440x900,768x1024,375x667
```

### 4. Interaction check

Tweaks, animations, button switching - the default static screenshots cannot be seen. **It is recommended that users open the browser and click it again**, or use Playwright to record the screen:

```python
page.video.record('interaction.mp4')
```

### 5. Check slides page by page

Deck-like HTML, cut out one by one:

```bash
python verify.py deck.html --slides 10  # Cut off the first 10 pictures
```

Generate `deck-slide-01.png`, `deck-slide-02.png`... for quick browsing.

## Playwright Setup

First time use requires:

```bash
# If you haven't installed it yet
npm install -g playwright
npx playwright install chromium

# Or Python version
pip install playwright
playwright install chromium
```

If the user has installed Playwright globally, they can use it directly.

## Best Practices for Screenshots

### Cut the complete page

```python
page.screenshot(path='full.png', full_page=True)
```

### Cut viewport

```python
page.screenshot(path='viewport.png')  # By default, only the visible area is cropped
```

### Cut specific elements

```python
element = page.query_selector('.hero-section')
element.screenshot(path='hero.png')
```

### HD screenshots

```python
page = browser.new_page(device_scale_factor=2)  # retina
```

### Wait for the animation to end before cutting

```python
page.wait_for_timeout(2000)  # Wait 2 seconds for the animation to settle
page.screenshot(...)
```

## Send screenshot to user

### Open local screenshot directly

```bash
open screenshot.png
```

Users will view it in their Preview/Figma/VSCode/browser.

### Upload image sharing link

If you need to show it to remote collaborators (such as Slack/Feishu/WeChat), let users upload it using their own drawing tool or MCP:

```bash
python ~/Documents/writing/tools/upload_image.py screenshot.png
```

Returns the permanent link to ImgBB, which can be pasted anywhere.

## When verification error occurs

### Page white screen

There must be something wrong with the console. First check:

1. Is the integrity hash of React+Babel script tag correct (see `react-setup.md`)
2. Is there a naming conflict with `const styles = {...}`?
3. Are cross-file components exported to `window`?
4. JSX syntax error (babel.min.js does not report an error, replace with babel.js non-compressed version)

### Animation card

- Record a segment using Chrome DevTools Performance tab
- Looking for layout thrashing (frequent reflow)
- Prioritize `transform` and `opacity` for animation effects (GPU acceleration)

### Wrong font

- Check if the url of `@font-face` is accessible
- Check fallback font
- Chinese fonts are slow to load: display fallback first, then switch after loading.

### Layout misalignment

- Check if `box-sizing: border-box` is applied globally
- Check `* margin: 0; padding: 0`reset
- Open gridlines in Chrome DevTools to see the actual layout

## Verification = Designer’s second set of eyes

**Always go through it yourself**. AI often appears when writing code:

- Looks right but there is a bug in the interaction
- Static screenshots are good but misaligned when scrolling
-Wide screen looks good but narrow screen crashes
- Forgot to test Dark mode
- Some components did not respond after Tweaks switching

**The last 1 minute of verification can save 1 hour of rework**.

## Commonly used verification script commands

```bash
# Basics: open + screenshot + catch errors
python verify.py design.html

# Multiple viewports
python verify.py design.html --viewports 1920x1080,375x667

# Multiple slides
python verify.py deck.html --slides 10

# Output to specified directory
python verify.py design.html --output ./screenshots/

# headless=false, open the real browser to show you
python verify.py design.html --show
```
