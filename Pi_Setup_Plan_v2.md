# Pi setup plan v2

**Date:** 2 October 2026
**Replaces:** `Pi_Multi_Agent_Architecture_Report.md`
**Status:** plan only. Nothing in this document has been applied.

---

## 1. What this plan does

It configures Pi 1.0 as one supervisor session plus the subagent extension you already have installed.

- Project state lives in files and git, never in the conversation.
- Each milestone runs in a fresh session, so context stays small.
- Parallel writers each get their own git worktree and a small task.
- Work is not "done" until checks run by the host, independent reviewers, and a real-browser QA pass all agree.
- The setup is two config files, two instruction files, three skills, one agent, one short hook and one short loop script. It adds no new orchestrator and no custom extension.

### Decisions I need from you before applying

1. **Quota tier.** Parallel long runs need more than ChatGPT Plus gave you in September (seven limit hits with one agent). Choose the Pro mapping or the Plus mapping in step 4.
2. **Watchdog.** An extra reviewer model call after each supervisor turn that changes the repo. Recommended on Pro, off on Plus.
3. **Node pin.** Your `pi` binary lives inside mise's Node 24 install. Node 26 becomes LTS on 28 October 2026; when mise's `lts` alias moves, `pi` disappears from PATH until reinstalled. Pin `node = "24"` in mise, or accept a reinstall then.

---

## 2. The design

```text
you ── goal ──▶ SUPERVISOR session (GPT-6.1 Sol)      one fresh session per milestone
                 │  reads and writes docs/plan/{SPEC,PLAN,STATUS,DECISIONS}.md
                 │
                 ├─ scout, researcher      read-only, parallel, cheap model
                 ├─ worker lanes ×1–3      one git worktree each, host-run gate
                 ├─ reviewers ×3           fresh context, stronger model than the worker
                 ├─ qa                     real browser through the Playwright CLI
                 └─ oracle                 second opinion on risky decisions
                 │
                 ▼
     integration branch: one small commit per task ──▶ CI ──▶ pull request
```

Why this shape:

- **One writer of history.** Workers never commit. The supervisor applies each accepted task and commits it, so every commit is small and follows one convention.
- **Parallel where it is safe.** Reading, research, review and QA always run in parallel. Writing runs in parallel only for tasks that share no files.
- **Fresh context beats compaction.** Anthropic, OpenAI and Cursor all rely on files plus fresh sessions for long runs. Your September session carried a 131k-token prompt on average for a 3,000-line repo.

### How one milestone runs

1. The supervisor reads `STATUS.md` and picks the next milestone.
2. It groups ready tasks into a wave: no unmet dependencies, no shared files.
3. Each task goes to a `worker` in its own worktree. The host, not the model, runs the quick check there.
4. The supervisor applies each lane's patch in order, reruns the quick check, and commits it.
5. It runs the full check and end-to-end tests on the integrated branch.
6. Three fresh-context reviewers inspect the milestone diff. Fixes go in as separate commits.
7. The `qa` agent walks the acceptance criteria in a real browser.
8. The supervisor writes the evidence into `STATUS.md`, commits, and stops. The next session starts clean.

---

## 3. Components

| Component | Decision | Reason |
|---|---|---|
| Pi 1.0.0 | Upgrade | Codemode, built-in MCP, per-model compaction; your default model GPT-5.5 retires from Codex on 14 October |
| pi-subagents 0.75.0 | Keep, upgrade | Already installed; has lanes, worktrees, host-run acceptance gates, watchdog, missions. 0.75.0 fixes background children on Pi 1.0 |
| pi-web-access 0.35.0 | Keep, upgrade | Web search and fetch for the `researcher` agent |
| @narumitw/pi-usage | Keep | Shows remaining account quota |
| Playwright 1.63 + its CLI | Add per project | The CLI saves page snapshots to files instead of the context, which Playwright's own docs recommend for coding agents |
| Context7 MCP | Optional | Version-specific library docs; zero schema cost under Pi's default `codemode` exposure |
| Taskplane | Not now | Second orchestrator; no release since before Pi 0.99; open issues are mostly resume and state-loss bugs |
| Graphify, pi-memory, agent-comms | No | No benefit at your repo sizes; more moving parts |
| Pi Durable | No | A library for building your own agent app, not an orchestrator |
| Custom extensions, model router | No | Git hooks, CI and built-in gates cover the same ground with no code to maintain |

