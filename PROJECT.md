# Project: contextual file converter

## Purpose

Build a Rust desktop utility that is always available after installation and setup. Use a shared core with separate OS adapters, allowing small native integration components and packaged document-conversion dependencies where necessary. Prefer on-demand activation; use a small resident helper only where integration requires it. A user selects one or more local files in Windows Explorer, macOS Finder, or a supported Linux file manager, presses a configurable shortcut or invokes a file-manager right-click action, chooses a feasible target format from a small popup, and receives converted files beside the originals. There is no main window. A tray or menu-bar control may expose settings, status, and quit.

“Any file type to any file type” is an aspiration, not a truthful product promise. The menu lists only conversions supported by an installed, enabled converter for the selected inputs. A conversion is an explicit path from one understood format to another; changing an extension alone is never conversion.

## Product contract

1. The shortcut is configurable and reports conflicts or unavailable permissions. Triggering it while an unsupported app has focus shows a brief, actionable status; it never guesses from the clipboard or silently scans a folder.
2. Capture the selected paths from the active supported file-manager view at invocation time. Preserve multi-selection. Ignore virtual items, directories, remote URLs, and files that cannot be read in the initial release, with a clear reason.
3. The popup is a transient menu anchored near the pointer or selection when the platform permits. It lists the intersection of feasible targets across all selected files, includes format names rather than only extensions, supports keyboard navigation and Escape, and closes after choosing or dismissing. Conversion work runs off the UI thread.
4. Save each result next to its input as `<stem>.<target extension>`. Never replace the original. If that path exists, choose a deterministic free name such as `<stem> (converted 2).<ext>`. Write to a temporary sibling file and publish only after successful completion. Report partial batch failures per file.
5. V1 supports conversion between still PNG, JPEG, and WebP images, plus DOCX → PDF and Markdown → PDF. PNG and WebP outputs use lossless encoding; JPEG uses a fixed high-quality setting selected and validated against fixtures with the chosen codec. When transparency is present, JPEG composites onto white and the choice is labeled “JPEG — white background”; PNG and WebP preserve transparency. Quality sliders, file-size presets, animated images, HEIC, SVG, TIFF, camera RAW, PDF → DOCX, OCR, and other text formats are deferred. Video is the next converter family after v1, followed by other files.
6. No network access, upload, account, or background file indexing is needed for conversion. The app only reads files selected for the current action.

## Platforms and release gate

V1 requires both a configurable keyboard shortcut and a file-manager right-click action on Windows Explorer, macOS Finder, and a named Ubuntu/GNOME Files environment. Ubuntu/GNOME is the first testing environment; Ubuntu development builds may proceed independently. Each entry point must snapshot the selected files and open the conversion popup directly, without a splash screen, main window, or manual application launch.

Prototype selection → shortcut/right-click → popup on all three platforms before building the full converter. Native verification on all three is a v1 release gate. If an integration cannot meet the requirement reliably, resolve it or obtain an explicit requirement revision. Mocked adapter tests and successful cross-compilation do not establish desktop support.

Implementation candidates to investigate with current documentation:

| Platform | Candidate integration | Required evidence |
| --- | --- | --- |
| Windows Explorer | Native hotkey registration, foreground Explorer selection via Shell APIs, Explorer context action | Correct foreground selection, both entry points, conflict feedback, installed-build behavior |
| macOS Finder | Native shortcut, Finder selection with appropriate consent, Finder context action | Both entry points, permission denial/recovery, installed-build behavior |
| Ubuntu/GNOME Files | File-manager extension/action and a supported shortcut mechanism | Actual selected paths for both entry points under the named session; no clipboard or folder-scanning fallback |

These are investigation directions, not verified API choices. Record exact OS, desktop, file-manager, and package versions in evidence. A global-shortcut facility alone does not establish access to file-manager selection.

## Installation and distribution

The GitHub repository is public. Provide native installers/packages for all three supported OSes, managing required conversion dependencies through installation. End users need no terminal, compiler, Python environment, or separately installed conversion tools. Initial permission prompts and shortcut configuration are acceptable. Everyday use requires no technical setup.

Also provide a documented build-from-source path from a clean checkout, including the supported Rust toolchain, OS-specific development dependencies, build/test/package steps, and how to install and remove the resulting utility. Source builds are an additional distribution option, not a replacement for native packages. FileShift source uses the MIT license (see LICENSE and ADR 0006). Verify dependency redistribution terms before public release.

Use Cargo for the Rust project. Docker Compose and uv are not requirements for the shipped utility. Determine package formats and dependency handling through prototypes. Measure idle CPU, resident memory, and activation latency, distinguishing cold and warm invocation; record measured baselines and establish numerical acceptance budgets before release. “Always available” does not mean a zero-memory resident process.

## Architecture

Keep the core independent of desktop APIs and of any one conversion library.

```text
shortcut adapter -> selection adapter -> capability planner -> transient popup
                                              |                    |
                                        converter registry <------+
                                              |
                                     job runner -> output writer -> status
```

