#!/usr/bin/env python3
"""Opt-in native Files action-handler smoke; does not establish right-click support."""

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from urllib.parse import quote

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi


def children(node):
    for index in range(node.get_child_count()):
        child = node.get_child_at_index(index)
        if child is not None:
            yield child


def application(name):
    desktop = Atspi.get_desktop(0)
    desktop.clear_cache()
    return next((app for app in children(desktop) if app.get_name() == name), None)


def window(application_name, title, owned_group=None):
    app = application(application_name)
    if app is None:
        return None
    app.clear_cache()
    for item in children(app):
        if item.get_name() != title:
            continue
        if owned_group is not None:
            try:
                if os.getpgid(item.get_process_id()) != owned_group:
                    continue
            except ProcessLookupError:
                continue
        return item
    return None


def descendants(node, depth=0):
    if depth > 40:
        raise RuntimeError("Accessibility tree exceeded the smoke-check depth limit")
    if node.get_name() == "Sidebar":
        return
    yield node
    for child in children(node):
        yield from descendants(child, depth + 1)


def wait_for(predicate):
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(0.1)
    raise RuntimeError("Timed out waiting for the fixture action or popup")


def action(node, name):
    interface = node.get_action_iface()
    index = next((i for i in range(interface.get_n_actions())
                  if interface.get_action_name(i) == name), None)
    if index is None or not interface.do_action(index):
        raise RuntimeError("Required native fixture action is unavailable")


def close_popup(popup):
    button = next(item for item in descendants(popup)
                  if item.get_role_name() == "button" and item.get_name() == "Close")
    action(button, "click")


def process_start(pid):
    # Linux stat field 22; the parenthesized command can itself contain spaces.
    return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19]


def launch_record(path):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def cleanup_owned_process(record):
    if record is None:
        return
    pid = record["pid"]
    try:
        if process_start(pid) == record["start"] and os.getpgid(pid) == pid:
            os.killpg(pid, signal.SIGTERM)
    except (FileNotFoundError, ProcessLookupError):
        pass


def cleanup_fixture_window(title):
    # A launch can succeed even if the initial accessibility discovery timed out.
    # Keep looking briefly, but only ever close this randomly named fixture frame.
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        frame = window("org.gnome.Nautilus", title)
        if frame is not None:
            action(frame, "window.close")
            return
        time.sleep(0.1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true",
                        help="open a disposable Files window, install an owned script, and show a popup")
    parser.add_argument("--binary", required=True, type=Path)
    args = parser.parse_args()
    if not args.run:
        parser.error("--run is required because this check changes the desktop temporarily")
    if window("zenity", "FileShift Prototype") is not None:
        parser.error("Close the existing FileShift Prototype popup before running this check")
    Atspi.set_timeout(1500, 1500)
    scripts = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "nautilus/scripts"
    setup = Path(__file__).with_name("setup_prototype.py")
    with tempfile.TemporaryDirectory(prefix="FileShift-native-smoke-") as temporary:
        root = Path(temporary)
        fixtures = root / ("fixtures-" + root.name)
        fixtures.mkdir()
        record_path = root / "launch.json"
        proxy = root / "launch-prototype"
        proxy.write_text(
            "#!/usr/bin/python3\n"
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "os.setsid()\n"
            "pid = os.getpid()\n"
            "start = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19]\n"
            f"Path({str(record_path)!r}).write_text(json.dumps({{'pid': pid, 'start': start, "
            "'cwd': os.getcwd(), 'argv': sys.argv[1:]}))\n"
            f"os.execv({str(args.binary)!r}, [{str(args.binary)!r}, *sys.argv[1:]])\n"
        )
        proxy.chmod(0o700)
        command = [sys.executable, str(setup), "install", "--binary", str(proxy),
                   "--scripts-dir", str(scripts)]
        subprocess.run(command, check=True, capture_output=True)
        frame = None
        launch_requested = False
        try:
            names = ["first space.png", "second-雪.png"]
            for name in names:
                (fixtures / name).write_bytes(b"Selection fixture, not an image.\n")
            launch_requested = True
            subprocess.run(["nautilus", "--new-window", str(fixtures)], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            frame = wait_for(lambda: window("org.gnome.Nautilus", fixtures.name))
            action(frame, "view.select-all")
            wait_for(lambda: sum(node.get_role_name() == "table cell" and
                                 node.get_state_set().contains(Atspi.StateType.SELECTED)
                                 for node in descendants(frame)) == 2)
            script_action = "view.script_" + quote((scripts / "FileShift Prototype").as_uri(), safe="")
            wait_for(lambda: any(frame.get_action_iface().get_action_name(i) == script_action
                                 for i in range(frame.get_action_iface().get_n_actions())))
            action(frame, script_action)
            record = wait_for(lambda: launch_record(record_path))
            if record["argv"][:2] != ["--nautilus-script", "--"]:
                raise RuntimeError("Native gateway supplied an unexpected invocation")
            received = [(Path(record["cwd"]) / path).resolve()
                        for path in record["argv"][2:]]
            if len(received) != 2 or set(received) != {fixtures / name for name in names}:
                raise RuntimeError("Native gateway did not capture the exact fixture selection")
            popup = wait_for(lambda: window("zenity", "FileShift Prototype", record["pid"]))
            label = wait_for(lambda: next((item for item in descendants(popup)
                         if item.get_role_name() == "label" and
                         item.get_name().startswith("prototype selection:")), None))
            if not label.get_name().startswith("prototype selection: 2 accepted; 0 rejected"):
                raise RuntimeError("Native popup did not report the fixture selection")
            def visible_and_active():
                popup.clear_cache()
                states = popup.get_state_set()
                return (states.contains(Atspi.StateType.SHOWING) and
                        states.contains(Atspi.StateType.ACTIVE))
            wait_for(visible_and_active)
            close_popup(popup)
            wait_for(lambda: window("zenity", "FileShift Prototype", record["pid"]) is None)
            print(json.dumps({"action_handler": "passed", "accepted": 2, "rejected": 0,
                              "exact_fixture_selection": "passed",
                              "popup_showing": True, "popup_active": True,
                              "close_button": "passed", "right_click_menu": "unverified",
                              "keyboard_escape": "unverified"}))
        finally:
            try:
                # Disable new invocations before discovering a late owned launcher.
                command[2] = "remove"
                subprocess.run(command, check=True, capture_output=True)
            finally:
                try:
                    if launch_requested:
                        cleanup_fixture_window(fixtures.name)
                finally:
                    # Never identify the popup by title alone during cleanup. The
                    # isolated process group belongs to the recorded launcher only.
                    deadline = time.monotonic() + 3
                    while time.monotonic() < deadline:
                        record = launch_record(record_path)
                        if record is not None:
                            cleanup_owned_process(record)
                            break
                        time.sleep(0.1)



if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Native smoke check failed: {str(error) if isinstance(error, RuntimeError) else type(error).__name__}. Native acceptance stays open.",
              file=sys.stderr)
        sys.exit(1)
