# Slide Decks: HTML slide production specifications

Making slideshows is a high-frequency scenario for design work. This document explains how to make an HTML slideshow—from architecture selection, single-page design, to the complete path to PDF/PPTX export.

**Ability coverage of this skill**:
- **HTML demo version (basic product, always required by default)** → Independent HTML + `assets/deck_index.html` aggregation for each page, keyboard page turning in the browser, full-screen presentation
- HTML → PDF export → `scripts/export_deck_pdf.mjs` / `scripts/export_deck_stage_pdf.mjs`
- HTML → Editable PPTX export → `references/editable-pptx.md` + `scripts/html2pptx.js` + `scripts/export_deck_pptx.mjs` (requires HTML to be written according to 4 hard constraints)

> **⚠️ HTML is the base, PDF/PPTX are derivatives. ** No matter what format is finally delivered, you must first create an HTML aggregation demo version (`index.html` + `slides/*.html`), which is the "source" of the slide show. PDF/PPTX is a snapshot exported from HTML with a one-line command.
>
> **Why HTML comes first**:
> - Best used in lectures/demonstrations (projector/shared screen directly full screen, keyboard page turning, does not rely on Keynote/PPT software)
> - During the development process, each page can be double-clicked to open the verification separately, so there is no need to re-run the export every time.
> - Is the only upstream for PDF/PPTX export (avoiding the endless loop of "finding out after exporting that you need to change the HTML and then re-export")
> - The deliverable can be "HTML + PDF" or "HTML + PPTX" in duplicate, whichever the recipient prefers to use.
>
> 2026-04-22 moxt brochure actual test: After aggregating 13 pages of HTML + index.html, `export_deck_pdf.mjs` exports PDF in one line with zero changes. The HTML version itself is a deliverable that can be delivered directly to the browser.

---

## 🛑 Confirm the delivery format before starting work (the hardest checkpoint)

**This decision comes before "single file or multiple files". **2026-04-20 Option Private Board Project Measurement: **Not confirming the delivery format before starting work = 2-3 hours of rework. **

### Decision tree (HTML-first architecture)

All deliveries start from the same set of HTML aggregation pages (`index.html` + `slides/*.html`). The delivery format only determines **HTML writing constraints** and **export commands**:

```
[Always default · Must do] HTML aggregation demo version (index.html + slides/*.html)
   │
├── As long as the browser speaks / local HTML archive → It is completed here, HTML has the greatest visual freedom
   │
├── You also need PDF (print/send to group/archive) → run export_deck_pdf.mjs to export with one click
│ HTML can be written freely and has no visual constraints
   │
└── It also needs to be editable PPTX (colleagues want to change the text) → From the first line of HTML, write according to 4 hard constraints
Run export_deck_pptx.mjs and export it with one click
Sacrifice gradient / web component / complex SVG
```

### Start-up skills (copy and use)

> Regardless of whether the final delivery is HTML, PDF or PPTX, I will first make an HTML aggregation version (`index.html` plus keyboard page turning) that can be switched and presented in the browser - this is the default basic product forever. On top of this, I would like to ask if you would like to provide additional PDF/PPTX snapshots.
>
> Which export format do you need?
> - **Just HTML** (lecture/archive) → Complete visual freedom
> - **PDF is also required** → Same as above, add an export command
> - **It also needs to be editable PPTX** (colleagues will change the text in PPT) → I have to write according to 4 hard constraints from the first line of HTML, which will sacrifice some visual capabilities (no gradient, no web component, no complex SVG).

### Why "If you want PPTX, you have to follow 4 hard constraints from scratch"

The prerequisite for PPTX to be editable is that `html2pptx.js` can translate DOM element by element into PowerPoint objects. It requires **4 hard constraints**:

1. body fixed 960pt × 540pt (matches `LAYOUT_WIDE`, 13.333″ × 7.5″, not 1920×1080px)
2. All text is wrapped in `<p>`/`<h1>`-`<h6>` (it is forbidden to put text directly in div, and it is forbidden to use `<span>` to carry the main text)
3. `<p>`/`<h*>` itself cannot have background/border/shadow (put in outer div)
4. `<div>` cannot be used with `background-image` (use `<img>` tag)
5. No CSS gradient, no web component, no complicated SVG decoration

**The default HTML of this skill has a high degree of visual freedom** - a large number of spans, nested flex, complex SVG, web components (such as `<deck-stage>`), CSS gradients - **almost none of them can naturally pass the constraints of html2pptx** (actually measured visually driven HTML is directly uploaded to html2pptx, and the pass rate is < 30%).

