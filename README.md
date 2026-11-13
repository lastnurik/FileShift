# FileShift

FileShift is a planned Rust desktop utility for converting files selected in a native
file manager. The product contract is in [PROJECT.md](PROJECT.md), terminology in
[CONTEXT.md](CONTEXT.md), and implementation sequence in [WORKFLOW.md](WORKFLOW.md).

There is no working converter or native installation package yet. No Windows, macOS,
or Ubuntu desktop integration has passed full native acceptance. A GNOME Files
action-handler smoke check reaches a visible popup and passes keyboard dismissal;
actual right-click menu acceptance remains open.

## Development environment

The current workspace has a local Rust installation under `.tools/` (ignored by Git).
From the repository root, enable it in the current shell:

```sh
. ./scripts/dev-env.sh
rustc --version
cargo --version
```

Verified on Ubuntu 26.04.1 LTS, GNOME Shell 50.1, Wayland, GNOME Files 50.2.2:
Rust/Cargo 1.99.1, rustfmt and Clippy are available; a temporary offline Cargo project
compiled, passed its smoke test, and ran. This verifies the toolchain, not FileShift.
The local installation is not part of a source checkout. For a clean Ubuntu source
checkout, install Rust with rustup and the system C linker toolchain, then run:

```sh
cargo build --workspace --locked --offline
cargo test --workspace --locked --offline
cargo clippy --workspace --all-targets --locked --offline -- -D warnings
python3 -m unittest discover -s platform/linux/tests -v
```

Build and tests also pass from a clean source archive with the host Rust/Cargo
1.99.1 toolchain on the environment above. The Cargo
workspace has no third-party dependencies. Python 3 is used only for developer
script setup/tests. The disposable Linux popup requires `/usr/bin/zenity`
(tested command interface: 4.2.1). Example without opening a popup:

```sh
target/debug/fileshift-prototype --check --nautilus-script -- README.md
```

The diagnostic output contains accepted/rejected counts and no paths. The real
popup is a clearly marked selection-inspection prototype with no conversion routes.
An opt-in native action-handler smoke check is also available on the tested host
with system Python GI and AT-SPI introspection installed:

```sh
python3 platform/linux/native_action_smoke.py --run --keyboard --freeze-check --decoy-window \
  --binary "$PWD/target/debug/fileshift-prototype"
```

It temporarily installs an owned script, opens a disposable fixture window and
popup, verifies its accessible state/counts, then removes the script and closes
its window. It refuses an existing script or popup. This passed on the named Ubuntu environment,
including exact selection, isolation from another window, frozen popup state,
Tab/Shift+Tab focus and Escape dismissal. Keyboard input uses a temporary,
version-specific Mutter test session; it is not part of product activation.

Native unusual-name, mixed-selection and empty-view cases also passed with
`--case unusual`, `--case mixed`, and `--case empty` respectively. The mixed case
requires an unprivileged user for its unreadable-file check. A redacted missing
executable dialog was verified with:

```sh
python3 platform/linux/native_setup_error_smoke.py --run
```

Actual context-menu navigation remains unverified. `--manual-menu` opens a
five-minute observation window; the previous wait expired without an invocation.
Native popup anchoring, tabs, remote views and restart/login remain open.

See the [prototype procedure](docs/research/ubuntu-prototype-procedure.md) for
staging, developer installation/removal, and pending native checks. No native
installer/package, global shortcut, or platform compatibility is established.

## Work tracking

The public repository is [lastnurik/FileShift](https://github.com/lastnurik/FileShift).
The [approved specification](https://github.com/lastnurik/FileShift/issues/1) and twelve
implementation tickets are published with native blocking links. The
[implementation proposal](docs/continuation-proposal.md) defines public test seams
and dependencies; local ticket records are in `.scratch/fileshift/issues/`.
See [bootstrap evidence](docs/bootstrap-evidence.md) for checks and open blockers.

The approved design baseline is commit
`1a75db0e1f32b22391a86a9ccde309611ec43cdd`, pushed through SSH to
`git@github.com:lastnurik/FileShift.git`. The latest session permits Git metadata
writes directly; initial setup required
approved escalation under the earlier sandbox. SSH uses an explicit empty config and
strict host-key checking because the default system include has an ownership issue
in this session. No SSH keys or system configuration were changed.

## Native integration research

Primary-source findings and proposed acceptance procedures are recorded for
[Ubuntu/GNOME Files](docs/research/ubuntu-integration.md),
[Windows Explorer](docs/research/windows-integration.md), and
[macOS Finder](docs/research/macos-integration.md). These are research, not native
support claims. Full converter work remains gated by integration feasibility.

## License

FileShift source and documentation use the [MIT license](LICENSE). Third-party
redistribution terms must be reviewed when dependencies and native packages are selected.
