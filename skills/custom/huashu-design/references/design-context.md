# Design Context: Starting from the existing context

**This is the most important thing in this skill. **

Good hi-fi design must grow out of the existing design context. **Making hi-fi out of thin air is the last resort, and it will definitely produce generic works**. So at the beginning of every design task, ask: Is there anything I can refer to?

## What is Design Context?

From high to low priority:

### 1. User’s Design System/UI Kit
The user’s own products already have component libraries, color tokens, font specifications, and icon systems. **The perfect situation**.

### 2. User’s Codebase
If the user contributes to the code base, there will be living component implementations in it. Read those component files:
- `theme.ts` / `colors.ts` / `tokens.css` / `_variables.scss`
- Specific components (Button.tsx, Card.tsx)
- Layout scaffold（App.tsx、MainLayout.tsx）
- Global stylesheets

**Read code and copy exact values**: hex codes, spacing scale, font stack, border radius. Don't redraw from memory.

### 3. Products published by the user
If the user has a live product but has not given the code, use Playwright or ask the user to provide screenshots.

```bash
# Screenshot a public URL using Playwright
npx playwright screenshot https://example.com screenshot.png --viewport-size=1920,1080
```

Let you see the real visual vocabulary.

### 4. Brand Guide/Logo/Existing Materials
Users may have: Logo files, brand color specifications, marketing materials, and slide templates. These are contexts.

### 5. Competitive product reference
The user said "like XX website" - asked him to provide the URL or screenshot. **Don't** rely on vague impressions from your training data.

### 6. Known design system (fallback)
If none of the above are available, use a recognized design system as a base:
- Apple HIG
- Material Design 3
- Radix Colors
- shadcn/ui (component)
- Tailwind default palette

Tell the user clearly what you are using and let him know that this is the starting point and not the final version.

## Process of obtaining Context

### Step 1: Ask the user

Checklist to ask at the beginning of the task (from `workflow.md`):

```markdown
1. Do you have a ready-made design system/UI kit/component library? Where?
2. Are there brand guidelines, color/font specifications?
3. Can you give me screenshots or URLs of existing products?
4. Is there a codebase that I can read?
```

### Step 2: When the user says "no", help him find it

Don't just give up. try:

```markdown
Let me see if I have any clues:
-Are there any related designs for your previous projects?
- What colors/fonts are used for the company’s marketing website?
-What style is the logo of your product? Can you give me one?
- Are there any products that you admire that you can use as a reference?
```

### Step 3: Read all contexts that can be found

If the user gives the codebase path, you read:
1. **List file structure first**: Find files related to style/theme/component
2. **Read theme/token file**: lift specific hex/px values
3. **Read 2-3 representative components**: Look at the visual vocabulary (hover state, shadow, border, padding node pattern)
4. **Read global stylesheet**: basic reset, font loading
5. **If there is a link/screenshot of Figma**: look at the picture, but **believe more in the code**

**Important**: **Don't** just take a look and act based on your impression. The lift is really achieved after reading 30+ specific values.

### Step 4: Vocalize the system you want to use

After reading the context, tell the user the system you want to use:

```markdown
Based on your codebase and product screenshots, I refined the design system:

**color**
- Primary: # C27558 (from tokens.css)
- Background: #FDF9F0
- Text: #1A1A1A
- Muted: #6B6B6B

**Font**
- Display: Instrument Serif (@font-face from global.css)
- Body: Geist Sans
- Mono: JetBrains Mono

**Spacing** (from your scale system)
- 4, 8, 12, 16, 24, 32, 48, 64

**Shadow pattern**
- `0 1px 2px rgba(0,0,0,0.04)`（subtle card）
- `0 10px 40px rgba(0,0,0,0.1)`（elevated modal）

**Border-radius**
- Widget 4px, card 12px, button 8px

**component vocabulary**
- Button: filled primary, outlined secondary, ghost tertiary, all rounded 8px
- Card: white background, subtle shadow, no border

I started working on this system. Are you sure there's no problem?
```

The user must confirm before proceeding.

## Design out of thin air (fallback when there is no Context)

**STRONG WARNING**: The quality of the output in this case will decrease significantly. Tell users clearly.

```markdown
You don’t have a design context, so I can only do it based on general intuition.
The output will be something that "looks OK but lacks uniqueness".
Would you like to continue, or provide some reference materials first?
```

The user insists that you make decisions in this order:

### 1. Choose an aesthetic direction
Don't give generic results. Pick a clear direction:
- brutally minimal
- editorial/magazine
- brutalist/raw
- organic/natural
- luxury/refined
- playful/toy
- retro-futuristic
- soft/pastel

Tell the user which one you selected.

### 2. Choose a known design system as the skeleton
- Use Radix Colors for color matching (https://www.radix-ui.com/colors)
- Use shadcn/ui as component vocabulary (https://ui.shadcn.com)
- Use Tailwind spacing scale (a multiple of 4)

### 3. Choose distinctive font pairings

Don't use Inter/Roboto. Suggested combinations (free from Google Fonts):
- Instrument Serif + Geist Sans
- Cormorant Garamond + Inter Tight
- Bricolage Grotesque + Söhne (paid)
- Fraunces + Work Sans (note that Fraunces has been used badly by AI)
- JetBrains Mono + Geist Sans（technical feel）

### 4. Every key decision has reasoning

Don’t choose silently. Write in the HTML comment:

```html
<!--
Design decisions:
- Primary color: warm terracotta (oklch 0.65 0.18 25) — fits the "editorial" direction  
- Display: Instrument Serif for humanist, literary feel
- Body: Geist Sans for cleanness contrast
- No gradients — committed to minimal, no AI slop
- Spacing: 8px base, golden ratio friendly (8/13/21/34)
-->
```

##Import strategy (the user gave the codebase)

If the user says "import this codebase for reference":

### Small (<50 files)
Read all and internalize the context.

### Medium (50-500 files)
Focus on:
- `src/components/` or `components/`
- All styles/tokens/theme related files
- 2-3 representative full-page components (Home.tsx, Dashboard.tsx)

### Large (>500 files)
Let the user specify focus:
- "I want to make settings page" → read existing settings related
- "I want to make a new feature" → read the whole shell + the closest reference
- Don’t seek perfection, seek accuracy

## Cooperation with Figma/design draft

If the user gives Figma a link:

- **Don't** expect that you can "convert Figma to HTML" directly - that requires additional tools
- Figma links are generally not publicly accessible
- Let the user: export it as a **screenshot** and send it to you + tell you the specific color/spacing values

If you only give Figma screenshots, tell the user:
- I can see the vision, but I can't get the exact values.
- Please tell me the key numbers (hex, px), or export as code (Figma supports)

## Final reminder

**The upper limit of design quality for a project is determined by the quality of the context you get**.

Spending 10 minutes collecting context is more valuable than spending an hour drawing hi-fi out of thin air.

**When encountering a situation where there is no context, give priority to asking the user for it instead of forcing it**.
