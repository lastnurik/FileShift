# Continuation proposal — approved breakdown and seams

Prepared 2026-11-12 from CODEX-TERMINAL.md, PROJECT.md, CONTEXT.md,
WORKFLOW.md, all five ADRs, and the installed to-spec, to-tickets, tdd,
code-review, and setup-matt-pocock-skills instructions. The user approved the proposed
ticket breakdown, dependencies, tracker configuration, and public test seams on
2026-11-12. This is not implementation evidence or a replacement product contract.

## Problem Statement

Users need to convert selected local files directly from their file manager,
without manually opening an application, protecting originals and existing outputs.

## Solution

A shared Rust core and separate native adapters open a transient conversion popup
from either a configurable shortcut or a file-manager context action. Advertise
only verified conversions feasible for every selected file. Prove desktop
integration before implementing the full converter.

## User Stories

1. As a desktop user, I want to invoke FileShift after setup without launching it manually.
2. As a file-manager user, I want a configurable shortcut to use my current selection.
3. As a file-manager user, I want a right-click action opening the same popup.
4. As a batch user, I want every selected file captured at invocation.
5. As a user, I want unsupported contexts and empty selections explained clearly.
6. As a user, I want shortcut conflicts and permission failures to be actionable.
7. As a keyboard user, I want navigation and Escape dismissal in the popup.
8. As a user, I want only targets feasible across my selection listed by format name.
9. As a user, I want PNG, JPEG, and WebP still-image conversions.
10. As a user, I want JPEG's white transparency background disclosed before choosing it.
11. As a user, I want PNG and WebP outputs to retain transparency and use lossless encoding.
12. As a document user, I want offline DOCX and Markdown export to PDF.
13. As a user, I want outputs beside their inputs without replacing any existing file.
14. As a batch user, I want per-file failures reported while successful results remain available.
15. As a privacy-conscious user, I want selected-file processing without uploads or indexing.
16. As an installer user, I want managed dependencies and no required terminal or toolchain.
17. As a source-build user, I want verified build, test, package, install, and removal instructions.
18. As a user, I want compatibility claims backed by native installed-build tests.

## Implementation Decisions

- Preserve Rust, separate platform adapters, both entry points on all three platforms,
  native installation, public GitHub distribution, source builds, and the v1 formats.
- Freeze selection before showing the popup; never infer it from clipboard contents,
  cached selection from a different window, or directory scans.
- Keep prototype targets visibly demonstrative; do not advertise working conversions
  until converter probing and output verification exist.
- Keep platform APIs and codecs outside the core. Existing contract boundaries remain
  the basis for injection; avoid speculative plugin loading and extra abstractions.
- Use immutable originals, bounded processing, temporary sibling outputs, collision-safe
  publication, redacted diagnostics, and per-file results.
- Resolve GUI toolkit, shortcut mechanism, codecs, fidelity, resource budgets, and package
  formats with evidence in their respective tasks.
- Select the repository license before publishing source. No license is assumed here.

## Testing Decisions — confirmed

Highest seam for the prototypes: desktop invocation → visible popup/status. A native
test selects real files, invokes each entry point, and observes the popup. This is the
only acceptance seam that establishes platform support.

Proposed automated application seam: activation request → popup model or actionable
status, using injected selection and presentation boundaries. Assert captured selection,
multi-selection, rejected contexts, and frozen snapshots through observable results.
Do not test private adapter methods or treat fake adapters as native evidence.

Later, after feasibility review, propose a second seam: explicit-file conversion request
→ per-file results and verified sibling artifacts. Cover originals, collisions, corrupt
inputs, limits, cleanup, alpha policies, stale files, cancellation, and batch failures.
There is no existing code/test prior art. Follow one observed failing behavioral test
with minimal implementation, then repeat, only after seam confirmation.

## Proposed tickets

Granularity and blocking edges are approved. Each completed task needs acceptance
evidence, separate standards/spec review, and its own commit. Individual local tickets
live under `.scratch/fileshift/issues/`; their corresponding GitHub issues are now
published as #2 through #13, with the specification at #1 and native blocking links.

