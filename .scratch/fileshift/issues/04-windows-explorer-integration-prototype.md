# FS-04: Windows Explorer integration prototype

**What to build:** Both entry points with actual foreground Explorer selection, multiple windows, conflict reporting, popup navigation/dismissal and installed activation; record exact native environment and performance evidence.

**Blocked by:** FS-01.

**Status:** ready for native implementation; native environment unavailable in the current session

## Acceptance criteria

- [ ] Both entry points with actual foreground Explorer selection, multiple windows, conflict reporting, popup navigation/dismissal and installed activation.
- [ ] record exact native environment and performance evidence.

## Evidence

Approved breakdown and public seams: docs/continuation-proposal.md.
No completed native acceptance, implementation review, or task commit.

**GitHub issue:** https://github.com/lastnurik/FileShift/issues/5

## Research update — 2026-11-12

Official Microsoft documentation supports RegisterHotKey plus foreground HWND → ShellWindows → active Shell view as a prototype candidate. Windows 11 active-tab correctness remains unverified. For the context action, IExplorerCommand::Invoke supplies a selection snapshot; modern menu integration needs package identity and native command registration. A native popup can be investigated before selecting a cross-platform GUI toolkit.

Sources: [RegisterHotKey](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey), [GetSelection(FALSE)](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-ifolderview2-getselection), [packaged Explorer integration](https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/integrate-packaged-app-with-file-explorer).

No Windows implementation, installed package or native acceptance has run. The baseline gate was subsequently completed under FS-01; the native environment gate remains open. Research findings are published under docs/research.

## Bootstrap dependency resolved — 2026-11-12

FS-01 is complete and issue #2 is closed. The approved dependency edge remains
recorded; its gate is satisfied. Source baseline and Rust prototype commits are
published. Native platform implementation/acceptance still requires the named
platform environment and remains open; Linux smoke evidence does not substitute.
