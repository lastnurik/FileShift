# Ubuntu integration feasibility research

Date: 2026-11-12. Status: source investigation and read-only environment checks;
no FileShift native interaction has been implemented or verified.

## Conclusion

The smallest useful prototype is a Files script action and its Files-local
keyboard accelerator, both launching one transient selection-inspection popup.
Nautilus 50.2.2 source shows both paths invoking the same callback, which reads
the view's selection at invocation. This is stronger evidence than assuming a
cached extension selection is current, but remains source evidence, not a native
test. It does **not** satisfy the complete global shortcut contract: when another
application has focus, a Files-local shortcut cannot show FileShift's required
unsupported-context status. No reliable global-trigger-to-active-Files-view
selection bridge has been verified. The final section on an explicit extension
gateway identifies a source-supported candidate for that bridge. Keep native
acceptance open until its experiment passes.

## Environment and provenance

Read-only checks in this session returned:

| Check | Observation |
| --- | --- |
| `/etc/os-release` | Ubuntu 26.04.1 LTS, Resolute Raccoon |
| Session environment | `XDG_SESSION_TYPE=wayland`, `XDG_CURRENT_DESKTOP=ubuntu:GNOME` |
| `dpkg-query` | Nautilus `1:50.2.2-0ubuntu0.2`; GNOME Shell `50.1-0ubuntu1.5` |
| Portal packages | `xdg-desktop-portal 1.21.1+ds-1ubuntu3.1`; `xdg-desktop-portal-gnome 50.0-0ubuntu1` |
| Portal version property | `(<uint32 1>,)` |

The last result came from this read-only call; it proves interface presence and
reported version, not successful registration, permissions, or activation:

```sh
gdbus call --session --dest org.freedesktop.portal.Desktop \
  --object-path /org/freedesktop/portal/desktop \
  --method org.freedesktop.DBus.Properties.Get \
  org.freedesktop.portal.GlobalShortcuts version
```

Context7 resolution for Nautilus returned an unrelated Subnautica library.
Resolution for GNOME Files found general GNOME collections; querying
`/websites/wiki_gnome` returned unrelated/old accelerator material, not the needed
Files mechanism. Context7 `/flatpak/xdg-desktop-portal` supplied general
request/session guidance but not sufficient shortcut-specific details. The
investigation therefore followed official versioned source.

Downloaded upstream archives were inspected under `/tmp` only:

