# iPhone And iOS Product Language

Use this reference for native iPhone software and phone-first products whose user explicitly wants iOS design discipline. It describes the interaction identity behind iPhone, not a recipe for reproducing Settings, Photos, or another Apple app.

## The iPhone Promise

A good iPhone app feels immediate, personal, and dependable in a changing physical context.

- The current content or task dominates the screen.
- The navigation model remains simple enough to recover after an interruption.
- Primary actions are comfortable to reach and forgiving to use with touch.
- Secondary capability stays discoverable without crowding the first view.
- Layout adapts to available space, safe areas, text size, appearance, keyboard, and system UI.
- Requests for personal data occur when their purpose is understandable.
- Standard gestures accelerate interaction but never become the only path to an important action.
- State survives app switching, transient failures, and accidental dismissal where the product can safely preserve it.

iPhone is not merely a narrow canvas. It is often used one-handed, while moving, for short bursts, with imprecise touch and frequent changes of attention.

## Start With The Information Architecture

Choose navigation from the meaning of the destination.

| Need | Prefer | Test |
| --- | --- | --- |
| Switch among stable top-level app areas | Tab bar | Would each destination still make sense as a first destination after launch? |
| Move deeper into related content | Navigation stack | Can Back retrace the exact hierarchy without inventing a second close behavior? |
| Perform a short scoped task and return | Sheet | Is the parent context still meaningful and is the exit path safe? |
| Perform a prolonged, immersive, or multistep task | Full-screen presentation or dedicated navigation flow | Would a partial-height sheet feel cramped or create nested sheets? |
| Reveal a small set of secondary commands | Menu | Are these commands related to the current context and safe to invoke from a compact list? |
| Choose among consequences of an action just initiated | Action sheet or confirmation dialog | Did the person intentionally begin the action that now needs clarification? |
| Warn about an unexpected problem or uncommon irreversible risk | Alert | Is interruption truly required now? |
| Change a value needed for the current task | Inline control or row | Would leaving the task to visit Settings break context? |
| Change a durable app preference | Focused in-app settings area or an appropriate system Settings destination | Does the value persist beyond the current task and is it understandable as a preference? |

Do not solve weak hierarchy with more modal layers. A person should be able to describe where they are, how they arrived, and how to leave.

## Use Tabs For Top-Level Structure

- Give tabs stable destinations, not actions such as Add, Scan, or Play.
- Keep the tab bar available while people move within top-level areas so location remains clear. Let each tab preserve its own navigation state.
- Use a small, legible set of destinations with concise labels. Avoid designing around an overflow or More destination when the information architecture can be clarified.
- Keep labels and icons together unless the platform component intentionally adapts them. Use familiar symbols and stable names.
- Do not hide or disable a tab merely because its content is empty. Show the destination and explain the empty state.
- Use badges for concise, actionable status, not as decoration or a permanent anxiety signal.
- If search is a primary app-wide destination, a distinct search tab can be appropriate. If search filters one collection, keep it with that collection.

## Use A Navigation Stack For Depth

- Let the top toolbar or navigation bar orient the person with a meaningful title and standard Back behavior.
- Use the standard Back control and preserve the interactive back gesture. The gesture accelerates Back; it does not replace the visible control.
- Avoid using both Back and Close for the same hierarchy. Back retraces depth; Close dismisses a presented context.
- Keep leading navigation and trailing actions in distinct groups. Separate a primary completion action such as Done from secondary symbols or menus.
- Place only current-view actions in the toolbar. If the item changes the top-level app area, it belongs in navigation instead.
- Decide whether a large or compact title supports scanning and context; do not use a large title solely as visual decoration.
- Preserve selection, scroll position, and edited state when moving deeper and returning, within the product's privacy and freshness constraints.

## Treat The Screen As Content Plus Functional Chrome

Think from top to bottom:

1. system status and safe area;
2. navigation and orientation controls;
3. the product's content or task;
4. context-specific actions;
5. tab bar or bottom toolbar when needed;
6. home indicator, keyboard, and changing system regions.

The content layer should remain stable and legible beneath adaptive system chrome. Current glass and translucency treatments belong primarily to navigation and controls that float above content. They do not justify placing every content group on a blurred capsule.

- Respect system safe areas for interactive controls and essential information. Full-bleed visual content may extend, but its important parts and actions must remain safe.
- Keep the status bar unless an immersive media or game experience clearly benefits from hiding it.
- Inset wide buttons from the screen edge and align them with the content margins. Edge-to-edge color does not require an edge-to-edge hit shape.
- Let content scroll behind system bars only when the resulting material, contrast, and scroll-edge behavior stay readable.

## Lists, Forms, And Settings-Like Screens

