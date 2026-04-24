# React + Babel project specifications

Technical specifications that must be followed when prototyping with HTML+React+Babel. Failure to comply will result in explosion.

## Pinned Script Tags (must use these versions)

Put these three script tags in the `<head>` of HTML, using **fixed version+integrity hash**:

```html
<script src="https://unpkg.com/react@18.3.1/umd/react.development.js" integrity="sha384-hD6/rw4ppMLGNu3tX5cjIb+uRZ7UkRJ6BPkLpg4hAu/6onKUg4lLsHAs9EBPT82L" crossorigin="anonymous"></script>
<script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js" integrity="sha384-u6aeetuaXnQ38mYT8rp6sbXaQe3NL9t+IBXmnYxwkUI2Hw4bsp2Wvmx4yRQF1uAm" crossorigin="anonymous"></script>
<script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js" integrity="sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y" crossorigin="anonymous"></script>
```

**Don't** use unpinned versions like `react@18` or `react@latest` - version drift/caching issues will occur.

**Don't** omit `integrity` - this is the line of defense once the CDN is hijacked or tampered with.

## File structure

```
Project name/
├── index.html               # Main HTML
├── components.jsx           # Component file (loaded with type="text/babel")
├── data.js                  # data file
└── styles.css               # Additional CSS (optional)
```

Loading method in HTML:

```html
<!-- React+Babel first -->
<script src="https://unpkg.com/react@18.3.1/..."></script>
<script src="https://unpkg.com/react-dom@18.3.1/..."></script>
<script src="https://unpkg.com/@babel/standalone@7.29.0/..."></script>

<!-- Then your component file -->
<script type="text/babel" src="components.jsx"></script>
<script type="text/babel" src="pages.jsx"></script>

<!--Last main entrance -->
<script type="text/babel">
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(<App />);
</script>
```

**Don't** use `type="module"` - it will conflict with Babel.

## Three rules that cannot be violated

### Rule 1: styles objects must be uniquely named

**Error** (will explode when there are multiple components):
```jsx
// components.jsx
const styles = { button: {...}, card: {...} };

// pages.jsx ← Same name coverage!
const styles = { container: {...}, header: {...} };
```

**Correct**: Use a unique prefix for styles in each component file.

```jsx
// terminal.jsx
const terminalStyles = { 
  screen: {...}, 
  line: {...} 
};

// sidebar.jsx
const sidebarStyles = { 
  container: {...}, 
  item: {...} 
};
```

**Or use inline styles** (recommended for widgets):
```jsx
<div style={{ padding: 16, background: '#111' }}>...</div>
```

This is **non-negotiable**. Every time you write `const styles = {...}`, you must replace it with a specific name, otherwise the full stack will report an error when loading multiple components.

### Rule 2: Scope is not shared and needs to be exported manually.

**Key knowledge**: Each `<script type="text/babel">` is compiled independently by Babel, and there is no **scope communication** between them. The `Terminal` component defined in `components.jsx` is undefined by default in `pages.jsx`.

**Solution**: At the end of each component file, export the component/tool ​​to be shared to `window`:

```jsx
// end of components.jsx
function Terminal(props) { ... }
function Line(props) { ... }
const colors = { green: '#...', red: '#...' };

Object.assign(window, {
  Terminal, Line, colors,
  // Everything you want to use elsewhere is listed here
});
```

Then `pages.jsx` can use `<Terminal />` directly, because JSX will go to `window.Terminal` to find it.

### Rule 3: Don’t use scrollIntoView

`scrollIntoView` will push the entire HTML container upwards, disrupting the layout of the web harness. **Never use**.

Alternative:
```js
// Scroll to a certain position within the container
container.scrollTop = targetElement.offsetTop;

// Or use element.scrollTo
container.scrollTo({
  top: targetElement.offsetTop - 100,
  behavior: 'smooth'
});
```

## Call Claude API (in HTML)

Some native design-agent environments (such as Claude.ai Artifacts) have configuration-free `window.claude.complete`, but most agent environments (Claude Code / Codex / Cursor / Trae / etc.) do not have it locally.

If your HTML prototype needs to call LLM for demo (such as making a chat interface), there are two options:

### Option A: No real adjustment, use mock

Demo scene is recommended. Write a fake helper that returns the default response:
```jsx
window.claude = {
  async complete(prompt) {
    await new Promise(r => setTimeout(r, 800)); // Analog delay
return "This is a mock response. Please replace it with the real API when deploying.";
  }
};
```

