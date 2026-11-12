# Ubuntu right-click prototype procedure

This is the FS-02 development experiment. It does not convert files or establish
Ubuntu support. FS-03's configurable global shortcut remains separate and open.
The coordinator maintains actual native results; the checks below are a procedure,
not claims that desktop acceptance has passed.

## Invocation contract

The installed `FileShift Prototype` script executes an absolute, configured
`fileshift-prototype` binary as:

```text
fileshift-prototype --nautilus-script -- <individual native path arguments>
```

The script preserves the launch working directory and every argument byte,
including embedded newlines and non-UTF-8 names. It does not split environment
lists, run a shell expression containing selected filenames, or scan a directory.
The Rust executable owns snapshot validation and the diagnostic popup. Empty argv
is ambiguous: a nonlocal selection can produce the same result as no selection.
The prototype must explain that ambiguity instead of claiming an empty selection.

The popup uses the installed Zenity program as disposable prototype plumbing;
this is not a final GUI toolkit or packaging decision. Python is needed only by
the developer setup/check commands, not by the installed shell gateway.

## Source and documentation checks

On 2026-11-12, Context7 resolution for GNOME Nautilus returned generic GNOME
libraries. Querying `/websites/wiki_gnome` did not supply relevant script API
documentation. The fallback was official
[GNOME Files help](https://help.gnome.org/gnome-help/nautilus-behavior.html),
which documents the Scripts submenu, executable script permissions, local selected
files as parameters, and absent parameters for remote folders. Exact Nautilus
50.2.2 argument/source behavior is recorded in
[Ubuntu integration research](ubuntu-integration.md).

## Build, stage and check

From the repository root, build the coordinator's Rust prototype and run the
gateway checks:

```sh
cargo build --bin fileshift-prototype
python3 -m unittest discover -s platform/linux/tests -v
```

Stage a script inside the checkout using explicit absolute paths:

```sh
python3 platform/linux/setup_prototype.py install \
  --binary "$PWD/target/debug/fileshift-prototype" \
  --scripts-dir "$PWD/.scratch/fileshift/staged-nautilus-scripts"
```

The setup command refuses to overwrite any existing destination, including
symlinks. Use a trusted, user-owned directory. It does not start/restart Files,
change shortcuts, or install dependencies. The absolute binary location must
remain present and executable while installed. Move/rebuild into a permanent
location before claiming installed-build support.

For a normal native GNOME Files installation, developer installation uses:

```sh
python3 platform/linux/setup_prototype.py install \
  --binary "$PWD/target/debug/fileshift-prototype" \
  --scripts-dir "${XDG_DATA_HOME:-$HOME/.local/share}/nautilus/scripts"
```

This last command changes the desktop user's files; an agent must use normal
filesystem approval handling when that directory is outside its writable roots.
Do not substitute a sandboxed Files installation without checking its script
location. Install/removal commands are development setup, not native end-user
packages. End-user distribution acceptance remains open.

## Native acceptance

Record OS release, session type, GNOME Shell, Files, and Zenity package versions,
plus the binary revision and script destination. Save evidence without real user
paths. Use disposable fixture files only. Do not force-close Files while the user
has active operations; ask them to close/reopen it if discovery needs a restart.

1. In GNOME Files, select two local fixture files and use right-click → Scripts →
   FileShift Prototype. Observe one directly opened, explicitly marked prototype
   popup with the correct accepted count. No main window or manual binary launch
   should be needed after setup.
2. Navigate the popup using keyboard controls; Escape must dismiss it. Repeat
   with the pointer at different positions and record actual placement/focus.
   Zenity placement does not by itself prove pointer anchoring.
3. Repeat across two Files windows and two tabs with distinct selections. Change
   the Files selection while the popup is open and verify its snapshot stays fixed.
4. Exercise local filenames containing spaces, Unicode, quotes, dollar signs,
   leading dashes, newlines, and non-UTF-8 bytes. The automated gateway test proves
   shell forwarding only; native Files argument delivery remains a separate check.
   Exact identity checks require disposable fixtures and an explicit test observer;
   a count alone does not establish which files arrived.
5. Try directories, symlinks, special files, unreadable and deleted files, a mixed
   selection, and a remote view. Record rejection reasons. Never report empty argv
   as proof of an empty selection. If Files hides the Scripts action with no
   selection, record that behavior rather than marking a popup test as passed.
6. Verify discovery after a clean Files restart, then logout/login when practical.
   Record failed startup (missing executable or Zenity) and whether the user sees
   actionable feedback. Shell stderr alone is not native actionable feedback.
7. Remove and reinstall, preserving other scripts. FS-02 stays open for any missing
   desktop observation; FS-03 and other-platform acceptance remain open regardless.

## Removal

Pass the same absolute binary path used during installation, even if the binary
has since been deleted. Removal verifies exact generated script contents and
refuses a modified script or symlink. It retains the containing directory and
other scripts:

```sh
python3 platform/linux/setup_prototype.py remove \
  --binary "$PWD/target/debug/fileshift-prototype" \
  --scripts-dir "${XDG_DATA_HOME:-$HOME/.local/share}/nautilus/scripts"
```

For the staged script, use the staging directory instead. A changed script needs
manual inspection before removal; the helper intentionally does not force it.

## Automated evidence before the native follow-up

Read-only environment inspection reported Ubuntu 26.04.1 LTS, Wayland,
`XDG_CURRENT_DESKTOP=ubuntu:GNOME`, Nautilus `1:50.2.2-0ubuntu0.2`, GNOME Shell
`50.1-0ubuntu1.5`, and Zenity `4.2.1-1`. These identify the host of the gateway
tests, not a verified native integration environment.

On 2026-11-12 the script gateway tests passed (2 tests). The first test initially
failed before setup existed, then passed after implementation; the second failed
before removal existed, then passed. They verify native argv bytes and cwd at the
launched executable boundary, lack of shell evaluation, refusal to overwrite,
preservation of modified scripts, and removal of an unchanged owned script.
Those gateway checks do not invoke GNOME Files or a real popup. At that stage,
no desktop installation, native selection capture or keyboard interaction had
been observed. The subsequent action-handler evidence is recorded below.

## Native action-handler evidence — 2026-11-12

After the session changed to unrestricted filesystem access, direct checks confirmed
writable Git metadata and HTTPS/SSH network access. Native accessibility inspection
became available through system Python GI/AT-SPI (python3-gi 3.56.2-1,
gir1.2-atspi-2.0 2.60.4-0ubuntu0.1). The named OS/session/Files versions above
were unchanged. This is desktop evidence, narrower than complete native acceptance.

The repeatable opt-in command is:

```sh
python3 platform/linux/native_action_smoke.py --run \
  --binary "$PWD/target/debug/fileshift-prototype"
```

It passed with two disposable local fixtures (space and Unicode names). A private
launcher observer confirmed both exact paths and launch cwd before exec of the
Rust binary; those paths were kept only in the temporary test directory. The
native Files view selected both files; its installed script action handler launched
an accessible, showing, active FileShift Prototype dialog reporting two accepted
and zero rejected files. The Close button dismissed it. The helper removed its
unchanged script and closed only its fixture window. No original or output changed.

This invokes the real action handler through accessibility; it does not exercise
physical right-click or navigate the Scripts submenu. A separate Escape synthesis
attempt returned true but left the popup open under Wayland; delivery is unproven,
so keyboard/Escape acceptance stays open. Pointer anchoring, unusual filename byte cases beyond these fixtures,
multiple-window/tab correctness, failure feedback, invalid/nonlocal item cases,
restart/login and full installed lifecycle also remain unverified.

Context7 resolved AT-SPI Rust documentation and supplied protocol/tree/action
background; Python binding coverage was unavailable. Official GNOME libatspi docs
were checked for [desktop traversal](https://gnome.pages.gitlab.gnome.org/at-spi2-core/libatspi/func.get_desktop.html),
[action invocation](https://gnome.pages.gitlab.gnome.org/at-spi2-core/libatspi/method.Action.do_action.html),
and [keyboard synthesis](https://gnome.pages.gitlab.gnome.org/at-spi2-core/libatspi/func.generate_keyboard_event.html).
The installed binding exposes get_action_name; the newer documentation's get_name
is unavailable on its Action interface, so the helper uses the working deprecated
binding. A synthesis API success return was not treated as observed keyboard delivery.

Review follow-up hardened timeout cleanup: the test launcher uses a new process
session and records its PID/start time. Popup ownership is verified by that process
group; cleanup signals only the matching live group and performs bounded discovery
of the uniquely named fixture window, including when initial discovery failed.
Success now requires both SHOWING and ACTIVE. The coordinator independently reran
the helper and observed exact fixture selection, active/showing popup and Close
all pass. Physical right-click and Escape remain unverified.

Failure-path check: the same helper with /bin/false as its disposable process
boundary returned the expected timeout failure. Independent inspection confirmed
zero owned fixture windows and no remaining installed script after cleanup.
