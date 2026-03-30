# Repository Showcase Design

**Goal**

Reposition this repository for interview-first GitHub browsing without changing runtime behavior.

**Audience**

- Hiring managers scanning the repo in under two minutes
- Interviewers who want to see architecture depth, not only prompts
- Engineers who still need enough instructions to run the backend locally

**Design**

- Add a root `README.md` that starts with project positioning, why the repo matters, implemented scope, architecture, API surface, and local run instructions.
- Move scattered design artifacts under `docs/` so the repository root highlights the runnable code instead of a flat file list.
- Keep technical docs intact and link them from the README rather than rewriting them.
- Be explicit that the repository is a runnable MVP with production-oriented design docs, not a fully deployed production system.

**Target Structure**

- `README.md`
- `pyproject.toml`
- `src/`
- `tests/`
- `docs/architecture`
- `docs/design`
- `docs/implementation`
- `docs/interview`
- `docs/roadmap`

**Non-Goals**

- No business logic changes
- No new APIs
- No generated diagrams or screenshots
- No rewrite of the existing design documents beyond path fixes

**Success Criteria**

- Root navigation is clear in GitHub
- README reflects the code that actually exists
- Existing tests still pass after the document move