---

## 4. Setup steps

### Step 0 — Back up

```bash
tar -czf ~/pi-agent-backup-2026-10-02.tgz -C ~/.pi/agent settings.json extensions trust.json
```

### Step 1 — Upgrade

pi-subagents 0.75.0 is in its repository's changelog, dated today, but npm still serves 0.74.0, which cannot start background children on Pi 1.0. Wait for it.

```bash
npm view pi-subagents version        # proceed only when this prints 0.75.0 or newer
npm install -g @earendil-works/pi-coding-agent@1.0.0
pi --version                         # expect 1.0.0
```

After step 2 writes the pinned package list:

```bash
pi update --extensions
pi list
```

Versions are pinned on purpose. Pi packages run with your full user permissions, so upgrades should be deliberate.

### Step 2 — `~/.pi/agent/settings.json`

Merge these keys; keep any keys Pi manages itself. Confirm the model IDs first with `pi --list-models gpt-6`.

```json
{
  "theme": "dark",
  "defaultProvider": "openai-codex",
  "defaultModel": "gpt-6.1-sol",
  "defaultThinkingLevel": "high",
  "showCacheMissNotices": true,
  "defaultTools": ["+codemode"],
  "compaction": {
    "modelOverrides": {
      "openai-codex/gpt-6.1-sol": { "reserveTokens": 110000 },
      "openai-codex/gpt-6-luna": { "reserveTokens": 110000 },
      "openai-codex/gpt-6-astra": { "reserveTokens": 110000 }
    }
  },
  "packages": [
    "npm:pi-subagents@0.75.0",
    "npm:pi-web-access@0.35.0",
    "npm:@narumitw/pi-usage@0.61.2"
  ],
  "subagents": {
    "defaultProvider": "openai-codex",
    "maxThinking": "high",
    "agentOverrides": {
      "scout": { "model": "openai-codex/gpt-6-luna", "thinking": "low" },
      "researcher": {
        "model": "openai-codex/gpt-6-luna",
        "thinking": "medium",
        "extensions": ["/Users/nycruslan/.pi/agent/npm/node_modules/pi-web-access/dist/index.js"]
      },
      "evidence-auditor": {
        "model": "openai-codex/gpt-6.1-sol",
        "thinking": "high",
        "extensions": ["/Users/nycruslan/.pi/agent/npm/node_modules/pi-web-access/dist/index.js"]
      },
      "worker": { "model": "openai-codex/gpt-6.1-sol", "thinking": "medium", "inheritGlobalContext": true },
      "reviewer": { "model": "openai-codex/gpt-6-astra", "thinking": "medium", "inheritGlobalContext": true },
      "oracle": { "model": "openai-codex/gpt-6-astra", "thinking": "high" },
      "delegate": { "model": "openai-codex/gpt-6-luna", "thinking": "medium" }
    },
    "watchdog": {
      "enabled": true,
      "main": { "model": "openai-codex/gpt-6-astra", "thinking": "medium" }
    }
  }
}
```

What each non-obvious key does:

| Key | Effect |
|---|---|
| `compaction.modelOverrides.*.reserveTokens: 110000` | Pi compacts when context exceeds window minus reserve. On a 272k window this fires at 162k (60%) instead of 256k (94%). It is a backstop; fresh sessions per milestone are the main control |
| `defaultTools: ["+codemode"]` | The model can run several tool calls in one script and return only the filtered result. Measure it in step 8; remove the line if it does not help |
| `showCacheMissNotices` | Shows when a request missed the prompt cache, so waste is visible |
| `inheritGlobalContext: true` | Subagents do not read your global `AGENTS.md` by default. This makes the worker and reviewer follow it |
| `maxThinking: "high"` | No subagent can run at `xhigh` or `max` by accident |
| `watchdog` | A second model reviews each supervisor turn that changed the repo and pushes back on unsupported claims |

