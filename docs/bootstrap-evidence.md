# Bootstrap evidence — 2026-11-12

Status: bootstrap is complete through approved escalation; a Linux development
prototype is implemented with automated checks. Native platform acceptance is open.
The initial inspection below is historical; follow-up results appear at the end.

## Observed environment

- OS: Ubuntu 26.04.1 LTS (Resolute Raccoon).
- Kernel: Linux 7.0.0-42-generic.
- Desktop/session: `XDG_CURRENT_DESKTOP=ubuntu:GNOME`, `XDG_SESSION_TYPE=wayland`.
- GNOME Shell: 50.1; package `50.1-0ubuntu1.5`.
- GNOME Files: 50.2.2; package `1:50.2.2-0ubuntu0.2`.
- `nautilus --version` returned its version but also emitted read-only Tracker database
  warnings. This command is not evidence of functional desktop integration.
- Git, SSH, GitHub CLI, C compiler and pkg-config are present on PATH.
- Cargo, rustc and rustup are absent from PATH. GTK4/libadwaita development packages and
  python3-nautilus are not installed according to dpkg-query.
- No Windows or macOS native environment has been verified.

## Git and publication

- `git status --short --branch`: not a Git repository.
- `.git` exists as a read-only directory (`dr-xr-xr-x`).
- `git init` failed with `Read-only file system` copying the Git template description.
- The session permits no approval escalation. No chmod, alternate Git directory, or
  other workaround was used. Baseline SHA, task commits, and Git review remain blocked.
- GitHub authentication succeeds for `lastnurik` with repository scope and SSH protocol.
- Public and authenticated owner-repository listing queries returned no case-insensitive
  FileShift match. This is an inspection result, not repository creation.
- `ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 git@github.com`
  failed before authenticating: `Bad owner or permissions on
  /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf`. SSH access is unverified.
- No repository was created and no source or issues published. License selection remains
  required before source publication.

## Documentation investigation

Context7 was resolved first for Nautilus; the only result was an unrelated embroidery
thumbnailer. Relevant Nautilus coverage was unavailable, so official GNOME docs were read:

