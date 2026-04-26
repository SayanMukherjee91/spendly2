# Technical Plan: Profile Page Design (Step 4)

## Context

Step 4 replaces the `/profile` stub and the placeholder `/dashboard` with three purpose-built pages. The work was shaped by user feedback during implementation: expense data was split off `/profile` into dedicated pages so each URL has a single responsibility. The final shape is:

- `/dashboard` — post-login landing: welcome + summary strip + charts
- `/expenses` — read-only expense list with Month column and client-side filters
- `/profile` — account management only: update name + change password

No schema changes were needed. Chart.js (CDN) is the only new runtime dependency.

---

## Files changed

| File | Action | Key changes |
|---|---|---|
| `app.py` | edit | `datetime` import; `month_name` Jinja filter; dashboard route expanded; profile route slimmed; `/expenses` route added |
| `templates/base.html` | edit | Expenses + Profile links added to logged-in navbar block |
| `templates/dashboard.html` | rewrite | Welcome card + summary strip + monthly bar + category pie; Chart.js in `{% block head %}` and `{% block scripts %}` |
| `templates/expenses.html` | create | Expense table with Month column; month/category filter dropdowns; IIFE-wrapped JS filter logic |
| `templates/profile.html` | rewrite | Profile card (avatar, name, email, member-since) + two edit forms only |
| `static/css/style.css` | edit | Appended: profile, summary, chart, table, and filter CSS classes |

---

## `app.py` changes in detail

### Custom Jinja filter (registered once at startup)
```python
_MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
app.jinja_env.filters['month_name'] = lambda n: _MONTHS[int(n) - 1]
```
Used in `expenses.html` as `{{ e["date"][5:7] | int | month_name }}`.

### `/dashboard` route — queries added
```python
summary    # COALESCE(SUM, 0), COUNT(*)
monthly    # strftime('%Y-%m', date), SUM(amount) GROUP BY month ORDER BY month ASC
by_category # category, SUM(amount) GROUP BY category ORDER BY total DESC
```
Passes `user`, `total_spend`, `tx_count`, `avg_spend`, `monthly`, `by_category` to template.  
`avg_spend = total_spend / tx_count if tx_count else 0.0` — guards division by zero.

### `/profile` route — queries removed
Only fetches the user row and computes `member_since`. Expense aggregation queries were removed entirely.

POST dispatch on hidden `action` field:
- `update_name` — validates non-empty, `UPDATE users SET name = ?`, redirect
- `change_password` — re-fetches current hash, validates with `check_password_hash`, checks length ≥ 8, `UPDATE users SET password_hash = ?`, redirect
- On error: falls through to GET rendering with `name_error` or `pw_error` set

`member_since` computed as:
```python
dt = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S")
member_since = dt.strftime("%B %Y")
```
Wrapped in `try/except (ValueError, TypeError)` with `datetime.now()` fallback.

### `/expenses` route
```python
expense_rows  # SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC
months        # SELECT DISTINCT strftime('%Y-%m', date) … ORDER BY month DESC
categories    # SELECT DISTINCT category … ORDER BY category
```
Passes `expenses`, `months`, `categories` to template.

---

## Template details

### `dashboard.html`
- Loads `chart.js@4` in `{% block head %}`
- `{% block scripts %}` wraps chart init in plain `if (monthly.length)` guard (not IIFE needed since no early `return` at top level)
- Monthly chart: `type: 'bar'`, `borderRadius: 4`, y-axis ticks prefixed with `₹`
- Category chart: `type: 'pie'` (not doughnut), legend at bottom, tooltip shows `₹XX.XX`
- Both charts use `maintainAspectRatio: false` inside a `.chart-canvas-wrap` div (`height: 280px`) so Chart.js sizes correctly
- Empty state shown when `monthly` list is empty (`{% if monthly %}`)

### `expenses.html`
- Table columns: Date · Month · Category · Description · Amount
- Month cell: `{{ e["date"][5:7] | int | month_name }} {{ e["date"][:4] }}` → "Apr 2026"
- Each `<tr>` carries `data-month="YYYY-MM"` and `data-category="Food"` attributes
- Filter dropdowns populated from `months` / `categories` passed by the route
- First option in both dropdowns: `<option value="">All</option>`
- JS filter logic wrapped in **IIFE** (`(function(){ … }())`) so `return` is valid as an early-exit when no expenses exist
- Month option labels re-formatted by JS at runtime: `"2026-04"` → `"Apr 2026"`
- `applyFilters()`: iterates rows, sets `display: none/""`, counts visible rows, shows/hides `#noResults` and `#clearFilters`
- **Clear** button: hidden by default; shown whenever `month || category` is truthy; resets both selects and calls `applyFilters()`