### Option B: Really adjust the Anthropic API

An API key is required, and users must fill in their own key in HTML to run. **Never hardcode keys in HTML**.

```html
<input id="api-key" placeholder="Paste your Anthropic API key" />
<script>
window.claude = {
  async complete(prompt) {
    const key = document.getElementById('api-key').value;
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': key,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5',
        max_tokens: 1024,
        messages: [{ role: 'user', content: prompt }]
      })
    });
    const data = await res.json();
    return data.content[0].text;
  }
};
</script>
```

**Note**: If the browser directly calls the Anthropic API, it will encounter CORS problems. If the preview environment given to you by the user does not support CORS bypass, this path will not work. At this time, use option A mock, or tell the user that a proxy backend is required.

### Option C: Use the LLM capability on the agent side to generate mock data

If it is only for local demonstration, you can temporarily call the agent's LLM capability (or the multi-model class skill installed by the user) in the current agent session to generate mock response data, and then hard-code it into HTML. In this way, the HTML runtime does not depend on any API at all.

## Typical HTML starter template

Copy this template as the skeleton of your React prototype:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Prototype Name</title>

  <!-- React + Babel pinned -->
  <script src="https://unpkg.com/react@18.3.1/umd/react.development.js" integrity="sha384-hD6/rw4ppMLGNu3tX5cjIb+uRZ7UkRJ6BPkLpg4hAu/6onKUg4lLsHAs9EBPT82L" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js" integrity="sha384-u6aeetuaXnQ38mYT8rp6sbXaQe3NL9t+IBXmnYxwkUI2Hw4bsp2Wvmx4yRQF1uAm" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js" integrity="sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y" crossorigin="anonymous"></script>

  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { height: 100%; width: 100%; }
    body { 
      font-family: -apple-system, 'SF Pro Text', sans-serif;
      background: #FAFAFA;
      color: #1A1A1A;
    }
    #root { min-height: 100vh; }
  </style>
</head>
<body>
  <div id="root"></div>

<!-- Your component file -->
  <script type="text/babel" src="components.jsx"></script>

<!-- Main entrance -->
  <script type="text/babel">
    const { useState, useEffect } = React;

    function App() {
      return (
        <div style={{padding: 40}}>
          <h1>Hello</h1>
        </div>
      );
    }

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(<App />);
  </script>
</body>
</html>
```

## Common errors and solutions

**`styles is not defined` or `Cannot read property 'button' of undefined`**
→ 你在一个文件里定义了`const styles`，另一个文件覆盖了。 Give each one a specific name.

**`Terminal is not defined`**
→ The scope is blocked when referencing across files. Add `Object.assign(window, {Terminal})` at the end of the file defining Terminal.

**The entire page is white screen and there are no errors in the console**
→ It's probably a JSX syntax error but Babel didn't report it in the console. Temporarily replace `babel.min.js` with the uncompressed version of `babel.js` to make the error message clearer.

**ReactDOM.createRoot is not a function**
→ The version is wrong.确认用了react-dom@18.3.1（而不是17或其他）。

**`Objects are not valid as a React child`**
→ You are rendering an object instead of a JSX/String. Usually `{someObj}` is written as `{someObj.name}`.

## How to split files in large projects

**>A single file with 1000 lines is difficult to maintain. Spin-off ideas:

```
project/
├── index.html
├── src/
│   ├── primitives.jsx      # Basic elements: Button, Card, Badge...
│   ├── components.jsx      # Business components: UserCard, PostList...
│   ├── pages/
│   │   ├── home.jsx        # front page
│   │   ├── detail.jsx      # Details page
│   │   └── settings.jsx    # settings page
│   ├── router.jsx          # Simple routing (React state switching)
│   └── app.jsx             # Entry component
└── data.js                 # mock data
```

Loading in order in HTML:
```html
<script type="text/babel" src="src/primitives.jsx"></script>
<script type="text/babel" src="src/components.jsx"></script>
<script type="text/babel" src="src/pages/home.jsx"></script>
<script type="text/babel" src="src/pages/detail.jsx"></script>
<script type="text/babel" src="src/pages/settings.jsx"></script>
<script type="text/babel" src="src/router.jsx"></script>
<script type="text/babel" src="src/app.jsx"></script>
```

**At the end of each file** there must be `Object.assign(window, {...})` to export what you want to share.
