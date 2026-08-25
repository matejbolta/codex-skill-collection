---
name: apple-inspired-product-ui
description: Review, specify, or refine macOS, iPhone/iOS, or cross-platform product interfaces with Apple-inspired hierarchy, platform-native behavior, restraint, adaptive craft, and accessibility. Use when Apple-platform design discipline or a Mac- or iPhone-appropriate interaction model is desired; do not use to copy Apple trade dress or for generic brand-identity work.
---

# Apple-Inspired Product UI

Create interfaces that feel intentional, trustworthy, understandable, and pleasant. Treat “Apple-inspired” as a decision discipline, not a skin: preserve the product's own identity while applying strong hierarchy, familiar behavior, adaptive layout, careful language, and exacting finish.

Before evaluating or making design choices:

1. Read [references/design-language.md](references/design-language.md) for the shared philosophy and quality order.
2. Identify the actual target environment and read the matching platform reference:
   - [references/macos-product-language.md](references/macos-product-language.md) for native Mac apps, Mac-first desktop products, or a request explicitly about macOS identity.
   - [references/iphone-ios-product-language.md](references/iphone-ios-product-language.md) for native iPhone apps, phone-first products, or a request explicitly about iOS identity.
   - Read both for a cross-platform product. Share concepts and data, but specify each platform's composition and behavior separately.
3. Read [references/research-foundations.md](references/research-foundations.md) when the request asks for evidence or rationale, concerns settings, accessibility, reach, modality, window management, or introduces a nonstandard interaction.

Use the references as decision tools, not as templates for copying a particular Apple screen.

## Select The Requested Mode

- **Review:** inspect the rendered experience and relevant source, then report prioritized findings with evidence. Do not edit merely because an improvement is apparent.
- **Design or specification:** define the intended behavior, hierarchy, states, and acceptance criteria. Produce implementation-ready decisions without implying that code was changed.
- **Implementation:** inspect the current experience, make only the requested changes in the existing stack, and verify the affected journey and adjacent states.

Honor the narrowest mode supported by the request. If the user asks for both a review and fixes, establish the baseline first and keep the review findings traceable to the implemented changes.

## Protect The Product First

- Read the nearest project instructions and inspect the existing interface, product language, component system, and relevant states before editing.
- Preserve domain semantics, data meaning, functional behavior, platform choice, and user-specified brand. Do not relabel or hide a concept merely because it is visually awkward.
- Treat defaults, calculations, persisted settings, permissions, and destructive behavior as product logic. Do not change them as a side effect of visual simplification.
- Resolve in this order: wrong or untrustworthy behavior, unclear meaning, inefficient interaction, then visual finish. A beautiful interface that obscures truth is a regression.
- If the design depends on domain judgment that cannot be recovered from the project, preserve the exact state and ask for the decision instead of guessing.

## Set The Platform Contract

Do not start from a generic responsive canvas. Record the target platform, input methods, window or scene behavior, content density, navigation model, and system capabilities before restructuring.

- **macOS is a user-arranged workspace.** Windows are movable and resizable units of work; the menu bar is the complete command map; toolbars contain frequent commands; sidebars navigate broad areas; inspectors edit contextual properties. Pointer precision, keyboard acceleration, multiwindow work, and personalization are core behavior, not desktop decoration.
- **iPhone is a personal, handheld, touch-first environment.** Content and the current task dominate; a navigation stack expresses depth; a tab bar switches stable top-level areas; sheets contain scoped work; reachable controls, safe areas, Dynamic Type, permissions in context, and interruption-resistant state are core behavior.
- **A cross-platform product shares meaning, not anatomy.** Preserve terminology, data, account state, and the conceptual hierarchy. Do not force identical control placement, density, navigation, or modality onto Mac and iPhone.
- **A web product may borrow the discipline without impersonating the operating system.** Use semantic web controls and the browser's behavior. Do not draw fake traffic-light controls, a fake macOS menu bar, or a pixel copy of iOS Settings.

## Design From Intention

Before restructuring, form a compact design contract from evidence in the request and product:

- the primary person, job, and next action;
- the feeling the experience should reinforce, such as calm confidence, momentum, focus, or safety;
- semantics, terminology, brand cues, platform conventions, and states that must be preserved;
- the observable journey and evidence that will show the change succeeded.

Keep this internal unless a design rationale or specification is part of the deliverable. Use it to make the primary content and next action obvious without explanation.

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