### `profile.html`
- No Chart.js, no expense queries
- Avatar: first letter of name, `.profile-avatar` (64 px circle, `--accent-light` background)
- Two-column grid (`.profile-grid`): Update Name form left, Change Password form right
- Each form posts to `/profile` with a hidden `<input name="action">` field
- Error banners use existing `.auth-error` class

### `base.html` navbar (logged-in)
```html
<a href="{{ url_for('dashboard') }}">Dashboard</a>
<a href="{{ url_for('expenses') }}">Expenses</a>
<a href="{{ url_for('profile') }}">Profile</a>
<a href="{{ url_for('logout') }}" class="nav-cta">Logout</a>
```

---

## CSS classes added to `style.css`

All use existing CSS variables — no hex literals.

| Class | Purpose |
|---|---|
| `.profile-page` | Full-width flex column container, `max-width: var(--max-width)`, `gap: 1.75rem` |
| `.profile-card`, `.expense-table-card` | White card surface: `var(--paper-card)`, border, `var(--radius-md)` |
| `.profile-header` | Flex row: avatar + text block, separated from edit grid by border-bottom |
| `.profile-avatar` | 64 px circle, `var(--accent-light)` bg, `var(--accent)` text, bold initial |
| `.profile-grid` | `grid-template-columns: 1fr 1fr; gap: 2rem` — collapses to 1 col at 900 px |
| `.summary-strip` | `grid-template-columns: repeat(3, 1fr)` — collapses to 1 col at 900 px |
| `.summary-card` | Card surface + `.summary-label` (small caps muted) + `.summary-value` (1.75 rem bold) |
| `.chart-grid` | `grid-template-columns: 1fr 1fr` — collapses to 1 col at 900 px |
| `.chart-card` | Card surface; `h3` uses `var(--font-display)` |
| `.chart-canvas-wrap` | `position: relative; height: 280px` — gives Chart.js a bounded container |
| `.expense-table` | `border-collapse: collapse`; `th` uppercase, muted, border-bottom; `td` border-bottom soft; last column right-aligned |
| `.category-badge` | Pill: `var(--accent-light)` bg, `var(--accent)` text |
| `.empty-state` | Centred card with icon, title, body in muted colours |
| `.expense-list-header` | Flex row: heading left, filters right, wraps on small screens |
| `.expense-filters` | Flex row of selects + clear button |
| `.filter-select` | Styled `<select>`: border, `var(--radius-sm)`, focus border `var(--accent)` |
| `.filter-clear` | Small ghost button (reuses `.btn-ghost` sizing override) |
| `.filter-no-results` | Centred muted paragraph shown when filter returns zero rows |

---

## Edge cases

| Scenario | Handling |
|---|---|
| User with zero expenses on dashboard | `{% if monthly %}` shows empty state; charts not rendered; no JS errors |
| User with zero expenses on expenses page | `{% if expenses %}` shows empty state; filter dropdowns not rendered; IIFE exits early via `if (!monthSelect) return` |
| Division by zero in `avg_spend` | `total / tx_count if tx_count else 0.0` in Python |
| `created_at` format variants | `try/except (ValueError, TypeError)` falls back to `datetime.now()` |
| Failed profile POST | Error variable set, both forms re-rendered; other form's fields unaffected |
| Successful profile POST + browser refresh | POST-redirect-GET pattern; Ctrl-R reloads GET, no resubmit prompt |
| NULL description in expense row | Template: `{{ e["description"] or "—" }}` |
| Filter combination with zero matches | `applyFilters()` detects `visible === 0`, shows `#noResults` paragraph |

---

## Verification checklist

1. `python app.py` starts without errors at `http://127.0.0.1:5001`
2. Logged-out `/dashboard`, `/expenses`, `/profile` all redirect to `/login`
3. Log in as `demo@spendly.com / demo123` — dashboard shows correct name, ₹316.49 total, 8 transactions, ≈₹39.56 avg
4. Monthly bar chart renders April 2026 bar(s); category pie chart shows 7 slices
5. Expenses page lists all 8 rows; Month column shows "Apr 2026"
6. Month dropdown → select "Apr 2026" → only April rows visible; select "All" → all rows restored
7. Category dropdown → select "Food" → only Food rows visible; combined with month filter → AND logic
8. Clear button resets both filters
9. Log in as `siddharth.pandey536@gmail.com / password123` (no expenses) — dashboard shows empty state; expenses page shows empty state; profile page still shows account forms
10. Profile: update name → new name shown on reload; blank name → inline error
11. Profile: correct current password + valid new → redirect → old password no longer works
12. Profile: wrong current password → "Current password is incorrect."; new password < 8 chars → length error
13. After successful profile update, Ctrl-R does not show "Resubmit form" prompt

---

## Out of scope

- Account deletion / data export
- Email change
- Avatar image upload (initial letter only)
- Server-side expense filtering (client-side JS covers the need)
- Date-range filtering on dashboard charts (all-time view only)
- Automated tests (no pytest infra in repo yet)
