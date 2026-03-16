---
name: tgtool
description: Select the most relevant local Codex skills for the user's request and proactively use them. Use when the user asks to choose suitable skills, to auto-apply matching skills, or to route a task through the best available skill workflow.
metadata:
  author: codex
  version: "1.0.0"
---

# TGTool

Use this skill when the user wants skill routing help, asks which skills fit a task, or expects the agent to proactively use matching local skills.

## Goal

Pick the smallest set of relevant local skills and immediately use them instead of treating skill choice as a separate planning step. By default, consult `$tool-advisor` first, then choose the most suitable **workflow skill** before selecting the final domain or task-specific execution skills.

If `superpowers` workflow skills are installed and available in the current session, prefer routing to them when they are a better match than `$stream-coding`.

## Mode selection

Before substantial work, first ask the user which mode to use unless the user already specified one.

Use a short direct question such as:

`Choose a tgtool mode: review, standard, autopilot, or max-autonomy.`

### Modes

- `review`
  - Recommend skills and plan first.
  - Do not execute until the user confirms.
- `standard`
  - Execute normally.
  - Ask when a meaningful branch or risk appears.
- `autopilot`
  - Execute end-to-end with minimal interruption.
  - Only stop for destructive actions, critical ambiguity, or required permission escalation.
- `max-autonomy`
  - Same as `autopilot`, but assume the strongest execution autonomy the session allows.
  - Still cannot bypass platform, sandbox, or tool-level permission prompts.
  - If an escalated command requires approval, request it immediately instead of asking a separate planning question.
  - Do not modify low-level system files, do not delete underlying system files, and do not perform actions that could disrupt normal system operation unless the user explicitly asks for them.

## Rules

1. Read the current session's available skill list first.
2. Unless the user explicitly forbids it, consult `$tool-advisor` first for environment-aware tool routing.
3. Then choose **one primary workflow skill** based on task shape. Do not default to `$stream-coding` if a better-fit `superpowers` workflow skill is available.
4. Match skills by direct user mention first, then by task fit.
5. Prefer the minimal set of skills that fully covers the request.
6. Avoid stacking overlapping workflow skills unless the task clearly spans multiple phases.
7. When the task would materially benefit from cross-session memory, project-history lookup, or reducing repeated context reconstruction, proactively consider `claude-mem` as a memory capability.
8. When the task would materially benefit from live web research, recent documentation, latest product information, or broad webpage discovery, proactively consider `exa` as a research capability.
9. If multiple skills apply, state the order and why in one short line.
10. After choosing, open each selected `SKILL.md` and follow it.
11. If a named skill is missing, say so briefly and continue with the best fallback.
12. Respect the selected mode throughout the task.
13. Do not stop after recommending skills; execute the task using them.
14. Continuously watch for memory-risk during planning and execution. If the expected operation may cause memory exhaustion or unsafe memory growth, stop and ask whether to switch to a safer plan.
15. Continuously watch for storage-capacity risk during planning and execution. If the expected operation may cause local disk exhaustion, report-bucket overflow, temporary-file growth beyond safe limits, or other unsafe storage pressure, stop and ask whether to switch to a safer plan.
16. Use Chinese by default for all user-facing interaction unless the user explicitly requests another language.
17. Be context-friendly: prefer reusing established facts from the current conversation instead of re-deriving or reloading them unless verification is actually needed.
18. Be token-efficient: prefer concise summaries, deltas, and direct conclusions over repeated background, repeated file inventories, or long verbatim command output.

## Selection heuristic

### Default routing order

1. `$tool-advisor`
   - Use to discover the current tool environment and suggest the most suitable execution path.
2. Workflow skill selection
   - Choose the single best workflow skill for the current task shape.
   - Candidate examples:
     - `$stream-coding`
     - `brainstorming`
     - `writing-plans`
     - `executing-plans`
3. Domain or task-specific skills
   - Use the results from the first two layers to choose the final execution skills, then carry out the task.
4. Memory capability selection
   - If the task depends on prior-session recall, project-history search, or avoiding repeated reconstruction of known context, consider `claude-mem`.
