# Prove desktop integration before building the full converter

V1 must provide both a keyboard shortcut and a file-manager right-click action on Windows, macOS, and a named Ubuntu/GNOME environment. Prototype selection capture and popup invocation on all three before building the full converter, because these interactions define the product and their feasibility must not be assumed from core conversion tests. Ubuntu/GNOME is the first testing environment; the other platforms remain v1 requirements.

Use a shared core with separate OS adapters. Prefer on-demand activation and allow a small resident helper where integration requires it: users must see the conversion popup directly after setup, with no manual launch, main window, or splash screen. Idle resource use and activation latency require measurement; budgets are still to be decided.

Ubuntu development builds may proceed independently, but v1 is blocked until selection → shortcut/right-click → popup behavior is demonstrated on all three supported platforms. Mocked adapter tests do not establish native platform support. If an integration cannot meet the requirement reliably, resolve it or obtain an explicit revision of the requirement; do not silently substitute a weaker interaction.
