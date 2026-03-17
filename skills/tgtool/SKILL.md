---
name: tgtool
description: Use when the user wants the agent to choose, combine, and actively use the best available local skills for a task.
metadata:
  author: codex
  version: "2.0.0"
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

`Choose a tgtool mode: review, standard, or autopilot.`

### Modes

- `review`
  - Recommend routing and plan first.
  - Do not execute until the user confirms.
- `standard`
  - Execute normally.
  - Ask when a meaningful branch, uncertainty, or risk appears.
- `autopilot`
  - Execute end-to-end with minimal interruption.
  - Stop only for destructive actions, critical ambiguity, or required permission escalation.

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

### Step 4: Add supporting capabilities only when they matter

These are optional support layers, not defaults.

#### `claude-mem`

Use when:

- the user asks what was done before
- the task continues a long-running effort
- prior experiments, decisions, or historical context would materially help
- repeated context reconstruction would waste tokens

Do not use for short, self-contained tasks where current-session context is already sufficient.

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

Do not use when the current installed skills already clearly cover the task.

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

If a task is long-running:

- use `claude-mem` only if the added recall value is real
- otherwise stay with current-session incremental context

## Output behavior

Before substantial work, first obtain the mode if needed.

Then say which skills are being used and why in one concise line.

Examples:

- `Using $tool-advisor to confirm available capabilities, $stream-coding as the workflow skill, and $bucketmanager-s3control-e2e for local S3Control validation.`
- `Using $tool-advisor first, then brainstorming because the request is still in the design phase.`
- `Using $tool-advisor first, then $stream-coding, and adding find-skills because the current installed skills do not clearly cover the requested capability.`

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