### Cost comparison of two real paths (2026-04-20 real pitfall)

| Path | Practice | Result | Cost |
|------|------|------|------|
| ❌ **Freely write HTML first, then remediate PPTX** | Single file deck-stage + a lot of SVG/span decoration | There are only two ways to edit PPTX:<br>A. Handwrite pptxgenjs with hundreds of lines of hardcode coordinates<br>B. Rewrite 17 pages of HTML into Path A format | 2-3 hours of rework, and the handwritten version **maintenance cost is sustainable** (change one word in HTML, PPTX To synchronize human flesh again) |
| ✅ **Write according to Path A constraints from the first step** | Each page has independent HTML + 4 hard constraints + 960×540pt | One command exports 100% editable PPTX, and can also give a full-screen speech in the browser (Path A HTML is the standard HTML that the browser can play) | Spend an extra 5 minutes thinking about "how to wrap text into `<p>`" when writing HTML, zero rework |

### What to do with mixed delivery

Users say "I want HTML presentation ** and ** editable PPTX" - **This is not a mix**, it is the PPTX requirement overriding the HTML requirement. The HTML written by pressing Path A can be displayed in full screen by the browser (just add a `deck_index.html` splicer). **No additional cost. **

Users say "I want PPTX **and** animation / web component" - **This is a real contradiction**. Tell users: To make PPTX editable, you have to sacrifice these visual capabilities. Let him make the choice, don't secretly make a handwritten pptxgenjs plan (it will become a perpetual maintenance debt).

### What to do if you find out later that you need PPTX (emergency remedy)

Rare cases: HTML has already been written before you realize you need PPTX. It is recommended to go through the **fallback process** (for complete instructions, see "Fallback: There is a visual draft but the user insists on editable PPTX" at the end of `references/editable-pptx.md`):

1. **First choice: convert PDF** (100% visual preservation, cross-platform, the recipient can view and print) - If the actual need of the recipient is "lecture/archiving", PDF is the best deliverable
2. **Second choice: AI uses the visual draft as a blueprint to rewrite a version of editable HTML** → Export editable PPTX - retain the design decisions of color/layout/copywriting, sacrificing visual capabilities such as gradients, web components, and complex SVG
3. **Not recommended: handwritten pptxgenjs reconstruction** - the position, font, and alignment must be manually adjusted, which is high maintenance cost, and any subsequent changes to the HTML will require human synchronization again.

Always tell the user your choice and let him decide. **Never start writing pptxgenjs by hand as the first reaction** - that's a last resort.

---

## 🛑 Before mass production: first make 2 pages of showcase custom grammar

**As long as the deck is ≥ 5 pages, you must not write directly from the first page to the last page. ** 2026-04-22 moxt brochure The correct order of actual combat verification:

1. Select **2 page types with the greatest visual difference** to make a showcase first (such as "Cover" + "Emotion/Quotation Page", or "Cover" + "Product Display Page")
2. Take a screenshot to allow users to confirm the grammar (masthead/font/color/spacing/structure/Chinese-English bilingual ratio)
3. After the direction is passed, the remaining N-2 pages will be pushed in batches, and the established grammar will be reused on each page.
4. After all is completed, synthesize HTML aggregation + PDF / PPTX derivatives together

**Why**: Write directly to the end of 13 pages → the user said "the direction is wrong" = rework 13 times. Do 2 pages of showcase first → wrong direction = rework 2 times. Once the visual grammar is established, the decision-making space for the subsequent N pages is greatly narrowed, leaving only "how to put the content."

**Showcase page selection principle**: Choose the two pages with the most different visual structures. Passed these two pages = can pass other intermediate states.

| Deck Type | Recommended showcase page combinations |
|-----------|---------------------|
| B2B brochure / product promotion | cover + content page (concept/emotion page) |
| Brand Release | Cover + Product Feature Page |
| Data report | Data big picture page + analysis conclusion page |
| Tutorial courseware | Chapter cover page + specific knowledge point page |

---

## 📐 Publication grammar template (moxt can be reused after actual testing)

Suitable for B2B brochure / product promotion / long report deck. Reusing this structure per page = 13 visually identical pages, 0 rework.

### Skeleton of each page