Not set, on purpose: `cacheWarming` (already the default, and it only applies to models that declare a cache lifetime, which in your installed catalog only Anthropic models do), `codemode.inlineBudget` and `transport` (defaults are fine until measured).

### Step 3 — `~/.pi/agent/extensions/subagent/config.json`

```json
{
  "toolDescriptionMode": "compact",
  "inlineToolDisplay": "summary",
  "fleetView": true,
  "asyncWidget": false,
  "disabledFeatures": ["panes", "external-machines", "extension-bindings", "control-overrides", "preflight", "lane-metadata"],
  "scheduledRuns": { "enabled": false },
  "globalConcurrencyLimit": 4,
  "parallel": { "maxTasks": 8, "concurrency": 4 },
  "maxSubagentDepth": 1,
  "maxSubagentSpawnsPerRun": 16,
  "maxSubagentSpawnsPerSession": 60,
  "maxActiveAsyncRunsPerSession": 3,
  "timeoutMs": 3600000,
  "checkpointBeforeDeadlineMs": 300000,
  "worktreeProvider": "native",
  "worktreeBaseDir": "~/.pi/worktrees",
  "worktreeSetupHook": "~/.pi/agent/extensions/subagent/setup-worktree.mjs",
  "worktreeSetupHookTimeoutMs": 300000,
  "artifactDir": "session"
}
```

- `disabledFeatures` removes parameters you will not use from the `subagent` tool schema, which is sent on every request once delegation is active.
- `maxSubagentDepth: 1` means subagents cannot spawn subagents.
- Four concurrent children is the cap. The build skill limits writers to three; your machine has 8 cores and 16 GB.

**`~/.pi/agent/extensions/subagent/setup-worktree.mjs`** — a new worktree has no `node_modules`, so checks would fail there. This installs dependencies once per worktree.

```js
#!/usr/bin/env node
// Installs dependencies in a new subagent worktree so checks can run there.
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const { worktreePath } = JSON.parse(readFileSync(0, "utf8"));
const has = (file) => existsSync(join(worktreePath, file));
const install =
  has("pnpm-lock.yaml") ? ["pnpm", ["install", "--frozen-lockfile", "--prefer-offline"]] :
  has("bun.lock") ? ["bun", ["install", "--frozen-lockfile"]] :
  has("yarn.lock") ? ["yarn", ["install", "--immutable"]] :
  has("package-lock.json") ? ["npm", ["ci", "--prefer-offline", "--no-audit", "--no-fund"]] :
  null;

if (install) {
  execFileSync(install[0], install[1], { cwd: worktreePath, stdio: ["ignore", "ignore", "inherit"] });
}
process.stdout.write(JSON.stringify({ syntheticPaths: [] }));
```

### Step 4 — Models and quota

The JSON in step 2 uses the Pro mapping. For Plus, change the cells that differ.

| Role | Pro (quality) | Plus (quota-lean) |
|---|---|---|
| Supervisor (main session) | GPT-6.1 Sol, high | GPT-6.1 Sol, medium |
| scout | GPT-6 Luna, low | same |
| researcher | GPT-6 Luna, medium | same |
| worker | GPT-6.1 Sol, medium | GPT-6 Luna, high |
| reviewer | GPT-6 Astra, medium | GPT-6.1 Sol, high |
| qa | GPT-6.1 Sol, medium | GPT-6 Luna, medium |
| oracle | GPT-6 Astra, high | GPT-6.1 Sol, high |
| watchdog | GPT-6 Astra, medium | off |
| Parallel writers | up to 3 | up to 2 |

Two rules hold in both columns: the reviewer is never the same model as the worker, and the reviewer is the stronger of the two.

Trade-off on Plus: OpenAI positions Luna for focused, well-specified coding. It will be weaker on tasks that need judgment, so the supervisor should keep hard tasks for itself as a single writer.

pi-subagents can also generate these mappings from the live catalog and re-check them when models are retired:

```text
/subagents-refresh-provider-models openai-codex
/subagents-generate-profiles openai-codex
/subagents-check-profile <name>
```

