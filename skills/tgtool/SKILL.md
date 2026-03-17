---
name: tgtool
description: Use when the user wants the agent to choose, combine, and actively use the best available local skills for a task.
metadata:
  author: codex
  version: "2.5.0"
---

# TGTool

Use this skill as the top-level router for local Codex skills.

Its job is to pick the **smallest useful skill set**, avoid redundant loading, and move directly into execution.

## Core idea

Route in layers:

1. Reuse current context first
2. Confirm what the current environment can already do
3. Choose one primary workflow skill
4. Add only the minimum supporting capabilities
5. Execute instead of lingering in skill-selection mode

The goal is not to use more skills. The goal is to use fewer, better.

## Mode selection

Before substantial work, ask for mode unless the user already specified one.

Use:

`Choose a tgtool mode: review (1/re), standard (2/st), or autopilot (3/auto).`

### Modes

- `review`
  - Recommend routing and plan first.
  - Do not execute until the user confirms.
  - In user-facing updates, explicitly state the current workflow stage and one short reason for the choice.
- `standard`
  - Execute normally.
  - Ask when a meaningful branch, uncertainty, or risk appears.
  - In user-facing updates, explicitly state the current workflow stage and one short reason for the choice.
- `autopilot`
  - Execute end-to-end with minimal interruption.
  - Stop only for destructive actions, critical ambiguity, or required permission escalation.

Accept these mode aliases:

- `review`: `1`, `re`, `review`
- `standard`: `2`, `st`, `standard`
- `autopilot`: `3`, `auto`, `autopilot`

## Session persistence

After the user explicitly invokes `tgtool` once, keep `tgtool` active across subsequent turns by default.

Rules:

- Treat the first explicit mention of `tgtool` as the start of a persistent routed session.
- After that, continue applying `tgtool` even if the user does not explicitly mention it again.
- End the persistent routed session only when the user explicitly says `tgend`.
- If the user says `tgend`, stop applying `tgtool` by default from the next turn onward unless they explicitly invoke it again.
- The first activation still requires an explicit `tgtool` invocation.

## Global rules

1. Use Chinese by default unless the user explicitly requests another language.
2. Reuse established facts from the current conversation before re-reading files, logs, or skills.
3. Prefer concise summaries, deltas, and direct conclusions over repeated background.
4. Keep active context compact. For very long inputs, summarize or segment before deeper routing.
5. Do not load extra skills unless they materially improve the result.
6. Do not stack overlapping workflow skills unless the task genuinely spans phases.
7. Respect the selected mode throughout the task.
8. Do not stop after recommending skills; execute with them unless the mode says not to.
9. Watch memory risk continuously. If the likely path may cause unsafe memory growth, stop and ask to switch to a safer plan.
10. Watch storage risk continuously. If the likely path may cause unsafe disk or artifact growth, stop and ask to switch to a safer plan.

## Decision flow

Apply this flow in order.

### Step 1: Check whether routing is even needed

Do not over-route.

- If the task is already clearly covered by one obvious skill, use that skill.
- If the user explicitly names a skill, use it.
- If the current session context is already enough and no extra capability is needed, keep routing minimal.

### Step 2: Use `$tool-advisor` first by default

Use `$tool-advisor` unless the user explicitly forbids it or the path is already obvious.

Use it to answer:

- What skills are already available?
- What tools, MCP servers, and local capabilities are already usable?
- Is the request already covered without installing or discovering anything else?

Do not use `$tool-advisor` as an excuse to reload everything. Use it to reduce uncertainty.

### Step 3: Choose one primary workflow skill

Choose exactly one unless the task clearly moves across phases.

Prefer installed `superpowers` workflow skills when they are a better fit than `$stream-coding`.

- Use `brainstorming`
  - For ambiguous requests, design exploration, tradeoff discussions, or requirement shaping
- Use `writing-plans`
  - When a multi-step implementation needs a written plan before execution
