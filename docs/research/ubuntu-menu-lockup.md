# FS-02 context-menu lockup investigation

Status: unresolved regression. Desktop installation is withdrawn. The user removed
the script and Files returned to normal; the agent confirmed the script is absent.
No product fix or successful everyday-desktop retest is claimed.

## Report and acceptance impact

After the documented installation, right-click stopped working in Files and its
window could not be closed. Uninstallation restored normal behavior. The exact
boundary (opening the menu versus invoking FileShift) is still being clarified.
FS-02 / GitHub issue #3 remains blocked; FS-03 must not advance on the old checks.

Earlier activation tests invoked the Files-owned script action directly. They
verified selection delivery and the diagnostic popup, but bypassed context-menu
construction. They could not catch this failure. Their results are retained only
as evidence for those narrower behaviors.

Known development versions: Ubuntu 26.04.1 LTS, GNOME Shell/Mutter 50.1, GNOME
Files 50.2.2, Wayland, Zenity 4.2.1. No display settings, extensions, installed
system packages or everyday Files windows were changed for this investigation.

## Isolated feedback loop

`platform/linux/isolated_menu_repro.py` requires a disposable root below `/tmp`,
HOME and every XDG directory below that root, and a distinct private session bus.
Its X11 mode additionally requires a distinct display with host Wayland unset.
The runner starts a fresh Xvfb and a bus that permits activation of only AT-SPI,
without inheriting the host session bus, home, credentials, or Wayland display.

The observable sequence is a physical click selecting the exact disposable
fixture, physical right-click, visible context menu, Escape dismissal, and Files
window-close responsiveness. No direct FileShift action substitutes for opening
the context menu. The installed X11 case also opens the Scripts submenu; its
private screenshot visibly contains FileShift Prototype.

Commands executed with an extracted Ubuntu Xvfb 21.1.22 development binary:

```sh
python3 scripts/run-isolated-menu-check.py --condition absent \
  --xvfb /tmp/fileshift-xvfb/root/usr/bin/Xvfb
python3 scripts/run-isolated-menu-check.py --condition installed \
  --xvfb /tmp/fileshift-xvfb/root/usr/bin/Xvfb
```

Both passed in isolated X11. The installed menu, submenu and subsequent Files
close worked; the user's actual failure was not reproduced in this configuration.
A separate calibration run with `--freeze-after-click` stops only the isolated
Files process. It fails both menu responsiveness and Files-close checks, then
terminates the owned process group and removes the private script. This proves
the detector can fail on a hang; the injected stop is not a reproduced product bug.

GTK's accessible virtual-cell bounds were not usable for pointer positioning.
An initial probe clicked the sidebar instead of the fixture. The loop was
corrected using a private-display screenshot and now requires the exact fixture
to be selected by the physical click before it tests the menu. The wrong-target
attempt was not counted as application failure.

## Wayland matching remains inconclusive

A second test server used a private headless GNOME Shell 50.1 compositor, with a
fresh home, runtime socket and bus. It did not attach to or inject input into the
real desktop. Context7 supplied official GNOME Shell test-tool guidance for
headless/virtual-monitor isolation; the installed CLI help confirmed the flags.

That baseline eventually selected the exact fixture and opened its context menu,
but did not dismiss it with Escape; the accessible Files-close action still
worked. The baseline therefore does not reproduce the user's combined failure
and is not a valid green control for an installed Wayland comparison. No installed
Wayland result or root cause is inferred from it. Private screenshot capture was
unsuccessful and removed from the acceptance sequence to avoid its error UI
contaminating input observations. No host screenshot fallback was used.

## Documentation coverage and next evidence

Context7 had generic GNOME documentation rather than coverage of Nautilus menu
internals. Official GNOME Files help and versioned source remain the platform
references. Xvfb documentation was checked against the official X.Org manual and
installed/extracted tool help. Test-tool downloads were extracted under `/tmp`;
no system package installation was performed.

The normal desktop integration remains uninstalled. The existing product code
has not been changed on an unconfirmed theory. Next evidence is whether the
reported freeze began before selecting FileShift or after its invocation; then
match that exact path in a controlled environment. No new everyday-desktop
installation or user-session restart is requested.

## Diagnostic review and cleanup verification

Review identified that Nautilus runs in its own process group, so an outer
controller deadline could interrupt inner cleanup and leave it behind. The inner
diagnostic now publishes PID/start-time ownership; the outer runner verifies that
identity before terminating the private Files group, including a stopped process.
A three-second outer deadline with deliberate freeze calibration returned the
expected timeout and cleanup result. Independent process inspection found no
remaining isolated Files processes.

The close assertion uses the accessible window-close action. It establishes
request responsiveness, not success of the user's physical title-bar close
button. It cannot rule out an input-grab failure, and is not a substitute for the
reported everyday-session symptom. No root-cause fix was inferred from a green
isolated control.
