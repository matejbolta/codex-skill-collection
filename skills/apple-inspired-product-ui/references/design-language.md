# Apple-Inspired Design Language

Use this reference when designing, implementing, or reviewing an interface with the skill. It translates Apple's design principles into project-agnostic product decisions. It is not a component library or a license to reproduce an Apple product.

## The Quality Order

Apply improvements in this order:

1. Correctness and trust: results, state, permissions, destructive behavior, and recovery are truthful.
2. Comprehension: hierarchy, words, relationships, feedback, and uncertainty are clear.
3. Efficiency: the common path is direct while expert capability remains reachable.
4. Accessibility and adaptation: the experience works across people, inputs, sizes, content, and appearances.
5. Aesthetic craft: material, typography, color, spacing, motion, and detail reinforce the product's intended feeling.

Later layers must not weaken earlier ones.

## Share Principles, Not Platform Anatomy

Apple platforms share purpose, agency, responsibility, familiarity, flexibility, simplicity, craft, and delight. They do not share one universal screen composition.

The current HIG also frames the visual system through three connected ideas:

- **Hierarchy:** functional controls and chrome must remain distinct from the content they operate on. Emphasis follows task importance rather than ornamental contrast.
- **Harmony:** shape, insets, material, type, and motion relate to one another and to the containing device or window. Concentric geometry is a consequence of related containers, not a command to round every object.
- **Consistency:** standard components preserve familiar anatomy and continuously adapt across sizes, displays, appearances, inputs, and accessibility settings. Consistency is behavioral before it is visual.

| Dimension | macOS | iPhone/iOS |
| --- | --- | --- |
| Primary context | User-arranged workspace, often several apps and windows | Personal handheld scene, often one immediate task amid interruptions |
| Dominant input | Precise pointer plus physical keyboard | Direct touch, virtual keyboard, voice, and device capabilities |
| Navigation | Windows, menu commands, sidebar/list/detail, inspectors | Stable top-level tabs, navigation stack, sheets for scoped work |
| Command model | Complete menu bar plus frequent toolbar subset and shortcuts | Visible current-view actions plus compact secondary menus |
| Density | Comfortable information density for sustained work | Focused content and forgiving touch targets for a smaller display |
| Personalization | Window arrangement, panes, toolbar, shortcuts, app settings | Appearance, accessibility, content and notification choices, task-relevant settings |
| Modality | Prefer modeless panes, inspectors, and separate windows | Use scoped sheets or full-screen flows, with a clear return to the parent |
| Adaptation | Resizable windows, multiple displays, active/inactive states | Safe areas, text size, keyboard, orientation, and dynamically available scene size |

For Mac-specific composition, controls, Settings, and verification, read [macos-product-language.md](macos-product-language.md). For iPhone-specific navigation, reach, lists, sheets, permissions, and adaptation, read [iphone-ios-product-language.md](iphone-ios-product-language.md). Do not approve a cross-platform design merely because the colors and corner radii match.

## Start With A Product Thesis

Write a one-sentence internal thesis before styling:

> Help [person] accomplish [primary job] while feeling [intended emotion].

Use it to decide what is prominent, quiet, deferred, summarized, or removed. If an element does not support the job, necessary context, trust, or recovery, challenge its place.

Do not confuse “few elements” with simplicity. A short explanation, progress indicator, comparison, or undo action can reduce cognitive work even though it adds UI.

Pair the thesis with a preservation contract: list the product terms, data meaning, defaults, persisted state, platform conventions, brand signals, and safety behavior that the redesign must not alter. Visual work can expose a logic problem, but it must not silently fix product logic outside the requested scope.

## Establish The Reading Order

People should be able to answer three questions quickly:

1. What deserves my attention?
2. What can I do here?
3. What happened after I acted?

Build the reading order with semantic structure first, then reinforce it through spacing, alignment, type, and contrast. The most important content generally appears earlier in reading order. Keep repeated actions and navigation in stable positions.

For task-oriented tools, a useful default is:

1. compact identity and context;
2. primary input or content;
3. primary action and immediate status;
4. common configuration;
5. advanced configuration in a disclosure;
6. result summary;
7. detailed or expert views.

Change this sequence when the actual task demands it; never force the template over domain logic.

## Translate Behavior Into Familiar Controls

