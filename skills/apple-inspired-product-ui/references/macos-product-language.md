# macOS Product Language

Use this reference for native Mac software and for desktop products whose user explicitly wants macOS design discipline. It describes the interaction identity behind macOS, not a recipe for reproducing Finder, System Settings, or another Apple app.

## The Mac Promise

A good Mac app feels like a capable workspace that belongs to the person using it.

- The work remains central while chrome stays legible and restrained.
- People arrange windows, panes, tools, and commands around their own workflow.
- Common actions are visible; the complete command set is systematically available.
- Pointer precision and information density support deep work without making targets fragile.
- Keyboard access accelerates expert work without becoming the only path.
- The app remembers useful workspace state without trapping people in it.
- Modality is exceptional. Context remains visible whenever the task permits it.

This is why simply widening an iPhone layout does not produce a Mac app. macOS identity comes from agency, command structure, multiple simultaneous contexts, and a durable workspace.

## Compose The Workspace

Give each major kind of interface a distinct responsibility.

| Need | Native home | Test |
| --- | --- | --- |
| Complete app command set | Menu bar | Can a person discover and invoke every app command even if the toolbar is hidden? |
| Frequent command in the current window | Toolbar | Is it used often enough to deserve permanent window space? |
| Broad source or section navigation | Sidebar | Does selection change the main area rather than edit the selected object's properties? |
| Deep hierarchy between source and detail | Content list or outline | Does an intermediate list preserve location and enable scanning? |
| Properties of the current selection | Trailing inspector or panel | Can the person keep working in the content while adjusting these properties? |
| Durable app-wide preference | Settings window | Does it affect the app beyond the current document or task? |
| Document-wide option | File or document command, document UI, or inspector | Would a second document reasonably use a different value? |
| Task-local option | Inline beside the task | Would leaving the task merely to change it create unnecessary context switching? |
| Short, window-scoped prerequisite | Sheet | Must the parent window wait for this information before continuing? |
| Independent or prolonged work | Separate window | Would keeping both contexts visible help comparison, reference, or multitasking? |
| Small supplementary status | Status area or unobtrusive inline status | Is it concise enough not to displace the content or an inspector? |

Do not use one container for several meanings. A sidebar full of editable switches, a toolbar that contains every feature, or a modal used as an inspector makes the product harder to predict.

## Windows Are Units Of Work

Use standard windows and system window controls. The frame, title, active state, resizing behavior, and traffic-light controls are operating-system behavior, not brand canvas.

### Window scope

- Open another window when it preserves a useful parallel context: another document, comparison, composition, preview, utility, or independently resumable task.
- Avoid opening a new window for every drill-down or lightweight choice. That creates management work without preserving meaningful context.
- Let a window become full screen when concentration or media benefits from it; do not treat full screen as the default desktop state.
- Use a sheet for a short prerequisite tied to one window. Use another window for work that is independent, prolonged, or useful beside the parent.

### Sizing and adaptation

- Define a smallest useful size based on actual control and content behavior, not a preferred screenshot.
- Allow generous expansion where more space can reveal more content, reduce nesting, or improve comparison.
- Recompose panes and control groups before content overlaps or labels become meaningless. A narrow window can collapse a sidebar, move infrequent toolbar items to system overflow, or change a multi-column region to a simpler composition.
- Test ultrawide, multiple-display, and increased-text situations. Do not pin primary content to an arbitrary fixed desktop width merely to imitate a marketing page.
- Keep important actions away from a fragile bottom-edge-only location; window edges can be obscured or distant, and long content can move them out of view.

### Window state

- Distinguish the key window, the app's main window, and inactive windows through system behavior. Do not invent a second competing active-state language.
- Preserve useful state such as size, position, pane visibility, selection, and sort order when doing so helps a person resume. Recover safely when a display is removed or the stored geometry no longer fits.
- Do not silently reopen sensitive content or revive a destructive transient state. State restoration serves continuity, not surveillance.
- If the product supports several windows, verify commands against the correct active window and selection.

## Menu Bar Is The Command Map

The menu bar expresses the app's complete, ordered command model. It is not a duplicate navigation bar.

