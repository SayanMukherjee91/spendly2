# Spec: Profile Page Design (Step 4)

## Overview
This step delivers three distinct pages that together replace the single `/profile` stub and the placeholder `/dashboard`:

1. **Dashboard** (`/dashboard`) — post-login landing page. Shows a personalised welcome card, a three-stat summary strip, a monthly column chart and a category pie chart. Charts are rendered with Chart.js (CDN). Empty state shown when the user has no expenses.
2. **Expenses** (`/expenses`) — read-only flat list of all the user's expenses with a Month column and client-side filter dropdowns for month and category. No charts, no account forms.
3. **Profile** (`/profile`) — account management only. Update display name and change password via two independent side-by-side forms. No expense data.

The navbar for logged-in users gains two new links: **Expenses** and **Profile**, giving the order: Dashboard · Expenses · Profile · Logout.

## Depends on
- **Step 1** — `database/db.py` must be complete (`users` table, `expenses` table, `get_db()`)
- **Step 2** — Registration must be complete (session, `/dashboard`)
- **Step 3** — Login/logout must be complete (session guards, navbar state)

## Routes

| Method | Path | Description | Access |
|---|---|---|---|
| `GET` | `/dashboard` | Summary strip + monthly column chart + category pie chart | logged-in |
| `GET` | `/expenses` | Full expense list with Month column and filter dropdowns | logged-in |
| `GET` | `/profile` | Account details + edit forms | logged-in |
| `POST` | `/profile` | Process name update or password change; redirect back | logged-in |

## Database changes
No database changes. All data comes from existing tables:
- `users`: `id`, `name`, `email`, `password_hash`, `created_at`
- `expenses`: `id`, `user_id`, `amount`, `category`, `date`, `description`, `created_at`

## Templates

| Action | File | Content |
|---|---|---|
| Modify | `templates/base.html` | Add Expenses + Profile nav links in logged-in block |
| Modify | `templates/dashboard.html` | Welcome card, summary strip, monthly bar chart, category pie chart |
| Create | `templates/expenses.html` | Expense table with Month column + filter dropdowns |
| Modify | `templates/profile.html` | Account card (avatar + info) + two edit forms |

## Files changed

- `app.py` — `from datetime import datetime` import; `month_name` Jinja filter; updated dashboard, profile, expenses routes
- `templates/base.html` — Expenses + Profile nav links
- `templates/dashboard.html` — full dashboard with charts
- `templates/expenses.html` — created: table + filters
- `templates/profile.html` — account management only (expense section removed)
- `static/css/style.css` — appended: `.profile-page`, `.profile-card`, `.profile-header`, `.profile-avatar`, `.profile-grid`, `.summary-strip`, `.summary-card`, `.chart-grid`, `.chart-card`, `.expense-table-card`, `.expense-table`, `.empty-state`, `.expense-list-header`, `.expense-filters`, `.filter-select`, `.filter-clear`, `.filter-no-results`

## New dependencies
No new pip dependencies. Chart.js loaded from CDN in `dashboard.html`:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
```

## Data each route passes to its template

### `GET /dashboard`
| Variable | Type | Description |
|---|---|---|
| `user` | `sqlite3.Row` | Full user row |
| `total_spend` | `float` | `SUM(amount)`, 0.0 if none |
| `tx_count` | `int` | `COUNT(*)` of expenses |
| `avg_spend` | `float` | `total_spend / tx_count`, 0.0 if none |
| `monthly` | `list[dict]` | `[{"month": "2026-04", "total": 316.49}, …]` oldest→newest |
| `by_category` | `list[dict]` | `[{"category": "Food", "total": 57.50}, …]` highest→lowest |

### `GET /expenses`
| Variable | Type | Description |
|---|---|---|
| `expenses` | `list[sqlite3.Row]` | All rows `ORDER BY date DESC` |
| `months` | `list[str]` | Unique `YYYY-MM` values `ORDER BY month DESC` |
| `categories` | `list[str]` | Unique category strings `ORDER BY category` |

### `GET /profile` / `POST /profile`
| Variable | Type | Description |
|---|---|---|
| `user` | `sqlite3.Row` | Full user row |
| `member_since` | `str` | `created_at` formatted as "April 2026" |
| `name_error` | `str\|None` | Error after failed name-update POST |
| `pw_error` | `str\|None` | Error after failed password-change POST |

## SQL queries

```sql
-- Dashboard: summary
SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS cnt
FROM expenses WHERE user_id = ?

