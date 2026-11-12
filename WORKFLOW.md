# FileShift implementation workflow

## Starting state

The design interview is concluded. Implement PROJECT.md; resolve remaining technical choices through documentation, prototypes, and measured evidence. Ask one question at a time when a product decision, credential, missing test environment, or mandatory skill checkpoint blocks progress.

The repository is public, with SSH Git transport, one commit per completed task,
native packages, and a source-build option. The design baseline is
`1a75db0e1f32b22391a86a9ccde309611ec43cdd`, pushed to lastnurik/FileShift.
The managed sandbox still mounts .git read-only; approved escalation enabled Git
initialization, commits, and the SSH push. Use normal approval handling for Git
metadata writes. See docs/bootstrap-evidence.md for historical and current checks.

## Bootstrap

1. Inspect files, Git state, tools, and actual desktop environment. Preserve existing work.
2. Read the installed Matt Pocock to-spec, to-tickets, tdd, and code-review skills. Synthesize the specification from PROJECT.md and prepare dependency-ordered tickets and public-interface test seams. Present concrete proposals for mandatory checkpoints; retain prior decisions.
3. Configure the tracker using the applicable installed setup skill. GitHub Issues is the proposed destination; keep drafts local while access or approval is pending. Tickets record blockers, acceptance criteria, status, and evidence.
4. Initialize Git when permitted and commit the design baseline before implementation. Record its SHA as the proposed review baseline. Check for an existing GitHub repository before creating the public repository under the authenticated account. Repository creation uses the available authenticated API/CLI; Git transport uses SSH. Select the repository license before publishing source. Report permission or credential blockers explicitly.

## Task sequence to turn into tickets

| Task | Blocked by | Deliverable and acceptance |
| --- | --- | --- |
| Ubuntu integration prototype | Bootstrap | Real GNOME Files selection reaches a popup through both shortcut and right-click. Verify multi-selection, Escape, no selection, unsupported context, and setup failures. |
| Windows integration prototype | Bootstrap | Both entry points work with real Explorer, including foreground selection, conflicts, and installed activation. |
| macOS integration prototype | Bootstrap | Both entry points work with real Finder, including permission denial/recovery and installed activation. |
| Integration feasibility review | All three prototypes | Native evidence, supported OS versions, adapter boundaries, GUI approach, activation strategy, and measured performance baselines recorded. Missing native testing remains open. |
| First complete image route | Feasibility review | Selection → feasible target → verified sibling output through core and adapters, plus repeatable explicit-file tests. Originals and existing outputs remain unchanged. |
| Complete v1 image routes | First image route | PNG/JPEG/WebP satisfy transparency/encoding policies; fixtures cover corruption, limits, collisions, stale selections, cleanup, and batch results. |
| DOCX to PDF | First image route | Offline export with documented fidelity/font policy, managed engine dependency, limits, verified outputs, and representative fixtures. |
| Markdown to PDF | First image route | Offline export with documented rendering policy, safe links/assets/embedded-content handling, limits, and verified PDF fixtures. |
| Native distribution and source builds | All v1 routes | Clean-machine installation/setup, both entry points, removal, and documented source builds on each OS. End users need no development toolchain. |
| V1 release review | Distribution and native evidence | Standards/spec findings resolved, route/desktop matrices evidenced, resource budgets established and met, accurate public-source and package documentation. |

Prototypes may include minimal Cargo scaffolding and disposable activation/UI code. Ubuntu development builds can proceed while other platforms await verification; the full converter remains gated by the feasibility review unless the user explicitly revises this decision. Implementations without native evidence remain incomplete tasks.

## Per-task loop

1. Select an unblocked ticket. State user outcome, OS/session, public test seam, and acceptance criteria. Consult current documentation before selecting APIs or dependencies.
2. Follow TDD at agreed seams: one behavioral test, observed failure, minimal complete implementation, relevant verification, repeat. Use native smoke procedures for behavior automated tests cannot establish.
3. Record exact checks, results, platform versions, and limitations. Test publication safety and converter failures through public interfaces.
4. Review standards and specification separately using code-review and a valid concrete baseline. Fix findings, rerun affected checks, and update evidence. Refactor during review where justified.
5. Update docs and ticket status, then commit the completed task with its identifier. Push through SSH when available. Keep unmet acceptance criteria open.
6. Continue to the next unblocked ticket. Pause dependent work at unmet gates and continue independent work where possible. Compilation and mocks alone do not prove platform support.

## Remaining technical decisions

Investigate toolkit/platform APIs, codecs/engines, package formats, metadata/orientation/color policy, fonts/document fidelity, Markdown assets, limits/cancellation, concurrency, and numerical memory/latency budgets in the relevant tickets. Propose evidence-backed defaults. These decisions cannot expand format scope or weaken platform requirements without user agreement.

## Completion report

Report delivered behavior, exact tests, supported platform versions, native/source installation instructions, repository URL, commit/push state, and open gates. Distinguish development builds from v1 readiness.
