# Repository Showcase Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the repository for interview-first GitHub browsing while keeping the backend behavior unchanged.

**Architecture:** This is a documentation-only refactor. The repository root becomes a clean entrypoint with a single README, detailed materials move under `docs/` by concern, and verification relies on link checks plus the existing `pytest` suite.

**Tech Stack:** Markdown, Git, pytest

---

### Task 1: Move scattered docs into a stable `docs/` structure

**Files:**
- Create: `docs/architecture/`
- Create: `docs/design/`
- Create: `docs/implementation/`
- Create: `docs/interview/`
- Create: `docs/roadmap/`
- Modify: repository file layout

- [ ] **Step 1: Create the target folders**

Run:

```bash
mkdir -p docs/architecture docs/design docs/implementation docs/interview docs/roadmap
```

Expected: all five folders exist.

- [ ] **Step 2: Move root-level design docs into the new folders**

Run:

```bash
mv customer-support-resolution-orchestrator-architecture.md docs/architecture/
mv customer-support-resolution-orchestrator-tech-spec.md docs/design/
mv customer-support-resolution-data-api-design.md docs/design/
mv customer-support-resolution-implementation-plan.md docs/implementation/
mv customer-support-resolution-resume-star.md docs/interview/
mv customer-support-resolution-roadmap.md docs/roadmap/
```

Expected: repository root only keeps code, config, tests, and the new README.

- [ ] **Step 3: Fix moved document references**

Update markdown links and plain-text references so they use the new relative paths.

- [ ] **Step 4: Verify the new layout**

Run:

```bash
find docs -maxdepth 2 -type f | sort
```

Expected: architecture, design, implementation, interview, and roadmap docs are all visible under `docs/`.

### Task 2: Write an interview-first README

**Files:**
- Create: `README.md`
- Read: `src/customer_support_resolution/api/routes.py`
- Read: `src/customer_support_resolution/services/workflow.py`
- Test: `tests/test_ticket_intake.py`
- Test: `tests/test_mcp_server.py`

- [ ] **Step 1: Capture the implemented scope**

Summarize the real backend behavior:

```text
Endpoints: /health, /tickets/intake, /runs/{run_id}
Workflow: triage -> investigate -> resolve -> verify
High-risk billing requests: approval_pending
MCP: crm_lookup JSON-RPC server
```

- [ ] **Step 2: Write the README sections**

Include:

```text
Project positioning
Why this repo is worth reading
Current implementation
Repository structure
Key workflow
API snapshot
Quick start
Documentation links
```

- [ ] **Step 3: Keep the README honest**

Add a short note that this is a runnable MVP with production-oriented docs, not a completed production deployment.

### Task 3: Verify repository health after the doc refresh

**Files:**
- Test: `tests/`

- [ ] **Step 1: Run the full test suite**

Run:

```bash
pytest
```

Expected: all tests pass.

- [ ] **Step 2: Review git status**

Run:

```bash
git status --short
```

Expected: only README additions, doc moves, and path-fix edits remain.

- [ ] **Step 3: Commit the documentation refresh**

Run:

```bash
git add README.md docs
git commit -m "docs: reorganize repo and add showcase README"
```

Expected: a single commit captures the documentation refresh.

