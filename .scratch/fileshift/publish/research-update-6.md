## Parent

https://github.com/lastnurik/FileShift/issues/1

# FS-05: macOS Finder integration prototype

**What to build:** Both entry points with actual Finder selection, permission denial/recovery, popup navigation/dismissal and installed activation; record exact native environment and performance evidence.

**Blocked by:** FS-01 (#2).

**Status:** blocked (ticket dependencies)

## Acceptance criteria

- [ ] Both entry points with actual Finder selection, permission denial/recovery, popup navigation/dismissal and installed activation.
- [ ] record exact native environment and performance evidence.


## Evidence

No native acceptance or implementation review is claimed. Keep open until all criteria and blocking issues are complete.

## Research update — 2026-11-12

The proposed native slice uses a small AppKit host, foreground Finder validation, a fixed Apple Events selection request, and a standalone NSMenu popup. An app-bundled file Service is the first right-click candidate. Its request pasteboard carries explicit invocation input; it does not read the general clipboard. Consent denial/recovery and actual Finder view semantics require installed-build checks. Finder Sync is scoped to managed directories, so it is not an assumed arbitrary-file selection solution. Native shortcut API availability and conflict behavior need target-SDK and OS evidence.

Sources: [frontmost application](https://developer.apple.com/documentation/appkit/nsworkspace/frontmostapplication), [Apple Events consent](https://developer.apple.com/videos/play/wwdc2019/701/), [Services provider](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/SysServices/Articles/providing.html), [Finder Sync scope](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/Finder.html).

No macOS implementation, installed package or native acceptance has run. Baseline and native environment gates remain open. Detailed findings are maintained locally for the eventual source commit.
