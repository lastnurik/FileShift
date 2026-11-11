# Issue tracker

Use GitHub Issues in the verified public repository `lastnurik/FileShift`:
https://github.com/lastnurik/FileShift. Git transport uses SSH.

The approved specification is issue #1. FS-01 through FS-12 are issues #2 through
#13, respectively. Native blocking dependencies are published. Local records under
`.scratch/fileshift/issues/` contain the corresponding URLs. Check current issue
bodies and comments before working; local records can lag remote updates.

While publication or repository access is blocked, keep one approved ticket per file
under `.scratch/fileshift/issues/`. Each ticket records blockers, acceptance criteria,
status, and evidence. These are local drafts for GitHub, not published issue numbers.

Use `gh` with an explicit `--repo lastnurik/FileShift` until an origin exists.
Read issue bodies and comments before working. Publish approved specifications and
tickets with `ready-for-agent`, in dependency order. Prefer native blocking links;
otherwise put actual blocker issue references in the issue body. Record remote issue
identifiers in the local records after publication. Never close or modify parent issues.
Use `--body-file` for multiline issue content. Do not include local private paths or
credentials in public evidence.

Close a ticket only after its acceptance checks, separate standards/spec review,
documentation, and individual task commit are complete. Native evidence cannot be
replaced by compilation or fake adapters. Keep missing acceptance open.

PRs as a request surface: no.