- Use `executing-plans`
  - When a plan already exists and the main need is disciplined execution
- Use `$stream-coding`
  - For direct implementation, structured engineering work, coding, testing, and repository changes

Only chain workflow skills when the task genuinely crosses phases, for example:

- `brainstorming -> writing-plans`
- `writing-plans -> executing-plans`
- `brainstorming -> stream-coding`

Workflow fallback rules:

- Once a task is routed into the `superpowers` workflow family, prefer to keep fallback and forward transitions inside that family.
- If `executing-plans` is selected but the plan is missing, incomplete, or no longer trustworthy, fall back to `writing-plans`.
- If `writing-plans` is selected but the requirements are still ambiguous, fall back to `brainstorming`.
- If `brainstorming` has already converged, move forward to `writing-plans` for structured planning.
- If `verification-before-completion` finds unresolved problems, fall back to `systematic-debugging` for failures and inconsistencies, or to `executing-plans` when the remaining work is implementation follow-through.
- If `requesting-code-review` is selected but the work is not yet ready for review, fall back to `executing-plans` when a plan exists, or to `writing-plans` / `brainstorming` when the underlying issue is missing structure or unclear scope.
- Use `$stream-coding` as a separate default execution workflow only when no `superpowers` workflow skill clearly fits, not as the default internal fallback once `superpowers` has been chosen.

### Step 4: Add supporting capabilities only when they matter

These are optional support layers, not defaults.

#### `claude-mem`

Use when:

- the user asks what was done before
- the task continues a long-running effort
- prior experiments, decisions, or historical context would materially help
- repeated context reconstruction would waste tokens

Do not use for short, self-contained tasks where current-session context is already sufficient.

When deciding whether to write or update memory, prefer high-value knowledge only.

Treat information as high-value when one or more of these are true:

- it is likely to recur across future sessions
- it captures an environment constraint, workflow constraint, or tested operational fact
- it is not obvious from reading the code alone
- it has been verified by testing, execution, or direct inspection
- preserving it will materially reduce future context rebuilding, repeated debugging, or repeated explanation

Do not write low-value memory for:

- one-off noise
- unverified guesses
- transient intermediate steps
- facts that are trivial to recover from the repo

When new verified information supersedes older memory, prefer updating the existing understanding instead of storing a conflicting duplicate.

#### `exa`

Use when:

- the user needs latest information
- the task needs live web research or external documentation
- recent product, library, or service state matters

Do not use for purely local code or repository work when the answer is already in the workspace.

#### `find-skills`

Use when:

- the user's request implies a capability gap in the currently installed skills
- the user explicitly wants to discover whether a skill exists
- a reusable skill likely exists and would materially improve the result

Use `find-skills` only when at least one of these harder conditions is true:

- there is no installed domain skill that directly matches the requested capability
- the available skills cover workflow only, but not the missing capability itself
- the requested capability looks reusable and general rather than one-off or project-specific
- installing or discovering a skill is likely to improve quality more than handling the task ad hoc

Do not use when the current installed skills already clearly cover the task.

Prefer direct handling instead of `find-skills` when one or more of these are true:

- the task is one-off, narrow, or tightly tied to the current project
- the missing capability is small enough that existing tools or reasoning can cover it cleanly
- installing a new skill would cost more time or context than solving the problem directly
- the request is primarily execution, not capability extension

### Step 5: Execute with the minimum skill set

After routing, open only the selected skill files and follow them.

Do not browse every skill body.
Do not reload the same skill unless something changed or verification is required.

## Long-context policy

When inputs are large, old, or repetitive:

- prefer incremental updates over restating background
- summarize before routing
- inspect only the needed files or sections
- avoid rereading large unchanged logs or documents
- prefer “what changed?” over “repeat everything”

Use this fixed compression flow:

1. Decide whether full reading is actually required.
2. If not, extract only:
   - objective
   - constraints
   - current state
   - deltas or failures
