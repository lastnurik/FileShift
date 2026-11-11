#!/bin/sh
# Source this file from the repository root for the workspace-local Rust installation.
if [ ! -x "$PWD/.tools/cargo/bin/rustup" ]; then
    printf '%s\n' 'Run this from the FileShift root after installing the local Rust toolchain.' >&2
    return 1 2>/dev/null || exit 1
fi
export CARGO_HOME="$PWD/.tools/cargo"
export RUSTUP_HOME="$PWD/.tools/rustup"
export PATH="$CARGO_HOME/bin:$PATH"
