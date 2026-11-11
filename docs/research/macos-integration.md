# macOS Finder integration investigation

Research date: 2026-11-12. Status: proposed prototype, **no native acceptance**.
The research host reports Linux; no macOS version, GUI session, Finder version,
installed application, signing identity, or native shortcut was tested. This
document supplies implementation direction without changing PROJECT.md or ADRs
0001/0005. The baseline-first implementation gate remains open.

## Documentation method and confidence

Context7 resolved Apple AppKit to `/websites/developer_apple_appkit` (official Apple
documentation, high source reputation). Focused queries covered foreground
application identity and window-independent menus. Apple Events, Services,
Finder Sync, signing, and hotkeys needed supplementary official Apple sources;
they were not established by those Context7 results. Some Apple material is
archived and the hotkey guidance is an Apple engineer's forum response, rather
than a complete modern API contract. SDK availability, Finder scripting behavior,
and installed interaction must be checked on the actual target OS before claiming
support. No minimum supported macOS version is selected by this research.

## Smallest concrete slice

Build a disposable native AppKit menu-bar application with no main window,
containing a native shortcut adapter, Finder selection adapter, Services provider,
and conversion popup presenter. Keep the shared Rust boundary a structured
selection snapshot plus diagnostics. Initially show a clearly marked prototype
action that acknowledges the snapshot; advertise no conversion routes. Measure
selection-to-popup latency and idle resource use before choosing a final toolkit.

Shortcut path:

