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
from gi.repository import Atspi, GLib


def children(node):
    try:
        count = node.get_child_count()
    except GLib.Error:
        return
    for index in range(count):
        try:
            child = node.get_child_at_index(index)
        except GLib.Error:
            continue
        if child is not None:
            yield child


def application(name):
    desktop = Atspi.get_desktop(0)
    desktop.clear_cache()
    for app in children(desktop):
        try:
            if app.get_name() == name:
                return app
        except GLib.Error:
            # An application can exit between desktop enumeration and lookup.
            continue
    return None


def window(application_name, title, owned_group=None):
    app = application(application_name)
    if app is None:
        return None
    app.clear_cache()
    for item in children(app):
        try:
            if item.get_name() != title:
                continue
            if owned_group is not None:
                if os.getpgid(item.get_process_id()) != owned_group:
                    continue
        except (GLib.Error, ProcessLookupError):
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


def wait_for(predicate, timeout=12):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(0.1)
    raise RuntimeError("Timed out waiting for the fixture action or popup")


def action(node, name):
    def invoke_when_ready():
        node.clear_cache()
        interface = node.get_action_iface()
        index = next((i for i in range(interface.get_n_actions())
                      if interface.get_action_name(i) == name), None)
        return index is not None and interface.do_action(index)
    wait_for(invoke_when_ready)


def close_popup(popup):
    button = next(item for item in descendants(popup)
                  if item.get_role_name() == "button" and item.get_name() == "Close")
    action(button, "click")


def keyboard_dismiss(popup, owned_group):
    """Test-only Mutter 50 input; never part of the product activation path."""
    import dbus

    def require_owned_focus():
        popup.clear_cache()
        if (os.getpgid(popup.get_process_id()) != owned_group or
                not popup.get_state_set().contains(Atspi.StateType.ACTIVE)):
            raise RuntimeError("Owned popup lost focus before keyboard test")

    require_owned_focus()
    bus = dbus.SessionBus(private=True)
    session = None
    started = False
    try:
        manager = dbus.Interface(bus.get_object("org.gnome.Mutter.RemoteDesktop",
                    "/org/gnome/Mutter/RemoteDesktop"), "org.gnome.Mutter.RemoteDesktop")
        session = dbus.Interface(bus.get_object("org.gnome.Mutter.RemoteDesktop",
                    manager.CreateSession()), "org.gnome.Mutter.RemoteDesktop.Session")
        session.Start()
        started = True
        # Linux evdev Tab, then Shift+Tab, then Escape. Verify focus after each
        # navigation step; a successful D-Bus call alone is insufficient evidence.
        def key(code):
            require_owned_focus()
            try:
                session.NotifyKeyboardKeycode(dbus.UInt32(code), True)
            finally:
                session.NotifyKeyboardKeycode(dbus.UInt32(code), False)

        button = next(item for item in descendants(popup)
                      if item.get_role_name() == "button" and item.get_name() == "Close")
        key(15)
        def button_focused():
            button.clear_cache()
            return button.get_state_set().contains(Atspi.StateType.FOCUSED)
        wait_for(button_focused)
        require_owned_focus()
        session.NotifyKeyboardKeycode(dbus.UInt32(42), True)
        try:
            key(15)
        finally:
            session.NotifyKeyboardKeycode(dbus.UInt32(42), False)
        wait_for(button_focused)
        require_owned_focus()
        key(1)
        wait_for(lambda: window("zenity", "FileShift Prototype", owned_group) is None)
    finally:
        try:
            if started:
                session.Stop()
        finally:
            bus.close()


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


