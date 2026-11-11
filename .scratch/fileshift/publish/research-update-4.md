## Parent

https://github.com/lastnurik/FileShift/issues/1

# FS-03: Ubuntu shortcut selection popup

**What to build:** Configurable shortcut snapshots the active GNOME Files view and opens the same popup; verify two windows with different selections, tab changes, unsupported foreground app, no selection, conflict/denial and recovery; measure cold/warm latency and idle usage. No stale cache or clipboard fallback.

**Blocked by:** FS-02 (#3).

**Status:** blocked (ticket dependencies)

## Acceptance criteria

- [ ] Configurable shortcut snapshots the active GNOME Files view and opens the same popup.
- [ ] verify two windows with different selections, tab changes, unsupported foreground app, no selection, conflict/denial and recovery.
- [ ] measure cold/warm latency and idle usage. No stale cache or clipboard fallback.


## Evidence

No native acceptance or implementation review is claimed. Keep open until all criteria and blocking issues are complete.

## Research update — 2026-11-12

Read-only inspection of this Ubuntu/GNOME Wayland session reports GlobalShortcuts interface version 1. Shortcut activation does not provide foreground window identity or file selection. The script accelerator is view-local and cannot alone provide unsupported-application feedback. GTK's existing window action export does not include Nautilus's view.script actions, so calling those directly over D-Bus is not a complete bridge.

A version-specific candidate is a small Nautilus C extension registering its own exported application action, plus a GNOME Shell companion that identifies the focused Files window. The gateway could validate the matching active window and invoke the existing fixed script action through GTK widget action activation, reaching the fresh-selection callback without cached selections or clipboard access. Action naming and lazy first-use registration remain version-bound implementation details. Source inspection supports investigating this route; no native prototype has run.

Sources: [Nautilus 50.2.2 source](https://gitlab.gnome.org/GNOME/nautilus/-/tree/50.2.2), [GlobalShortcuts interface](https://github.com/flatpak/xdg-desktop-portal/blob/1.21.1/data/org.freedesktop.portal.GlobalShortcuts.xml), [GNOME Shell 50.1](https://gitlab.gnome.org/GNOME/gnome-shell/-/tree/50.1).

Native acceptance must test window/tab matching, first invocation before opening a menu, races between focus and selection capture, unsupported foreground apps, permission/conflict/rebinding behavior, popup focus/activation tokens, restart and installed lifecycle. Do not use unsafe Shell Eval, simulated keystrokes or stale extension caches as substitutes. The baseline-first gate remains open.
