---
name: apple-inspired-product-ui
description: Design or refine product interfaces with Apple-inspired hierarchy, familiarity, restraint, responsive craft, and accessibility. Use for UI/UX implementation or redesign when a calm Apple-platform feel is desired; do not use for copying Apple product trade dress or generic brand-identity work.
---

# Apple-Inspired Product UI

Create interfaces that feel intentional, trustworthy, understandable, and pleasant. Treat “Apple-inspired” as a decision discipline, not a skin: preserve the product's own identity while applying strong hierarchy, familiar behavior, adaptive layout, careful language, and exacting finish.

Before making design choices, read [references/design-language.md](references/design-language.md). Use its translation patterns and verification rubric rather than copying a particular Apple screen.

## Protect The Product First

- Read the nearest project instructions and inspect the existing interface, product language, component system, and relevant states before editing.
- Preserve domain semantics, data meaning, functional behavior, platform choice, and user-specified brand. Do not relabel or hide a concept merely because it is visually awkward.
- Resolve in this order: wrong or untrustworthy behavior, unclear meaning, inefficient interaction, then visual finish. A beautiful interface that obscures truth is a regression.
- If the design depends on domain judgment that cannot be recovered from the project, preserve the exact state and ask for the decision instead of guessing.

## Design From Intention

Identify the interface's primary job and the feeling it should reinforce, such as calm confidence, momentum, focus, or safety. Then make the primary content and next action obvious without explanation.

Use these principles as tradeoff tools:

- Purpose: every visible element earns the time and attention it asks for.
- Agency: people can choose, inspect, undo, and recover without being trapped in a prescribed path.
- Responsibility: permissions, destructive actions, uncertainty, and data use are clear at the moment they matter.
- Familiarity: conventional controls look and behave conventionally; equivalent elements behave consistently.
- Flexibility: the interface adapts to window size, input method, appearance, content length, and accessibility preferences.
- Simplicity: remove friction and redundancy, but retain context that helps people decide. Simplicity is not visual emptiness.
- Craft: wording, alignment, focus, motion, loading, empty, error, and edge states receive the same care as the happy path.
- Delight: aim for the intended emotional result through the whole experience, not ornamental effects.

## Restructure Before Styling

Prefer this reading order when it matches the product: essential context, primary content or input, primary action, immediate options, advanced configuration, then results or secondary detail.

- Give one action clear visual priority. Keep secondary actions available but quieter; distinguish destructive actions by meaning, not drama.
- Group controls by the user's mental model, not the data model. Put advanced or infrequent choices in a labeled disclosure while preserving their current state.
- Choose controls by behavior: segmented choices for a small mutually exclusive set, switches for immediate binary settings, checkboxes for selection, sliders for bounded values with an exact readout, and text or number fields for open-ended precision.
- Summarize dense results before exposing full detail. Keep semantic tables and expert data available; allow local scrolling when density is intrinsic.
- Use plain, concise labels. Keep necessary domain terms and add contextual help near them instead of inventing vague friendly language.

## Build A Coherent System

- Reuse the project's design system where one exists. Otherwise establish a small semantic token layer for surfaces, text hierarchy, accent, borders, radii, spacing, focus, motion, and light/dark appearances.
- Separate background, content, and functional chrome. Use translucency or blur only when it clarifies a real layer relationship; keep the content layer stable and legible.
- Establish hierarchy mostly through order, spacing, alignment, weight, and contrast. Avoid solving every distinction with another border, card, color, or shadow.
- Prefer system or highly legible typography, few type families, moderate weights, and type that scales without truncating essential meaning.
- Recompose at narrow widths instead of proportionally shrinking desktop UI. Keep touch targets comfortable, keyboard focus visible, content zoomable, and intentional data regions scrollable without causing page-level horizontal overflow.
- Use motion to explain state change or acknowledge interaction. Keep it brief and interruptible, and honor reduced-motion preferences.

## Implement In The Existing Stack

Work within the product's current framework and component conventions unless the user requests a migration. Preserve behavior and settings while changing presentation. Prefer semantic native controls and HTML before custom interaction code; style the actual interactive target, not only its visual label.

Make one coherent improvement at a time and replay its affected states. Avoid a simultaneous brand rewrite, information-architecture rewrite, and component-library migration unless all are explicitly in scope.

## Verify The Experience

For browser-rendered work, use `browser-visual-qa` when it is available; otherwise use the project's real preview and browser tooling. Visual verification is part of the implementation, not an optional polish pass.

Verify the primary viewport plus the smallest useful adjacent state set:

- desktop or product-default width;
- the narrow layout and both sides of important breakpoints;
- relevant empty, populated, loading, error, disabled, expanded, hover, focus, and selected states;
- light and dark appearances when supported;
- long labels, large values, dense data, and scrolling or clipping behavior;
- console errors and warnings, keyboard access, target geometry, reduced motion, and page-level overflow.

Use screenshots for composition and DOM bounds or platform inspectors for exact geometry. Exercise the changed interaction rather than inferring it from markup. Distinguish automated checks, local visual-fixture checks, and live-browser checks in the handoff, and state any unverified gap plainly.

## Finish Cleanly

Leave the product with a coherent implemented improvement, verification evidence, and concise reasons for non-obvious decisions. Do not introduce Apple logos, copy proprietary product layouts, or erase the product's own taste. The result should feel considered because it works beautifully, not because it impersonates Apple.
