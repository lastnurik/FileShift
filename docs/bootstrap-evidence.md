# Bootstrap evidence — 2026-11-12

Status: approved planning/tracker configuration applied; bootstrap is incomplete.
No FileShift code or native prototype has been implemented or tested. AGENTS.md now
links the approved tracker/domain configuration. The initial inspection below is
historical; follow-up results appear at the end.

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