| Need | Prefer | Avoid |
| --- | --- | --- |
| Navigate to a different place | A link or navigation control with a destination | A button styled like a link with no navigation semantics |
| Perform an action in the current context | A button named for the result | A link or vague label such as “Continue” when the result is consequential |
| Choose one of 2–5 short peers | Segmented control or radio group | A dropdown that hides all options |
| Toggle an immediate setting | Switch with a persistent label | An ambiguous icon-only toggle |
| Select items for a later action | Checkbox | A switch that implies immediate effect |
| Adjust a bounded continuum | Slider plus exact current value | A tiny number field with undiscoverable limits |
| Enter a precise or open-ended value | Number/text field with constraints | A slider that cannot express precision |
| Reveal infrequent complexity | Clearly labeled disclosure | Hiding the primary path in a generic menu |
| Explain specialized terminology | Nearby contextual help | Replacing exact domain language with vague copy |
| Compare an optimized result | Summary plus baseline/delta and explanation | Showing a changed number without provenance |
| Present dense expert data | Summary, semantic table, optional compact view | Flattening everything into decorative cards |
| Confirm a consequential destructive action | Specific action name, consequence, and safe cancel; offer undo when truthful | Generic “Are you sure?”, red decoration without meaning, or a false promise of reversibility |

A control's visual footprint and actual hit target must agree. Use the native element across the full visible target when possible. Keep keyboard focus obvious and labels programmatically associated.

Decide whether a change is immediate or deferred before choosing the control. Immediate settings need visible feedback and truthful persistence state. Deferred edits need an explicit apply/save action, dirty-state handling, and a safe way to cancel without implying that changes already took effect.

## Use A Three-Layer Surface Model

Think in layers:

1. Background establishes environment and broad separation.
2. Content contains the product's information and work.
3. Functional chrome contains navigation, transient controls, and persistent actions above content.

Use opaque or standard translucent surfaces for content. Use stronger translucency, blur, or glass only when a functional layer genuinely floats over visible content and the effect preserves contrast. Never add blur merely because it looks “Apple-like.” Excess material effects collapse hierarchy and make the interface feel synthetic.

Use a small radius family with related geometry. Outer containers generally have larger radii than nested controls, and inset spacing should make the curves feel concentric. A practical system might have small, control, panel, and container radii rather than a different value for every element.

Prefer subtle boundaries:

- whitespace and background shift before a border;
- a low-contrast border before a heavy shadow;
- one purposeful elevation level before many stacked shadows.

## Create Hierarchy With Type And Space

Prefer the platform system stack or the product's established legible typeface. Use one text family and, only when useful, one data or code family. Establish roles such as title, section label, body, control label, secondary explanation, and numeric result.

- Use size and weight together sparingly; avoid thin weights for small text.
- Use muted color only for genuinely secondary content, never required instructions or state.
- Keep line lengths comfortable and allow text to wrap before truncating meaning.
- Let text scaling reflow the layout. Stacked arrangements are often more robust than squeezing multiple labels into a row.
- Use uppercase and letter spacing only for short navigational or section cues, not paragraphs.

Spacing should reveal relationships. Use tighter gaps inside a group, larger gaps between groups, and consistent insets for comparable surfaces. If a screen feels busy, first remove unnecessary boundaries and repair spacing before muting everything.

## Write For Recognition And Trust

Preserve the product's established voice and exact domain terms. Improve labels by making the result recognizable, not by making every phrase casual.

- Name actions for what they do: “Export CSV” is clearer than “Continue.”
- Put the label beside the value or control it explains; avoid placeholder-only labels.
- State errors in terms of what happened, what remains safe, and the next available recovery step.
- Distinguish estimates, cached values, partial results, and generated suggestions from authoritative facts.
- When a result changes because of an optimization, filter, or model, retain the baseline, delta, units, and relevant provenance.
- Use icon-only actions only when the symbol is conventional in this context and an accessible name remains available.

## Treat Color As Meaning

Define semantic color tokens such as background, content surface, elevated chrome, primary text, secondary text, separator, accent, positive, warning, destructive, focus, and selection. Give light and dark appearances independent values; do not mechanically invert colors.

Use the accent for primary action, selection, focus, or meaningful data emphasis. When everything is accented, nothing is primary. Do not communicate status by color alone.

Test text and control contrast in actual rendered states, including transparency over changing content, hover, disabled, focus, selected, and increased-contrast settings where relevant.

## Make Layout Adapt, Not Shrink

Design around content and input constraints rather than device-name breakpoints.

- Preserve the primary task and action at every width.
- Change multi-column control groups to one column when labels or targets become cramped.
- Let bounded peer choices scroll locally only when wrapping would destroy their relationship; ensure the selected item remains visible.
- Keep wide data tables semantic and locally scrollable. Consider sticky identifiers or a compact companion view when the first columns provide context.
- Avoid page-level horizontal overflow. Treat overflow inside an intentional data region differently from accidental clipping.
- Check both sides of each meaningful breakpoint and at least one width between major layouts.
- Test extreme content: long localized labels, large numbers, empty values, many rows, validation copy, and browser zoom.

