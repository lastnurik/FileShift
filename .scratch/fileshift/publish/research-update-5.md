## Parent

https://github.com/lastnurik/FileShift/issues/1

# FS-04: Windows Explorer integration prototype

**What to build:** Both entry points with actual foreground Explorer selection, multiple windows, conflict reporting, popup navigation/dismissal and installed activation; record exact native environment and performance evidence.

**Blocked by:** FS-01 (#2).

**Status:** blocked (ticket dependencies)

## Acceptance criteria

- [ ] Both entry points with actual foreground Explorer selection, multiple windows, conflict reporting, popup navigation/dismissal and installed activation.
- [ ] record exact native environment and performance evidence.


## Evidence

No native acceptance or implementation review is claimed. Keep open until all criteria and blocking issues are complete.

## Research update — 2026-11-12

Official Microsoft documentation supports RegisterHotKey plus foreground HWND → ShellWindows → active Shell view as a prototype candidate. Windows 11 active-tab correctness remains unverified. For the context action, IExplorerCommand::Invoke supplies a selection snapshot; modern menu integration needs package identity and native command registration. A native popup can be investigated before selecting a cross-platform GUI toolkit.

Sources: [RegisterHotKey](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey), [GetSelection(FALSE)](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-ifolderview2-getselection), [packaged Explorer integration](https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/integrate-packaged-app-with-file-explorer).

No Windows implementation, installed package or native acceptance has run. Baseline and native environment gates remain open. Detailed findings are maintained locally for the eventual source commit.
