# Multi-Codex Orchestration Adapter Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tgtool-compatible multi-Codex orchestration path that keeps tgtool as the top-level router while delegating complex multi-agent execution through an orchestration adapter.

**Architecture:** tgtool remains the entrypoint and applies global rules, mode handling, and safety boundaries. For qualifying tasks, tgtool routes into a new orchestration adapter layer that normalizes task context, selects role splits, and then calls a compatible external framework or a local wrapper implementation. The adapter returns status and merged outputs back into the active tgtool session.

**Tech Stack:** Codex skills (`tgtool`, `writing-skills`), Markdown docs, optional wrapper scripts, existing Codex agent tools (`spawn_agent`, `send_input`, `wait_agent`, `close_agent`).

---

## Chunk 1: Scope and routing design

### Task 1: Define the tgtool scenario trigger

**Files:**
- Create: `docs/superpowers/specs/2026-03-27-multi-codex-orchestration-design.md` (optional follow-up if spec is formalized)
- Modify: `skills/tgtool/SKILL.md`
- Test: manual review of routing language in `skills/tgtool/SKILL.md`

- [ ] **Step 1: Add a new tgtool scenario category for multi-Codex orchestration**

Add explicit trigger criteria covering:
- user explicitly requests multiple Codex agents / virtual team / parallel agent work
- task can be decomposed into 2+ relatively independent subproblems
- sequential single-agent execution would be materially worse
- a role split such as planner / implementer / verifier / reviewer is beneficial

- [ ] **Step 2: Add non-trigger criteria to prevent over-routing**

Document that this path should NOT be selected for:
- tiny fixes
- tightly coupled single-threaded work
- pure read-only diagnosis without parallel value
- work that would create agent contention on the same write scope

- [ ] **Step 3: Add expected routing result**

Document that tgtool should:
- remain the top-level router
- keep mode handling, global rules, session visibility, and safety boundaries
- invoke the orchestration adapter as a support path for this scenario
- avoid replacing ordinary superpowers flows for normal development tasks

- [ ] **Step 4: Review wording for overlap with existing superpowers rules**

Check that the new route does not conflict with:
- `using-superpowers`
- `dispatching-parallel-agents`
- `subagent-driven-development`

- [ ] **Step 5: Commit**

```bash
git add skills/tgtool/SKILL.md
git commit -m "feat: add tgtool multi-codex orchestration route"
```

### Task 2: Add README-level explanation

**Files:**
- Modify: `README.md`
- Test: manual review of README wording

- [ ] **Step 1: Add a short README note describing the new route**

Document that tgtool can route complex parallel tasks into a multi-Codex orchestration path while preserving tgtool as the main entrypoint.

- [ ] **Step 2: Clarify boundary with existing skills**

Add one sentence saying this route complements existing superpowers and subagent skills rather than replacing them.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: describe tgtool orchestration adapter route"
```

## Chunk 2: Adapter contract

### Task 3: Specify adapter inputs and outputs

**Files:**
- Create: `docs/orchestration-adapter-schema.md`
- Test: manual schema review

- [ ] **Step 1: Define adapter input contract**

Write a schema that includes:
- task summary
- tgtool mode
- workspace path
- confirmed constraints
- candidate role split
- optional support layers such as `planning-with-files` or `claude-mem`

- [ ] **Step 2: Define adapter output contract**

Write a schema that includes:
- orchestration session id
- spawned roles
- per-role status
- summarized outputs
- unresolved blockers
- final merged result

- [ ] **Step 3: Define failure and fallback contract**

Document explicit adapter return states for:
- framework unavailable
- decomposition rejected
- role collision detected
- framework execution partial failure

- [ ] **Step 4: Commit**

```bash
git add docs/orchestration-adapter-schema.md
git commit -m "docs: define orchestration adapter contract"
```

### Task 4: Define role ownership rules

**Files:**
- Create: `docs/orchestration-role-model.md`
- Test: manual review of role boundaries

- [ ] **Step 1: Define the minimal role set**

Document four default roles:
- planner
- implementer
- verifier
- reviewer

- [ ] **Step 2: Define ownership constraints**

State that:
- planner does not own production code edits
- reviewer does not own the main implementation write scope
- verifier focuses on non-overlapping verification work
- implementer owns explicit files or modules only

- [ ] **Step 3: Add optional researcher role**

Document when a fifth `researcher` role is worth spawning and when it is unnecessary.

- [ ] **Step 4: Commit**

```bash
git add docs/orchestration-role-model.md
git commit -m "docs: define orchestration role model"
```

## Chunk 3: External framework boundary

### Task 5: Define the wrapper boundary

**Files:**
- Create: `docs/external-framework-boundary.md`
- Test: manual review of boundary language

- [ ] **Step 1: Define what remains inside tgtool**

Document that tgtool keeps:
- mode selection
- read-only and safety boundaries
- support-layer selection
- concise user-facing routing explanation

- [ ] **Step 2: Define what moves into the adapter/framework**

Document that the adapter or framework owns:
- task decomposition for selected orchestration sessions
- role spawning and lifecycle
- subtask dispatch
- aggregation and intermediate state

- [ ] **Step 3: Define the framework-agnostic boundary**

Document that the adapter should not hard-bind tgtool to a single framework implementation. It should be possible to swap a local wrapper, Codex-native orchestration, or an external framework backend later.

- [ ] **Step 4: Commit**

```bash
git add docs/external-framework-boundary.md
git commit -m "docs: define orchestration framework boundary"
```

### Task 6: Define fallback behavior

**Files:**
- Modify: `skills/tgtool/SKILL.md`
- Test: manual review of fallback language

- [ ] **Step 1: Add fallback language when orchestration is unavailable**

Specify fallback order:
- local `subagent-driven-development`
- `dispatching-parallel-agents`
- ordinary superpowers path

- [ ] **Step 2: Add a conflict rule for overlapping write scopes**

Specify that tgtool must avoid orchestration when role ownership cannot be made disjoint enough for safe parallel execution.

- [ ] **Step 3: Commit**

```bash
git add skills/tgtool/SKILL.md
git commit -m "feat: add orchestration fallback rules"
```

## Chunk 4: First implementation path

### Task 7: Choose initial backend strategy

**Files:**
- Create: `docs/orchestration-backend-evaluation.md`
- Test: manual comparison table

- [ ] **Step 1: Compare three initial backends**

Create a comparison covering:
- Codex-native wrapper using current agent tools
- tmux-based Codex orchestration
- external orchestration framework adapter

- [ ] **Step 2: Recommend the first implementation target**

Default recommendation should favor the smallest integration that preserves current tgtool and skills behavior.

- [ ] **Step 3: Commit**

```bash
git add docs/orchestration-backend-evaluation.md
git commit -m "docs: evaluate orchestration backend options"
```

### Task 8: Prepare execution handoff

**Files:**
- Modify: `README.md`
- Modify: `skills/tgtool/SKILL.md`
- Test: manual consistency review

- [ ] **Step 1: Confirm terminology is consistent**

Use one stable term everywhere, for example:
- `multi-codex orchestration`
- `orchestration adapter`

- [ ] **Step 2: Confirm tgtool still owns the top-level route**

Verify the wording never implies that the external framework replaces tgtool as the main entrypoint.

- [ ] **Step 3: Commit**

```bash
git add README.md skills/tgtool/SKILL.md
git commit -m "docs: align orchestration terminology"
```

Plan complete and saved to `docs/superpowers/plans/2026-03-27-multi-codex-orchestration-adapter.md`. Ready to execute?