For a native Apple interface, follow the current platform metrics: Apple's accessibility guidance lists 44×44 points as the default iOS/iPadOS control size and 28×28 points as the default macOS size, with 28×28 and 20×20 points respectively as minimums. Treat minimums as exceptional lower bounds, not goals. For a touch-oriented web surface, a 44×44 CSS-pixel target is a useful baseline when the project has no stronger standard. For pointer-dominant surfaces, retain adequate separation and visible focus. Prefer the more forgiving target when one responsive product genuinely serves both inputs.

Use the project's declared accessibility target. When none exists, state the baseline chosen rather than silently assuming conformance; for a public web product, WCAG 2.2 AA is a practical minimum target. Verify rendered contrast, keyboard operation, focus order and visibility, labels and roles, zoom/reflow, text alternatives, and reduced motion in proportion to the changed surface. Do not claim conformance from linting alone.

## Use Motion As Feedback

Motion should preserve spatial understanding, acknowledge interaction, reveal state change, or connect cause and effect.

- Prefer short, calm transitions for state changes.
- Avoid perpetual, decorative, or large peripheral motion.
- Do not make a person wait for an animation before acting.
- Keep interaction responsive when interrupted or repeated.
- Honor reduced-motion settings; substitute fades or immediate changes when movement is not essential.
- Verify the no-motion experience rather than merely including a media query.

Delight comes from responsiveness, confidence, and a few product-specific details. It does not require bounce, confetti, glow, or glass.

## Design The Whole State Machine

The interface is not only its populated default. Identify and deliberately handle the states that can occur:

- first use and empty;
- editing and dirty;
- loading, progress, and cancellation;
- success and confirmation;
- partial data and stale data;
- validation and recoverable error;
- unavailable, disabled, and permission blocked;
- destructive confirmation and undo;
- expanded, selected, hover, active, and keyboard focus;
- offline or retry, when the product can encounter them.

Show enough status to maintain agency. Preserve input across recoverable failures. Avoid blank screens, unexplained disabled controls, and success messages that do not say what changed.

## Verification Rubric

Review the rendered product, not only the source.

### Purpose And Hierarchy

- Is the primary job obvious in the first viewport?
- Is there one visually primary next action?
- Does secondary configuration remain discoverable without competing?
- Does the result explain itself, including comparisons or uncertainty?
- Can the primary journey be completed end to end without relying on hidden context?

### Familiarity And Agency

- Do control types match their behavior?
- Do equivalent controls behave consistently?
- Can people undo, cancel, recover, or inspect before consequential actions?
- Are labels and feedback concise and specific?
- Are immediate and deferred changes distinguishable, with truthful persistence feedback?

### Adaptation And Accessibility

- Do narrow layouts recompose cleanly?
- Are text scaling, keyboard order, visible focus, touch targets, labels, contrast, and reduced motion verified?
- Are long content and dense data readable without accidental clipping or page overflow?
- Do light and dark appearances each preserve hierarchy?

### Craft

- Are alignments and spacing systematic rather than approximate?
- Are surfaces and materials expressing real layers?
- Are loading, empty, error, expanded, and interaction states finished?
- Are scrollbars, sticky regions, dialogs, and focus rings visually and behaviorally correct?
- Is the browser console clean while the changed interaction is exercised?

Capture screenshots at meaningful states and use DOM bounds or platform inspectors for exact target size, overflow, alignment, and sticky behavior. A code review or automated test is not visual verification.

## Common Failure Modes

- “Apple-like” becomes a monochrome clone with rounded rectangles everywhere.
- Glass appears on every surface, so content and chrome become indistinguishable.
- Advanced capability is removed instead of progressively disclosed.
- Icons replace words even where the action is unfamiliar.
- Tiny, low-contrast typography is mistaken for elegance.
- Desktop UI is merely squeezed onto mobile.
- The visual label is large but the actual input remains a tiny target.
- Animation decorates the interface without communicating state.
- A polished happy path hides weak loading, error, focus, or empty states.
- The redesign changes data meaning, defaults, or persisted settings.

## First-Party Anchors

Use these as evolving primary references, not as templates to copy:

- [Apple Human Interface Guidelines: Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Principles of great design, WWDC26](https://developer.apple.com/videos/play/wwdc2026/250/)
- [Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Windows](https://developer.apple.com/design/human-interface-guidelines/windows)
- [Settings](https://developer.apple.com/design/human-interface-guidelines/settings)
- [Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- [Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [W3C Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)