- [Nautilus 50.2.2 archive](https://download.gnome.org/sources/nautilus/50/nautilus-50.2.2.tar.xz),
  SHA-256 `e1e285efddf42ed30dda5b29f7f8d242dab4bc1409a9054863b367bad4b34d5a`.
- [GNOME Shell 50.1 archive](https://download.gnome.org/sources/gnome-shell/50/gnome-shell-50.1.tar.xz),
  SHA-256 `1b47760172c14f3f4edd1c9aff365f4de45583517bf0f80df4d3acbd4e4cb294`.
- [GlobalShortcuts XML at portal 1.21.1](https://github.com/flatpak/xdg-desktop-portal/blob/1.21.1/data/org.freedesktop.portal.GlobalShortcuts.xml).

Hashes identify inspected downloads; they are not independent authenticity
verification. Ubuntu downstream patches were not inspected. Tagged file links
below identify source locations; the browser could not render GitLab pages, so
the downloaded official archives supplied the source text.

## Files-owned activation and argument fidelity

In Nautilus 50.2.2, `run_script` changes to the view directory, calls
`nautilus_files_view_get_selection` on that script action's view, constructs
arguments/environment, launches the script, and restores the directory and
environment. It does not reuse a prior extension selection.
`add_script_to_scripts_menus` connects the menu action to `run_script` and binds
the configured accelerator to that same `view.script_…` action. The view's
shortcut controller uses managed scope. These are application/view shortcuts,
not compositor-wide registration. See
[files-view.c, lines 4996–5229 and 9565–9568](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-files-view.c).

`nautilus_load_custom_accel_for_scripts` reads
`$XDG_CONFIG_HOME/nautilus/scripts-accels` (normally
`~/.config/nautilus/scripts-accels`), splitting each line once on a space into
accelerator and script display name. Both fields are limited to 100 bytes.
The table initializes lazily when scripts menus are built; this code path does
not reload an existing table. A clean Files restart and first-use test are
therefore necessary after configuration changes. Example proposed prototype
entry: `<Control><Alt>f FileShift Prototype`, subject to conflict testing.
[Parser and initialization, lines 5257–5330](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-files-view.c).

For an ordinary native installation, scripts live under the user data directory's
`nautilus/scripts` subdirectory; the source separately handles sandboxed Files.
[Directory helper, lines 125–147](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-file-utilities.c).
GNOME documents the user entry point as right-click → Scripts → script name.
[GNOME Files help](https://help.gnome.org/gnome-help/nautilus-behavior.html).

Arguments are paths relative to the view directory when possible, otherwise
absolute local paths. If any selected item lacks a local path, the argument
array becomes null. The helper individually quotes arguments before passing its
command line through GAppInfo. This warrants tests of arbitrary filenames; it is
not a reason for FileShift to reconstruct or evaluate a shell command.
[Argument construction, lines 4996–5039](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-files-view.c);
[launch helper, lines 221–249 and 299–330](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-program-choosing.c).

Design consequence: pass native argv unchanged into the Rust adapter, preserve
OS-string bytes, and resolve relative paths against the launch working directory.
Never split `NAUTILUS_SCRIPT_SELECTED_FILE_PATHS` on newlines: the source builds
that variable by appending raw paths and newline separators, making embedded
newlines ambiguous. The source also supplies selected URIs and current URI;
these can support an explicit unsupported-context diagnostic, but require a
separately tested URI parser before per-item classification. Do not interpret
empty argv as proof of empty selection: nonlocal items can also produce it.
[Environment construction, lines 5042–5135](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-files-view.c).

## Global activation and the unresolved bridge

The portal specifies session creation, shortcut binding, asynchronous activation,
and an optional activation token. `Activated` contains session, shortcut ID,
timestamp, and options; its documented options do not include foreground app,
window, active Files tab, or selected paths. A binding response can contain fewer
shortcuts than requested, including none. `ConfigureShortcuts` was introduced in
interface v2, whereas this session reports v1. Use actual version/results and
provide setup failure feedback; do not assume the installed package version
equals the exposed interface version.
[Versioned GlobalShortcuts specification](https://github.com/flatpak/xdg-desktop-portal/blob/1.21.1/data/org.freedesktop.portal.GlobalShortcuts.xml).

The public `NautilusMenuProvider` callback receives provider plus file list, with
no window/view identity. Nautilus calls it using a particular view's selection,
but does not pass that view through the extension interface. A single cached
list cannot establish which foreground window or tab it belongs to.
[Extension header](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/libnautilus-extension/nautilus-menu-provider.h);
[callback site, lines 4792–4814](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-files-view.c).

The inspected FileManager1 interface exposes show operations and location
properties, including window/location mappings, but no selection getter. The
separate FileOperations2 interface explicitly describes itself as private and
also provides no selection query. A directory location is not a selection.
[FileManager1 XML](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/data/freedesktop-dbus-interfaces.xml);
[FileOperations2 XML](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/data/dbus-interfaces2.xml).

GNOME Shell internally accesses `global.display.focus_window` and registers key
bindings. This makes a version-specific Shell companion a research candidate
for foreground classification, not an established external application API or
selection bridge. Shell's D-Bus Eval refuses execution unless unsafe mode is
enabled; do not use it as an integration workaround.
[Shell window manager, lines 917–924, 1002, 1078–1090](https://gitlab.gnome.org/GNOME/gnome-shell/-/blob/50.1/js/ui/windowManager.js);
[Eval guard, lines 70–74](https://gitlab.gnome.org/GNOME/gnome-shell/-/blob/50.1/js/ui/shellDBus.js).

The exact remaining mechanism is: a global activation must identify the focused
supported Files view and request its fresh selection without clipboard access,
folder scanning, stale caches, or unsafe Shell evaluation. A Shell companion
alone does not solve the second half. Do not globally grab the same accelerator
and assume the Files-local action will also receive it. A native prototype must
prove a view-specific bridge or obtain an explicit product revision; neither has
occurred. The later gateway section records a source-supported candidate for
that experiment.

## Focused GTK window → exported action bridge: ruled out

A follow-up checked this concrete proposal: obtain the focused `Meta.Window` in
a Shell companion, retrieve its GTK unique bus name/window object path, and call
the Files script through `org.gtk.Actions`. **The unmodified applications do not
provide that route.** The metadata exists, but the script action is not in the
exported action group.

Installed packages are GTK `4.22.4+ds-0ubuntu0.1` and Mutter
`50.1-0ubuntu2.4`. Context7 `/gnome/gtk` confirmed the distinction between window
GActionMap actions and widget-inserted action groups; exact export behavior was
then traced in the official
[GTK 4.22.4 archive](https://download.gnome.org/sources/gtk/4.22/gtk-4.22.4.tar.xz)
(SHA-256 `51bd9f60c7d23a665a556c7364c21fb2e4e282566b3e7e092455e8f910330893`)
and [Mutter 50.1 archive](https://download.gnome.org/sources/mutter/50/mutter-50.1.tar.xz)
(SHA-256 `9344502ce473f788795f26b45f8b8ff53c0a36b867470d705a11a3ee0911021e`).
Ubuntu downstream patches remain unreviewed; the live observations below check
the relevant result on this installation.

1. Mutter's GTK Wayland protocol handler stores window D-Bus metadata;
   `meta_window_get_gtk_unique_bus_name` and
   `meta_window_get_gtk_window_object_path` return those nullable fields. Thus a
   Shell-side focused-window association is plausible at source level. This
   investigation did not execute a Shell companion or verify focused-window
   metadata at runtime.
   [Wayland handler, lines 73–102](https://gitlab.gnome.org/GNOME/mutter/-/blob/50.1/src/wayland/meta-wayland-gtk-shell.c);
   [window getters, lines 6863–6897](https://gitlab.gnome.org/GNOME/mutter/-/blob/50.1/src/core/window.c).
2. GTK's `gtk_application_impl_dbus_window_added` exports the result of
   `gtk_application_window_get_action_group`, which returns `priv->actions`.
   GTK inserts that group into its widget resolver as `win`, but exports the
   group itself, with unprefixed action names. It does not export the widget's
   complete action resolver.
   [D-Bus export, lines 404–424](https://gitlab.gnome.org/GNOME/gtk/-/blob/4.22.4/gtk/gtkapplication-dbus.c);
   [group getter and initialization, lines 534–537 and 640–645](https://gitlab.gnome.org/GNOME/gtk/-/blob/4.22.4/gtk/gtkapplicationwindow.c).
3. Nautilus mounts the active view's action group under `view` on its root
   widget and the active slot's group under `slot`. `gtk_widget_insert_action_group`
   inserts into a `GtkActionMuxer`; it does not add those actions to the window's
   `priv->actions`. Scripts are added to the view group, not the window group.
   [Active view, lines 3038–3070 and 8955–8966](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-files-view.c);
   [active slot, lines 3151–3155](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-window-slot.c);
   [widget insertion, lines 11288–11302](https://gitlab.gnome.org/GNOME/gtk/-/blob/4.22.4/gtk/gtkwidget.c).
4. Nautilus's actual window action table contains tab/window/navigation actions,
   undo and redo, but no generic action-forwarding or selection/script action.
   Prefixing a script with `win.`, `slot.`, or `view.` cannot create an exported
   action that was never registered there.
   [Window table, lines 1086–1115](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-window.c).

Read-only session inspection found an existing window endpoint at
`/org/gnome/Nautilus/window/1`. `org.gtk.Actions.List` there returned exactly:
`go-to-tab`, `tab-move-right`, `new-tab`, `close-current-view`, `undo`,
`toggle-sidebar`, `redo`, `restore-tab`, `tab-move-new-window`, `tab-move-left`,
`go-home`, `current-location-menu`, `close-other-tabs`. The application endpoint's
List likewise contained no script or generic view-action forwarding operation.
`org.gtk.Actions.Describe` for `view.copy` returned
`org.freedesktop.DBus.Error.InvalidArgs: The named action ('view.copy') does not exist.`
No action activation, state change, file-location property output, selection
inspection, or Shell evaluation was performed. Endpoint IDs are observations,
not identifiers to hard-code in an implementation.

The failure is therefore precise: the available bus endpoint exposes only the
window action group, while fresh-selection script execution lives in the
unexported active-view group. A newly implemented in-process forwarding/export
boundary would be a different mechanism requiring a supported integration point
and separate review. The following candidate supplies that boundary; native
acceptance remains open.

## Explicit extension gateway: source-supported candidate

A small C extension can plausibly register a new, fixed application action that
forwards to the active view's script using public GTK APIs. This avoids the
unexported-action obstacle above. **It is an untested, version-specific candidate,
not verified native support or a stable Nautilus extension API guarantee.**

Nautilus startup chains GTK initialization before `nautilus_module_setup`;
the loader calls `nautilus_module_initialize`. GApplication establishes its
default instance during construction. An extension can therefore check
`g_application_get_default()` and register a namespaced GSimpleAction on that
application's GActionMap. GLib inserts it into the same group exported over
D-Bus; the exporter tracks added actions.
[Nautilus startup, lines 983–996](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-application.c);
[module loader, lines 65–98](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-module.c);
[GLib construction/action registration, lines 1398–1403, 2883–2890](https://gitlab.gnome.org/GNOME/glib/-/blob/2.88.0/gio/gapplication.c);
[exporter, lines 590–637](https://gitlab.gnome.org/GNOME/glib/-/blob/2.88.0/gio/gactiongroupexporter.c).
Context7 `/gnome/glib` was queried first; official
[GLib 2.88.0 source](https://download.gnome.org/sources/glib/2.88/glib-2.88.0.tar.xz)
was inspected, matching installed `2.88.0-1ubuntu0.1` upstream version.

Proposed flow: Shell companion validates focused Nautilus bus/window metadata,
then invokes only the new application action with that window ID. The callback
uses `gtk_application_get_window_by_id`, verifies the expected window is still
active, and calls `gtk_widget_activate_action_variant(window, fixed_action, NULL)`.
That public API resolves widget-inserted groups, including the mounted `view`
group. Do not rely solely on `gtk_application_get_active_window`: its documented
meaning is most-recently-focused within the application, even when another app
has focus. Recheck `gtk_window_is_active`, fail closed on mismatch, and test
focus/tab changes during dispatch.
[Window lookup semantics, lines 926–977](https://gitlab.gnome.org/GNOME/gtk/-/blob/4.22.4/gtk/gtkapplication.c);
[activation, lines 11804–11841](https://gitlab.gnome.org/GNOME/gtk/-/blob/4.22.4/gtk/gtkwidget.c);
[active state, lines 6010–6031](https://gitlab.gnome.org/GNOME/gtk/-/blob/4.22.4/gtk/gtkwindow.c).

The fixed action name is `view.script_` plus
`g_uri_escape_string(installed_script_uri, NULL, TRUE)`, not the display name.
Its handler reads fresh selection. This internal naming and lazy script-action
creation require version checks and first-use native evidence. Missing action
must yield setup feedback, not simulated input or selection fallback.
[Script registration, lines 5178–5220](https://gitlab.gnome.org/GNOME/nautilus/-/blob/50.2.2/src/nautilus-files-view.c).

Proposed ownership: Linux adapter implementer adds
`platform/linux/nautilus-extension/` for the fixed gateway and
`platform/linux/gnome-shell-extension/` for focus classification, configurable
binding, and unsupported-app status. Do not accept arbitrary action names or
file paths through the gateway. Native experiment must prove export visibility,
cold first invocation, current-tab correctness, focus-change rejection, actual
popup arrival (API return alone is insufficient), status/activation tokens,
shortcut conflicts, and uninstall/restart behavior. No extension, action,
binding, or desktop change was installed for this investigation.

## Smallest prototype and ownership

Proposed code, after the baseline-first workflow gate clears:

| Owner | Proposed files and responsibility |
| --- | --- |
| Linux adapter implementer | `platform/linux/nautilus-script/`, `platform/linux/src/activation.rs`: executable script entry, argument snapshot/validation, setup assets, reversible removal |
| Core implementer | `crates/fileshift-core/src/activation.rs`, `crates/fileshift-core/tests/activation.rs`: injectable activation/selection/presenter boundary, frozen snapshot and structured outcomes |
| Linux UI implementer | `platform/linux/src/prototype_popup.rs`: transient diagnostic popup showing selection count and rejection reasons, keyboard focus and Escape; no advertised conversion routes |
| Coordinator/reviewer | Native evidence record and README, independent review, task status and measurements |

These are proposed responsibilities, not existing modules. One script executable
should feed the same public activation boundary from menu and local shortcut.
Use an absolute executable path and argv forwarding; do not shell-interpolate
filenames. Accept only validated regular local files and preserve per-item
rejection reasons. Freeze accepted input identities before showing the popup.
Do not create outputs in this experiment.

Start public-seam TDD with an activation snapshot that stays unchanged after the
fake provider's selection changes; then empty selection, invalid inputs, and
presenter failure. These tests cannot establish native selection provenance.
Keep a separate portal diagnostic experiment for version, registration outcome,
activation token, and permission/conflict behavior. Its completion does not
complete the Files integration ticket.

## Native smoke and measurement plan

All following checks are **pending**; no shortcut registration or desktop settings
changes were performed during this research.

1. Record OS/package/session versions and Ubuntu source patches before installing
   the prototype. Preserve existing scripts/accelerators and record exact changes.
   Restart Files safely, then test the shortcut before opening any context menu.
2. Select two known local fixtures; invoke right-click → Scripts → FileShift
   Prototype, then the configured local accelerator. Confirm exact file identities
   and one directly opened popup. Escape closes it; keyboard focus is usable.
3. Repeat with two Files windows and two tabs holding different selections. Switch
   focus without modifying selection; test search, recent, location-entry focus,
   background selection changes, and an already-open context menu. Reject wrong
   view, missing first activation, stale selection, or duplicate popup behavior.
4. Exercise spaces, Unicode, quotes, dollar signs, leading dashes, embedded
   newlines, and non-UTF-8 names using private fixtures. Compare native argv/identity
   inside a test-only observer; do not log real user paths by default.
5. Test empty selection, directories, symlinks, unreadable/deleted files, remote
   and virtual views, and mixed selections. Distinguish unsupported context from
   no selection; neither may trigger fallback discovery.
6. Change selection while the popup is open; its snapshot must remain fixed.
   Repeat after Files restart, logout/login, and prototype removal/reinstallation.
7. Test another foreground application, denied binding, occupied binding, rebinding,
   unavailable portal, and helper exit. The local-only design is expected to leave
   unsupported-foreground feedback unmet; record that failure rather than waive it.
8. Measure cold and warm activation separately over at least 20 runs each. Record
   a monotonic adapter-entry timestamp and first-presented-frame timestamp, plus
   external input-to-visible latency where observable. Adapter timing excludes
   shortcut dispatch and process startup; report both scopes honestly. Record
   medians/p95, idle CPU over a fixed 60-second interval, and RSS/PSS for each
   helper plus incremental Files/Shell overhead against the same-session baseline.
   Record hardware and measurement method. Numerical release budgets remain open.

The Ubuntu ticket stays incomplete until the full required global behavior and
installed activation have native evidence. Windows/macOS evidence and the full
converter feasibility gate remain separate and open.