| ID | Title | Blocked by | End-to-end deliverable and acceptance |
| --- | --- | --- | --- |
| FS-01 | Preserve baseline and configure tracking | None | Confirm this proposal and test seams; configure GitHub tracking with local drafts while access is blocked; initialize Git and commit untouched design baseline; record SHA; select license before source publication; check existing repository, create public repository if absent, and verify SSH origin/push. |
| FS-02 | Ubuntu right-click selection popup | FS-01 | Actual GNOME Files selection opens a visibly marked prototype popup from a context action; multi-selection, keyboard navigation, Escape, invalid local items and no-selection behavior checked; record install/removal and exact session versions. |
| FS-03 | Ubuntu shortcut selection popup | FS-02 | Configurable shortcut snapshots the active GNOME Files view and opens the same popup; verify two windows with different selections, tab changes, unsupported foreground app, no selection, conflict/denial and recovery; measure cold/warm latency and idle usage. No stale cache or clipboard fallback. |
| FS-04 | Windows Explorer integration prototype | FS-01 | Both entry points with actual foreground Explorer selection, multiple windows, conflict reporting, popup navigation/dismissal and installed activation; record exact native environment and performance evidence. |
| FS-05 | macOS Finder integration prototype | FS-01 | Both entry points with actual Finder selection, permission denial/recovery, popup navigation/dismissal and installed activation; record exact native environment and performance evidence. |
| FS-06 | Integration feasibility review | FS-03, FS-04, FS-05 | Review native evidence, choose supported versions, activation strategy, GUI approach and adapter contracts; measure baselines and propose numerical budgets. Missing native evidence blocks completion and full conversion work. |
| FS-07 | First complete image conversion | FS-06 | One verified image route from selection through feasible target to sibling output, plus repeatable explicit-file invocation; protect originals/existing outputs; reopen outputs; verify failure cleanup and probing. |
| FS-08 | Complete still-image routes | FS-07 | PNG/JPEG/WebP routes with lossless PNG/WebP, validated fixed JPEG quality, labeled white compositing, corruption/limits/collision/stale-selection/batch fixtures and output verification. Record metadata/orientation/color policies. |
| FS-09 | DOCX to PDF | FS-07 | Offline bounded export with fixture-based layout/font policy, managed engine and redistribution review, disabled embedded execution/remote fetches, and verified PDF outputs. |
| FS-10 | Markdown to PDF | FS-07 | Offline bounded export with rendering/font/link/asset/embedded-content policies, managed engine and redistribution review, and verified PDF fixtures. |
| FS-11 | Native distribution and source builds | FS-08, FS-09, FS-10 | Each OS installs on a clean machine with managed runtime dependencies, both entry points and removal; source checkout build/test/package/install/remove verified for each claimed platform. |
| FS-12 | V1 release review | FS-11 | Resolve standards/spec findings; validate route/desktop matrices, publication/license terms, source instructions and native packages; set and satisfy numerical resource/latency budgets. |

Splitting Ubuntu right-click and shortcut work makes the first native slice independently
demonstrable. Both remain required; completing FS-02 alone establishes neither Ubuntu
support nor the feasibility gate. Windows and macOS prototypes can proceed independently
of Ubuntu after bootstrap, but need native environments.

Numbered checkpoint summary (the table above contains acceptance criteria):

1. FS-01 — Bootstrap, baseline and tracking. No ticket dependencies; permission,
   toolchain, checkpoint and publication prerequisites must be resolved.
2. FS-02 — Ubuntu right-click selection popup. Blocked by FS-01.
3. FS-03 — Ubuntu shortcut selection popup. Blocked by FS-02 to reuse its popup and
   selection boundary; shortcut feasibility research can proceed independently.
4. FS-04 — Explorer selection popup through both entry points. Blocked by FS-01.
5. FS-05 — Finder selection popup through both entry points. Blocked by FS-01.
6. FS-06 — Native integration feasibility review. Blocked by FS-03, FS-04 and FS-05.
7. FS-07 — First verified sibling image output. Blocked by FS-06.
8. FS-08 — Complete PNG/JPEG/WebP conversions. Blocked by FS-07.
9. FS-09 — Offline DOCX PDF output. Blocked by FS-07.
10. FS-10 — Offline Markdown PDF output. Blocked by FS-07.
11. FS-11 — Installed native packages and verified source builds. Blocked by FS-08,
    FS-09 and FS-10.
12. FS-12 — Verified v1 release. Blocked by FS-11.

## Astra's independent slice check

Astra reviewed the design read-only and recommended treating fresh foreground selection
under Wayland as the earliest feasibility experiment. A Files-owned shortcut or script
accelerator is only a candidate: even a working Files-local shortcut leaves unsupported-
application feedback unresolved. Never cache the last extension callback's selection
and assume it belongs to the current window/tab.

Proposed future ownership: Linux activation/selection/popup glue and setup assets under
platform/linux; minimal Cargo workspace and public activation boundary owned by the core
implementer; README, acceptance evidence and ADRs owned by the coordinator/reviewer.
No converter ownership is assigned before feasibility review.

First proposed red/green behavior: changing selection after activation cannot change the
popup snapshot. Native acceptance additionally switches between two windows and two tabs
with different selections without modifying the destination selection, then invokes each
entry point. Include spaces, Unicode, metacharacters, unreadable/deleted files, invalid
items, keyboard focus, restart/login activation and setup failure. No such test has run.

## Out of Scope

Full converters before feasibility review; video, animation, additional image formats,
PDF import, OCR, online processing, arbitrary third-party plugins, sliders/presets,
and a main application window. Compilation and mocks are not native acceptance.

## Further Notes

The continuation environment still prevents baseline creation. Rust is now installed
locally and smoke-verified; tracker configuration and individual tickets are applied
and published to the public GitHub repository. The source license is MIT. See the
companion bootstrap evidence record. No FileShift tests, implementation, source commits,
package or compatibility claim have been finalized.

## Tracker setup — applied and published

GitHub Issues in `lastnurik/FileShift` is the configured tracker. The specification
is issue #1; FS-01 through FS-12 are issues #2 through #13, with the
`ready-for-agent` label and native blocking links. Local records under
`.scratch/fileshift/issues/` retain the corresponding URLs and evidence.

AGENTS.md links docs/agents/issue-tracker.md and docs/agents/domain.md. Those files
are the authoritative tracker and single-context domain configuration. External PR
triage remains off. Keep CONTEXT.md and docs/adr as the domain glossary/decision
layout; PROJECT.md remains the product contract.