iOS Settings is a strong example of row semantics, grouping, and hierarchy. It is not a universal visual template.

### Give every row one main meaning

| Row result | Trailing treatment | Behavior |
| --- | --- | --- |
| Immediate binary preference | Switch | Tapping the switch changes the value now; tapping the label may focus or explain but must not navigate unexpectedly |
| Navigate to a deeper group | Disclosure indicator | The whole row opens the next level |
| Choose one item from a list | Current value summary, then checkmark in the choice list | The row opens choices; the selected choice remains recognizable on return |
| Show detail without navigating hierarchy | Info button only when truly supplementary | The info control reveals details; the row's main action remains distinct |
| Trigger an immediate action | Clearly action-oriented label or button styling | The result is named, with confirmation only when risk warrants it |
| Enter or edit a value | Field, picker, or dedicated edit view | Scope, constraints, persistence, and keyboard behavior are clear |

Do not combine a switch, disclosure chevron, and row navigation unless each has an unambiguous independent target and the complexity is justified.

### Group for comprehension

- Group related rows by the person's goal, not the model or service that stores them.
- Use concise section headers. Use footers for consequences, privacy scope, prerequisites, or examples that genuinely help a decision.
- Put the most commonly needed and broadly understandable settings earlier. Move rare expert controls into a named subsection rather than hiding them behind a vague Advanced label.
- Keep rows scannable and let essential labels wrap under large text. A giant row full of prose is usually better as a detail view.
- Preserve a stable row order. Moving controls based on their current value makes settings harder to relocate.

### Design actual settings, not implementation knobs

1. Choose a safe, useful default.
2. Keep a choice inline when it affects only the current task.
3. Expose a durable app setting only when people can understand and value control over the outcome.
4. Use system Settings for permissions and system-managed choices, but request access at the moment of need.
5. Do not duplicate the same setting in several places unless every entry point edits one shared value and the duplication materially reduces context switching.

- For immediate settings, show the new state without an unnecessary Save button and persist it truthfully.
- For a staged form, provide explicit Save or Done, a safe Cancel path, validation, and dirty-state handling. Do not mix immediate switches and a page-wide Save button without explaining which model applies.
- If a change requires restart, sync, download, authentication, or affects other devices, state that before commitment.
- Offer Reset only at the relevant scope and explain what will and will not be reset.

## Put Touch And Reach Into The Layout

Touch input is less precise than a pointer, and the hand gripping the device limits reach.

- Use the system's 44×44-point default control target for ordinary iPhone interactions. Apple's current accessibility guidance lists 28×28 points as a minimum; treat that as an exceptional lower bound with adequate separation, not as the design target.
- Verify the hit region of the actual control. A 44-point row containing a 16-point icon fails if only the icon receives the tap.
- Keep enough distance between adjacent targets to prevent accidental activation, especially around destructive or mutually exclusive actions.
- Place frequent, time-sensitive actions in the middle or lower region when the hierarchy allows. Keep orientation, Back, and global context stable even when they remain at the top.
- Do not optimize for a mythical universal thumb zone. Hand size, grip, handedness, case, device size, posture, and motion change reach. Test both hands and support alternatives.
- Avoid placing destructive actions where an ordinary scroll, swipe, or grip adjustment can trigger them accidentally.
- Keep long-press, swipe actions, and edge gestures as accelerators. Provide a visible, accessible route to the same important result.
- Avoid custom gestures that conflict with system edges or require a specific hand, multiple fingers, or memorized motion for routine work.

## Buttons And Immediate Actions

- Give one completion action clear prominence when the view has a natural next step. Name the result: `Add Card`, `Save Route`, `Send Message`.
- Do not label a consequential action `Continue` when the result is payment, deletion, publication, or data sharing.
- Never make a destructive action the visually primary default. Use the destructive role and a deliberate confirmation only for uncommon, hard-to-recover outcomes.
- Keep secondary actions quieter but discoverable. A More menu is useful only when its reduced visibility matches the action's frequency and importance.
- Use symbol-only buttons for familiar actions such as Share, Search, or More. Add an accessibility label and verify comprehension in the product context.
- When an action is in progress, prevent duplicate submission while keeping the current state and destination clear. Preserve the button's geometry when substituting progress.
- Explain unavailable primary actions through nearby validation or requirements. An unexplained dim button forces trial and error.
- Keep persistent bottom actions above the home indicator and keyboard, and ensure they do not cover the last content or error message.

## Sheets, Action Sheets, Alerts, And Menus

These presentations all reduce visible context, so use the smallest interruption that preserves understanding.

### Sheets