Optional cross-family reviewer: pi-subagents ships a `claude-code` agent that sends a handoff to the Claude Code CLI under your Claude login. It has no tools, so it only reviews the diff text it is given. It needs the `claude` CLI on PATH, which is not installed today.

### Step 5 — `~/.pi/agent/AGENTS.md`

Loaded into every session and, through `inheritGlobalContext`, into the worker and reviewer. Short on purpose: it costs tokens on every request.

```markdown
# Engineering rules (all projects)

## Before writing code
- Read the project AGENTS.md and docs/plan/ first. If a task has no acceptance criteria, write them and confirm before coding.
- Check current official docs before using or configuring any library, framework, CLI or API. Find the installed version first, then read the docs for that version. Treat remembered APIs as possibly out of date.
- Record the doc URL in DECISIONS.md or the commit body when it drove a decision.
- Prefer the documented default way. Do not wrap a framework feature in your own layer.

## Code
- Make the smallest change that meets the acceptance criteria. No speculative options, flags, layers or config.
- No new abstraction until there are three real uses. No new dependency when the standard library or an existing dependency does the job.
- Delete dead code, unused exports and commented-out code. No TODOs, stubs, partial implementations or placeholder data.
- Match the surrounding code's style, naming and structure. Comments explain why, never what.
- Handle an error where something can be done about it. Never swallow one.

## Tests and verification
- Every behaviour change comes with a test that fails without the change.
- Never delete, skip or weaken a test to make a run pass. If a test is wrong, say so and fix it in its own commit.
- Done requires evidence: the exact commands run and their exit codes for lint, typecheck, tests and build, plus the Playwright run for anything with a UI. A check that was not run is reported as not run.
- Keep command output out of the conversation: quiet reporters, long output to a temp file, read only the failures.

## Commits
- One logical change per commit, with its tests, reviewable in a few minutes. Aim under 300 changed lines.
- Conventional Commits: `type(scope): summary` in the imperative. The body says why.
- Never mix refactoring with behaviour changes. Never commit generated files, secrets or unrelated formatting.
- Never use `--no-verify`, never force-push, never commit to the default branch.
- Subagents do not stage or commit unless their task says so. The supervisor commits.

## Working method
- State lives in files. Update docs/plan/STATUS.md at every milestone and before stopping.
- Delegate to keep this context small: `scout` maps code, `researcher` reads the web and docs, `reviewer` reviews, `qa` tests in a browser. Do not paste large files or web pages into this conversation.
- One writer per working tree. Parallel writers only in separate worktrees on tasks with no shared files.
- When blocked or facing a product decision, ask. Do not guess.
```

### Step 6 — `~/.pi/agent/WATCHDOG.md`

Standing instructions for the watchdog reviewer. Skip this step if the watchdog is off.

```markdown
Flag as high importance:
- A claim that a check passed with no matching command in the tool log.
- A test deleted, skipped or weakened, or an assertion removed.
- Changes outside the task's stated scope or files.
- A new abstraction, dependency, option or layer that the acceptance criteria do not require.
- TODOs, stubs, placeholder data, swallowed errors, or `--no-verify`.
- A commit that mixes unrelated changes or is far larger than 300 changed lines.
Say nothing when the turn is clean.
```

### Step 7 — Skills

Skills cost one line of context each until used; the body loads only when the task matches.

**`~/.pi/agent/skills/build/SKILL.md`**

