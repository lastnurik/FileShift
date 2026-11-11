# Agent instructions

Read [PROJECT.md](PROJECT.md), [CONTEXT.md](CONTEXT.md), and [WORKFLOW.md](WORKFLOW.md) before planning or implementing. PROJECT.md is the product contract; consult docs/adr before changing architectural decisions.

- Follow the task loop in WORKFLOW.md. Each completed task gets its own commit and acceptance evidence.
- Keep the Rust core independent of UI, OS, and codec implementations through small injectable boundaries. Prototype actual desktop integration before building the full converter.
- Preserve originals and existing outputs. Treat inputs and converter processes as untrusted; apply PROJECT.md resource, privacy, and publication rules.
- State the exact OS/session/file manager tested. Native support requires native evidence; keep unavailable platform acceptance open.
- Use Context7 for current library, framework, SDK, API, CLI, and cloud documentation: resolve-library-id first, then query-docs scoped to the concept. Prefer official OS documentation for platform behavior. If Context7 lacks coverage, record that and consult official sources.
- Read and use installed Matt Pocock to-spec, to-tickets, tdd, and code-review skills. Preserve settled user decisions; ask at most one question at a time for real blockers or mandatory checkpoints.
- Ask Astra for a concrete vertical slice and acceptance check when available, with explicit file ownership. Independently review its changes and run verification; report tool unavailability honestly.
- Update README with verified native installation, source-build commands, and compatibility evidence as implementation lands. Keep product decisions in PROJECT.md and their reasons in ADRs.

Postman CLI is available for API engineering if needed; it is not a required dependency.

## Agent skills

### Issue tracker

Use GitHub Issues, with local drafts while publication is blocked. Before reading,
publishing, or updating tickets, read [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md).

### Domain docs

Use single-context terminology and decisions. Before exploring or changing domain
behavior, read [docs/agents/domain.md](docs/agents/domain.md).
