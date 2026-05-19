# Webapp

This directory contains the browser UI served by CP. It is a dependency-light
AlpineJS single-page application with no frontend build step.

For the broader map, see [`../docs/CODEMAP.md`](../docs/CODEMAP.md).

## What Belongs Here

- Browser markup and Alpine template bindings.
- UI state, hash routing, API calls, and client-side data shaping.
- CSS for page layout, tables, modals, cards, and responsive behavior.
- Static images used by the UI.

## What Does Not Belong Here

- Backend business rules.
- CP metadata SQL.
- Managed-cluster SQL.
- Security decisions that must be enforced by the API/service layer.

## Entry Points

| File | Purpose |
| --- | --- |
| `index.html` | Main UI shell, route sections, modals, and Alpine bindings. |
| `script.js` | `app()` state object, hash routing, API calls, filtering, sorting, and UI actions. |
| `style.css` | Layout, components, tables, cards, dialogs, and responsive rules. |
| `static/` | Logo, favicon, and cloud/provider images. |

## Common Pattern

Most user-facing features touch all three main files:

1. Add state and API methods in `script.js`.
2. Add or update markup in `index.html`.
3. Add focused styles in `style.css`.

Prefer explicit API calls in `script.js`; it should be easy to search for an
endpoint path and find the UI code that uses it.

## Routing

The UI uses hash-based routing controlled from `script.js`. Search for
`setView`, `handleHashRoute`, and the `view === ...` sections in `index.html`
when adding or changing a page.

## API Boundaries

The webapp may reshape API data for display, such as merging database role group
mappings into database cards. It should not duplicate backend validation or rely
on hidden assumptions that are not enforced by the API.
