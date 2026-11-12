# FS-01: Preserve baseline and configure tracking

**What to build:** Establish an approved, licensed, publicly tracked project and preserve its design baseline before implementation.

**Blocked by:** None.

**Status:** complete

## Acceptance criteria

- [x] Confirm specification, ticket breakdown, blocking dependencies and public test seams.
- [x] Configure GitHub tracking and publish the approved specification and twelve tickets.
- [x] Choose source license before source publication: MIT, recorded in LICENSE and ADR 0006.
- [x] Check existing repository, create public repository if absent, and verify administrative access.
- [x] Verify GitHub SSH authentication and read access to the intended repository.
- [x] Install and smoke-verify Rust, Cargo, rustfmt and Clippy.
- [x] Initialize local Git and commit the preserved design baseline.
- [x] Record baseline SHA for the required standards/spec review.
- [x] Configure SSH origin and verify source push.
- [x] Complete separate standards/spec review and individual task commit.

## Evidence

The user approved configuration, dependencies and public test seams on 2026-11-12,
then delegated routine decisions and requested autonomous completion.

Public repository: https://github.com/lastnurik/FileShift
Approved specification: https://github.com/lastnurik/FileShift/issues/1
Specification/tickets: 13 open ready-for-agent issues; all 15 native blocking links verified.

Rust/Cargo 1.99.1 installed locally, compiler/linker/test/run smoke passed; no product
implementation or native interaction is claimed. SSH authentication for the repository
owner and git ls-remote read access passed with explicit SSH configuration and strict
host-key checking.

Approved escalation initialized Git and preserved design baseline
`1a75db0e1f32b22391a86a9ccde309611ec43cdd`. SSH origin is configured and main
was pushed successfully. Sandbox metadata remains read-only; approved escalation
handles writes without changing the managed configuration.

Detailed checks: docs/bootstrap-evidence.md.

Commit 824b327 records FS-01 evidence. Independent standards and spec reviewers
each reported zero findings against baseline 1a75db0. No native acceptance is implied.

**GitHub issue:** https://github.com/lastnurik/FileShift/issues/2
