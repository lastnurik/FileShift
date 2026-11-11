# FileShift

FileShift is a planned Rust desktop utility for converting files selected in a native
file manager. The product contract is in [PROJECT.md](PROJECT.md), terminology in
[CONTEXT.md](CONTEXT.md), and implementation sequence in [WORKFLOW.md](WORKFLOW.md).

There is no working converter or native installation package yet. No Windows, macOS,
or Ubuntu desktop integration has passed native acceptance.

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
The local installation is not part of a source checkout; no FileShift Cargo project,
source-build instructions, or package/install commands exist yet.

## Work tracking

The public repository is [lastnurik/FileShift](https://github.com/lastnurik/FileShift).
The [approved specification](https://github.com/lastnurik/FileShift/issues/1) and twelve
implementation tickets are published with native blocking links. The
[implementation proposal](docs/continuation-proposal.md) defines public test seams
and dependencies; local ticket records are in `.scratch/fileshift/issues/`.
See [bootstrap evidence](docs/bootstrap-evidence.md) for checks and open blockers.

GitHub SSH authentication was verified for `lastnurik` using an explicit empty SSH config
and strict host-key checking. Default SSH fails on a system include's ownership as
exposed in this session. Git initialization remains blocked by the session's read-only
`.git` mount, so there are no local commits or configured origin and no source push.
Remote repository access over SSH was verified with `git ls-remote`; the repository
currently has no source commits. The intended origin is
`git@github.com:lastnurik/FileShift.git`.

## Native integration research

Primary-source findings and proposed acceptance procedures are recorded for
[Ubuntu/GNOME Files](docs/research/ubuntu-integration.md),
[Windows Explorer](docs/research/windows-integration.md), and
[macOS Finder](docs/research/macos-integration.md). These are research, not native
support claims. Full converter work remains gated by integration feasibility.

## License

FileShift source and documentation use the [MIT license](LICENSE). Third-party
redistribution terms must be reviewed when dependencies and native packages are selected.