def cleanup_fixture_window(title, frame=None):
    # Keep the owned accessible reference: search/tab actions can change its title.
    if frame is not None:
        try:
            action(frame, "window.close")
            return
        except GLib.Error:
            pass
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
    parser.add_argument("--keyboard", action="store_true",
                        help="exercise Tab/Shift+Tab/Escape with test-only Mutter input")
    parser.add_argument("--manual-menu", action="store_true",
                        help="wait up to 5 minutes for a human to invoke the Scripts menu")
    parser.add_argument("--case", choices=["regular", "unusual", "mixed", "empty"], default="regular")
    parser.add_argument("--freeze-check", action="store_true",
                        help="change the fixture selection after popup arrival and check it stays frozen")
    parser.add_argument("--decoy-window", action="store_true",
                        help="open another selected Files view before invoking the fixture action")
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
        decoy_frame = None
        decoy_requested = False
        decoy = root / ("decoy-" + root.name)
        launch_requested = False
        try:
            names = ["first space.png", "second-雪.png"]
            if args.case == "unusual":
                names += ["quote'\".png", "$(touch PWNED).png", "-option.png",
                          "line\nbreak.png", os.fsdecode(b"raw-\xff.png")]
            elif args.case == "empty":
                names = []
            for name in names:
                (fixtures / name).write_bytes(b"Selection fixture, not an image.\n")
            expected_accepted, expected_rejected = len(names), 0
            if args.case == "mixed":
                (fixtures / "directory").mkdir()
                (fixtures / "link.png").symlink_to(fixtures / names[0])
                os.mkfifo(fixtures / "pipe.png")
                (fixtures / "unreadable.png").write_bytes(b"private fixture")
                (fixtures / "unreadable.png").chmod(0)
                if os.access(fixtures / "unreadable.png", os.R_OK):
                    raise RuntimeError("Unreadable native fixture requires an unprivileged user")
                names += ["directory", "link.png", "pipe.png", "unreadable.png"]
                expected_rejected = 4
            launch_requested = True
            subprocess.run(["nautilus", "--new-window", str(fixtures)], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            frame = wait_for(lambda: window("org.gnome.Nautilus", fixtures.name))
            if names:
                action(frame, "view.select-all")
            wait_for(lambda: sum(node.get_role_name() == "table cell" and
                                 node.get_state_set().contains(Atspi.StateType.SELECTED)
                                 for node in descendants(frame)) == len(names))
            script_action = "view.script_" + quote((scripts / "FileShift Prototype").as_uri(), safe="")
            wait_for(lambda: any(frame.get_action_iface().get_action_name(i) == script_action
                                 for i in range(frame.get_action_iface().get_n_actions())))
            if args.decoy_window:
                decoy.mkdir()
                for index in range(3):
                    (decoy / f"decoy-{index}.png").write_bytes(b"Decoy fixture")
                decoy_requested = True
                subprocess.run(["nautilus", "--new-window", str(decoy)], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                decoy_frame = wait_for(lambda: window("org.gnome.Nautilus", decoy.name))
                action(decoy_frame, "view.select-all")
                wait_for(lambda: sum(node.get_role_name() == "table cell" and
                                     node.get_state_set().contains(Atspi.StateType.SELECTED)
                                     for node in descendants(decoy_frame)) == 3)
            if args.manual_menu:
                print("Waiting for right-click → Scripts → FileShift Prototype in the disposable fixture window.", flush=True)
            else:
                action(frame, script_action)
            record = wait_for(lambda: launch_record(record_path), 300 if args.manual_menu else 12)
            if record["argv"][:2] != ["--nautilus-script", "--"]:
                raise RuntimeError("Native gateway supplied an unexpected invocation")
            # Compare lexical paths: resolve() would hide symbolic-link identity.
            expected_paths = {fixtures / name for name in names}
            received = [Path(os.path.abspath(Path(record["cwd"]) / path))
                        for path in record["argv"][2:]]
            if len(received) != len(names) or set(received) != expected_paths:
                raise RuntimeError("Native gateway did not capture the exact fixture selection")
            popup = wait_for(lambda: window("zenity", "FileShift Prototype", record["pid"]))
            label = wait_for(lambda: next((item for item in descendants(popup)
                         if item.get_role_name() == "label" and
                         (item.get_name().startswith("prototype selection:") or
                          item.get_name().startswith("Select regular local files"))), None))
            expected_text = (f"prototype selection: {expected_accepted} accepted; {expected_rejected} rejected"
                             if expected_accepted else "Select regular local files")
            if not label.get_name().startswith(expected_text):
                raise RuntimeError("Native popup did not report the fixture selection")
            def visible_and_active():
                popup.clear_cache()
                states = popup.get_state_set()
                return (states.contains(Atspi.StateType.SHOWING) and
                        states.contains(Atspi.StateType.ACTIVE))
            wait_for(visible_and_active)
            if args.freeze_check:
                if not names:
                    raise RuntimeError("Freeze check requires a nonempty fixture selection")
                action(frame, "view.invert-selection")
                wait_for(lambda: not any(node.get_role_name() == "table cell" and
                                         node.get_state_set().contains(Atspi.StateType.SELECTED)
                                         for node in descendants(frame)))
                label.clear_cache()
                if not label.get_name().startswith(expected_text):
                    raise RuntimeError("Popup changed after the Files selection changed")
            if args.keyboard:
                keyboard_dismiss(popup, record["pid"])
            else:
                close_popup(popup)
            wait_for(lambda: window("zenity", "FileShift Prototype", record["pid"]) is None)
            print(json.dumps({"action_handler": "passed", "case": args.case,
                              "accepted": expected_accepted, "rejected": expected_rejected,
                              "exact_fixture_selection": "passed",
                              "selection_frozen": "passed" if args.freeze_check else "not exercised",
                              "other_window_isolation": "passed" if args.decoy_window else "not exercised",
                              "popup_showing": True, "popup_active": True,
                              "close_button": "not exercised" if args.keyboard else "passed",
                              "right_click_menu": "human confirmation required" if args.manual_menu else "unverified",
                              "keyboard_escape": "passed" if args.keyboard else "unverified"}))
        finally:
            try:
                # Disable new invocations before discovering a late owned launcher.
                command[2] = "remove"
                subprocess.run(command, check=True, capture_output=True)
            finally:
                try:
                    try:
                        if launch_requested:
                            cleanup_fixture_window(fixtures.name, frame)
                    finally:
                        if decoy_requested:
                            cleanup_fixture_window(decoy.name, decoy_frame)
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