- `ShortcutAdapter`: `register(binding) -> result`, `unregister()`, and an invocation callback. It reports conflicts, permission issues, and unsupported sessions.
- `SelectionAdapter`: `get_selection() -> SelectionResult(paths, source, diagnostics)`. It validates the foreground manager and returns a snapshot, not a mutable live selection.
- `ConverterPlugin`: declares source/target MIME or format IDs, probes a file without trusting its extension alone, reports availability and limitations, and performs one conversion into an explicitly supplied temporary output path. No plugin may claim a route solely because a library can open a file.
- `CapabilityPlanner`: computes available routes for every selected input, then the batch intersection. It gives the popup human-readable reasons when no route is available. Its output is a plan frozen before execution.
- `JobRunner` and `OutputWriter`: enforce limits, cancellation where supported, collision-safe naming, temporary files, atomic publication where the filesystem permits, and per-file results. The UI consumes structured progress and errors.
- `PopupPresenter`: shows only the plan and starts the selected job. The popup's lifetime and focus behavior are tested per OS. A minimal tray/menu-bar settings surface is separate from conversion.

Platform code lives under `platform/windows`, `platform/macos`, and `platform/linux`; converters live under `converters`. Keep platform adapters and converter plugins injectable so the core can be tested with fakes. Prefer a small built-in plugin registry first. Define versioned plugin metadata before loading third-party plugins.

## Security and data handling

- Treat selected files as untrusted. Validate regular local files, canonicalize carefully, reject unsupported symlinks or special files in v1, and recheck identity/existence before opening. Do not follow a changed selection after the popup appears.
- Converter parsers and external tools can have vulnerabilities. Pin and update dependencies, cap input size and resource use per plugin, set timeouts for subprocesses, pass arguments as arrays with no shell, and allowlist executable paths. Consider process isolation for complex codecs before offering third-party plugins.
- Use least-privilege permissions. Explain macOS Automation consent at the moment it is needed. Do not request Accessibility or broad disk access merely to avoid implementing a proper integration.
- Keep originals immutable. Write output to a sibling temporary file, clean up on failure, and avoid following symlinks during final publication. Resolve collisions without overwriting existing files; handle cross-device and network-filesystem behavior explicitly.
- Log format IDs, outcomes, durations, and redacted error categories by default. File names and contents are private; diagnostics with paths require an explicit user action. Do not execute code embedded in documents or load arbitrary plugin code without opt-in.

## Execution and acceptance

Follow [WORKFLOW.md](WORKFLOW.md) for the prototype-first task sequence, TDD/review loop, and commit policy. Record implementation evidence and platform acceptance in README and task records. The architecture above defines logical boundaries, not a mandated file tree or a promise that all adapters are implemented.

Each conversion route must define input probing, fidelity, output verification, resource limits, and failure behavior before being advertised. Document conversion must work offline without executing embedded content or fetching remote resources. Establish fixture-based DOCX layout/font and Markdown rendering policies before choosing converters. Metadata/orientation/color handling and numerical limits remain technical decisions to resolve and record during those tasks.

## Test plan

- Core unit tests: path naming, collisions, route intersection, probe mismatch, failure cleanup, per-file batch results, and settings validation.
- Converter integration tests: representative images, lossy and alpha behavior, malformed files, resource limits, and output verification by reopening the result.
- Adapter contract tests: mocked foreground selection, no selection, permission denial, conflicting shortcut, and stale/removed files.
- Native smoke tests on each supported OS/session: shortcut registration, active file-manager detection, actual selected paths, popup focus/placement, packaged permissions, and output beside the source. Record OS and file-manager versions in the test report.
- Security tests: symlink and special-file refusal, output collision race, subprocess timeout, cleanup, and no shell interpretation of paths with spaces or metacharacters.

## Implementation status

This repository contains design documents and a Linux selection-inspection prototype, not a working converter. Rust is selected; GUI toolkit, codecs, document engines, exact platform version support, package formats, and numerical resource budgets require documented prototype evidence. README must publish only commands that exist and have been verified. Planned user-facing capabilities include diagnostics, explicit-file conversion for repeatable testing, and desktop activation; finalize command names during implementation.

## Decision records

See [docs/adr](docs/adr) for the reasons behind platform gates, installation, format scope, and language selection. [CONTEXT.md](CONTEXT.md) defines product terminology.

## Platform references

- Microsoft: [RegisterHotKey](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey), [ShellFolderView.SelectedItems](https://learn.microsoft.com/en-us/windows/win32/shell/shellfolderview-selecteditems), [Explorer automation model](https://learn.microsoft.com/en-us/windows/win32/shell/developing-with-windows-explorer).
- Apple: [Apple-events usage description](https://developer.apple.com/documentation/bundleresources/information-property-list/nsappleeventsusagedescription), [Apple Events entitlement](https://developer.apple.com/documentation/BundleResources/Entitlements/com.apple.security.automation.apple-events), [Automation consent](https://developer.apple.com/videos/play/wwdc2019/701/).
- Linux: [GlobalShortcuts portal interface](https://github.com/flatpak/xdg-desktop-portal/blob/main/data/org.freedesktop.portal.GlobalShortcuts.xml), [GNOME Files selection extension interface](https://gnome.pages.gitlab.gnome.org/nautilus/vfunc.MenuProvider.get_file_items.html), [GNOME Files script behavior](https://help.gnome.org/gnome-help/nautilus-behavior.html).
- GUI toolkit selection remains open; evaluate it against the native interaction prototypes rather than the previous Python implementation proposal.
