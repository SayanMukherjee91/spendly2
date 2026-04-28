---
name: spendly-ui-designer
description: >
  Generates modern, production-ready UI components and pages for the Spendly2 personal expense
  tracker (https://github.com/SayanMukherjee91/spendly2). Use this skill IMMEDIATELY whenever
  the user says anything like "design the ___ page", "create UI for ___", "build a component
  for ___", "redesign ___", "improve the look of ___", or any other request involving frontend
  UI work on Spendly -- even vague requests like "make this look better" or "add a new section".
  Always trigger for Spendly-related UI work. Never skip this skill for frontend requests
  within the Spendly project.
---

# Spendly UI Designer

You generate clean, modern, production-ready HTML/CSS UI components and pages for the Spendly2
personal expense tracker. The project is a Flask + Jinja2 app with pure custom CSS -- no Tailwind,
no Bootstrap. Your job is to extend the existing design system faithfully and produce code that
feels native to the project.

## Project Context

- Stack: Flask (Python), Jinja2 templates, pure CSS, Chart.js 4, SQLite
- Repo: https://github.com/SayanMukherjee91/spendly2
- Currency: Indian Rupee (Rs.)
- Existing pages: landing, login, register, dashboard, expenses, profile, privacy, terms

---

## Design System

Always use these exact CSS custom properties. Never invent new color names or override these.

### Colors

```css
/* Ink (text) */
--ink:        #0f0f0f;
--ink-soft:   #2d2d2d;
--ink-muted:  #6b6b6b;
--ink-faint:  #a0a0a0;

/* Paper (backgrounds) */
--paper:      #f7f6f3;
--paper-warm: #f0ede6;
--card:       #ffffff;

/* Accent -- forest green (primary brand color) */
--accent:       #1a472a;
--accent-light: #e8f0eb;

/* Accent 2 -- amber/gold (secondary emphasis) */
--accent-2:       #c17f24;
--accent-2-light: #fdf3e3;

/* Danger */
--danger:       #c0392b;
--danger-light: #fdecea;

/* Borders */
--border:      #e4e1da;
--border-soft: #eeebe4;
```

### Typography

- Display / headings: 'DM Serif Display', Georgia, serif -- page titles, hero text, section headers
- Body / UI: 'DM Sans', system-ui, sans-serif -- all other text (weights 300, 400, 500, 600)

Both fonts are already loaded via Google Fonts in base.html. Do not re-import them.

### Spacing (8px grid)

All spacing values must be multiples of 8px:

- 0.5rem = 8px
- 1rem = 16px
- 1.5rem = 24px
- 2rem = 32px
- 3rem = 48px

Never use arbitrary values like 13px or 22px.

### Border Radius

- Small (6px): inputs, badges, buttons
- Medium (12px): cards, panels
- Large (20px): modals, large containers

### Shadows

```css
/* Standard card shadow */
box-shadow: 0 8px 40px rgba(0,0,0,0.07);

/* Subtle hover / nested element */
box-shadow: 0 2px 12px rgba(0,0,0,0.05);
```

### Buttons

```css
/* Primary button */
.btn-primary {
  background: var(--ink);
  color: var(--card);
  padding: 0.65rem 1.5rem;
  border-radius: 6px;
  font-family: 'DM Sans', system-ui, sans-serif;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-primary:hover { background: var(--accent); }

/* Ghost button */
.btn-ghost {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--ink-soft);
  padding: 0.65rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
}
```

### Cards

```css
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 40px rgba(0,0,0,0.07);
}
```

### Layout

- Max content width: 1200px, centered with margin: 0 auto
- Auth containers: 440px max-width
- Use CSS grid or flexbox -- no floats
- Responsive breakpoints:
  - 900px and below: multi-column collapses to single column
  - 600px and below: mobile-friendly; reduce padding, hide secondary nav links

---

## Icons

Use Lucide Icons for all iconography. Add to the head if not already present in base.html:

```html
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
```

Render icons with:

```html
<i data-lucide="icon-name"></i>
```

Initialize at the bottom of any script block:

```js
lucide.createIcons();
```

Semantically meaningful icon choices:

- Balance / wallet: wallet
- Income: trending-up
- Expense / spending: trending-down
- Transaction: receipt
- Profile: user
- Category: tag
- Calendar: calendar
- Settings: settings
- Delete: trash-2
- Edit: pencil
- Add: plus-circle

---

## Output Format

For every request, produce output in this order:

### 1. UI Structure (brief)

Describe the layout in 5-10 bullet points covering:
- Overall grid/flex structure
- Key sections and their purpose
- Notable UX decisions and why you made them

Keep this concise -- it is a design brief, not a full spec.

### 2. Code

Produce a clean, self-contained Jinja2 template structured like this:

```
{% extends "base.html" %}
{% block content %}
  <!-- scoped <style> block at top -->
  <!-- page markup -->
  <!-- <script> block at bottom if needed -->
{% endblock %}
```

Code rules:
- Put CSS in a style block inside the block content, scoped to descriptive class names
- Class names follow the existing BEM-ish pattern (e.g., .expense-card, .expense-card__amount, .summary-strip)
- No inline styles except for dynamic Jinja2 values (e.g., style="width: {{ pct }}%")
- Vanilla JS only -- no frameworks
- Chart.js 4 for data visualization (already in the project)
- Use Jinja2 loops and conditionals wherever data-driven rendering is needed

### 3. Design Notes (optional)

Only include this section if something is non-obvious -- an accessibility consideration,
a subtle animation, a responsive edge case, or a suggested enhancement.

---

## Design Rules

- Minimal fintech aesthetic: clean, professional -- no decoration for its own sake
- Card-based layout: group related content in cards with consistent radius and shadow
- Hierarchy through typography: DM Serif Display for emphasis, DM Sans for clarity
- Consistent spacing: always use 8px-grid multiples
- Accent colors sparingly: use --accent and --accent-2 on CTAs, icons, and key data -- not as backgrounds everywhere
- Never clutter: if a section feels crowded, strip it back rather than squeezing content in
- Empty states matter: always design what the page looks like with no data -- use a friendly empty-state component with a Lucide icon and a short message

---

## Consistency Rule

Always match the design system above. If the user's request would introduce something that conflicts
(e.g., a clashing color palette, a different font, Bootstrap components), flag it and offer a
design-system-compatible version -- or ask for clarification.

If you need visual context that the user has not provided, ask:
"Could you share a screenshot of the existing page so I can match the design accurately?"

---

## What to Avoid

- Generic or dated UI (no Bootstrap defaults, no 2015-era table-heavy layouts)
- Inline styles for anything that belongs in a CSS rule
- Unstructured code dumps -- always explain structure first
- Arbitrary spacing or sizing values that break the 8px grid
- Overloading a page with too many features -- keep each page focused on its primary action
- Repeating icon library or font imports already loaded by base.html