5. Research capability selection
   - If the task depends on live web search, recent information, broad website discovery, or external documentation lookup, consider `exa`.

- If the user explicitly names a skill, always use it.
- If a task clearly matches one domain, use one skill.
- If one skill covers execution and another covers research or orchestration, use both.
- If long-lived context would materially improve accuracy or token efficiency, add `claude-mem`; otherwise do not load it by default.
- If recent external information would materially improve accuracy or save tool effort, add `exa`; otherwise do not load it by default.
- Avoid broad stacking. Do not load extra skills unless they materially change the outcome.

### Workflow-skill chooser

- Prefer installed `superpowers` workflow skills when they match well and are available in the current session.
- Use `$stream-coding` for implementation, structured execution, repeatable engineering workflows, or when the user wants build/test/change work done end-to-end.
- Use `brainstorming` for early-stage exploration, option generation, ambiguous requirements, or design discussion.
- Use `writing-plans` when the task needs a detailed execution plan before action.
- Use `executing-plans` when a plan already exists and the main need is disciplined execution.
- If two workflow skills overlap, prefer one. Only chain them when the task genuinely moves across phases, for example `brainstorming -> stream-coding`.

### Memory chooser

- Use `claude-mem` when the user asks what was done before, asks to continue a long-running effort, needs prior experiments or decisions recalled, or when repeated context reconstruction would waste tokens.
- Do not use `claude-mem` for short, self-contained tasks where current-session context is already sufficient.
- When chosen, treat it as a supporting memory capability, not a replacement for workflow or domain skills.

### Research chooser

- Use `exa` when the user needs latest information, external references, broad web discovery, or current documentation outside the local workspace.
- Do not use `exa` for purely local code tasks, purely historical recall, or when current-session/local-repo context is already sufficient.
- When chosen, treat it as a supporting research capability, not a replacement for workflow or domain skills.

## Safety notes

- `max-autonomy` is not permissionless mode. It is high-autonomy mode within the current session limits.
- Even in `max-autonomy`, avoid touching low-level system files, deleting system-critical files, or performing actions that may destabilize the host unless the user explicitly requested that exact action.
- For large-data, large-build, or large-memory tasks, estimate memory pressure early. If the safer path differs materially from the fastest path, surface that choice to the user before proceeding.
- For large-data, large-build, or artifact-heavy tasks, estimate storage pressure early. If the safer path differs materially from the fastest path, surface that choice to the user before proceeding.
- Keep active context compact: load only the files and logs needed for the current step, summarize intermediate findings, and avoid re-reading large files unless something has changed or verification is required.
- When continuing a multi-turn task, prefer incremental updates based on what is already known. Do not restate large unchanged context unless it helps a new decision.

## Output behavior

Before substantial work, first obtain the mode if it is not already specified. Then say which skill or skills you are using and why in one concise line. If `$tool-advisor` is used first, summarize its effect, then state the chosen workflow skill, then the final execution skills and plan.

Examples:

- `Using $tool-advisor to confirm the environment, $stream-coding as the workflow skill, and $bucketmanager-s3control-e2e for the local bitmap end-to-end test path.`
- `Using $tool-advisor first, then brainstorming as the workflow skill because this request is still in the design phase.`

## Common combinations

- Tool discovery or environment-aware execution:
  - `tool-advisor`
- Superpowers-assisted design or planning:
  - `brainstorming`
  - `writing-plans`
  - `executing-plans`
- Structured implementation or spec-first work:
  - `stream-coding`
- Cross-session history and persistent memory lookup:
  - `claude-mem`
- Live web research and external source lookup:
  - `exa`
- Local bucketmanager bitmap E2E and rebuild testing:
  - `bucketmanager-s3control-e2e`
- Creating or updating a skill:
  - `skill-creator`

## Scope

This skill does not replace the selected skill. It is the router and activator: it should first consult `$tool-advisor`, then choose the most appropriate workflow skill, then proactively call the final execution skills and carry out the work.
