# Tweaks: real-time parameter adjustment of design variants

Tweaks are a core capability in this skill - allowing users to switch variations/adjust parameters in real time without changing the code.

**Cross-agent environment adaptation**: Some design-agent native environments (such as Claude.ai Artifacts) rely on the host's postMessage to write the tweak values ​​back to the source code for persistence. This skill uses the **pure front-end localStorage solution** - the effect is the same (refreshing the retained state), but persistence occurs in the browser localStorage instead of the source code file. This solution works in any agent environment (Claude Code / Codex / Cursor / Trae / etc.).

## When to add Tweaks

- Users explicitly request "can adjust parameters"/"switch between multiple versions"
- When the design has multiple variations that need to be compared
- The user didn’t say it clearly, but your subjective judgment** adding a few inspiring tweaks can help users see the possibilities**

Default recommendation: **Add 2-3 tweaks to each design** (color theme/font size/layout variations) Even if the user does not ask for it - letting users see the possibility space is part of the design service.

## Implementation method (pure front-end version)

### Basic structure

```jsx
const TWEAK_DEFAULTS = {
  "primaryColor": "#D97757",
  "fontSize": 16,
  "density": "comfortable",
  "dark": false
};

function useTweaks() {
  const [tweaks, setTweaks] = React.useState(() => {
    try {
      const stored = localStorage.getItem('design-tweaks');
      return stored ? { ...TWEAK_DEFAULTS, ...JSON.parse(stored) } : TWEAK_DEFAULTS;
    } catch {
      return TWEAK_DEFAULTS;
    }
  });

  const update = (patch) => {
    const next = { ...tweaks, ...patch };
    setTweaks(next);
    try {
      localStorage.setItem('design-tweaks', JSON.stringify(next));
    } catch {}
  };

  const reset = () => {
    setTweaks(TWEAK_DEFAULTS);
    try {
      localStorage.removeItem('design-tweaks');
    } catch {}
  };

  return { tweaks, update, reset };
}
```

### Tweaks panel UI

Floating panel in the lower right corner. Foldable:

```jsx
function TweaksPanel() {
  const { tweaks, update, reset } = useTweaks();
  const [open, setOpen] = React.useState(false);

  return (
    <div style={{
      position: 'fixed',
      bottom: 20,
      right: 20,
      zIndex: 9999,
    }}>
      {open ? (
        <div style={{
          background: 'white',
          border: '1px solid #e5e5e5',
          borderRadius: 12,
          padding: 20,
          boxShadow: '0 10px 40px rgba(0,0,0,0.12)',
          width: 280,
          fontFamily: 'system-ui',
          fontSize: 13,
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: 16,
          }}>
            <strong>Tweaks</strong>
            <button onClick={() => setOpen(false)} style={{
              border: 'none', background: 'none', cursor: 'pointer', fontSize: 16,
            }}>×</button>
          </div>

{/* color */}
          <label style={{ display: 'block', marginBottom: 12 }}>
            <div style={{ marginBottom: 4, color: '# 666' }}>Main color</div>
            <input 
              type="color" 
              value={tweaks.primaryColor} 
              onChange={e => update({ primaryColor: e.target.value })}
              style={{ width: '100%', height: 32 }}
            />
          </label>

{/* Font size slider */}
          <label style={{ display: 'block', marginBottom: 12 }}>
            <div style={{ marginBottom: 4, color: '# 666' }}>Font size ({tweaks.fontSize}px)</div>
            <input 
              type="range" 
              min={12} max={24} step={1}
              value={tweaks.fontSize}
              onChange={e => update({ fontSize: +e.target.value })}
              style={{ width: '100%' }}
            />
          </label>

{/* density options */}
          <label style={{ display: 'block', marginBottom: 12 }}>
            <div style={{ marginBottom: 4, color: '# 666' }}>Density</div>
            <select 
              value={tweaks.density}
              onChange={e => update({ density: e.target.value })}
              style={{ width: '100%', padding: 6 }}
            >
<option value="compact">Compact</option>
<option value="comfortable">Comfortable</option>
<option value="spacious">Loose</option>
            </select>
          </label>

{/* Dark mode toggle */}
          <label style={{ 
            display: 'flex', 
            alignItems: 'center',
            gap: 8,
            marginBottom: 16,
          }}>
            <input 
              type="checkbox" 
              checked={tweaks.dark}
              onChange={e => update({ dark: e.target.checked })}
            />
<span>Dark Mode</span>
          </label>

          <button onClick={reset} style={{
            width: '100%',
            padding: '8px 12px',
            background: '#f5f5f5',
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer',
            fontSize: 12,
}}>Reset</button>
        </div>
      ) : (
        <button 
          onClick={() => setOpen(true)}
          style={{
            background: '#1A1A1A',
            color: 'white',
            border: 'none',
            borderRadius: 999,
            padding: '10px 16px',
            fontSize: 12,
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          }}
        >⚙ Tweaks</button>
      )}
    </div>
  );
}
```