```
┌─ masthead (top strip + horizontal line)────────────┐
│  [logo 22-28px] · A Product Brochure                Issue · Date · URL │
├──────────────────────────────────────────┤
│                                          │
│── kicker (green dash + uppercase label) │
│  CHAPTER XX · SECTION NAME                 │
│                                          │
│ H1 (Chinese Noto Serif SC 900) │
│ Key words should be displayed separately with the main color of the brand │
│                                          │
│ English subtitle (Lora italic, subtitle) │
│ ─────────── Divider line ────────── │
│                                          │
│ [Specific content: double column 60/40 / 2x2 grid / list] │
│                                          │
├──────────────────────────────────────────┤
│ section name                     XX / total │
└──────────────────────────────────────────┘
```

### Style convention (copied directly)

- **H1**: Chinese Noto Serif SC 900, font size 80-140px. Depending on the amount of information, key words should be in the main brand color alone (do not pile up the color in the entire text)
- **English sub**: Lora italic 26-46px, brand signature words (such as "AI team") bold + main color italic
- **Text**: Noto Serif SC 17-21px, line-height 1.75-1.85
- **accent highlighting**: Use the main color to boldly mark keywords in the text, no more than 3 places per page (too many will lose the anchor point effect)
- **Background**: Warm rice base #FAFAFA + very light radial-gradient noise (`rgba(33,33,33,0.015)`) to increase the paper feel

### The visual protagonist must be differentiated

If 13 pages were all "text + one screenshot", it would be too monotonous. **Visual protagonist type rotation per page**:

| visual type | appropriate section |
|---------|---------------|
| Cover layout (large characters + masthead + pillar) | Home page / Chapter cover |
| Single character portrait (oversized single momo, etc.) | Introducing a single concept/character |
| Multi-character group photo/Avatar cards side by side | Team/User case |
| Timeline card progression | Showing "long-term relationship" and "evolution" |
| Knowledge graph / connection node graph | Show "collaboration" and "flow" |
| Before/After comparison card + middle arrow | Show "change" and "difference" |
| Product UI screenshot + stroked device box | Specific function display |
| big-quote (half-page large font) | sentiment page / question page / quotation page |
| Real person avatar + quote card (2×2 or 1×4) | User testimonials/usage scenarios |
| Large font back cover + URL oval button | CTA / end |

---

## ⚠️ Common pitfalls (moxt practical summary)

### 1. Emoji does not render when exported by Chromium / Playwright

Chromium does not have colored emoji fonts by default, and emojis are displayed as empty boxes when using `page.pdf()` or `page.screenshot()`.

**Countermeasure**: Replace with Unicode text symbols (`✦` `✓` `✕` `→` `·` `—`), or directly change to plain text ("Email · 23" instead of "📧 23 emails").

### 2. `export_deck_pdf.mjs` error `Cannot find package 'playwright'`

Reason: ESM module resolution looks up `node_modules` from the location of the script. The script is in `~/.claude/skills/huashu-design/scripts/`, there are no dependencies there.

**Countermeasure**: Copy the script to the deck project directory (for example `brochure/build-pdf.mjs`), run `npm install playwright pdf-lib` at the project root, and then `node build-pdf.mjs --slides slides --out output/deck.pdf`.

### 3. Take a screenshot before Google Fonts is loaded → Chinese characters are displayed in the system default boldface

Playwright requires at least `wait-for-timeout=3500` before taking screenshot/PDF to let webfont download and paint. Or self-host the fonts to `shared/fonts/` to reduce network dependencies.

### 4. Information density imbalance: too many pages filled with content

The first version of the moxt philosophy page used 2×2 = 4 paragraphs + 3 creeds at the bottom = 7 blocks of content, squeezed and repeated. After changing to 1×3 = 3 segments, the feeling of breathing returned immediately.

**Countermeasures**: Each page should be controlled at "1 core information + 3-4 auxiliary points + 1 visual protagonist". If it exceeds, split it to a new page. **Less is more** - The audience reads a page for 10 seconds, giving him 1 memory point is easier to remember than 4 memory points.

---

## 🛑Determine the structure first: single file or multiple files?

**This choice is the first step in making a slideshow. If you make a mistake, you will be in trouble again and again. Read this section first before proceeding. **

### Comparison of two architectures