```markdown
---
name: build
description: Plan and build a feature or whole system end to end, with parallel subagents, host-run gates, independent review and QA. Use for any multi-step implementation or long-running build, and when asked to continue a build from docs/plan/STATUS.md.
---

# Build

State lives in `docs/plan/`. Create the files if missing. Never rely on conversation history for state.

- `SPEC.md` — goal, constraints, testable acceptance criteria.
- `PLAN.md` — milestones, each split into tasks.
- `STATUS.md` — first line `Plan status: in progress` or `Plan status: complete`; then each milestone's state and evidence.
- `DECISIONS.md` — decisions with reasons, versions and doc links.

## 1. Plan (once, or when the spec changes)

1. If requirements are unclear, ask. Write `SPEC.md`.
2. Launch `scout` for the code and `researcher` for the current official docs of every library involved, in parallel. Record versions and links in `DECISIONS.md`.
3. Write `PLAN.md`. Each milestone ends in a working state you can demonstrate. Each task fits one commit and lists:
   - Depends on
   - May touch (files or globs)
   - Acceptance criteria
   - Check command
4. For a risky design choice, ask `oracle` before committing to it.

## 2. Build one milestone per session

1. Read `STATUS.md`. Pick the next milestone. Work on branch `build/<plan-slug>`, created from the default branch if missing.
2. Form a wave from tasks with no unmet dependencies and no shared files. Tightly coupled work is one task for one writer.
3. Run the wave.
   - One task: do it yourself, or give it to one `worker`.
   - Several tasks: commit or stash first so the checkout is clean. Then make one workflow call that fans out with `runs.all`, at most 3 children, each `agent: "worker"`, `worktree: true`, and
     `acceptance: { level: "verified", evidence: ["changed-files", "tests-added", "commands-run", "residual-risks"], verify: [{ id: "check", command: "<the task's check command>" }] }`.
   - Give each worker only its task block, the acceptance criteria and file pointers. Tell it not to stage or commit.
   - Read `subagent({ action: "guide", topic: "workflows" })` for the exact syntax of the installed version.
4. Integrate lanes in dependency order. For each: take the patch named in the lane's handoff manifest, `git apply --3way <patch>`, run the quick check, commit as one Conventional Commit. On a conflict or a failing check, fix it with a single writer. Never force.
5. Milestone gate: follow the `qa-gate` skill for the full check and end-to-end run. Fix failures before review.
6. Review with three fresh-context `reviewer`s in parallel:
   - correctness and regressions;
   - tests: would each test fail if the code were wrong?
   - simplicity: anything the acceptance criteria do not require;
   - add security when input, auth or stored data is touched.
   Apply P0 and P1 findings with one writer, one commit per fix. Re-review only what changed. Stop after 3 rounds and report what remains.
7. For UI work, launch `qa` with the milestone's acceptance criteria.
8. Update `STATUS.md` with the result, the evidence, open risks and the next milestone. When every milestone is done, set the first line to `Plan status: complete`. Commit. Stop.

## Rules

- One milestone per session. The next session starts from `STATUS.md`.
- In headless runs use `async: false` so the session waits for its children.
- On a usage-limit or provider error: commit what is green, update `STATUS.md`, stop.
- Never mark a milestone done with a failing, skipped or unrun gate.
```

**`~/.pi/agent/skills/qa-gate/SKILL.md`**

```markdown
---
name: qa-gate
description: Verify work before calling it done. Runs the project's checks, Playwright end-to-end and accessibility tests, and exploratory browser testing, then reports evidence. Use before claiming any task, milestone or bug fix is complete, and when writing or fixing end-to-end tests.
---

# QA gate

Run layers in order. Stop at the first failing layer, fix, and rerun from that layer.

| Layer | What runs | Proves |
|---|---|---|
| 1 Static | lint, format check, typecheck, dead-code check | no type errors, nothing unused |
| 2 Tests | unit and integration tests, coverage on changed files | the logic is right |
| 3 Build | production build | it ships |
| 4 End-to-end | Playwright | real user flows work in a browser |
| 5 Accessibility | axe scan inside Playwright | no serious violations |
| 6 Exploratory | `qa` agent | acceptance criteria hold; no console errors or failed requests |
| 7 Supply chain | dependency audit, secret scan | no known-vulnerable packages, no leaked secrets |

The commands are in the project `AGENTS.md`: `check:quick`, `check`, `e2e`.

## Keep output out of context

- Use quiet reporters such as `dot` or `line`.
- Send full output to a file in the OS temp directory. Read only the failing sections.
- When codemode is available, run independent checks in one script with `Promise.allSettled` and return only failures.

## Playwright

Read `references/playwright.md` before writing or changing end-to-end tests.

## A bug found here

Reproduce it with a failing test first. Then fix it. Then rerun from layer 1.

## Evidence report

Required in the final message and in `STATUS.md`. For each layer: the command, exit code, and counts of passed, failed and skipped. A layer that was not run is listed as not run with the reason. Never report it as passed.
```