### Apply Tweaks

Use Tweaks in the main component:

```jsx
function App() {
  const { tweaks } = useTweaks();

  return (
    <div style={{
      '--primary': tweaks.primaryColor,
      '--font-size': `${tweaks.fontSize}px`,
      background: tweaks.dark ? '#0A0A0A' : '#FAFAFA',
      color: tweaks.dark ? '#FAFAFA' : '#1A1A1A',
    }}>
{/* your content */}
      <TweaksPanel />
    </div>
  );
}
```

Using variables in CSS:

```css
button.cta {
  background: var(--primary);
  color: white;
  font-size: var(--font-size);
}
```

## Typical Tweak options

What tweaks to add to different types of designs:

### General
- Main color (color picker)
- Font size (slider 12-24px)
- Font (select: display font vs body font)
- Dark mode (toggle)

### Slide deck
- Theme (light/dark/brand)
- Background style (solid/gradient/image)
- Font contrast (more decorative vs more restrained)
- Information density (minimal/standard/dense)

### Product prototype
- Layout variations (layout A/B/C)
- Interaction speed (animation speed 0.5x-2x)
- Data volume (number of mock data 5/20/100)
- Status (empty/loading/success/error)

### Animation
- Speed ​​(0.5x-2x)
- Loop (once/loop/ping-pong)
- Easing（linear/easeOut/spring）

### Landing page
- Hero style (image/gradient/pattern/solid)
- CTA copy (several variations)
- Structure (single column / two column / sidebar)

## Tweaks design principles

### 1. Meaningful options, not tormenting people

Each tweak must demonstrate **real design options**. Don’t add the kind of tweaks that no one will actually switch (such as border-radius 0-50px slider - after users adjust it, they find that all the intermediate values ​​are ugly).

Good tweaks expose discrete, thoughtful variations:
- "Rounded corners style": no rounded corners / micro rounded corners / large rounded corners (three options)
- Not: "rounded corners": 0-50px slider

### 2. Less is more

A designed Tweaks panel has up to 5-6 options. Any more and it becomes a "configuration page" and loses the meaning of quickly exploring variations.

### 3. The default value is to complete the design

Tweaks are the **icing on the cake**. The default must be a complete, releasable design in its own right. What the user sees after closing the Tweaks panel is the output.

### 4. Reasonable grouping

Multiple options are displayed in groups:

```
---- Vision ----
Main color | Font size | Dark mode

---- Layout ----
Density | Sidebar Position

---- content ----
Display data amount | status
```

## Forward compatible with source-level persistence host

If you later want to upload the design to an environment that supports source-level tweaks (such as Claude.ai Artifacts) and run it, keep the **EDITMODE tag block**:

```jsx
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "primaryColor": "#D97757",
  "fontSize": 16,
  "density": "comfortable",
  "dark": false
}/*EDITMODE-END*/;
```

标记块在 localStorage 方案里**无作用**（只是个普通注释），但在支持源码回写的 host 里会被读取，实现源码级持久化。 Plus this is harmless to the current environment while remaining forward compatible.

## FAQ

**Tweaks panel blocks design content**
→ Make it closeable. It is closed by default and displays a small button, which will be expanded after the user clicks it.

**Users must repeat settings after switching tweaks**
→ LocalStorage has been used. If it is not persistent after refreshing, check whether localStorage is available (incognito mode will fail, so you need to catch it).

**Multiple HTML pages want to share tweaks**
→ Add project name to localStorage key: `design-tweaks-[projectName]`.

**I want there to be a linkage between tweaks**
→ Add logic in `update`:

```jsx
const update = (patch) => {
  let next = { ...tweaks, ...patch };
  // Linkage: Automatically switch font color matching when dark mode is selected
  if (patch.dark === true && !patch.textColor) {
    next.textColor = '#F0EEE6';
  }
  setTweaks(next);
  localStorage.setItem(...);
};
```