- Use the conventional App, File, Edit, View, Window, and Help structure where the concepts apply, and place product-specific menus between the standard groups.
- Put commands where people already look for their meaning: creation, opening, saving, export, and document operations in File; editing and selection in Edit; presentation and pane visibility in View; window management in Window; durable app settings in the App menu.
- Make every toolbar command available in a menu because toolbars can be hidden or customized. Not every menu command deserves toolbar space.
- Keep labels verb-led and specific. Reflect state with a checkmark, selected value, changed title, or enabled state using the system menu behavior.
- Use an ellipsis when choosing the command requires more information before it executes, not merely because another view appears.
- Assign conventional shortcuts first. Add memorable shortcuts for frequent app-specific actions; expose them in the menu instead of relying on documentation.
- Keep unavailable commands visible but disabled when their stable position teaches the command model. If the reason is not obvious and the action matters, provide contextual explanation elsewhere.
- A context menu accelerates relevant commands at the pointer location. It must not be the only path to an important or unfamiliar action.

## Toolbars Are The Frequent Subset

A Mac toolbar gives quick access to important commands in the current window and helps orient the person in that window.

### Placement and grouping

- Put back, forward, sidebar visibility, and the window or document title toward the leading region when present.
- Put common, optionally customizable tools in the center region.
- Put inspector visibility, search, a More menu when truly necessary, and an essential primary action toward the trailing region.
- Group by function and frequency, not by equal visual spacing. Aim for no more than three clearly legible groups.
- Separate text-labeled and symbol-only actions when adjacency could make them read as a single combined control.
- Let the platform manage overflow. Decide which commands remain visible and verify the narrowest useful width.

### Toolbar behavior

- Consider customization for feature-rich apps used for long sessions. Preserve a sensible default and a way to restore it.
- Do not put Settings in the main toolbar; it is not a frequent window command and has a conventional App-menu home.
- Do not place a control in the toolbar only because there is empty space. Toolbar permanence signals importance and frequency.
- Prefer standard toolbar items and system grouping APIs. Current material and shape treatments depend on correct component anatomy.
- Keep action names, enabled state, shortcuts, and results consistent between toolbar, menus, context menus, Touch Bar replacements where relevant, and automation surfaces.

## Sidebars, Content Lists, And Inspectors

These three regions form a common Mac workspace, but they are not interchangeable.

### Sidebar

- Use a sidebar for a broad, mostly flat set of sources, scopes, collections, or top-level areas.
- Keep it scannable. When hierarchy exceeds roughly two visible levels, add an intermediate content list or outline rather than nesting indefinitely.
- Make the selected location clear and keep navigation selection stable while the detail changes.
- Let people hide or resize the sidebar when the workflow benefits, and provide the standard toolbar or menu command to restore it.
- Do not place unrelated actions at the end of the sidebar just to fill space. A small, clearly scoped add action can belong near the collection it changes.

### Content list or outline

- Use a list for a collection and an outline for a genuine parent-child hierarchy.
- Preserve sorting, filtering, multi-selection, range selection, and keyboard movement when the domain supports them.
- Keep row labels concise but do not erase distinguishing information. Middle truncation can preserve both ends of file-like identifiers.
- Use persistent selection to clarify the relationship between a list and its detail view.

### Inspector

- Put properties of the current document object or selection in a trailing inspector or separate panel, not in navigation.
- Update the inspector predictably when selection changes. When several items are selected, show shared values, mixed state, or an explicit multi-selection summary rather than a misleading single value.
- Keep the inspected object visible and interactive unless the edit truly requires a modal commitment.
- Allow the inspector to hide, and preserve its useful width. Do not overload the bottom status area with a vertical property form.

## Buttons And Controls

The Mac control language is compact, precise, and stateful. It is not a field of oversized pills.

### Buttons

- Use a standard push button for an instantaneous action. Name it for the result: `Export`, `Move to Trash`, `Create Project`.
- Assign the primary role to the likely, nondestructive completion action. A default button may respond to Return.
- Never make a destructive action visually primary merely because it is likely. Destructive meaning and likely completion are different signals.
- Provide Cancel for a reversible modal decision and support Escape or Command-Period where the platform expects it.
- Append an ellipsis when the button opens a flow that needs additional input before the named action can occur.
- Use symbol-only buttons for well-known compact actions; give them accessible names and hover help. Prefer text when the meaning is domain-specific or consequential.
- Use a flexible-height push button only when its content genuinely requires extra height, not to make ordinary controls look more promotional.

### Selection and value controls