**`~/.pi/agent/skills/qa-gate/references/playwright.md`**

```markdown
# Playwright rules

Check the installed version with `npx --no-install playwright --version` and read the docs for that version at playwright.dev before using an API you have not verified.

## Tests
- Locate by role, label, text or test id. No CSS or XPath chains.
- Assert with web-first assertions such as `await expect(locator).toBeVisible()`. No fixed sleeps.
- Every test is independent: its own context and data. Set up state through the API or fixtures. Mock third-party network calls.
- Test what the user sees, not implementation details.
- Accessibility: run `@axe-core/playwright` on each main page and fail on serious or critical violations.
- Use `toMatchAriaSnapshot()` for page structure. Use screenshot assertions only for stable components.

## Config
- `webServer` starts the app. `fullyParallel: true`. `forbidOnly` in CI.
- `retries: 2` and `failOnFlakyTests: true` in CI; no retries locally.
- `trace: 'on-first-retry'`, `screenshot: 'only-on-failure'`.
- Chromium for every run. Add Firefox and WebKit for the release gate.

## Running
- `npx playwright test --reporter=line`
- Rerun only failures with `--last-failed`. Run only tests affected by a change with `--only-changed=<base-ref>`.
- For a failure, inspect the trace with the `playwright trace` commands instead of rerunning blindly.

## Exploratory testing with the CLI
- Use `npx playwright cli` when Playwright is installed in the project, otherwise `playwright-cli`. Run `--help` once for the command list.
- `open <url>`, then `snapshot`, act on element refs, `console`, `requests`, `screenshot`.
- Snapshots are written to files. Read only the parts you need; use `find` or a depth limit on large pages.
```

**`~/.pi/agent/skills/project-setup/SKILL.md`**

```markdown
---
name: project-setup
description: Give a repository the quality baseline that the build and qa-gate skills rely on (check scripts, git hooks, Playwright, CI, plan files and a short project AGENTS.md). Use once per new or existing project before the first build.
---

# Project setup

Confirm each tool's current setup in its official docs for the version you install. Use what the project already has. Add only what is missing. Commit each item separately.

1. Scripts. The names are the contract; implement them with the project's own tools.
   - `check:quick` — lint, typecheck, unit tests related to the change. Under about 60 seconds.
   - `check` — lint, format check, typecheck, all tests with coverage, build, dead-code check, dependency audit.
   - `e2e` — Playwright with the line reporter.
2. Git hooks, with lefthook or the hook tool already in the project.
   - pre-commit: format and lint staged files, typecheck, secret scan.
   - commit-msg: Conventional Commits.
   - pre-push: `check:quick`.
3. Lint limits that keep code simple: cyclomatic complexity, nesting depth, function length, unused code.
4. Playwright per `qa-gate/references/playwright.md`: one smoke test per critical user flow, an axe check on main pages.
5. CI: one workflow on push and pull request that runs `check` and `e2e` and uploads the Playwright report and traces on failure.
6. `docs/plan/` with `SPEC.md`, `PLAN.md`, `STATUS.md`, `DECISIONS.md`.
7. Project `AGENTS.md`, under 100 lines: what the project is, how to run it, the three commands above, architecture boundaries, known gotchas. Link to docs instead of copying them.
```

### Step 8 — The `qa` agent

**`~/.pi/agent/agents/qa.md`** (use the Plus model from step 4 if that is your tier)

