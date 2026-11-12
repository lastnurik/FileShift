#!/usr/bin/env python3
"""Developer-only Nautilus script setup; never changes shortcuts or starts Files."""

import argparse
import os
from pathlib import Path
import shlex
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["install", "remove"])
    parser.add_argument("--binary", required=True, type=Path,
                        help="absolute path of the built prototype executable")
    parser.add_argument("--scripts-dir", required=True, type=Path,
                        help="explicit staging directory or Nautilus scripts directory")
    args = parser.parse_args()
    if not args.binary.is_absolute() or not args.scripts_dir.is_absolute():
        parser.error("binary and scripts directory must be absolute paths")
    if args.operation == "install" and (
        not args.binary.is_file() or not os.access(args.binary, os.X_OK)
    ):
        parser.error("binary must be an existing executable file")
    # Quote only the configured executable. Selected names remain individual argv.
    content = os.fsencode(
        "#!/bin/sh\n# FileShift development prototype gateway v1\n"
        f'exec {shlex.quote(str(args.binary))} --nautilus-script -- "$@"\n'
    )
    script = args.scripts_dir / "FileShift Prototype"
    try:
        if args.operation == "remove":
            if script.is_symlink() or script.read_bytes() != content:
                print("Refusing to remove a script that differs from this prototype.",
                      file=sys.stderr)
                return 1
            script.unlink()
            print("Prototype script removed; directory and other scripts retained.")
            return 0
        args.scripts_dir.mkdir(parents=True, exist_ok=True)
        # Exclusive creation also refuses existing symlinks, including dangling ones.
        with script.open("xb") as output:
            output.write(content)
            os.fchmod(output.fileno(), 0o700)
    except OSError:
        print("Prototype setup failed; check permissions and existing script. "
              "No existing script was replaced.", file=sys.stderr)
        return 1
    print("Prototype script installed. Native acceptance remains pending.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