| Dimensions | Single file + `deck_stage.js` | **Multiple files + `deck_index.html` splicer** |
|------|--------------------------|--------------------------------------|
| Code structure | One HTML, all slides are `<section>` | Each page is independent HTML, `index.html` is spliced ​​with iframe |
| CSS scope | ❌ Global, the style of one page may affect all pages | ✅ Natural isolation, each iframe has its own world |
| Verification granularity | ❌ JS goTo is required to switch to a certain page | ✅ Single-page files can be viewed in the browser by double-clicking |
| Parallel development | ❌ One file, multiple agents can modify it and conflicts will occur | ✅ Multiple agents can modify different pages in parallel, with zero conflict merge |
| Debugging difficulty | ❌ One CSS error will cause the whole deck to overturn | ✅ An error on one page will only affect you |
| Embedded interaction | ✅ Sharing status across pages is easy | 🟡 PostMessage is required between iframes |
| Print PDF | ✅ Built-in | ✅ Splicer beforeprint traverse iframe |
| Keyboard navigation | ✅ Built-in | ✅ Built-in splicer |

### Which one to choose? (decision tree)

```
│ Question: How many pages are expected to be in the deck?
├── ≤10 pages, in-deck animation or cross-page interaction required, pitch deck → single file
└── ≥10 pages, academic lectures, courseware, long deck, multi-agent parallel → multiple files (recommended)
```

**Multiple file paths are taken by default**. It's not an "alternative", it's the main path for longer decks and teamwork. Reason: Every advantage of a single-file architecture (keyboard navigation, printing, scale) is available in multiple files, but the scope isolation and verifiability of multiple files cannot be compensated by a single file.

### Why is this rule so hard? (Real accident record)

The single-file architecture once caused four pitfalls in the production of AI psychology lecture decks:

1. **CSS specific override**: `.emotion-slide { display: grid }` (Specificity 10) Dry flip `deck-stage > section { display: none }` (Specificity 2), causing all pages to render overlay at the same time.
2. **Shadow DOM slot rule is suppressed by outer CSS**: `::slotted(section) { display: none }` cannot block the coverage of outer rule, and sections refuse to be hidden.
3. **localStorage + hash navigation race**: After refreshing, it does not jump to the hash position, but stops at the old position recorded by localStorage.
4. **High verification cost**: You must use `page.evaluate(d => d.goTo(n))` to intercept a certain page, which is twice as slow as directly `goto(file://.../slides/05-X.html)`, and errors are often reported.

The whole root cause is a single global namespace - the multi-file architecture eliminates these problems from the physical level.

---

## Path A (default): multi-file architecture

### Directory structure

```
My Deck/
├── index.html              # Copied from assets/deck_index.html and changed to MANIFEST
├── shared/
│   ├── tokens.css          # Shared design token (color palette/font size/common chrome)
│   └── fonts.html          # <link> includes Google Fonts (include per page)
└── slides/
    ├── 01-cover.html       # Each file is full 1920×1080 HTML
    ├── 02-agenda.html
    ├── 03-problem.html
    └── ...
```

### The template skeleton of each slide

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>P05 · Chapter Title</title>
<link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
<link rel="stylesheet" href="../shared/tokens.css">
<style>
/* Style unique to this page. Using any class name will not pollute other pages. */
  body { padding: 120px; }
  .my-thing { ... }
</style>
</head>
<body>
<!-- 1920×1080 content (locked by the width/height of body in tokens.css) -->
  <div class="page-header">...</div>
  <div>...</div>
  <div class="page-footer">...</div>