```markdown
---
name: qa
description: Browser QA. Verifies acceptance criteria in a real browser with Playwright and reports defects with reproduction steps. Does not fix code.
tools: read, grep, find, ls, bash, contact_supervisor
model: openai-codex/gpt-6.1-sol
thinking: medium
systemPromptMode: replace
inheritProjectContext: true
inheritGlobalContext: true
inheritSkills: false
skills: qa-gate
acceptanceRole: read-only
---

You are a QA engineer. You verify; you do not fix.

For each acceptance criterion you are given:
1. Start the app as the project AGENTS.md describes, or use the URL provided.
2. Drive it with the Playwright CLI. Save snapshots and screenshots to files and read only what you need.
3. After each flow, check the browser console and network requests for errors.
4. Try the unhappy paths: empty, invalid and oversized input, double submit, back and refresh, keyboard-only use, a narrow viewport.

Report a table of criteria with PASS or FAIL and the evidence for each: screenshot path, console line or request. For each failure give exact reproduction steps, expected versus actual, and the file you suspect. End with `QA verdict: PASS` or `QA verdict: FAIL`. Never report PASS for something you did not exercise.
```

### Step 9 — Docs lookup (optional)

The `researcher` agent already covers web and docs research. Context7 adds version-specific library docs to the main session.

```bash
pi mcp add context7 --url https://mcp.context7.com/mcp --description "Current, version-specific library documentation"
pi mcp list
```

Pi exposes MCP tools through codemode by default, so nothing is added to the tool list. A free API key raises the rate limit; pass it with `--bearer-token-env-var`.

### Step 10 — Long-running loop

**`~/.pi/agent/bin/pi-build-loop`** — runs one milestone per fresh session until the plan is complete. A non-zero exit (usage limit, provider error, crash) waits 30 minutes and retries from `STATUS.md`.

```bash
#!/usr/bin/env bash
# One milestone per fresh Pi session until docs/plan/STATUS.md says the plan is complete.
set -u
max_sessions=${1:-30}
for i in $(seq 1 "$max_sessions"); do
  grep -q '^Plan status: complete' docs/plan/STATUS.md 2>/dev/null && exit 0
  pi --print --name "build-$i" \
    "Use the build skill. Continue from docs/plan/STATUS.md with the next milestone, then stop." \
    || sleep 1800
done
```

Run it from the project root:

```bash
caffeinate -i ~/.pi/agent/bin/pi-build-loop 30
```

Because every session is fresh, a resume after a usage-limit wait re-reads a small plan file rather than re-sending a 250k-token conversation at full price, which is what cost you a third of your uncached input in September.

### Step 11 — Container for unattended runs

Pi has no sandbox, and step 10 runs without you watching. Before the first unattended run, put Pi in a container.

- Follow Pi's documented plain-Docker recipe: a Node 24 image with Pi installed, the project mounted at `/workspace`, and a named volume for `/root/.pi/agent`.
- Do not mount your host `~/.pi/agent`. Log in once inside the container and copy in only the files from steps 2 to 8.
- Install Playwright's Chromium and system dependencies in the image.
- Use two lanes inside the container on this machine.

Until then, do not leave the loop unattended on this machine. Run it only while you are watching.

---

## 5. The QA system

| # | Gate | When | Enforced by |
|---|---|---|---|
| 1 | Format, lint, typecheck, secret scan | every commit | git pre-commit hook |
| 2 | Commit message convention | every commit | git commit-msg hook |
| 3 | Quick check | every worker task | pi-subagents acceptance gate, run by the host in the worker's worktree |
| 4 | Full check: all tests with coverage, build, dead-code check, audit | every milestone | supervisor, `qa-gate` skill |
| 5 | End-to-end and accessibility | every milestone with a UI or API surface | Playwright and axe |
| 6 | Three independent reviews | every milestone | fresh-context `reviewer` on a stronger model |
| 7 | Exploratory browser QA | milestones with a UI | `qa` agent, Playwright CLI |
| 8 | Turn-boundary review | each supervisor turn that changed the repo | pi-subagents watchdog |
| 9 | CI | every push | GitHub Actions |

Gates 1, 2, 3 and 9 are deterministic: the model cannot talk its way past them. A worker's own statement that tests passed does not count; the host runs the command.

Limit: no QA system catches every bug. This one makes "done" mean that nine separate checks, four of them not under the model's control, found nothing.

Optional for core logic: mutation testing (Stryker) on changed files. It is the only check that tests the tests. Off by default because it is slow.

---

## 6. After applying: verify and measure