-- Dashboard: monthly
SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total
FROM expenses WHERE user_id = ?
GROUP BY month ORDER BY month ASC

-- Dashboard: by category
SELECT category, SUM(amount) AS total
FROM expenses WHERE user_id = ?
GROUP BY category ORDER BY total DESC

-- Expenses: full list
SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC

-- Expenses: distinct months for dropdown
SELECT DISTINCT strftime('%Y-%m', date) AS month
FROM expenses WHERE user_id = ? ORDER BY month DESC

-- Expenses: distinct categories for dropdown
SELECT DISTINCT category FROM expenses WHERE user_id = ? ORDER BY category
```

## Template layouts

### dashboard.html
```
┌─ Welcome card ───────────────────────────────────────┐
│  [Avatar]  Welcome back, Name!  ·  email             │
└──────────────────────────────────────────────────────┘
┌─ Summary strip ──────────────────────────────────────┐
│  [ Total Spent ]  [ Transactions ]  [ Avg / Tx ]     │
└──────────────────────────────────────────────────────┘
┌─ Charts (hidden if no expenses) ─────────────────────┐
│  Monthly Spend (bar)  │  By Category (pie)           │
└──────────────────────────────────────────────────────┘
```

### expenses.html
```
┌─ All Expenses ──────────────────── [Month ▾] [Category ▾] [Clear] ┐
│  Date | Month    | Category | Description | Amount                 │
│  2026-04-12 | Apr 2026 | Shopping | New shoes | ₹60.00            │
│  …                                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### profile.html
```
┌─ Profile card ───────────────────────────────────────┐
│  [Avatar]  Name  ·  Email  ·  Member since Apr 2026  │
│  ────────────────────────────────────────────────    │
│  [Update Name form]   │   [Change Password form]     │
└──────────────────────────────────────────────────────┘
```

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()`
- Parameterised queries only — never interpolate user input into SQL
- Passwords hashed with `werkzeug.security.generate_password_hash`; verified with `check_password_hash`
- Use CSS variables — never hardcode hex values in any template or stylesheet
- All templates extend `base.html`
- Session guard on all three routes: redirect to `url_for('login')` if session missing
- Profile POST-redirect-GET: successful name/password update always redirects; failed POST re-renders with the error variable set
- `month_name` custom Jinja filter registered in `app.py`: converts integer month `n` → 3-letter abbreviation (`_MONTHS[int(n)-1]`)
- Expense filter JS wrapped in an IIFE (`(function(){ … }())`) so `return` is valid as an early-exit guard
- Month dropdown options formatted as "Apr 2026" by client-side JS (raw value stored as `YYYY-MM` for `data-month` comparison)
- Both filter dropdowns start with an "All" option (`value=""`) that shows all rows
- "Clear" button is hidden by default; shown only when at least one filter is active
- Chart colours read from CSS variables at runtime via `getComputedStyle`; fallback hex literals only as last resort
- `avg_spend` guarded against division-by-zero: `total / tx_count if tx_count else 0.0`

## Definition of done
- [ ] `/dashboard`, `/expenses`, `/profile` all redirect to `/login` when accessed logged-out
- [ ] Logged-in navbar shows: Dashboard · Expenses · Profile · Logout
- [ ] Dashboard welcome card shows correct name and email for every registered user
- [ ] Dashboard summary strip shows correct total, transaction count, and average with ₹ prefix
- [ ] Dashboard monthly column (bar) chart renders with correct month labels ("Apr 2026") and amounts
- [ ] Dashboard category pie chart renders with correct slices and legend
- [ ] Dashboard shows empty state when user has no expenses; charts are not rendered
- [ ] Expenses page shows full list with Date, Month, Category, Description, Amount columns
- [ ] Month column displays "Apr 2026" format (not raw "2026-04")
- [ ] Month dropdown lists all unique months; selecting one hides non-matching rows instantly
- [ ] Category dropdown lists all unique categories; selecting one hides non-matching rows instantly
- [ ] Combined month + category filter applies AND logic
- [ ] "All" option in each dropdown restores full list
- [ ] "Clear" button appears when any filter is active and resets both dropdowns
- [ ] "No expenses match" message shown when filter combination has zero results
- [ ] Profile page shows avatar initial, name, email, member-since date
- [ ] Update name form: blank name shows inline error; valid name updates DB and redirects
- [ ] Change password form: wrong current password shows inline error; short new password shows inline error; correct inputs update hash and redirect
- [ ] After any successful profile POST, page refresh does not resubmit the form