| Behavior | Prefer | Avoid |
| --- | --- | --- |
| Immediate binary setting | Switch | Checkbox when the visual model implies a system-like on/off state |
| Independent option or inclusion | Checkbox | Switch when changes are staged or represent membership |
| One choice from a short visible set | Radio group or segmented control | Hidden pop-up for two obvious peers |
| One choice from a compact value list | Pop-up button | Using menu items as unrelated actions |
| Bounded continuous value | Slider with meaningful endpoints and, when precision matters, an exact value | Unlabeled slider or false precision |
| Small discrete increment | Stepper paired with a value | Stepper with no readable current value |
| Exact open-ended input | Text or number field with formatter and validation | Slider for values that require exact entry |
| Advanced detail | Disclosure control beside what it reveals | Several distant disclosure controls with unclear ownership |

- Use labels that remain visible when a field contains a value. Put units and constraints where they can be understood before error.
- Preserve the system focus ring. It is input feedback, not an optional visual flourish.
- Let the framework supply control metrics. Apple's current accessibility guidance lists 28×28 points as the default macOS control size and 20×20 points as a minimum; the minimum is an exception, not a density target.
- Make adjacent small controls sufficiently separated and verify the actual clickable region, not only the symbol bounds.

## Design A Real Settings Experience

Settings are durable preferences, not every choice the product exposes.

### Decide whether a setting belongs

1. Choose a useful default that works for most people.
2. Ask whether the person reasonably wants this behavior to persist across sessions or windows.
3. If it affects only the current task, keep it inline.
4. If it affects only one document, put it with document commands or properties.
5. If it is a rare implementation detail with no understandable user outcome, do not expose it merely because the system has a configuration value.

Fewer, better settings make control more usable. Removing a setting is safe only when the default and migration behavior preserve user intent.

### Settings entry and window

- Provide `Settings…` in the App menu and support Command-Comma.
- Do not rely on a Settings button in each main window or keep the Settings window in the Dock.
- For a multi-pane native settings window, use a stable, noncustomizable toolbar whose selected item clearly identifies the active pane.
- Give each pane a plain category name and a title that reflects the active pane. Restore the last useful pane when appropriate.
- Dim the minimize and maximize controls for a conventional pane-sized Settings window: Command-Comma makes it quick to reopen, and the pane defines the needed size.
- Size the window to the pane content and avoid turning settings into another resizable document workspace unless the volume and search behavior genuinely require it.
- Add search when the setting set is large enough that recognition by category is no longer sufficient. Search results should reveal the setting in its real context, not create a second editing surface with different behavior.

### Settings content

- Group by a person's mental model: general behavior, appearance, accounts, notifications, privacy, shortcuts, or domain-specific categories that the product actually has. Do not expose the internal service architecture.
- Put a concise explanation below or beside a setting when the consequence, data use, scope, or restart requirement is not evident from the label.
- Prefer immediate application for ordinary reversible preferences and show the result directly. If changes are staged, make Apply, Cancel, dirty state, validation, and persistence explicit.
- Show dependencies honestly. Disable a dependent control only when its parent state makes it inapplicable; retain enough context to explain how to enable it.
- Avoid warning dialogs for ordinary preference changes. Use undo, reset-to-default, or a targeted confirmation for an uncommon irreversible consequence.
- For account, security, and privacy changes, state scope, data effect, and authentication requirements at the decision point.

## Sheets, Alerts, Popovers, And Panels

Choose transient UI according to its relationship with the parent.

- **Sheet:** a short, focused task the parent window cannot continue without. Keep the parent visible, offer a safe exit, and avoid sheet-on-sheet chains.
- **Alert:** an unexpected condition or uncommon irreversible risk that requires attention. Do not alert for common undoable actions, routine success, startup advertising, or information that can remain inline.
- **Popover:** a lightweight, anchored choice or detail that does not need a full window. Dismissal must not silently lose important edits.
- **Inspector or panel:** supplementary controls needed while the main content remains interactive.
- **Window:** independent, comparative, or prolonged work.

Use system button order and roles. Do not hand-position buttons to mimic a screenshot; semantic roles let the platform produce familiar behavior for locale, keyboard, and accessibility.

## Visual Identity Without Costume

macOS hierarchy is typically quieter and denser than a marketing site.

- Let content occupy the stable content layer. Use system material for functional chrome such as toolbars, sidebars, and floating controls where the platform supplies it.
- Treat current glass or translucency as a relationship between chrome and content, not as a texture for every card. Verify legibility with Reduce Transparency and Increased Contrast.
- Use the system type hierarchy or the product's established legible type. Avoid enormous page titles, ultra-light small text, and letter-spaced all-caps as a substitute for structure.
- Use accent color for selection, focus, and a small number of primary actions. Respect the person's system accent choice when the framework provides it.
- Prefer SF Symbols or the platform's standard symbols for familiar commands. Keep optical weight and baseline aligned; add text or help for domain-specific meaning.
- Use separators, background shifts, and spacing to express pane structure before adding cards, shadows, or thick borders.
- Match corner relationships through system components. Do not apply the same large radius to windows, tables, fields, toolbars, and every content group.

