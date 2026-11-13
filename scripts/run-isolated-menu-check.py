#!/usr/bin/env python3
"""Run the Files context-menu diagnostic on a disposable X11 display and bus."""

import argparse
import json
import os
from pathlib import Path
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time


def stop_group(process):
    if process is None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def stop_recorded_files(root):
    record_file = root / "files-process.json"
    if not record_file.exists():
        return
    record = json.loads(record_file.read_text())
    pid = record["pid"]

    def owned_alive():
        try:
            fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
            return fields[19] == record["start"] and fields[0] != "Z" and os.getpgid(pid) == pid
        except (FileNotFoundError, ProcessLookupError):
            return False

    if not owned_alive():
        return
    os.killpg(pid, signal.SIGTERM)
    # The detector's deliberate SIGSTOP calibration otherwise defers SIGTERM.
    os.killpg(pid, signal.SIGCONT)
    deadline = time.monotonic() + 2
    while owned_alive() and time.monotonic() < deadline:
        time.sleep(0.05)
    if owned_alive():
        os.killpg(pid, signal.SIGKILL)
    print('{"stage":"outer_owned_files_cleanup","result":"terminated"}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", choices=["absent", "installed"], required=True)
    parser.add_argument("--xvfb", type=Path, default=shutil.which("Xvfb"))
    parser.add_argument("--freeze-after-click", action="store_true",
                        help="calibrate detection by stopping only the isolated Files process")
    parser.add_argument("--deadline-seconds", type=float, default=45,
                        help="outer diagnostic deadline, from 1 to 60 seconds")
    args = parser.parse_args()
    if not 1 <= args.deadline_seconds <= 60:
        parser.error("deadline must be between 1 and 60 seconds")
    if args.xvfb is None or not os.access(args.xvfb, os.X_OK):
        parser.error("Provide an available Xvfb executable with --xvfb")
    project = Path(__file__).resolve().parents[1]
    binary = project / "target/debug/fileshift-prototype"
    if not binary.is_file():
        parser.error("Build fileshift-prototype before running the isolated diagnostic")
    host_display = os.environ.get("DISPLAY", "")
    host_bus = os.environ.get("DBUS_SESSION_BUS_ADDRESS", "")
    with tempfile.TemporaryDirectory(prefix="fileshift-menu-isolation-") as temporary:
        root = Path(temporary)
        env = {"PATH": os.environ["PATH"], "LANG": "C.UTF-8"}
        for key, dirname in [("HOME", "home"), ("XDG_DATA_HOME", "data"),
                             ("XDG_CONFIG_HOME", "config"), ("XDG_CACHE_HOME", "cache"),
                             ("XDG_RUNTIME_DIR", "runtime")]:
            directory = root / dirname
            directory.mkdir(mode=0o700)
            env[key] = str(directory)
        env.update(GDK_BACKEND="x11", XDG_SESSION_TYPE="x11", NO_AT_BRIDGE="0",
                   GTK_A11Y="atspi", GIO_USE_VFS="local", GSETTINGS_BACKEND="memory",
                   GSK_RENDERER="cairo")
        services = root / "services"
        services.mkdir()
        (services / "org.a11y.Bus.service").symlink_to(
            "/usr/share/dbus-1/services/org.a11y.Bus.service")
        config = root / "bus.conf"
        config.write_text(
            f'<busconfig><type>session</type><listen>unix:tmpdir={root / "runtime"}</listen>'
            f'<auth>EXTERNAL</auth><servicedir>{services}</servicedir>'
            '<policy context="default"><allow own="*"/><allow send_destination="*"/>'
            '<allow receive_sender="*"/></policy></busconfig>')
        read_fd, write_fd = os.pipe()
        server = None
        child = None
        try:
            with (root / "xvfb.log").open("wb") as log:
                server = subprocess.Popen(
                    [str(args.xvfb), "-displayfd", str(write_fd), "-screen", "0",
                     "1280x800x24", "-nolisten", "tcp"], env=env,
                    pass_fds=(write_fd,), stdout=log, stderr=log, start_new_session=True)
            os.close(write_fd)
            write_fd = None
            if not select.select([read_fd], [], [], 10)[0]:
                raise RuntimeError("Isolated Xvfb startup timed out")
            number = os.read(read_fd, 64).decode().strip()
            if not number.isdigit():
                raise RuntimeError("Isolated Xvfb did not create a display")
            env["DISPLAY"] = ":" + number
            command = ["dbus-run-session", "--config-file", str(config), "--", "python3",
                       str(project / "platform/linux/isolated_menu_repro.py"),
                       "--isolation-root", str(root), "--binary", str(binary),
                       "--condition", args.condition, "--host-display", host_display,
                       "--host-bus-address", host_bus]
            if args.freeze_after_click:
                command.append("--freeze-after-click")
            child = subprocess.Popen(command, env=env, cwd=project, start_new_session=True)
            try:
                return child.wait(timeout=args.deadline_seconds)
            except subprocess.TimeoutExpired:
                raise RuntimeError("Isolated context-menu diagnostic exceeded its deadline")
        finally:
            try:
                stop_group(child)
            finally:
                try:
                    stop_recorded_files(root)
                finally:
                    stop_group(server)
                    os.close(read_fd)
                    if write_fd is not None:
                        os.close(write_fd)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
