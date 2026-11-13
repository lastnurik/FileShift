# FS-02: Ubuntu right-click selection popup

**What to build:** Actual GNOME Files selection opens a visibly marked prototype popup from a context action; multi-selection, keyboard navigation, Escape, invalid local items and no-selection behavior checked; record install/removal and exact session versions.

**Blocked by:** FS-01.

**Status:** in progress (native handler/keyboard/selection checks passed; actual menu invocation pending)

## Acceptance criteria

- [ ] Actual GNOME Files selection opens a visibly marked prototype popup from a context action.
- [x] multi-selection, keyboard navigation, Escape, invalid local items and no-selection behavior checked.
- [x] record install/removal and exact session versions.

## Evidence

Approved breakdown and public seams: docs/continuation-proposal.md.
Native acceptance is incomplete. The development implementation is committed and
reviewed separately; see the dated implementation/review evidence below.

**GitHub issue:** https://github.com/lastnurik/FileShift/issues/3

## Research update — 2026-11-12

Nautilus 50.2.2 source shows the Scripts context action and its view-local accelerator calling the same run_script callback, which reads that view's selection at invocation. Preserve argv as OS strings and resolve relative paths against the launch working directory. Do not split the newline-delimited selected-path environment variable: embedded newlines make that ambiguous. Empty argv can also represent nonlocal selections, not only no selection.

Sources: [Nautilus 50.2.2 files-view implementation](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-files-view.c), [GNOME script behavior](https://help.gnome.org/gnome-help/nautilus-behavior.html).

This is inspected source behavior, not native acceptance. No popup, installation, selection capture or file conversion has been demonstrated. The baseline-first gate was subsequently completed under FS-01.

## Development implementation — 2026-11-12

FS-01 bootstrap is complete. Rust activation model and Linux selection validator,
Zenity diagnostic presenter, and Nautilus script setup/removal are implemented.
Cargo tests (3) and gateway tests (2), Clippy and formatting pass. Workspace staging
checks installation and removal; direct --check invocation also passes. No converters are advertised.
Native desktop observation remains unavailable; all native acceptance boxes stay open.
See docs/research/ubuntu-prototype-procedure.md for the pending smoke procedure.

## Independent review

Standards review found platform-specific text in the Rust core; fixed by returning
structured status codes and rendering GNOME instructions in the Linux presenter.
Spec review confirmed native observations remain pending and identified stale
historical ticket text, corrected here. Automated checks cannot establish native
identity, selection provenance, focus, placement or keyboard dismissal.

## Native action-handler smoke — 2026-11-12

A real Files fixture selection reached the installed script action handler and a
showing, active FileShift Prototype popup (2 accepted, 0 rejected); its Close
button dismissed it. The repeatable helper removed its script and closed its
fixture window. Ubuntu 26.04.1 LTS, GNOME Shell 50.1, Wayland, Files 50.2.2,
Zenity 4.2.1. Full right-click menu and keyboard/Escape acceptance remain open:
Escape synthesis acknowledged the request but did not close the popup.
See docs/research/ubuntu-prototype-procedure.md for exact command and limits.

The follow-up native run also verified both exact fixture paths through a private
launcher observer, required SHOWING and ACTIVE, and used scoped process ownership
for timeout cleanup. The fixture identity case passed; unusual filename bytes,
multiple windows/tabs and full desktop interaction still require native checks.

## Continuation — 2026-11-13

On Ubuntu 26.04.1, GNOME Shell 50.1, Wayland, Files 50.2.2 and Zenity 4.2.1:

- Native exact delivery passed for seven unusual filenames, including newline and
  a non-UTF-8 byte; 7 accepted and 0 rejected.
- Native mixed selection passed: 2 regular files accepted; directory, symlink,
  FIFO and unreadable file rejected. Empty local-view status passed separately.
- Native popup remained frozen after source selection changed; a different Files
  window's three-file selection did not replace the invoked window's selection.
- Temporary compositor input verified Tab/Shift+Tab focus and actual Escape
  dismissal, superseding earlier inconclusive accessibility synthesis.
- Missing executable now yields a visible redacted setup error. Six Rust tests,
  four gateway tests, formatting and Clippy passed. Scripts/windows were removed
  after the checks; originals and outputs were untouched.

Actual menu navigation remains unchecked. A human observation window expired
without a recorded invocation; no right-click result was inferred from the handler
checks. Keep the issue open. Broader tabs/remote/restart/placement evidence and all
other-platform acceptance remain open; no converter/package is claimed.
