#!/usr/bin/env python3
"""Debug-only isolated desktop context-menu loop; never use the host desktop."""

import argparse
import json
import os
from pathlib import Path
import pwd
import signal
import stat
import subprocess
import sys
import tempfile
import time


def report(stage, **details):
    print(json.dumps({"stage": stage, **details}), flush=True)


def require_isolation(args):
    root = args.isolation_root.resolve(strict=True)
    real_home = Path(pwd.getpwuid(os.getuid()).pw_dir).resolve()
    if not root.is_relative_to(Path("/tmp")) or root == Path("/tmp") or root == real_home:
        raise RuntimeError("Refusing a non-disposable isolation root")
    for key in ("HOME", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_RUNTIME_DIR"):
        value = Path(os.environ.get(key, "/")).resolve()
        if value == root or not value.is_relative_to(root):
            raise RuntimeError(f"{key} must be a directory below the isolation root")
        if value == real_home:
            raise RuntimeError("Refusing the desktop user's real home")
    display = os.environ.get("DISPLAY")
    if args.backend == "x11":
        if not display or display == args.host_display or os.environ.get("WAYLAND_DISPLAY"):
            raise RuntimeError("Requires a separate X11 display with WAYLAND_DISPLAY unset")
    else:
        socket_name = os.environ.get("WAYLAND_DISPLAY", "")
        if display or not socket_name or Path(socket_name).is_absolute():
            raise RuntimeError("Requires only a relative private Wayland socket, without DISPLAY")
        socket = (Path(os.environ["XDG_RUNTIME_DIR"]) / socket_name).resolve(strict=True)
        if not socket.is_relative_to(root) or not stat.S_ISSOCK(socket.stat().st_mode):
            raise RuntimeError("Wayland socket must belong to the isolated runtime")
    bus = os.environ.get("DBUS_SESSION_BUS_ADDRESS")
    if not bus or bus == args.host_bus_address:
        raise RuntimeError("Requires a separate dbus-run-session bus")
    if args.backend == "wayland" and f"unix:path={os.environ['XDG_RUNTIME_DIR']}/" not in bus:
        raise RuntimeError("Wayland input bus must be hosted in the isolated runtime")
    if not args.binary.is_absolute():
        raise RuntimeError("Prototype executable path must be absolute")


class DesktopInput:
    """Version-specific test input; never imported by the product executable."""

    def __init__(self, backend):
        self.backend = backend
        self.bus = None
        self.session = None

    def __enter__(self):
        if self.backend == "wayland":
            import dbus
            self.bus = dbus.SessionBus(private=True)
            try:
                properties = dbus.Interface(self.bus.get_object("org.gnome.Shell", "/org/gnome/Shell"),
                                            "org.freedesktop.DBus.Properties")
                properties.Set("org.gnome.Shell", "OverviewActive", dbus.Boolean(False), timeout=3)
                manager = dbus.Interface(self.bus.get_object("org.gnome.Mutter.RemoteDesktop",
                    "/org/gnome/Mutter/RemoteDesktop"), "org.gnome.Mutter.RemoteDesktop")
                path = manager.CreateSession(timeout=3)
                self.session = dbus.Interface(self.bus.get_object("org.gnome.Mutter.RemoteDesktop", path),
                                             "org.gnome.Mutter.RemoteDesktop.Session")
                self.session.Start(timeout=3)
            except Exception:
                self.__exit__(None, None, None)
                raise
        return self

    def __exit__(self, *_):
        try:
            if self.session is not None:
                self.session.Stop(timeout=3)
        finally:
            if self.bus is not None:
                self.bus.close()

    def click(self, button, x=None, y=None):
        if self.backend == "x11":
            command = ["xdotool"]
            if x is not None:
                command.extend(["mousemove", str(x), str(y)])
            subprocess.run([*command, "click", str(button)],
                           check=True, capture_output=True, timeout=3)
        else:
            import dbus
            if x is not None:
                # The private compositor has exactly one 1280x800 monitor.
                self.session.NotifyPointerMotionRelative(-100000.0, -100000.0, timeout=3)
                time.sleep(0.1)
                self.session.NotifyPointerMotionRelative(float(x), float(y), timeout=3)
                time.sleep(0.1)
                # Clamping passes through GNOME's hot corner; dismiss only this
                # private Shell's overview after motion, before targeting Files.
                properties = dbus.Interface(self.bus.get_object("org.gnome.Shell", "/org/gnome/Shell"),
                                            "org.freedesktop.DBus.Properties")
                properties.Set("org.gnome.Shell", "OverviewActive", dbus.Boolean(False), timeout=3)
                time.sleep(0.3)
            code = dbus.Int32({1: 272, 3: 273}[button])
            try:
                self.session.NotifyPointerButton(code, True, timeout=3)
            finally:
                self.session.NotifyPointerButton(code, False, timeout=3)

    def escape(self):
        if self.backend == "x11":
            subprocess.run(["xdotool", "key", "Escape"], check=True, capture_output=True, timeout=3)
        else:
            import dbus
            try:
                self.session.NotifyKeyboardKeycode(dbus.UInt32(1), True, timeout=3)
            finally:
                self.session.NotifyKeyboardKeycode(dbus.UInt32(1), False, timeout=3)

    def screenshot(self, prefix):
        if self.backend == "wayland":
            # The extracted screenshot client failed in the private headless
            # session and created error UI. Do not contaminate menu/keyboard
            # observations by retrying it during the acceptance sequence.
            report("isolated_screenshot", result="unavailable_private_wayland")
            return
        from PIL import ImageGrab
        fd, path = tempfile.mkstemp(prefix=prefix, suffix=".png")
        os.close(fd)
        ImageGrab.grab(xdisplay=os.environ["DISPLAY"]).save(path)
        report("isolated_screenshot", path=path)


def worker(fixtures, condition, freeze_after_click, backend):
    with DesktopInput(backend) as desktop:
        check_menu(fixtures, condition, freeze_after_click, desktop)


def check_menu(fixtures, condition, freeze_after_click, desktop):
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    Atspi.set_timeout(600, 600)

    def children(node):
        node.clear_cache()
        for index in range(node.get_child_count()):
            child = node.get_child_at_index(index)
            if child is not None:
                yield child

    def walk(node, depth=0):
        if depth > 25:
            return
        yield node
        if node.get_name() == "Sidebar":
            return
        for child in children(node):
            yield from walk(child, depth + 1)

    def frame():
        for app in children(Atspi.get_desktop(0)):
            if app.get_name() == "org.gnome.Nautilus":
                for child in children(app):
                    if child.get_name() == fixtures.name:
                        return child
        return None

    def wait(predicate, label, seconds=5):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            value = predicate()
            if value:
                return value
            time.sleep(0.08)
        raise RuntimeError(label + " timed out")

    owned = wait(frame, "fixture window", 10)
    if desktop.backend == "x11":
        ids = subprocess.run(["xdotool", "search", "--all", "--onlyvisible", "--pid",
                          str(owned.get_process_id()), "--name", "^" + fixtures.name + "$"],
                         check=True, capture_output=True, text=True, timeout=3).stdout.split()
        if len(ids) != 1:
            raise RuntimeError("Cannot identify a unique isolated X11 fixture window")
        subprocess.run(["xdotool", "windowfocus", "--sync", ids[0]],
                   check=True, capture_output=True, timeout=3)
    else:
        maximize = wait(lambda: next((node for node in walk(owned)
            if node.get_role_name() == "button" and node.get_name() == "Maximize"), None),
            "owned window maximize control")
        interface = maximize.get_action_iface()
        click = next((i for i in range(interface.get_n_actions())
                      if interface.get_action_name(i) == "click"), None)
        if click is None or not interface.do_action(click):
            raise RuntimeError("Could not maximize isolated Files window")
        last_geometry = None
        def maximized():
            nonlocal last_geometry
            owned.clear_cache()
            bounds = owned.get_component_iface().get_extents(Atspi.CoordType.SCREEN)
            active = owned.get_state_set().contains(Atspi.StateType.ACTIVE)
            geometry = (bounds.x, bounds.y, bounds.width, bounds.height, active)
            if geometry != last_geometry:
                report("owned_frame_geometry", x=bounds.x, y=bounds.y,
                       width=bounds.width, height=bounds.height, active=active)
                last_geometry = geometry
            return bounds.width == 1280
        wait(maximized, "maximized isolated Files window")
    cell = wait(lambda: next((node for node in walk(owned)
        if node.get_role_name() == "table cell" and "fixture.txt" in node.get_name()), None),
        "fixture cell")
    # This disposable Xvfb fixture uses the default 890x550 Files window at 0,0.
    # Coordinates were inspected from its private screenshot. GTK's virtual cell
    # SCREEN bounds report 0,0 here, so do not mistake those for screen geometry.
    # Validate the target by selecting the exact fixture before right-clicking.
    x, y = 280, (160 if desktop.backend == "wayland" else 130)
    desktop.click(1, x, y)
    if desktop.backend == "wayland":
        # The bounded fullscreen input probe showed that the first click after
        # leaving Overview was swallowed, while a later click hit exact x,y.
        time.sleep(0.7)
        desktop.click(1)
    def fixture_selected():
        return any(node.get_role_name() == "table cell" and "fixture.txt" in node.get_name()
                   and node.get_state_set().contains(Atspi.StateType.SELECTED)
                   for node in walk(owned))
    try:
        wait(fixture_selected, "pointer targets exact fixture")
    except RuntimeError:
        if desktop.backend == "wayland":
            target = owned.get_component_iface().get_accessible_at_point(x, y, Atspi.CoordType.SCREEN)
            report("target_accessible", role=target.get_role_name() if target else None,
                   name=target.get_name() if target else None)
            desktop.screenshot("fileshift-isolated-wayland-target-")
            report("fixture_target_state", active=owned.get_state_set().contains(Atspi.StateType.ACTIVE),
                   cells=[(node.get_name(), node.get_state_set().contains(Atspi.StateType.SELECTED))
                          for node in walk(owned) if node.get_role_name() == "table cell"])
            report("private_shell_visible", nodes=[(node.get_role_name(), node.get_name())
                for app in children(Atspi.get_desktop(0)) if app.get_name() != "org.gnome.Nautilus"
                for node in walk(app) if node.get_name() and
                node.get_state_set().contains(Atspi.StateType.SHOWING)][:80])
        raise
    if desktop.backend == "wayland":
        owned.clear_cache()
        report("owned_files_focus", active=owned.get_state_set().contains(Atspi.StateType.ACTIVE),
               targeting_guard="exact fixture selected by physical click")
    report("fixture_ready", x=x, y=y)
    desktop.click(3)
    report("right_click_sent")
    if freeze_after_click:
        os.kill(owned.get_process_id(), signal.SIGSTOP)
        report("detector_calibration", injected="owned Files process stopped")

    def menu_visible():
        return any(node.get_role_name() in ("menu", "popup menu", "menu item") and
                   node.get_state_set().contains(Atspi.StateType.SHOWING)
                   for node in walk(owned))

    menu_error = None
    try:
        wait(menu_visible, "context menu visible")
        time.sleep(0.2)
        wait(menu_visible, "context menu remains visible")
        report("menu_open", result="passed")
        desktop.screenshot("fileshift-isolated-menu-open-")
        if condition == "installed" and desktop.backend == "x11":
            # Grounded in this isolated fixture's menu screenshot (Scripts row).
            desktop.click(1, 330, 217)
            time.sleep(0.5)
            desktop.screenshot("fileshift-isolated-submenu-")
    except RuntimeError as error:
        menu_error = error
        report("menu_open", result="failed", error=str(error))
        desktop.screenshot("fileshift-isolated-menu-")
    desktop.escape()
    if menu_error is None:
        try:
            wait(lambda: not menu_visible(), "context menu dismissal")
            report("menu_dismissed", result="passed")
        except RuntimeError as error:
            menu_error = error
            report("menu_dismissed", result="failed", error=str(error))
    # Closing through the real accessible window action establishes that Files
    # still serves requests after menu construction; no script handler is invoked.
    try:
        interface = owned.get_action_iface()
        if interface is None:
            raise RuntimeError("Files close interface is unresponsive after context menu")
        index = next((i for i in range(interface.get_n_actions())
                      if interface.get_action_name(i) == "window.close"), None)
        if index is None or not interface.do_action(index):
            raise RuntimeError("Files did not accept window close after context menu")
        wait(lambda: frame() is None, "Files window close")
    except Exception as error:
        report("files_responsive_and_closed", result="failed", error=str(error))
        raise
    report("files_responsive_and_closed", result="passed")
    if menu_error is not None:
        raise menu_error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--isolation-root", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--condition", choices=("absent", "installed"), required=True)
    parser.add_argument("--host-display", required=True)
    parser.add_argument("--host-bus-address", required=True)
    parser.add_argument("--backend", choices=("x11", "wayland"), default="x11")
    parser.add_argument("--freeze-after-click", action="store_true",
                        help="calibrate failure detection by stopping only isolated Files")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    require_isolation(args)
    fixtures = args.isolation_root / "FileShift-isolated-menu-fixtures"
    if args.worker:
        worker(fixtures, args.condition, args.freeze_after_click, args.backend)
        return 0

    import dbus
    bus = dbus.SessionBus(private=True)
    try:
        if bus.name_has_owner("org.gnome.Nautilus"):
            raise RuntimeError("Isolated bus already has Files; use a fresh session")
    finally:
        bus.close()
    fixtures.mkdir(exist_ok=True)
    (fixtures / "fixture.txt").write_text("Disposable context-menu fixture.\n")
    scripts = Path(os.environ["XDG_DATA_HOME"]) / "nautilus/scripts"
    if (scripts / "FileShift Prototype").exists():
        raise RuntimeError("Use a fresh isolated home without an existing prototype script")
    setup = Path(__file__).with_name("setup_prototype.py")
    command = [sys.executable, str(setup), "install", "--binary", str(args.binary),
               "--scripts-dir", str(scripts)]
    installed = False
    process = None
    try:
        if args.condition == "installed":
            subprocess.run(command, check=True, capture_output=True)
            installed = True
        report("condition", value=args.condition)
        with (args.isolation_root / "nautilus-menu.log").open("w") as log:
            process = subprocess.Popen(["nautilus", "--new-window", str(fixtures)],
                stdout=log, stderr=log, start_new_session=True)
            # The outer deadline can interrupt this parent's finally block.
            # Publish ownership so it can also clean up this detached session.
            start = Path(f"/proc/{process.pid}/stat").read_text().rsplit(")", 1)[1].split()[19]
            identity = args.isolation_root / "files-process.partial"
            identity.write_text(json.dumps({"pid": process.pid, "start": start}))
            identity.replace(args.isolation_root / "files-process.json")
            # A separate worker gives the entire accessibility/input sequence a
            # hard deadline even if a native accessibility call blocks forever.
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                     *sys.argv[1:], "--worker"], timeout=30)
            return result.returncode
    except subprocess.TimeoutExpired:
        report("worker_deadline", result="failed", seconds=30)
        return 1
    finally:
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        if installed:
            command[2] = "remove"
            subprocess.run(command, check=True, capture_output=True)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        report("failure", error=str(error))
        sys.exit(1)
