---
name: browser-visual-qa
description: Visually inspect, test, and iterate on browser-rendered interfaces in a real browser. Use for UI/UX implementation or review, layout and styling changes, responsive behavior, browser-extension pages, interaction states, and local web-app visual verification; do not use for backend-only or otherwise nonvisual work.
---

# Browser Visual QA

Make browser-facing work observable. Use the project's actual rendered UI and
leave evidence that another person can reproduce.

## Choose the test surface

- Read the nearest project instructions and inspect existing development,
  preview, Storybook, fixture, screenshot, and visual-test scripts before
  inventing a new harness.
- Prefer a repository-owned visual harness or sanitized fixture when it exists.
  It usually represents extension popups, side panels, authenticated pages, and
  hard-to-reach states more safely and repeatably than a live service.
- Use a listed Browser, Chrome, or Playwright skill for real browser control. If
  `browser:control-in-app-browser` is available, read and follow it; it owns
  browser selection, browser safety, and local-page interaction. Do not replace
  real browser inspection with a visualization renderer or code-only reasoning.
- Respect an explicitly requested browser. Do not silently substitute a
  different browser surface.

## Run a tight visual loop

1. Discover the affected route, component state, build command, and start
   command. Reuse an already-running server when it is clearly the correct one.
2. For an existing UI, inspect the affected state before editing. Capture the
   route, relevant viewport, visible behavior, console state, and any important
   geometry. A screenshot is useful evidence, but measure DOM bounds when exact
   width, spacing, alignment, overflow, or breakpoint behavior matters.
3. Make only changes authorized by the user. A visual review or diagnosis does
   not authorize implementation.
4. Rebuild or reload as the project requires. Reuse the same browser tab and
   reproduce the same state so the before/after comparison is meaningful.
5. Verify the primary state plus the smallest proportional set of adjacent
   states that could regress:
   - the relevant desktop or product viewport;
   - a narrow viewport that crosses an affected breakpoint, when responsive
     behavior is in scope;
   - hover, focus, expanded, disabled, loading, empty, or error states only when
     the change can affect them;
   - scrolling, clipping, overlap, and horizontal overflow where content density
     or fixed-size surfaces make them plausible.
6. Inspect browser console errors and warnings. Exercise the changed interaction
   when it is safe, then take a fresh screenshot or DOM snapshot after the
   interaction rather than relying on the initial render.

Keep the development server and browser session alive during iteration when
practical. Reload after each relevant build instead of repeatedly rediscovering
the page.

## Keep evidence honest

Distinguish these verification levels in notes and the final response:

- **Automated:** unit, integration, type, or build checks. These do not prove
  appearance.
- **Visual fixture:** rendered local fixture or preview checked in a real
  browser. This proves the inspected fixture and viewport, not live integration.
- **Live browser:** the actual site or installed extension checked in its target
  browser. Signed-in flows and browser-internal extension pages may still need
  user-controlled verification.

Never say a UI was visually verified if only source, tests, static HTML, or a
DOM emulator was inspected. Report the routes or surfaces, states, viewports,
interactions, console result, and any remaining live-browser gap concisely.

## Safety and privacy

- Do not submit forms, purchase, publish, send messages, start games, or trigger
  another external side effect merely to test presentation. Use a fixture or
  stop before the side effect unless the user explicitly authorizes it.
- Treat signed-in captures, account data, cookies, tokens, browser profiles, and
  session markup as private. Do not add them to tracked fixtures, screenshots,
  logs, documentation, or final responses.
- If browser policy blocks a local URL or page type, do not bypass it with raw
  browser protocols, data URLs, or a different automation surface. Use an
  existing sanitized/static project fixture when allowed, or report exactly
  which visual check remains unavailable.
- Do not weaken application security, browser permissions, or production
  behavior to make visual testing easier.

When the project has no usable preview path, create the smallest reusable local
harness only if implementation is in scope. Keep it project-owned, deterministic,
free of private data, and documented by an obvious package or task command.
