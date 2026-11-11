# FS-02: Ubuntu right-click selection popup

**What to build:** Actual GNOME Files selection opens a visibly marked prototype popup from a context action; multi-selection, keyboard navigation, Escape, invalid local items and no-selection behavior checked; record install/removal and exact session versions.

**Blocked by:** FS-01.

**Status:** blocked (ticket dependencies)

## Acceptance criteria

- [ ] Actual GNOME Files selection opens a visibly marked prototype popup from a context action.
- [ ] multi-selection, keyboard navigation, Escape, invalid local items and no-selection behavior checked.
- [ ] record install/removal and exact session versions.

## Evidence

Approved breakdown and public seams: docs/continuation-proposal.md.
No completed native acceptance, implementation review, or task commit.

**GitHub issue:** https://github.com/lastnurik/FileShift/issues/3

## Research update — 2026-11-12

Nautilus 50.2.2 source shows the Scripts context action and its view-local accelerator calling the same run_script callback, which reads that view's selection at invocation. Preserve argv as OS strings and resolve relative paths against the launch working directory. Do not split the newline-delimited selected-path environment variable: embedded newlines make that ambiguous. Empty argv can also represent nonlocal selections, not only no selection.

Sources: [Nautilus 50.2.2 files-view implementation](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-files-view.c), [GNOME script behavior](https://help.gnome.org/gnome-help/nautilus-behavior.html).

This is inspected source behavior, not native acceptance. No popup, installation, selection capture or file conversion has been demonstrated. The baseline-first gate remains open.