## Pointer, Keyboard, Selection, And Dragging

A Mac app must support more than clicking the visible happy path.

- Make hover additive. Tooltips, previews, and hover emphasis can accelerate discovery, but no essential action or meaning may exist only on hover.
- Provide logical focus order and visible focus. Verify keyboard-only access, Full Keyboard Access where applicable, and text navigation conventions.
- Use Return for the default nondestructive action and Escape for cancellation only when those meanings are truthful.
- Support Command-click, Shift-click, range selection, Select All, and arrow-key navigation where the collection model warrants them.
- Provide context menus for pointer efficiency and menu-bar equivalents for discoverability and keyboard use.
- Use drag and drop when the object model makes the source, destination, preview, accepted operation, and cancellation clear. Do not make dragging the only way to move or import data.
- Change the pointer only to communicate a real interaction mode. A hand cursor, resize cursor, or precision cursor must match actual behavior.

## Accessibility And Adaptation

- Preserve native roles, names, values, groups, headings, selected state, and relationships for VoiceOver.
- Check keyboard operation without a pointer, including menus, toolbar items, sidebar, lists, inspector fields, dialogs, and restoration of focus after dismissal.
- Support system text and display preferences in the scope of the app. Avoid clipping when people enlarge text or use a lower effective resolution.
- Verify light and dark appearances, Increase Contrast, Differentiate Without Color, Reduce Transparency, and Reduce Motion.
- Never rely on a faint hover effect, color alone, or a tiny glyph to communicate selection, destructive meaning, or required state.
- Keep animations interruptible and ensure window, pane, and selection changes remain understandable without motion.

## macOS Review Pass

### Workspace

- Does each window represent coherent work, resize usefully, and restore safely?
- Can people use multiple documents or contexts without artificial single-screen navigation?
- Are sidebar, content list, detail, and inspector roles distinct?
- Does the layout remain useful at the smallest window and on a large or secondary display?

### Commands

- Is the full command set in the menu bar and the frequent subset in the toolbar?
- Are standard menu locations, shortcuts, enabled state, ellipses, and labels correct?
- Does toolbar overflow or customization leave every command reachable?
- Are context menus accelerators instead of hidden requirements?

### Settings and controls

- Are app settings separated from document properties and task-local controls?
- Does Settings open through the App menu and Command-Comma?
- Do controls match immediate versus staged behavior?
- Is the default action nondestructive, Cancel safe, and the actual click target adequate?

### Input and accessibility

- Can the journey be completed with pointer and keyboard independently?
- Do focus, selection, active window, mixed values, drag targets, and unavailable states remain clear?
- Are VoiceOver semantics and macOS accessibility appearance preferences verified?

## macOS Failure Modes

- A giant single window behaves like a website and ignores multiwindow work.
- Important commands exist only as unlabeled toolbar icons.
- The toolbar becomes a crowded feature inventory while the menu bar is incomplete.
- A sidebar mixes navigation, settings, status, and unrelated actions.
- Object properties open a modal instead of remaining available in an inspector.
- Settings are duplicated in the main toolbar and each document window.
- Every control is an oversized rounded pill, reducing useful density and platform familiarity.
- Custom traffic lights, title bars, focus rings, or window materials imitate appearance but break behavior.
- The app assumes mouse input, while keyboard order, shortcuts, and VoiceOver relationships are incomplete.
- The design copies Finder or System Settings instead of expressing the product's own domain.

## First-Party Anchors

- [Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/)
- [Windows](https://developer.apple.com/design/human-interface-guidelines/windows)
- [The menu bar](https://developer.apple.com/design/human-interface-guidelines/the-menu-bar)
- [Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- [Sidebars](https://developer.apple.com/design/human-interface-guidelines/sidebars)
- [Settings](https://developer.apple.com/design/human-interface-guidelines/settings)
- [Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)
- [Menus](https://developer.apple.com/design/human-interface-guidelines/menus)
- [Alerts](https://developer.apple.com/design/human-interface-guidelines/alerts)
- [Build an AppKit app with the new design, WWDC25](https://developer.apple.com/videos/play/wwdc2025/310/)