1. At the callback, before activating FileShift or showing permission UI, obtain
   `NSWorkspace.shared.frontmostApplication` and compare its bundle identifier
   with Finder's expected `com.apple.finder`. AppKit defines this property as the
   application receiving key events and provides the running application's bundle
   identifier. Reject unsupported foreground apps without requesting their
   selection. [NSWorkspace](https://developer.apple.com/documentation/appkit/nsworkspace/frontmostapplication),
   [NSRunningApplication](https://developer.apple.com/documentation/appkit/nsrunningapplication).
2. Request Finder's selection once through an in-process, fixed AppleScript or
   Apple Events request. Prototype `tell application "Finder" to get selection`
   against the installed Finder scripting dictionary, coercing individual file
   references to aliases and obtaining POSIX paths. Apple's scripting guide
   documents Finder references, alias coercion, and POSIX-path extraction; it does
   not establish all current selection/view semantics. Preserve a typed list,
   rather than joining paths with newline delimiters. Never interpolate paths
   into script source or pass them through a shell.
   [Apple file-reference guide](https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/ReferenceFilesandFolders.html).
3. A consent prompt introduces a race: if permission is requested, abandon that
   invocation after authorization and tell the user to invoke again in Finder.
   For already authorized requests, recheck foreground identity after the reply;
   abort if it changed. These are proposed mitigations, not proof of an atomic
   selection-at-keypress API. Test rapid focus and selection changes; the contract
   is unresolved if Finder returns selection from the wrong view.
4. Validate a bounded list of local regular files, preserving multi-selection.
   Diagnose directories, aliases/symlinks, unreadable or removed files, and cloud
   placeholders without initiating downloads. Freeze the snapshot before the
   popup; no clipboard inference or folder enumeration.
5. On the main thread display `NSMenu.popUp(positioning:at:in:)` at pointer screen
   coordinates with a nil view. AppKit explicitly permits a menu disconnected
   from a window and distinguishes selection from cancellation. Native tests must
   establish keyboard navigation, Escape, focus, multi-display placement, and
   behavior after the originating Finder menu closes.
   [NSMenu popup](https://developer.apple.com/documentation/appkit/nsmenu/popup(positioning:at:in:)).

Right-click path: implement an application-bundled file Service first. Declare
`NSServices`, a localized menu item, supported file input types, and `NSMessage`;
register a services provider and immediately copy the invocation's supplied file
URLs to the same snapshot boundary. The Service's supplied pasteboard is explicit
request input, distinct from reading the user's general clipboard. Apple's
provider guide describes runtime registration, method shape, application-bundled
installation, and request pasteboard handling; current keys describe declared
input types. Confirm Finder actually exposes the item from a file right-click
and preserves all selections in an installed build.
[Services provider guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/SysServices/Articles/providing.html),
[NSServices](https://developer.apple.com/documentation/bundleresources/information-property-list/nsservices),
[file URL type](https://developer.apple.com/documentation/appkit/nspasteboard/pasteboardtype/fileurl).

Do not apply the hotkey's frontmost-app rejection after the Service has activated
FileShift: invocation itself can change focus. The Services path uses supplied
URLs, not a later Apple Events query. Validate its actual Finder invocation
behavior separately; it is not an authorization mechanism for arbitrary callers.

## Consent and least permissions

The signed application needs a meaningful `NSAppleEventsUsageDescription`, for
example “Read the files you selected in Finder when you invoke FileShift.” A
hardened-runtime build also needs the Apple Events automation entitlement to
request permission for another app. Neither setting guarantees consent.
[Usage description](https://developer.apple.com/documentation/bundleresources/information-property-list/nsappleeventsusagedescription),
[Automation entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.security.automation.apple-events).

Use `AEDeterminePermissionToAutomateTarget` to distinguish permission state and
request consent only during an explicit Finder invocation. Apple's security
session describes permitted, prompt-required, target-not-running, and error
results. Map denial to an actionable status, not repeated prompts or an empty
successful selection. Recovery: explain System Settings → Privacy & Security →
Automation → FileShift → Finder; after enabling, retry from Finder. Test initial
denial, cancellation, revocation, and reauthorization using the installed app's
identity, not just Script Editor or a terminal process.
[Apple security session](https://developer.apple.com/videos/play/wwdc2019/701/),
[Automation settings](https://support.apple.com/guide/mac-help/mchl07817563/mac).

Avoid Accessibility/UI scripting, event taps, and broad input monitoring in this
slice. They are unnecessary to the proposed event-registration and Finder
scripting design; absence of prompts still needs installed-build evidence. Do
not request Full Disk Access. Automation authorization does not prove access to
the selected files: protected locations have separate file-access controls.
Report a file-access failure rather than broadening permissions automatically.
[Apple file-access security](https://support.apple.com/guide/security/secddd1d86a6/web).

## Configurable shortcut, activation, and conflicts

Evaluate legacy HIToolbox `RegisterEventHotKey`/`UnregisterEventHotKey` from a small
native shim with an event handler. The target SDK's headers must confirm exact
signatures, event constants, and error meanings; a complete current Apple web
reference was not found in this investigation. Retain returned registration
handles, surface failed registration as a structured error, and test duplicate
registration from a second process. Do not claim that a successful return detects
every reserved system or application shortcut.

Record key combinations in settings and provide capture, registration feedback,
and a “press to verify” step. Prefer Command or Control in the initial suggestion;
do not promise a universally free default. Rebinding should keep the prior working
registration until the new one succeeds, then release the old one; verify restart
persistence, keyboard layout changes, and rejection recovery. Apple's engineer
documents modifier restrictions introduced in macOS Sequoia and a later 15.2 beta
change, demonstrating that behavior depends on OS build. This source does not
establish every later release's behavior.
[Apple hotkey engineering response](https://developer.apple.com/forums/thread/763878).

A registered shortcut requires its host to be available. Prototype a small
menu-bar app enabled at login through `SMAppService`; the framework supports
login items and helper registration on macOS 13+, subject to user approval.
Expose disabled/requires-approval state and removal. Using this candidate would
require an explicit supported-version decision after testing; older systems
need separate investigation. Services remain an on-demand entry point.
[SMAppService](https://developer.apple.com/documentation/servicemanagement/smappservice).

## Context-action alternatives and packaging

| Candidate | Assessment for this prototype |
| --- | --- |
| App-bundled Service | First experiment: selected file input and small packaging footprint. Finder right-click visibility, activation timing, file type declarations, and discovery after installation remain native acceptance items. |
| Packaged Quick Action | Fallback if Service discoverability fails. Apple documents file-input Quick Actions in Finder and Services. Ship the workflow or native action as part of installation; do not require users to author an Automator workflow. Exact right-click presentation and installation/uninstallation need proof. |
| Finder Sync extension | Poor default fit: Apple describes sync-oriented UI in managed folders; `selectedItemURLs()` is valid only during menu construction/actions and can return nil outside managed directories. It is not a general hotkey selection API. Do not monitor the filesystem root to manufacture coverage. |

[Quick Action guide](https://support.apple.com/guide/automator/aut73234890a/mac),
[Finder Sync scope](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/Finder.html),
[selectedItemURLs restrictions](https://developer.apple.com/documentation/findersync/fifindersynccontroller/selecteditemurls()).

Propose a Developer ID signed, hardened, notarized application for direct
distribution first. Apple documents these protections and notarization for
outside-store software; include all shipped executable components in packaging
verification. This is a proposal, not a completed signing or license decision.
[Apple notarization guide](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution).

Hardened Runtime and App Sandbox are separate choices. The Mac App Store requires
App Sandbox; sandboxed Apple Events need additional target entitlements or
exceptions. Inspect Finder's actual scripting groups rather than assuming an
entitlement. Sandboxed input access also does not establish permission to create
a sibling output. Prototype that separately before distribution selection; no
App Store compatibility claim is justified here.
[App Sandbox](https://developer.apple.com/documentation/security/app_sandbox),
[Apple Events sandbox exceptions](https://developer.apple.com/library/archive/documentation/Miscellaneous/Reference/EntitlementKeyReference/Chapters/AppSandboxTemporaryExceptionEntitlements.html).

## Future ownership and installed-build acceptance

After the baseline gate, assign one implementation owner `platform/macos/**`
(AppKit host, shortcut/selection/Services adapters, bundle metadata, prototype
packaging). Assign a separate review owner the shared Rust adapter contracts;
agree any contract changes before editing outside the platform directory. A
native acceptance owner records `docs/evidence/macos-prototype.md` and supplies
README compatibility evidence only after observed results. No files in those
proposed scopes were implemented by this investigation.

- Record exact macOS build, CPU architecture, Finder version, Xcode/SDK, Rust
  toolchain, package digest, signing identity/entitlements, and GUI session.
- Install as a normal user from the intended package. After setup/login, invoke
  both entry points without terminal use or a manual app launch.
- In multiple Finder windows and view modes, preserve real multi-selection,
  Unicode, spaces, newlines, and metacharacters. Exercise no selection, desktop,
  rapid focus changes, unsupported foreground apps, and stale files.
- Exercise Automation allow, deny, cancel, revoke, recover; verify the correct
  application is named in consent. Check protected folders independently and
  confirm no unnecessary Accessibility, Input Monitoring, or Full Disk Access.
- Prove right-click discovery, selection snapshot timing, cold/warm activation,
  keyboard choice, Escape, outside-click dismissal, and multi-display placement.
- Test duplicate/reserved shortcuts, rejected registration, successful rebind,
  failed rebind preserving the old shortcut, settings persistence, and login-item
  disable/re-enable. Record measured idle CPU/RSS and cold/warm latency.
- Verify uninstall removes action/login registration. Keep macOS prototype and
  cross-platform feasibility gates open until these checks have native evidence.