- [MenuProvider.get_file_items](https://gnome.pages.gitlab.gnome.org/nautilus/vfunc.MenuProvider.get_file_items.html)
  supplies selected files to an extension. The online page identifies library 52.alpha;
  installed Files is 50.2.2, so validate against installed headers/version before use.
- [GNOME Files scripts](https://help.gnome.org/gnome-help/nautilus-behavior.html)
  receive selected local files as arguments. A script is a candidate for the first
  context-action experiment, not proof of direct placement, packaging, shortcut support,
  or arbitrary-filename fidelity.
- [GlobalShortcuts portal](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.GlobalShortcuts.html)
  documents shortcut sessions and activation. It does not itself provide Files selection.
  Do not equate successful shortcut registration with a valid current selection.
- Context7 resolved GitHub CLI to `/websites/cli_github_manual` and queried read-only
  account/repository inspection. See [gh api](https://cli.github.com/manual/gh_api)
  and [gh repo list](https://cli.github.com/manual/gh_repo_list).

No native API mechanism, GUI toolkit or converter dependency was selected from these
pages. Native prototype checks remain open, including active-window selection under
Wayland, popup focus/placement, permissions, installed behavior, and timing/resource use.

## Mandatory checkpoints

- to-spec: confirm proposed public test seams before finalizing/publishing the spec.
- tdd: no tests before the user confirms those seams.
- to-tickets: approve breakdown and blocking edges before creating individual tickets.
- setup-matt-pocock-skills: review tracker/domain configuration draft before applying it.
- code-review: requires a valid concrete Git baseline and nonempty committed diff before
  separate standards/spec agent review. Neither exists yet; review was not claimed.

Concrete proposals are in continuation-proposal.md. Keep independent preparation moving
without treating missing approvals, permissions, toolchains or native evidence as passed.

Astra was available through a read-only delegated review and supplied a concrete Ubuntu
slice, future file ownership, public activation seam, and native acceptance checks. These
were incorporated into the proposal. No changes by Astra needed implementation review;
the formal two-axis code review remains blocked by the missing Git baseline.

## Follow-up after user approval

The user approved the ticket breakdown, dependencies, tracker configuration, and public
test seams, requested Rust installation and resolution of blockers, and confirmed their
GitHub SSH setup.

- Installed official rustup with `--profile minimal --default-toolchain stable
  --component rustfmt,clippy --no-modify-path`. Installer downloaded from
  `https://sh.rustup.rs` over TLS; installation is inside `.tools/` because the session
  cannot write the normal home-directory locations. `.tools/` is ignored by Git.
- Verified rustc 1.99.1 (`58cf8f9c3`, 2026-10-13), Cargo 1.99.1 (`5f94df478`,
  2026-08-27), rustfmt 1.10.0-stable, and Clippy 0.1.99.
- Sourcing `scripts/dev-env.sh` sets CARGO_HOME, RUSTUP_HOME and PATH for this local
  installation. Shell syntax validation passed.
- A temporary Cargo project built and ran offline and passed one smoke test. The
  temporary project was removed. This is compiler/linker verification, not product TDD
  or native acceptance.
- Context7 resolved `/rust-lang/rustup` and documented the installer flags and custom
  installation directories before installation. See [rustup installation docs](https://rust-lang.github.io/rustup/installation/index.html).
- The problematic system SSH include is a symlink exposed as owned by nobody/nogroup;
  it configures systemd local socket/VM transports rather than github.com. No system
  configuration, keys, host-key checking or credential setup was changed.
- `ssh -F /dev/null -T -o BatchMode=yes -o StrictHostKeyChecking=yes
  -o ConnectTimeout=10 git@github.com` returned GitHub's successful authentication
  greeting for `lastnurik`. Exit code 1 is the normal GitHub no-shell result. This
  confirms SSH authentication; default-config invocation still fails before auth.
- Rechecked authenticated owner repository listing: no case-insensitive FileShift match.
- Created twelve approved local tickets and tracker/domain configuration. No public
  issues were created. License decision is requested before source publication.
- `git init` still fails with a read-only `.git` filesystem. There is no approval
  escalation tool in this session. A writable Git metadata mount/session is required
  before baseline creation, task commits, formal Git-diff review, or push.

FS-01 remains open. FS-02 and subsequent implementation tickets remain blocked by the
agreed baseline-first workflow. Windows/macOS native evidence remains unavailable.

## Autonomous continuation and publication

The user subsequently delegated all routine decisions and requested continued work
without further checkpoints. MIT was selected for original source/documentation,
recorded in LICENSE and ADR 0006, and reflected in PROJECT.md. No third-party
dependency redistribution approval is implied.

Completed independently of local Git initialization:

- Created the public repository [lastnurik/FileShift](https://github.com/lastnurik/FileShift)
  after rechecking that no matching owned repository existed. Verified public
  visibility, issues enabled, ADMIN permission, and SSH URL.
- Published the approved [specification](https://github.com/lastnurik/FileShift/issues/1)
  and FS-01 through FS-12 as issues #2 through #13, using body files and the
  `ready-for-agent` label. All thirteen remain open.
- Created and independently read back all fifteen native issue dependency edges.
  The original approved dependency graph is preserved.
- Verified `git ls-remote git@github.com:lastnurik/FileShift.git` succeeds with
  `GIT_SSH_COMMAND='ssh -F /dev/null -o BatchMode=yes -o StrictHostKeyChecking=yes
  -o ConnectTimeout=10'`. The empty result and exit code 0 establish SSH repository
  read access; no source refs exist. This does not configure a local origin or prove push.
- Applied tracker/domain configuration, linked it from AGENTS.md, and maintained
  corresponding local ticket URLs/status. README contains only verified toolchain
  commands and states that no converter/package exists.
- Used independent research agents to inspect primary documentation/source for all
  three platforms. Findings and pending native smoke procedures are under
  `docs/research/`. Astra owns the Ubuntu research and supplied concrete slice and
  acceptance proposals; no implementation changes by agents were accepted unreviewed.

Outstanding gates are unchanged where external evidence is required: `.git` is a
read-only filesystem in this session, native Windows/macOS sessions are unavailable,
and Ubuntu selection/popup behavior is not demonstrated. No source files were uploaded
through APIs to circumvent the baseline/commit restriction. No native package or v1
support is claimed. Formal standards/spec Git-diff review still needs a real baseline.

Final independent preparation checks:

- `statvfs('.git')` reports `ST_RDONLY=True`, confirming a filesystem mount
  restriction rather than a normal writable directory with a missing Git config.
- LICENSE matches the official GitHub MIT template after year/attribution substitution.
- Local README/agent/domain/ADR links, final newlines and whitespace checks passed;
  `sh -n scripts/dev-env.sh` passed and sourcing it still resolves Rust/Cargo 1.99.1.
- Read back FS-01 on GitHub: it remains open with baseline initialization, baseline
  SHA, SSH origin/source push and formal review/task commit still unchecked.
- Added primary-source research updates to the Ubuntu right-click/shortcut, Windows,
  and macOS tickets. Parent specification was not modified or closed.
- Ubuntu follow-up ruled out invoking existing script actions directly over the
  exported GTK window action group. A version-specific native extension gateway plus
  Shell companion is a source-supported candidate. Its fixed action name, lazy
  registration, fresh active-tab selection, focus races, popup arrival, settings and
  installed lifecycle all still require native evidence. No extension was installed.

No user decision or approval is pending for routine work. The remaining baseline gate
requires a writable Git metadata session; Windows/macOS acceptance requires native
environments. These cannot be supplied by the current execution tools. All tracked
implementation and release acceptance remains open.

## New-session permission recheck and baseline

2026-11-12: `/status` is not an exposed session tool; attempting it through the
shell returned no such file or directory. Effective settings report workspace-write
and enabled network. Direct checks verified workspace temporary-file creation and
HTTPS github.com HTTP 200. `statvfs(.git)` still reports ST_RDONLY in the sandbox,
and ordinary git init failed. Normal approval escalation succeeded; no filesystem
permissions, mount, or alternate metadata directory was changed.

- Initialized Git, set branch main and SSH origin.
- Preserved all 52 existing project/design files in baseline
  `1a75db0e1f32b22391a86a9ccde309611ec43cdd` before implementing.
- Pushed main successfully over SSH using the previously verified explicit config
  and strict host-key checking; upstream tracking was established.
- Read installed to-spec, to-tickets, tdd and code-review skills. User approvals
  already cover specification, tickets, dependencies and public seams.
- No native integration acceptance was established by these checks.

## FS-02 development implementation

Implemented a dependency-free Cargo workspace with a desktop-independent activation
model, Linux local-path validator, Zenity diagnostic presenter and Nautilus script
setup/removal. Astra owned the script gateway and native procedure; the coordinator
reviewed its code and independently ran both gateway checks. No converter exists.

Observed TDD: snapshot test failed on missing public types, passed after the model;
empty/unsupported status test failed on missing variants, passed after handling;
CLI validation test failed on absent output, passed after validation/presentation.
Astra reports individual red/green gateway setup and removal tests. Final checks:
Cargo test (3 tests), Clippy -D warnings, rustfmt, gateway unittest (2 tests), and
workspace-staged install/remove and direct --check invocation. No dependency download is required.

Context7 could not resolve Zenity (only unrelated names returned). Used installed
GNOME Zenity 4.2.1 help pages info.page/usage.page and --help-info/--help-general for
command flags/exit codes; the former web help URL returned 404. GTK4-rs was resolved
but not selected: GTK development packages are absent, and a disposable existing
Zenity presenter is sufficient for this experiment without settling the GUI toolkit.

Environment remains Ubuntu 26.04.1 LTS, GNOME Shell 50.1, Wayland, Files 50.2.2,
Zenity 4.2.1. Automated native-app control is unavailable in this session (browser
control is available only); no Files interaction or popup observation was performed.
FS-02 remains open for real selection, popup focus/placement, keyboard/Escape,
setup failure feedback and native installation/removal. FS-03 and Windows/macOS
native acceptance remain open; the feasibility gate still blocks full conversion.

FS-02 independent standards review found GNOME presentation text in the core.
Moved that wording into the Linux presenter; core returns structured status codes.
Spec review confirmed native requirements remain pending and requested historical
ticket text corrections; those are applied. Rechecked Cargo tests, Clippy,
formatting and gateway checks after the review fix.

## Unrestricted-session continuation and native action smoke

The subsequent session reports danger-full-access with enabled network and no
approval prompts. Direct statvfs now confirms .git is writable. Configured the
previously verified explicit SSH command locally and pushed FS-01 and FS-02.
Final review rechecks: standards finding resolved; spec reviewer found no new
incorrect behavior, with native requirements correctly left open.

Native Python GI/AT-SPI is available despite the browser tool lacking native
computer APIs. Installed the developer script and opened only disposable Files
fixture windows. A repeatable native_action_smoke.py now verifies real Files
selection → installed script action handler → showing/active Zenity popup with
2 accepted, 0 rejected → Close button dismissal. The successful run cleaned up
its script and fixture window. A failed early harness attempt was corrected for
the installed action-name binding and asynchronous selection delivery; leftover
owned scripts/windows were removed. No existing scripts were overwritten.

An Escape synthesis return of true did not close the dialog; event delivery is
unproven and Escape remains unverified. Actual context-menu interaction, exact
argument identity, full keyboard flow, placement and broader native cases remain
open. This is a native action-handler smoke, not completed FS-02 or Ubuntu support.
See docs/research/ubuntu-prototype-procedure.md for command, versions and limits.

A clean source archive of commit b6b5301 was extracted into a temporary directory
without .tools or target. Using the verified host Rust/Cargo toolchain, offline
workspace build, all 3 Rust tests and both Python gateway tests passed from that
archive. This checks source completeness on this Ubuntu host, not a clean-machine
native package installation or another platform.

Native smoke review identified timeout cleanup ownership and the need to enforce
ACTIVE on future passes. Astra hardened the launcher/process-group tracking,
bounded fixture-window cleanup, exact argv/cwd observation and active-state check.
The coordinator independently reran the native helper successfully: exact fixture
selection passed, popup SHOWING/ACTIVE true, and Close passed. Private fixture
paths existed only in the removed temporary directory; default diagnostics remain
redacted. Physical right-click and keyboard/Escape acceptance remain open.

Failure-path verification invoked the native smoke with /bin/false as a deliberately
failing process boundary. It exited 1 after the expected popup timeout. Independent
inspection found zero owned fixture windows and no installed prototype script.
This checks timeout cleanup without claiming keyboard or menu acceptance.

## FS-02 continuation — 2026-11-13

Native handler checks now cover exact unusual-name delivery (7 accepted), mixed
selection (2 accepted, 4 rejected), empty local-view status, frozen popup state and
isolation from a second Files window. Test-only private Mutter 50.1 input verified
Tab/Shift+Tab focus and observed Escape dismissal on the owned active popup.
No clipboard/screen capture or product activation dependency was added. Focus is
rechecked immediately before each key-down; modifiers/session are released on exit.

Observed failures led to minimal harness corrections: stale accessibility objects,
startup action registration, disabled Select All on an empty view, and retaining
owned frame identity across title changes. A red/green public gateway check exposed
an unredacted missing-executable shell error; gateway v2 now shows a visible generic
setup dialog and redacted stderr. Exact legacy v1 removal remains supported.
Native staged-gateway setup-error UI verification passed.

All six Rust tests and four gateway tests, rustfmt and Clippy passed. Actual
right-click-menu observation was requested once; its five-minute wait expired and
cleaned up without an invocation. It remains open, alongside broader tabs, remote
views, pointer anchoring and restart/login evidence. FS-02 is not closed, and the
full converter feasibility gate is unchanged. Full commands and results are in
docs/research/ubuntu-prototype-procedure.md.

The final independent standards review confirmed the immediate per-key focus check
resolved its input-scope finding. Standards: zero remaining findings. Spec: zero
new findings; the actual context-menu checkbox correctly remains open. Astra's
CLI regression additions were independently run by the coordinator; no unreviewed
agent implementation was accepted.

## User-reported Files lockup — investigation open

The user reports right-click and window closing stopped responding after the
published installation commands, and removing the script restored Files. The
normal desktop script is absent. Installation guidance is withdrawn; FS-02 is
blocked and FS-03 must not advance. Prior action-handler checks did not cover
context-menu construction.

Added a guarded isolated menu diagnostic and Xvfb/session-bus runner. Fresh X11
controls with script absent/installed pass actual right-click, menu dismissal and
Files-close responsiveness. The installed Scripts submenu was visually confirmed
on a private screenshot. A deliberate SIGSTOP calibration fails the same checks;
this is detector validation, not reproduction of the user's bug. Private headless
Wayland baseline remains inconclusive (menu opens, Escape not observed, accessible
close still works), so no installed Wayland pass or product fix is claimed.

The investigation used temporary homes/displays/buses and extracted development
tools; it did not reinstall into the user's real desktop or restart real Files.
See docs/research/ubuntu-menu-lockup.md. Root cause remains unconfirmed pending
exact before-menu/after-invocation evidence and a matching controlled reproduction.