</body>
</html>
```

**Key Constraints**:
- `<body>` is the canvas and is laid out directly on it. Do not wrap `<section>` or other wrappers.
- `width: 1920px; height: 1080px` is locked by the `body` rule in `shared/tokens.css`.
- Reference `shared/tokens.css` to share design tokens (color palette, font size, page-header/footer, etc.).
- The font `<link>` is written on each page (it is not expensive to import fonts individually, and each page can be opened independently).

### Splicer: `deck_index.html`

**Copy directly from `assets/deck_index.html`**. You only need to change one thing - the `window.DECK_MANIFEST` array to list all slide file names and human-readable tags in order:

```js
window.DECK_MANIFEST = [
{ file: "slides/01-cover.html", label: "Cover" },
{ file: "slides/02-agenda.html", label: "Directory" },
{ file: "slides/03-problem.html", label: "Problem Statement" },
  // ...
];
```

The splicer has built-in: keyboard navigation (←/→/Home/End/numeric key/P printing), scale + letterbox, lower right counter, localStorage memory, hash page jump, print mode (traverse iframe to output PDF by page).

### Single page validation (this is the killer advantage of multi-file architecture)

Each slide is independent HTML. **After finishing a picture, double-click to open it in the browser**:

```bash
open slides/05-personas.html
```

Playwright screenshots are also directly `goto(file://.../slides/05-personas.html)`, which does not require JS page jumps and will not be interfered by CSS of other pages. This makes the workflow cost of "modify a little and test a little" close to zero.

### Parallel development

Split the tasks of each slide to different agents and run them at the same time - the HTML files are independent of each other and there is no conflict when merging. This parallel approach can reduce the production time to 1/N for long decks.

### What to put in `shared/tokens.css`

Only put things that are truly shared across pages:

- CSS variables (swatches, font size levels, spacing levels)
- `body { width: 1920px; height: 1080px; }` such canvas lock
- `.page-header` / `.page-footer` uses exactly the same chrome for each page

**Don't** stuff a single-page layout class into it - that will revert to the global pollution problem of a single-file architecture.

---

## Path B (small deck): single file + `deck_stage.js`

Suitable for ≤10 pages, situations where state needs to be shared across pages (for example, a React tweaks panel needs to control all pages), or extremely compact scenarios such as pitch deck demo.

### Basic usage

1. Read content from `assets/deck_stage.js` and embed HTML in `<script>` (or `<script src="deck_stage.js">`)
2. Use `<deck-stage>` to package slide in body
3. 🛑 **script tag must be placed after `</deck-stage>`** (see hard constraints below)

```html
<body>

  <deck-stage>
    <section>
      <h1>Slide 1</h1>
    </section>
    <section>
      <h1>Slide 2</h1>
    </section>
  </deck-stage>

<!-- ✅ Correct: script is after deck-stage -->
  <script src="deck_stage.js"></script>

</body>
```

### 🛑 Script position hard constraints (2026-04-20 real trap)

**You cannot put `<script src="deck_stage.js">` inside `<head>`. ** Even if it can define `customElements` in `<head>`, the parser will trigger `connectedCallback` when it parses to the `<deck-stage>` start tag - at this time, the sub-`<section>` has not been parse, `_collectSlides()` gets an empty array, the counter displays `1 / 0`, and all pages are overlaid and rendered at the same time.

**Three ways to write compliance** (choose one):

```html
<!-- ✅ Most recommended: script after </deck-stage> -->
</deck-stage>
<script src="deck_stage.js"></script>

<!-- ✅ Also: script in head but add defer -->
<head><script src="deck_stage.js" defer></script></head>

<!-- ✅ Also available: module script naturally defer -->
<head><script src="deck_stage.js" type="module"></script></head>
```

`deck_stage.js` itself has built-in `DOMContentLoaded` delayed collection defense. Even if the script is placed in the head, it will not be completely blown up - but `defer` or placed at the bottom of the body is still a cleaner approach to avoid relying on the defense branch.

### ⚠️ CSS pitfalls of single-file architecture (must read)

The most common pitfall of single-file architecture is that the `display` attribute is stolen by single-page styles**.

Common error posture 1 (write display: flex directly into section):

```css
/* ❌ External CSS specificity 2, overriding shadow DOM's ::slotted(section){display:none} (also 2)*/
deck-stage > section {
display: flex; /* All pages will be overlaid and rendered at the same time! */
  flex-direction: column;
  padding: 80px;
  ...
}
```

Common wrong posture 2 (section has a class with higher specificity):

```css
.emotion-slide { display: grid; } /* Specificity: 10, worse */
```

Both will make **all slides overlay and render at the same time** - the counter may show `1 / 10` to pretend to be normal, but visually the first page covers the second page and the third page.

### ✅ Starter CSS (copy directly when starting work, no pitfalls)

**section itself** only cares about "visible/invisible"; **layout (flex/grid, etc.) is written to `.active`**:

```css
/* section only defines non-display common styles */
deck-stage > section {
  background: var(--paper);
  padding: 80px 120px;
  overflow: hidden;
  position: relative;
/* ⚠️ Don’t write display! */
}

/* Lock "not activated or hidden" - specificity + weight double insurance */
deck-stage > section:not(.active) {
  display: none !important;
}

/* Only write the required display + layout after activating the page */
deck-stage > section.active {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* Print mode: all pages must be displayed, override :not(.active) */
@media print {
  deck-stage > section { display: flex !important; }
  deck-stage > section:not(.active) { display: flex !important; }
}
```

Alternative: **Write the flex/grid of a single page to the internal wrapper `<div>`**, the section itself is always just a switcher for `display: block/none`. This is the cleanest way to do it:

```html
<deck-stage>
  <section>
    <div class="slide-content flex-layout">...</div>
  </section>
</deck-stage>
```

### Custom size

```html
<deck-stage width="1080" height="1920">
<!-- 9:16 vertical version -->
</deck-stage>
```

---

## Slide Labels

Deck_stage and deck_index both label each page (counter display). Give them **more meaningful** labels:

**Multiple files**: Write `{ file, label: "04 Problem Statement" }` in `MANIFEST`
**Single file**: Add `<section data-screen-label="04 Problem Statement">` to section

**Key: Slide numbering starts from 1, not 0**.

When the user says "slide 5", he is referring to slide 5, never array position `[4]`. Humans don't say 0-indexed.

---

## Speaker Notes

**Not added by default**, only added when explicitly requested by the user.

By adding speaker notes, you can reduce the text on the slide to a minimum and focus on impactful visuals—notes carry the complete script.

### Format

**Multiple files**: In `<head>` of `index.html` write:

```html
<script type="application/json" id="speaker-notes">
[
"The script of the first picture...",
"The script of the second picture...",
  "..."
]
</script>
```

**Single File**: Same location as above.

### Notes Writing Points

- **Complete**: Not an outline, but what you really want to say
- **Conversational**: Speak as you normally would, not written language
- **Correspondence**: The Nth item in the array corresponds to the Nth slide
- **Length**: 200-400 words is best
- **Emotional Line**: mark accents, pauses, and emphasis points

---

## Slide design pattern

### 1. Establish a system (must do)

After exploring the design context, **first verbally describe the system you want to use**:

```markdown
Deck system:
- Background color: up to 2 types (90% white + 10% dark section divider)
- Font type: Instrument Serif for display, Geist Sans for body
- Rhythm: section divider uses full-bleed color + white text, ordinary slide uses white background
- Image: hero slide uses full-bleed photos, data slide uses chart

I'll follow this system, let me know if you have any questions.
```

After the user confirms, proceed.

### 2. Commonly used slide layouts

- **Title slide**: solid color background + huge title + subtitle + author/date
- **Section divider**: color background + chapter number + chapter title
- **Content slide**: white background + title + 1-3 bullet points
- **Data slide**: title + large chart/number + short description
- **Image slide**: full-bleed photo + small caption at the bottom
- **Quote slide**: blank + huge quote + attribution
- **Two-column**: left and right comparison (vs/before-after/problem-solution)

A deck can use up to 4-5 layouts.

### 3. Scale (emphasis again)

- Minimum text size **24px**, ideal 28-36px
- Title **60-120px**
- Hero font **180-240px**
- The slides are for viewing from 10 meters away, and the text must be large enough

### 4. Visual rhythm

Deck requires **intentional variety**:

- Color rhythm: mostly white background + occasional color section divider + occasional dark segment
- Density rhythm: a few text-heavy ones + a few image-heavy ones + a few quote blank ones
- Font size rhythm: normal title + occasional giant hero text

**Don’t make every slide the same length** – that’s a PPT template, not a design.

### 5. Space breathing (must read for data-intensive pages)

**The most common pitfall for novices**: cram all the information that can be put into one page.

Information density ≠ effective information communication. Academic/speech decks should especially avoid:

- List/Matrix page: Don't draw all N elements to the same size. Use **primary and secondary layering** - the 5 enlargements we are going to talk about today will be used as protagonists, and the remaining 16 reduced ones will be used as background hints.
- Big numbers page: the numbers themselves are the visual protagonists. The surrounding caption should not exceed 3 lines, otherwise the viewer’s eyes will jump back and forth.
- Quotation page: There should be white space between quotation and attribution, do not paste them together.

Compare the two self-examinations of "whether the data is the protagonist" and "whether the text is crowded together", and change it until leaving it blank makes you a little uneasy.

---

## Print to PDF

**Multiple files**: `deck_index.html` has handled the `beforeprint` event and outputs PDF by page.

**Single file**: `deck_stage.js` is processed similarly.

The print style has been written, and there is no need to write additional `@media print` CSS.

---

## Export to PPTX/PDF (self-service script)

HTML first is first citizen. But users often require PPTX/PDF delivery. Two common scripts are provided, which can be used by any multi-file deck, under `scripts/`:

### `export_deck_pdf.mjs` — Export vector PDF (multiple file architecture)

```bash
node scripts/export_deck_pdf.mjs --slides <slides-dir> --out deck.pdf
```

**Features**:
- Text **keep vector** (copyable, searchable)
- 100% visual fidelity (Playwright embedded Chromium rendering and printing)
- **No need to change any HTML word**
- Each slide is independent of `page.pdf()`, and then merged using `pdf-lib`

**Dependencies**: `npm install playwright pdf-lib`

**Limitations**: PDF text can no longer be edited - you have to change it back to HTML.

### `export_deck_stage_pdf.mjs` — Single file deck-stage architecture specific ⚠️

**When to use**: deck is a single HTML file + `<deck-stage>` web component wrapping N `<section>` (i.e. path B structure). At this time, the `export_deck_pdf.mjs` set of "one `page.pdf()` per HTML" does not work, and this special script is needed.

```bash
node scripts/export_deck_stage_pdf.mjs --html deck.html --out deck.pdf
```

**Why can’t you reuse export_deck_pdf.mjs** (2026-04-20 real pitfall record):

1. **Shadow DOM beats `!important`**: There is `::slotted(section) { display: none }` in the shadow CSS of deck-stage (only the active one `display: block`). Even if you use `@media print { deck-stage > section { display: block !important } }` in light DOM, it cannot be suppressed - after `page.pdf()` triggers the print media, Chromium will finally render only the active one, resulting in **the entire PDF having only 1 page** (a duplication of the current active slide).

2. **Loop goto still only outputs 1 page per page**: The intuitive solution "for each `#slide-N` navigate again `page.pdf({pageRanges:'1'})`" also fails - because print CSS also has `deck-stage > section { display: block }` outside the shadow DOM. After the rule is overridden, the final rendering will always be the first one in the section list (not the page you navigate to). As a result, 17 P01 covers were obtained in 17 iterations.

3. **Absolute child elements run to the next page**: Even if all sections are successfully rendered, if the section itself is `position: static`, its absolutely positioned `cover-footer`/`slide-footer` will be positioned relative to the initial containing block - when the section is forced to a height of 1080px by print, the absolute footer may be pushed to the next page (shown as the PDF has 1 page more than the number of sections, and the extra page only contains footer orphan).

**Fix Strategy** (script implemented):

```js
// After opening the HTML, use page.evaluate to extract the section from the deck-stage slot.
// Hang it directly into a normal div under the body, and inline style to ensure position:relative + fixed size
await page.evaluate(() => {
  const stage = document.querySelector('deck-stage');
  const sections = Array.from(stage.querySelectorAll(':scope > section'));
  document.head.appendChild(Object.assign(document.createElement('style'), {
    textContent: `
      @page { size: 1920px 1080px; margin: 0; }
      html, body { margin: 0 !important; padding: 0 !important; }
      deck-stage { display: none !important; }
    `,
  }));
  const container = document.createElement('div');
  sections.forEach(s => {
    s.style.cssText = 'width:1920px!important;height:1080px!important;display:block!important;position:relative!important;overflow:hidden!important;page-break-after:always!important;break-after:page!important;background:#F7F4EF;margin:0!important;padding:0!important;';
    container.appendChild(s);
  });
  // Disable pagination on the last page to avoid blank pages at the end
  sections[sections.length - 1].style.pageBreakAfter = 'auto';
  sections[sections.length - 1].style.breakAfter = 'auto';
  document.body.appendChild(container);
});

await page.pdf({ width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
```

**Why this works**:
- Unplug the section from the shadow DOM slot to an ordinary div in the light DOM - completely bypassing the `::slotted(section) { display: none }` rule
- Inline `position: relative` allows absolute child elements to be positioned relative to the section without overflowing
- `page-break-after: always` allows the browser to print each section on a separate page
- `:last-child` does not paginate to avoid trailing blank pages

**Note when verifying with `mdls -name kMDItemNumberOfPages`**: macOS's Spotlight metadata is cached. After rewriting the PDF, you must run `mdimport file.pdf` to force a refresh, otherwise the old page number will be displayed. Use `pdfinfo` or `pdftoppm` to count the number of files to get the real number.

---

### `export_deck_pptx.mjs` — Export editable PPTX

```bash
# Only mode: the text box is natively editable (the font will fall back to the system font)
node scripts/export_deck_pptx.mjs --slides <dir> --out deck.pptx
```

Working principle: `html2pptx` reads computedStyle element by element and translates DOM into PowerPoint objects (text frame / shape / picture). The text becomes a real text box and can be edited by double-clicking it in PPT.

**Hard constraints** (HTML must be satisfied, otherwise the page will be skipped, see `references/editable-pptx.md` for details):
- All text must be inside `<p>`/`<h1>`-`<h6>`/`<ul>`/`<ol>` (naked text divs are prohibited)
- `<p>`/`<h*>` tag itself cannot have background/border/shadow (put in outer div)
- No need to use `::before`/`::after` to insert decorative text (pseudo elements cannot be extracted)
- Inline elements (span/em/strong) cannot have margins
- No CSS gradient (non-renderable)
- div without `background-image` (use `<img>`)

The script has built-in **automatic preprocessor** - automatically wraps "bare text in leaf div" into `<p>` (retained class). This solves the most common violation (bare text). But other violations (border on p, margin on span, etc.) still require HTML source compliance.

**Font fallback caveat**:
- Playwright uses webfont to measure text-box size; PowerPoint/Keynote uses native fonts for rendering
- When the two are different, there will be **overflow or misalignment** - each page must be checked with the naked eye
- It is recommended that the target machine install the fonts used in HTML, or fallback to `system-ui`

**Don’t take this path for visual-first scenarios** → Use `export_deck_pdf.mjs` to export PDF instead. PDF is 100% visual fidelity, vector, cross-platform, and text-searchable—it’s the true home of a visual-first deck, not a “non-editable compromise.”

### Make HTML export-friendly from the start

For the deck with the most stable performance: **Write according to the four hard constraints of editable when writing HTML**. In this way, `export_deck_pptx.mjs` can be passed directly. The additional costs are modest:

```html
<!-- ❌ Not good -->
<div class="title">Key findings</div>

<!-- ✅ OK (p package, class inheritance) -->
<p class="title">Key findings</p>

<!-- ❌ bad (border is on p) -->
<p class="stat" style="border-left: 3px solid red;">41%</p>

<!-- ✅ OK (border is in the outer div) -->
<div class="stat-wrap" style="border-left: 3px solid red;">
  <p class="stat">41%</p>
</div>
```

### When to choose which one?

| Scenario | Recommendation |
|------|------|
| To the organizer/archive | **PDF** (general, high-fidelity, text searchable) |
| Send to collaborators to fine-tune the text | **PPTX editable** (accepts font fallback) |
| Give a live speech without changing the content | **PDF** (vector fidelity, cross-platform) |
| HTML is the preferred presentation medium | Direct browser playback, export is just a backup |

## Export depth paths to editable PPTX (long-term projects only)

If your deck will be maintained for a long time, repeatedly modified, and teamed up - it is recommended to write HTML according to html2pptx constraints from the beginning, so that `export_deck_pptx.mjs` can be passed directly. For details, see `references/editable-pptx.md` (4 hard constraints + HTML template + common error quick check + fallback process for existing visual drafts).

---

## FAQ

**Multiple files: The page in the iframe cannot be opened / white screen**
→ Check whether the `file` path of `MANIFEST` is correct relative to `index.html`. Use the browser DevTools to see if the src of the iframe can be accessed directly.

**Multiple files: The style of a certain page conflicts with another page**
→ Not possible (iframe isolation). If you feel a conflict, it's the cache - Cmd+Shift+R to force refresh.

**Single file: multiple slides simultaneously rendered and overlaid**
→ CSS specific issues. See the “CSS Pitfalls of Single-File Architecture” section above.

**Single file: scaling doesn't look right**
→ Check if all slides are hung directly under `<deck-stage>` as `<section>`. `<div>` cannot be included in the middle.

**Single file: want to jump to a specific slide**
→ URL plus hash: `index.html#slide-5` Jump to the 5th picture.

**Applicable to both architectures: characters are inconsistently positioned on different screens**
→ Use fixed size (1920×1080) and `px` units, do not use `vw`/`vh` or `%`. Scaling is handled uniformly.

---

## Verification checklist (must pass after completing deck)

1. [ ] Open `index.html` (or main HTML) directly in the browser and check that there are no broken images on the homepage and that the fonts have been loaded.
2. [ ] Press the → key to turn to each page. There are no blank pages or layout misalignments.
3. [ ] Press P key to print preview, each page is exactly one A4 (or 1920×1080) without cropping
4. [ ] Randomly select 3 pages Cmd+Shift+R to force refresh, localStorage memory works normally
5. [ ] Playwright batch screenshots (single page architecture: traverse `slides/*.html`; single file architecture: switch with goTo), go through it with the naked eye
6. [ ] Search for `TODO` / `placeholder` remnants and confirm that they have been cleaned up
