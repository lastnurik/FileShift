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


## Out of Scope

Full conversion before native feasibility review; video, animation, extra image formats, PDF import, OCR, online processing, arbitrary plugin loading, quality sliders and a main window.

## Further Notes

The product is not implemented. Approved public test seams and dependencies guide prototype-first development. Source license: MIT. Native verification on Windows, macOS and Ubuntu is mandatory before v1.