- Use a sheet for a focused task closely related to the parent view.
- Present only one sheet from the main interface at a time. Close or transform the first context before presenting another; avoid sheet-on-sheet navigation.
- Choose a detent based on the content and interaction, not a preferred silhouette. The sheet must still work with large text, keyboard, errors, and expanded content.
- Pair Done with Cancel or Back. Do not show Cancel, Back, and Done simultaneously without a truly distinct need.
- Protect dirty edits from an accidental drag dismissal. Confirm only when data would actually be lost, or preserve a draft and say so.
- Use full-screen presentation or a dedicated flow for complex, prolonged, immersive, or deeply nested work.
- Use a nonmodal sheet only when changes intentionally affect the parent while both remain interactive and the relationship stays clear.

### Action sheets or confirmation dialogs

- Use one after a person initiates an action that now requires a small set of related choices.
- Keep the title short and omit redundant body text.
- Put destructive choices in the destructive role and include a safe Cancel path when data could be lost.
- Keep the choice set small enough not to scroll. If it needs categories, search, or explanation, use another structure.

### Alerts

- Reserve an alert for an unexpected situation or uncommon irreversible risk requiring a decision now.
- Do not alert for startup announcements, routine success, common undoable deletion, connectivity that can be shown inline, or validation beside the field.
- State what happened, what remains safe, and the next useful choice. Keep titles short enough to scan without scrolling.
- If the action is recoverable through undo or a recently deleted area, prefer that recovery over repeated confirmation.

### Menus

- Use a menu for secondary commands related to the current context, not for a hidden primary journey.
- Use labels first and symbols where they improve recognition. Keep grouping and destructive roles consistent.
- A menu command executes or opens its clearly named flow. A menu should not impersonate a settings form full of persistent toggles unless the compact choice genuinely belongs there.

## Search Placement Follows Search Scope

Current iOS supports several valid search entry points. Choose by product hierarchy, not fashion.

- Use a dedicated search tab when search is a primary, app-wide destination and people benefit from discovery or immediate input.
- Put search in a bottom toolbar when it is important and reachability helps, provided it does not cover bottom content that is itself primary.
- Put search in the top toolbar when bottom content must remain visible or no bottom toolbar exists.
- Keep search inline with a collection when it filters or navigates that local content.
- Prefer one clearly identified app-wide search location. Add local search only for genuinely distinct collections.
- Preserve query, scope, and result context when moving into a result and back. Clearly distinguish filtering the current view from searching the entire app.
- Use helpful prompt text, useful suggestions, recent searches where appropriate, and an obvious way to clear or cancel.

## Forms, Keyboard, And Data Entry

- Use persistent labels and the appropriate keyboard/content type. Placeholder text can offer an example, but must not be the only label.
- Keep the active field, instructions, validation, and completion action visible when the keyboard appears.
- Scroll the focused field into view without disorienting jumps. Restore a meaningful position when the keyboard dismisses.
- Validate as soon as the person has enough information to act, not on every keystroke when that creates noise and not only after losing all context.
- Preserve entered data across recoverable errors, app switching, and short navigation detours.
- Use pickers for bounded known values and direct entry for open or precise values. Do not force long wheel-like selection for a value that search or typing would express faster.
- Respect autofill, password managers, passkeys, one-time codes, dictation, paste, and privacy-sensitive keyboard behavior where the field supports them.
- Give the keyboard return key an accurate action such as Next, Search, Go, or Done, and ensure hardware-keyboard focus is usable.

## Permissions, Privacy, And System Capabilities

Permission timing is part of the product experience.

- Request only data or capabilities the current feature needs.
- Wait until the person invokes or clearly approaches the feature so the reason for the system prompt is evident.
- If context alone is insufficient, explain the benefit and scope immediately before the request without mimicking or coercing the system alert.
- Let a denial preserve as much app value as possible. Explain what is unavailable and offer a later path to system Settings when changing the decision can restore the feature.
- Do not repeatedly nag after a denial or make the less-private choice visually deceptive.
- Distinguish app data, device data, cloud sync, sharing with other people, and third-party processing at the moment each matters.
- Use platform capabilities such as authentication, payments, sharing, location, camera, and contacts through standard system flows when they satisfy the task.

## Adapt To Available Space, Not A Device Screenshot

- Respect safe areas, layout margins, Dynamic Island and camera regions, the home indicator, status bar, keyboards, bars, and transient system UI.
- Support Dynamic Type by reflowing groups, allowing labels to wrap, and moving horizontal control rows to vertical arrangements before they collide.
- Test light and dark appearances, bold text, increased contrast, reduced transparency, reduced motion, Display Zoom, right-to-left layout, long localization, and supported orientations.
- Derive layout from the current scene or containing view. Current platform environments can resize an iPhone app in iPhone Mirroring or on iPad; device idiom, fixed screen bounds, and orientation labels are not reliable layout specifications.
- Use size and content constraints to adapt. Extra width can reveal useful supporting information, but it must not arbitrarily transform a phone hierarchy into an unrelated desktop UI.
- Keep artwork aspect ratios intact and preserve important focal content across changing aspect ratios.