3. Route using that compressed view first.
4. Open original long content only for the specific sections needed by the selected skill.
5. Preserve the compressed summary as the working context instead of repeatedly rebuilding it.

If a task is long-running:

- use `claude-mem` only if the added recall value is real
- otherwise stay with current-session incremental context

## Memory writeback policy

At natural completion points, briefly evaluate whether memory should be written or updated.

Use this rule:

1. Ask whether the result has durable reuse value.
2. If no, do not store it.
3. If yes, prefer concise, validated conclusions over process noise.
4. If the new result corrects or supersedes prior memory, update that understanding rather than duplicating it.
5. Only write memory that would plausibly help a future session make better decisions faster.

### Memory update rules

When deciding between updating prior memory and writing a new memory:

- Update existing memory when the new result is about the same workflow, environment fact, operational constraint, or previously recorded conclusion.
- Write a new memory only when the result introduces a genuinely new reusable fact that is not simply a correction or refinement of an older one.
- If old and new memories conflict, prefer the newer result only when it is more directly verified by execution, testing, or direct inspection.
- If confidence is still mixed or the evidence is weak, do not overwrite high-confidence memory with speculation.
- Prefer one clean updated understanding over multiple partially conflicting notes.

Priority of trust:

1. direct execution or test results
2. direct inspection of current code, config, or runtime state
3. previously stored memory
4. inference or guesswork

If the new result does not beat the old one on that scale, do not treat it as an authoritative update.

## Routing explanation policy

When reporting routing decisions, be concise but explain enough to audit the choice.

Always include:

- the selected skill or skill set
- the main reason it was selected

When there is an obvious alternative that was not chosen, briefly state why it was not chosen, for example:

- current context was already sufficient
- a more specific installed skill already covered the task
- the task was implementation-heavy, not research-heavy
- no real cross-session value justified `claude-mem`
- no actual capability gap justified `find-skills`

Do not enumerate every rejected skill. Mention only the most plausible skipped candidate when that explanation improves trust in the routing choice.

## Output behavior

Before substantial work, first obtain the mode if needed.

Then say which skills are being used and why in one concise line.

In `review` and `standard` modes, also include:

- the current workflow stage
- one short reason for why this stage or routing choice is being used now

While the persistent `tgtool` session is active, end each user-facing reply with one short line asking whether to end the current routed session.

Use:

`如需结束本轮 tgtool 调用，请回复 tgend。`

Examples:

- `Using $tool-advisor to confirm available capabilities, $stream-coding as the workflow skill, and $bucketmanager-s3control-e2e for local S3Control validation.`
- `Using $tool-advisor first, then brainstorming because the request is still in the design phase.`
- `Using $tool-advisor first, then $stream-coding, and adding find-skills because the current installed skills do not clearly cover the requested capability.`

## Completion recap

At the end of a routed task, prefer a very short recap when it adds value.

Use this shape:

- what skill path was used
- whether the routing worked well or exposed a gap
- whether memory should be updated
- whether a missing capability suggests using `find-skills` next time

Keep this recap compact. Use it only when it helps future execution or user understanding.

## Common routing patterns

- Environment-aware execution:
  - `tool-advisor`
- Ambiguous design work:
  - `tool-advisor` + `brainstorming`
- Planned execution:
  - `tool-advisor` + `executing-plans`
- Direct coding and testing:
  - `tool-advisor` + `stream-coding`
- Cross-session recall:
  - `tool-advisor` + `claude-mem`
- External research:
  - `tool-advisor` + `exa`
- Skill discovery:
  - `tool-advisor` + `find-skills`
- Local bucketmanager S3Control testing:
  - `tool-advisor` + `stream-coding` + `bucketmanager-s3control-e2e`

## Scope

This skill is the router and activator.

It should:

1. minimize routing overhead
2. choose the best fitting skills
3. keep context lean
4. move into execution quickly

It should not become a second planning layer that delays work.