1. `pi --version` prints 1.0.0 and `pi list` shows the three pinned packages.
2. `/subagents-doctor` is clean and `/subagents-models` shows the mapping from step 4.
3. On a throwaway repo: run `/skill:project-setup`, then a build with a two-task wave. Confirm the gate ran on the host, two small commits landed, reviewers ran, and the evidence report lists every layer.
4. Compare against your September baseline using `/session` and `/subagent-cost`.

| Measure | September | Target |
|---|---|---|
| Supervisor mean prompt | 131k tokens | under 60k |
| Compactions per session | 4–5 | 0 in a milestone session |
| Cache hit ratio | 98% | 95% or better |
| Uncached input after a wait | 116k–247k per resume | under 20k |
| Work delegated to subagents | none | all research, review and QA |

If codemode or the watchdog does not improve these numbers, turn it off.

---

## 7. Risks and open points

- **pi-subagents 0.75.0 is not on npm yet.** Step 1 waits for it.
- **Model IDs and limits change.** GPT-5.5 retires from Codex on 14 October. Run `/subagents-check-profile` after each Pi update.
- **Luna as a worker** is weaker on tasks that need judgment. Keep tasks small and specified.
- **Third-party packages run with your permissions**, on a machine that also holds private projects and credentials. Versions are pinned; step 11 is the real boundary.
- **Machine capacity.** Three worktrees each installing dependencies and running tests is close to the limit of 8 cores and 16 GB. Start with two.
- **Not tested.** I installed nothing. Step 6 is where the configuration is proven.

---

## 8. When to revisit what was left out

| Left out | Revisit when |
|---|---|
| Taskplane | You need more than three lanes with automated merges, and it has shipped a release tested on Pi 1.x |
| Graphify | A repo passes roughly 100k lines and scouts keep missing cross-file links |
| Second provider | You want a reviewer from a different model family; an API key or the `claude-code` agent both work |
| Custom done-gate extension | The supervisor claims completion with failing checks despite gates 1–9 |
| Pi Durable | You decide to build your own agent application |

---

## Sources

- Pi 1.0 docs: [settings](https://pi.dev/docs/latest/settings), [compaction](https://pi.dev/docs/latest/compaction), [codemode](https://pi.dev/docs/latest/codemode), [MCP](https://pi.dev/docs/latest/mcp), [CLI](https://pi.dev/docs/latest/cli), [changelog](https://pi.dev/changelog), [model catalog](https://pi.dev/models)
- pi-subagents: [repository](https://github.com/nicobailon/pi-subagents), [changelog](https://github.com/nicobailon/pi-subagents/blob/main/CHANGELOG.md), [tool reference](https://github.com/nicobailon/pi-subagents/blob/main/docs/tool-reference.md), [workflows](https://github.com/nicobailon/pi-subagents/blob/main/docs/workflows.md), [watchdog](https://github.com/nicobailon/pi-subagents/blob/main/docs/watchdog.md), [agents](https://github.com/nicobailon/pi-subagents/blob/main/docs/agents.md), [models](https://github.com/nicobailon/pi-subagents/blob/main/docs/models.md)
- Playwright: [best practices](https://playwright.dev/docs/best-practices), [test agents](https://playwright.dev/docs/test-agents), [release notes](https://playwright.dev/docs/release-notes), [CLI](https://github.com/microsoft/playwright-cli)
- OpenAI: [Codex models](https://learn.chatgpt.com/docs/models), [Codex pricing and limits](https://learn.chatgpt.com/docs/pricing), [long-horizon tasks](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex)
- Context7: [repository](https://github.com/upstash/context7)
- Long-running and multi-agent practice: [Anthropic harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), [Anthropic C compiler](https://www.anthropic.com/engineering/building-c-compiler), [Cursor self-driving codebases](https://cursor.com/blog/self-driving-codebases), [Cognition on multi-agents](https://cognition.com/blog/multi-agents-working), [Claude Code agent teams](https://code.claude.com/docs/en/agent-teams)
- Node.js 26 LTS date: [release coverage](https://www.inmotionhosting.com/support/news/nodejs-v26-released/)