## Visual And Motion Identity

- Use system typography and semantic text styles so Dynamic Type can preserve hierarchy. Do not simulate refinement with tiny low-contrast text.
- Use the app accent for selection, focus, and a limited number of important actions. Preserve status meaning without color alone.
- Use grouped backgrounds, separators, and spacing to reveal relationships before adding cards. A settings-like list does not need a rounded card inside every row.
- Keep content on readable surfaces. Reserve glass, blur, and strong translucency for functional chrome that genuinely floats over content.
- Use SF Symbols or similarly coherent product symbols for familiar commands, but keep accessible names and visible text for unfamiliar meanings.
- Use haptics as confirmation or texture, never as the only feedback. Avoid haptic noise for every tap.
- Let motion preserve spatial understanding: push for hierarchy, present for scoped work, expand from an origin when the object relationship matters. Keep it responsive and honor Reduce Motion.
- Delight should come from speed, continuity, good defaults, and a few product-specific moments, not ornamental bounce or copied system effects.

## Accessibility And Interruption Resilience

- Give every meaningful element a correct accessibility label, value, trait, hint only when needed, and position in a logical VoiceOver order.
- Group a composite row when it represents one action; expose separate children when they perform separate actions. The accessibility structure must match the touch behavior.
- Verify the largest content sizes, not only the default. Keep primary actions, errors, and navigation reachable when text occupies much more space.
- Do not rely on swipe, drag, color, animation, or haptics alone. Support Voice Control, Switch Control, keyboard access where relevant, and simple visible alternatives.
- Keep touch targets comfortable for limited dexterity and avoid timing-dependent gestures for essential work.
- Preserve drafts and task context when the app moves to the background, a call or permission flow interrupts it, connectivity changes, or authentication expires.
- Announce asynchronous results and errors without stealing focus or repeatedly interrupting assistive technology.

## iPhone Review Pass

### Structure and navigation

- Are tabs stable top-level destinations and stacks a clear hierarchy?
- Are Back, Close, Cancel, and Done used for distinct meanings?
- Can a person recover location and state after app switching or a failed request?
- Are sheets scoped and non-nested, with dirty-edit dismissal handled?

### Touch and controls

- Are actual hit targets comfortable, separated, and usable with either hand?
- Are frequent actions reachable without making destructive actions accident-prone?
- Do row accessories match behavior: switch, disclosure, value, info, or checkmark?
- Is the primary action specific, nondestructive by default, and visible above keyboard and safe areas?

### Settings, search, and privacy

- Are task-local choices kept in context and durable preferences grouped by user goals?
- Is search placed according to app-wide or local scope rather than copied from another app?
- Are permissions requested at the moment of need, with a graceful denied state and recovery path?
- Do settings communicate scope, persistence, sync, restart, and data consequences?

### Adaptation and accessibility

- Does the screen work with extreme Dynamic Type, long localization, RTL, keyboard, Display Zoom, and changing available size?
- Are VoiceOver structure, custom gesture alternatives, contrast, Reduce Motion, and Reduce Transparency verified?
- Does the content remain clear beneath adaptive bars and materials in light and dark appearances?

## iPhone Failure Modes

- A desktop toolbar is squeezed into a row of tiny icons.
- Tabs perform actions, disappear in deeper views, or lose state unpredictably.
- Every task opens a sheet, and sheets open more sheets.
- A settings row contains both navigation and an ambiguous toggle.
- Tiny glyphs sit inside large visual containers but retain tiny hit targets.
- The only route to a command is swipe, long press, or a hidden More menu.
- Permission prompts appear during generic onboarding before the feature has meaning.
- A bottom action covers content, the keyboard, or the home indicator.
- Fixed screen or device checks break when the app is resized, mirrored, zoomed, localized, or displayed with large text.
- The interface copies the visual arrangement of iOS Settings while ignoring the product's own task and identity.

## First-Party Anchors

- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- [Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars)
- [Lists and tables](https://developer.apple.com/design/human-interface-guidelines/lists-and-tables)
- [Settings](https://developer.apple.com/design/human-interface-guidelines/settings)
- [Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields)
- [Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets)
- [Action sheets](https://developer.apple.com/design/human-interface-guidelines/action-sheets)
- [Alerts](https://developer.apple.com/design/human-interface-guidelines/alerts)
- [Gestures](https://developer.apple.com/design/human-interface-guidelines/gestures/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Modernize your UIKit app, WWDC26](https://developer.apple.com/videos/play/wwdc2026/278/)
