# FileShift

FileShift converts selected local files through desktop file-manager interactions.

## Language

**Always available**:
After initial installation and setup, FileShift can be invoked without manually launching an application. This describes availability to the user, not a requirement for the conversion engine to remain running.
_Avoid_: Always running, zero-memory background process

**Conversion popup**:
The transient interface opened for selected files through a keyboard shortcut or file-manager right-click action, where the user chooses a feasible target format.
_Avoid_: Main application window