Place each decision in its native home:

- On Mac, distinguish app commands, view commands, document settings, contextual properties, and durable app settings before choosing a toolbar item, menu command, inspector, inline control, or Settings pane.
- On iPhone, distinguish top-level navigation, hierarchical navigation, an action on current content, a transient choice, a scoped task, and a durable setting before choosing a tab, navigation control, toolbar action, menu, sheet, or settings row.
- Determine whether every setting applies immediately or is staged. Immediate changes need direct feedback and truthful persistence; staged changes need explicit Apply or Save, dirty-state handling, and a safe Cancel path.
- Keep permissions out of generic onboarding when the request can be made at the moment a feature clearly needs access.

## Build A Coherent System

- Reuse the project's design system where one exists. Otherwise establish a small semantic token layer for surfaces, text hierarchy, accent, borders, radii, spacing, focus, motion, and light/dark appearances.
- Separate background, content, and functional chrome. Use translucency or blur only when it clarifies a real layer relationship; keep the content layer stable and legible.
- Establish hierarchy mostly through order, spacing, alignment, weight, and contrast. Avoid solving every distinction with another border, card, color, or shadow.
- Prefer system or highly legible typography, few type families, moderate weights, and type that scales without truncating essential meaning.
- Recompose at narrow widths instead of proportionally shrinking desktop UI. Keep touch targets comfortable, keyboard focus visible, content zoomable, and intentional data regions scrollable without causing page-level horizontal overflow.
- Use motion to explain state change or acknowledge interaction. Keep it brief and interruptible, and honor reduced-motion preferences.

## Implement In The Existing Stack

Work within the product's current framework and component conventions unless the user requests a migration. Preserve behavior and settings while changing presentation. On the web, prefer semantic HTML and native controls before custom interaction code. In native products, prefer the established platform framework, standard control behavior, and platform accessibility semantics. Style the actual interactive target, not only its visual label.

Make one coherent improvement at a time and replay its affected states. Avoid a simultaneous brand rewrite, information-architecture rewrite, and component-library migration unless all are explicitly in scope.

Prefer system components because their value is behavioral: they carry platform metrics, keyboard and gesture conventions, accessibility semantics, state appearance, material treatment, and adaptation. A custom control must justify the behavior it adds and reproduce every relevant input, state, and accessibility path; visual resemblance alone is insufficient.

## Verify The Experience

For browser-rendered work, use `browser-visual-qa` when it is available; otherwise use the project's real preview and browser tooling. For native work, use the closest real preview, simulator, or target device available. Rendered verification is part of implementation, not an optional polish pass.

Verify the primary viewport plus the smallest useful adjacent state set:

- desktop or product-default width;
- the narrow layout and both sides of important breakpoints;
- relevant empty, populated, loading, error, disabled, expanded, hover, focus, and selected states;
- light and dark appearances when supported;
- long labels, large values, dense data, and scrolling or clipping behavior;
- console errors and warnings, keyboard access, target geometry, reduced motion, and page-level overflow.

Add platform-specific verification:

- **macOS:** smallest and largest useful window sizes; active and inactive windows; toolbar overflow and customization when supported; sidebar and inspector shown and hidden; menu command presence, state, and shortcuts; pointer, keyboard-only, Return, Escape, context menu, drag and drop, and multiwindow state restoration.
- **iPhone/iOS:** compact and expanded available sizes rather than one device screenshot; portrait and supported landscape behavior; safe-area and keyboard avoidance; smallest and largest Dynamic Type categories in scope; left- and right-hand reach of frequent actions; tab and navigation-state preservation; sheet dismissal with dirty edits; permission allowed, denied, and later-recovery paths; VoiceOver order and custom gesture alternatives.

Replay the changed primary journey end to end. Use screenshots for composition and DOM bounds or platform inspectors for exact geometry. Exercise the changed interaction rather than inferring it from markup.

In the handoff, distinguish automated checks, rendered fixture or preview checks, and live target checks. Identify the surface, states, viewport or form factor, interaction exercised, and any unverified gap. Never claim rendered verification from source inspection alone.

## Finish Cleanly

Leave the product with a coherent implemented improvement, verification evidence, and concise reasons for non-obvious decisions. State which decisions are shared, macOS-specific, iPhone-specific, or constrained by the existing stack. Do not introduce Apple logos, copy proprietary product layouts, or erase the product's own taste. The result should feel considered because it works beautifully, not because it impersonates Apple.
