#!/usr/bin/env python3
"""Observe the installed gateway's redacted missing-executable error dialog."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from native_action_smoke import (action, cleanup_owned_process, descendants,
                                 process_start, wait_for, window)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="show and dismiss a temporary setup-error dialog")
    args = parser.parse_args()
    if not args.run:
        parser.error("--run is required to exercise the desktop")
    title = "FileShift setup required"
    if window("zenity", title) is not None:
        parser.error("Close the existing FileShift setup dialog first")
    with tempfile.TemporaryDirectory(prefix="FileShift-setup-smoke-") as temporary:
        root = Path(temporary)
        binary = root / "private executable fixture"
        binary.write_text("#!/bin/sh\nexit 0\n")
        binary.chmod(0o700)
        command = [sys.executable, str(Path(__file__).with_name("setup_prototype.py")),
                   "install", "--binary", str(binary), "--scripts-dir", str(root / "scripts")]
        subprocess.run(command, check=True, capture_output=True)
        binary.unlink()
        child = None
        record = None
        try:
            child = subprocess.Popen([str(root / "scripts/FileShift Prototype")],
                                     start_new_session=True, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            record = {"pid": child.pid, "start": process_start(child.pid)}
            popup = wait_for(lambda: window("zenity", title, child.pid))
            message = "FileShift prototype executable is unavailable; reinstall the prototype."
            if not any(item.get_role_name() == "label" and item.get_name() == message
                       for item in descendants(popup)):
                raise RuntimeError("Expected redacted setup message was not visible")
            button = next(item for item in descendants(popup) if item.get_role_name() == "button")
            action(button, "click")
            stdout, stderr = child.communicate(timeout=12)
            wait_for(lambda: window("zenity", title, child.pid) is None)
            if child.returncode != 1 or stdout or stderr != (message + "\n").encode():
                raise RuntimeError("Setup failure did not preserve redacted diagnostics")
            print(json.dumps({"missing_executable_dialog": "passed", "redacted_diagnostics": "passed"}))
        finally:
            try:
                cleanup_owned_process(record)
                if child is not None:
                    child.wait(timeout=5)
            finally:
                command[2] = "remove"
                subprocess.run(command, check=True, capture_output=True)


if __name__ == "__main__":
    main()
