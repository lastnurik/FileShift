## Parent

https://github.com/lastnurik/FileShift/issues/1

# FS-01: Preserve baseline and configure tracking

**What to build:** Establish an approved, licensed, publicly tracked project and preserve its design baseline before implementation.

**Blocked by:** None (external session permission gate remains).

**Status:** blocked (read-only Git metadata mount)

## Acceptance criteria

- [x] Confirm specification, ticket breakdown, blocking dependencies and public test seams.
- [x] Configure GitHub tracking and publish the approved specification and twelve tickets.
- [x] Choose source license before source publication: MIT, recorded in LICENSE and ADR 0006.
- [x] Check existing repository, create public repository if absent, and verify administrative access.
- [x] Verify GitHub SSH authentication and read access to the intended repository.
- [x] Install and smoke-verify Rust, Cargo, rustfmt and Clippy.
- [ ] Initialize local Git and commit the preserved design baseline.
- [ ] Record baseline SHA for the required standards/spec review.
- [ ] Configure SSH origin and verify source push.
- [ ] Complete separate standards/spec review and individual task commit.

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

The execution session mounts .git read-only. Git initialization fails with Read-only
file system, and no approval escalation is available. No alternate metadata directory,
API source commit, or filesystem workaround was used. There is no local baseline,
configured origin, source push, or formal Git-diff review.

Detailed checks: docs/bootstrap-evidence.md.

