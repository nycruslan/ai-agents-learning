# High-Performance Long-Running Multi-Agent Architecture for Pi

**Final researched design**  
**Verified:** October 2, 2026  
**Goal:** Build applications autonomously for hours or days with high throughput, reliable recovery, controlled parallelism, strong code quality, and minimized context/token waste.

---

## Executive Summary

The strongest Pi-based architecture is **not** a large swarm of agents sharing one giant context. The better design is a small, adaptive fleet of isolated workers coordinated by one durable control plane, with state externalized to Git/files/databases, selective retrieval, structured handoffs, sticky model routing, and deterministic tooling wherever possible.

The recommended practical stack today is:

- **Pi 1.0** as the agent runtime.
- **Taskplane** as the current turnkey orchestrator for dependency-aware parallel coding.
- **3 concurrent code-writing workers by default**, with a normal ceiling of 4 unless the repository has unusually clean module boundaries.
- **Git worktree isolation** for every code-writing worker.
- **Pi Subagents** for short-lived specialists, especially read-only research, code scouting, review, test investigation, and architecture analysis.
- **Pi Codemode** for parallel deterministic tool work and aggressive filtering of large outputs before they enter model context.
- **Graphify** as a selective structural retrieval layer for dependency/path/impact questions, not as a replacement for source code or exact search.
- **Repo-local hierarchical memory** for architecture decisions, contracts, invariants, task state, and discoveries.
- **Pi's native compaction**, augmented with structured handoff summaries and exact pinned invariants.
- **Sticky role-based model routing** so each long-lived worker remains on the same physical model where possible, preserving prompt-cache benefits.
- **Targeted tests during implementation**, wider integration checks at merge boundaries, and full validation at major milestones/final integration.
- **Pi Durable** as the intended future control plane once its experimental API stabilizes enough for production use.

The governing principle is:

> **Use the smallest number of agents and the smallest amount of context that can complete the work correctly, while putting all durable truth outside the LLM conversation.**

---

# 1. What the System Is Optimizing For

The target is not simply “maximum parallel agents.” The system should optimize the following simultaneously:

1. **Wall-clock throughput**: independent application components should be built concurrently where that is safe.
2. **Correctness**: parallel work must not increase merge errors, architectural drift, or test failures.
3. **Durability**: a process crash, machine restart, provider failure, context reset, or worker replacement should not lose project state.
4. **Context efficiency**: workers should receive only the information required for their current task.
5. **Token efficiency**: avoid repeatedly sending tool schemas, logs, old conversation history, unrelated source files, and other agents' reasoning.
6. **Prompt-cache stability**: stable prefixes and sticky physical models should be preserved when possible.
7. **Observability**: task progress, blocked dependencies, tests, retries, cost, tokens, and failures must be measurable.
8. **Safety and isolation**: concurrent writers should not accidentally corrupt one another's files or gain unnecessary machine credentials.
9. **Recoverability**: every worker should be replaceable from persistent task state rather than requiring its original chat history.
10. **Scalability of coordination**: adding agents should not create an all-to-all communication problem.

These goals lead to a **centralized orchestration + isolated execution + externalized memory** architecture.

---

# 2. Final Architecture

```text
                              USER
                                │
                                ▼
                     ┌────────────────────┐
                     │ SUPERVISOR/PLANNER │
                     │ durable state      │
                     │ routing            │
                     │ dependency DAG     │
                     └─────────┬──────────┘
                               │
                     Adaptive scheduler
                      1-4 writers normally
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
      ┌───────────┐      ┌───────────┐      ┌───────────┐
      │ Worktree A│      │ Worktree B│      │ Worktree C│
      │ Worker A  │      │ Worker B  │      │ Worker C  │
      │ private ctx│     │ private ctx│     │ private ctx│
      └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               ▼
                    Integration/orch branch
                               │
                               ▼
                       Dedicated reviewer
                               │
                               ▼
                      Verification/test gate
                               │
                               ▼
                              Merge

                ───────── KNOWLEDGE PLANE ─────────

       exact search           structure          project knowledge
       rg/read/git            Graphify           ADRs/contracts/docs
            │                    │                       │
            └────────────────────┼───────────────────────┘
                                 ▼
                         Retrieval router

                ───────── DURABLE STATE ───────────

          Git + task state + status files + artifacts
          + decisions + tests + event journal + metrics

                ───────── CONTROL PLANE ───────────

           Taskplane today → Pi Durable longer term
```

The LLM conversation is **working memory**, not project state.

---

# 3. Orchestration: One Control Plane Only

Do not combine several orchestration frameworks at once. Avoid configurations such as:

```text
Taskplane + pi-spine + pi-long-task + custom supervisor
```

They overlap in responsibility and create conflicting scheduling/state models.

## Recommended now: Taskplane

Taskplane is currently the best turnkey starting point for this design because it provides Pi-oriented multi-agent coding with parallel execution, fresh-context worker loops, cross-model review, automated integration, and worktree-oriented orchestration.

Use it as the main control plane while the architecture is being validated.

### Responsibilities of the supervisor

The supervisor should:

- Parse the user goal.
- Establish architecture and hard constraints.
- Produce a dependency DAG.
- Decide which tasks are safe to run concurrently.
- Assign ownership boundaries.
- Route models and tools.
- Track blockers.
- Accept structured worker results.
- Decide when project memory must be updated.
- Trigger review/integration.
- Control retry and escalation policies.

The supervisor should **not** normally implement application code itself. Mixing orchestration and implementation causes its context to grow too quickly and makes the control plane fragile.

---

# 4. Future Control Plane: Pi Durable

Pi Durable was released experimentally alongside Pi 1.0 on October 1, 2026. It is explicitly designed for long-running durable agents.

It provides key primitives that matter for this use case:

- Persistent conversations.
- Concurrent conversations inside one harness.
- Storage backends including memory, SQLite, and JSONL, with a small interface for custom backends.
- Checkpointed model/tool tasks.
- Crash recovery and resumption.
- Background tasks.
- Exactly-once submission support through request IDs.
- Per-conversation model/tool/instruction/working-directory configuration.
- Durable application documents stored alongside conversations.
- Forkable conversations without manually copying all history.
- Steering and queued follow-ups while conversations are running.

This matches the desired long-term model almost perfectly:

```text
Pi Durable Harness
│
├── supervisor conversation
├── planner/architect conversation
├── worker A conversation + worktree/container
├── worker B conversation + worktree/container
├── worker C conversation + worktree/container
├── reviewer conversation
└── merger/integration conversation

+ durable task documents
+ Git
+ artifacts
+ metrics
```

However, Pi Durable is currently described by its authors as **experimental**. Therefore the preferred sequence is:

```text
Phase 1: Taskplane
Phase 2: instrument and benchmark
Phase 3: custom Pi Durable control plane
```

Do not rebuild Taskplane immediately. First learn which parts of its behavior are valuable on real projects.

---

# 5. Parallelism: Use Adaptive Concurrency

The goal is not to maximize the number of writers. The goal is to maximize **useful independent work per unit time**.

## Default concurrency

Start with:

```text
Code-writing workers: 3
Normal ceiling:       4
Read-only specialists: flexible, usually 2-6
Reviewer:             1
Supervisor:           1
Merger/integrator:    1 when needed
```

Only raise writer concurrency when ownership boundaries are clearly independent.

## Example

Safe parallel tasks:

```text
frontend dashboard
backend billing service
Terraform deployment
integration-test harness
```

Unsafe parallel decomposition:

```text
agent A changes UserService
agent B refactors UserService
agent C modifies UserService tests and API shape
agent D changes shared DTOs
```

The second setup creates coordination and merge work faster than the agents create useful code.

## Scheduler rule

```text
If tightly coupled → 1 writer + scouts/reviewer
If 2 independent components → 2 writers
If 3-4 independent modules → 3-4 writers
If large modular monorepo → consider >4 only after measurements prove a gain
```

Concurrency should therefore be a property of the **task graph**, not a static fleet size.

---

# 6. Build a Dependency DAG Before Spawning Writers

A large request should first become tasks with explicit dependencies.

Example:

```text
T001 architecture + interfaces
      │
      ├──────────────┬──────────────┐
      ▼              ▼              ▼
T010 database   T020 UI shell   T030 deployment base
      │              │
  ┌───┴────┐     ┌───┴────────┐
  ▼        ▼     ▼            ▼
T011 auth T012 billing  T021 dashboard T022 admin
  │        │       │            │
  └────────┴───────┴────────────┘
                    │
                    ▼
              T040 integration
                    │
                    ▼
               T050 full E2E
```

Only dependency-ready nodes run.

Each task must have:

- Goal.
- Owned paths/modules.
- Readable dependencies.
- Files/modules it must not modify.
- Acceptance criteria.
- Validation commands.
- Expected artifacts.
- Retry budget.
- Review requirement.

A task without parseable work steps or acceptance criteria should fail preflight rather than entering the worker queue.

---

# 7. Worktree Isolation Is Mandatory for Writers

Every code-writing agent should operate in its own Git worktree/branch.

```text
project/
worktrees/
  T011-auth/
  T012-billing/
  T021-dashboard/
```

Workers commit into their own branch. The orchestrator merges completed work into an orchestration/integration branch.

Benefits:

- Writers cannot overwrite each other's uncommitted work.
- Diffs remain task-scoped.
- Failed workers can be discarded cheaply.
- Review can operate on a commit/branch instead of a huge conversation.
- A worker can be restarted from Git + task state.

Pi Subagents currently supports `isolation: worktree` for exactly this kind of use case.

### Important limitation

A worktree is **not a security sandbox**.

The worker may still access the same user account, home directory, network, credentials, or other machine resources available to the Pi process.

For unattended production-grade execution, move writers toward:

```text
ephemeral container/VM
+ one worktree mounted
+ minimal credentials
+ resource limits
+ restricted network where possible
```

---

# 8. Context Management: Agents Should Start Small

The highest-value context optimization is simple:

> **Do not inherit the parent conversation by default.**

Pi Subagents currently defaults `inherit_context` to `false`, which is the correct default for this architecture.

A new worker should receive only:

```text
role/system instructions
+ exact invariants relevant to its task
+ task PROMPT
+ current STATUS if resuming
+ dependency RESULTs
+ relevant architecture/contracts
+ artifact/source pointers
```

It should **not** receive:

```text
supervisor's full conversation
other workers' full conversations
all terminal logs
entire project documentation
unrelated source files
old abandoned reasoning
```

The worker should discover additional context on demand.

---

# 9. Context Hierarchy

Use five conceptual layers.

## Layer 0: Canonical truth

Highest authority:

- Current source code.
- Executable tests.
- Database schema/migrations.
- API/schema contracts.
- Git commits/diffs.

## Layer 1: Exact pinned invariants

Rules that should not be summarized away:

```text
Do not change public API X.
Never delete tests merely to make the suite pass.
All DB migrations must be reversible.
Never commit credentials.
Authentication protocol is frozen unless task explicitly changes it.
```

Store these in something like `.agent/INVARIANTS.md` and inject relevant rules verbatim.

## Layer 2: Project knowledge

- Architecture descriptions.
- ADRs.
- API contracts.
- Conventions.
- Known gotchas.
- Important discoveries.
- Accepted design rationale.

## Layer 3: Task memory

- `PROMPT.md`.
- `STATUS.md`.
- `RESULT.md`.
- Owned paths.
- Dependency outputs.
- Commits.
- Test state.
- Blockers.

## Layer 4: Active working context

- Current Pi session.
- Recent tool output.
- Temporary reasoning.
- Currently opened source sections.

## Layer 5: Archive

- Complete raw transcripts.
- Full logs.
- historical events.
- superseded artifacts.

Archive data should almost never be automatically injected.

---

# 10. Compaction Must Not Be the Only Memory Strategy

Pi's current compaction defaults are:

```json
{
  "compaction": {
    "enabled": true,
    "reserveTokens": 16384,
    "keepRecentTokens": 20000
  }
}
```

Compaction is useful as a safety mechanism but should not be trusted to preserve every exact invariant indefinitely.

Recent 2026 work on long-running agent memory specifically identifies a **compaction cliff**: rules and episodic history often get summarized together even though they require different retention policies. Separate exact rules from compressible history.

A particularly interesting recent direction is **CliffCompaction**, which avoids accumulating summary drift by dropping/truncating original information instead of repeatedly rewriting summaries of summaries.

The system should therefore use **typed retention**:

```text
exact constraints → pinned verbatim
source truth       → retrieve from repo
important decisions→ structured project memory
progress           → STATUS/RESULT
old interaction    → summarize/drop/archive
```

---

# 11. Structured Handoffs Before/At Compaction

Configure or implement a structured handoff format rather than relying on generic prose summaries.

Example:

```markdown
# Mission
Implement subscription billing.

# Immutable constraints
- See .agent/INVARIANTS.md

# Completed
- Stripe client
- subscription creation
- webhook validation

# Current state
Cancellation flow is being implemented.

# Commits
- a912ef1 Stripe client
- b351fa2 subscription API

# Owned files
- src/billing/**
- tests/billing/**

# Verification
PASS unit billing
PASS webhook unit
FAIL cancellation integration

# Decisions
- ADR-014 defines subscription state transitions

# Blockers
None

# Next action
Fix cancellation integration behavior.
```

A fresh worker should be able to resume using:

```text
PROMPT + STATUS + RESULT + Git + exact invariants
```

without the original transcript.

That is the test for whether memory design is good enough.

---

# 12. Repo-Local Memory Layout

Recommended structure:

```text
.agent/
├── INVARIANTS.md
├── PROJECT.md
│
├── architecture/
│   ├── overview.md
│   ├── boundaries.md
│   └── data-flow.md
│
├── decisions/
│   ├── ADR-001.md
│   └── ...
│
├── contracts/
│   ├── users.md
│   ├── auth.md
│   └── billing.md
│
├── tasks/
│   ├── T011/
│   │   ├── PROMPT.md
│   │   ├── STATUS.md
│   │   └── RESULT.md
│   └── ...
│
├── discoveries/
│   └── ...
│
├── artifacts/
│   └── ...
│
└── events/
    └── events.jsonl
```

This makes the repository itself a recoverable organizational memory.

OpenAI's 2026 long-horizon Codex experiment reinforces this pattern: a roughly 25-hour autonomous coding run used persistent specification, plan, implementation instructions, and continuously updated documentation rather than relying on one giant conversation alone.

---

# 13. Memory Writes Should Be Curated

Do not allow every worker to freely write canonical project memory.

Use a **single-writer or validated-write** model:

```text
worker discovers something
        │
        ▼
memory proposal
        │
        ▼
supervisor validates/deduplicates/classifies
        │
        ├── task-only → STATUS
        ├── durable decision → ADR/project memory
        ├── exact contract → contract file
        ├── transient → ignore
        └── global preference → optional global memory
```

Example proposal:

```json
{
  "type": "memory_proposal",
  "scope": "project",
  "category": "gotcha",
  "fact": "Cancellation webhooks may arrive after subscription state updates.",
  "evidence": [
    "src/billing/webhooks.ts",
    "tests/billing/cancel.test.ts"
  ]
}
```

This prevents project memory from becoming a noisy unverified diary.

---

# 14. pi-memory: Use It Narrowly

`pi-memory` can be valuable, but it should **not** become the main source of rapidly changing project execution state.

Its current default `stable` snapshot strategy is useful because it keeps the injected prefix byte-stable between deliberate refresh points, preserving KV/prompt cache behavior.

Its optional `per-turn` mode performs prompt-dependent retrieval injection every turn and explicitly trades away that cache stability.

Recommendation:

```text
pi-memory stable mode:
  YES for long-lived personal/global coding preferences
  YES for general reusable lessons
  MAYBE for a small number of stable project defaults

pi-memory per-turn automatic retrieval:
  NO by default for the main coding fleet
```

Use on-demand memory search instead of making every prompt mutate its memory prefix.

Store fast-changing project state in the repository/task database.

---

# 15. Retrieval Should Be Routed by Question Type

There is no single best retrieval technology.

Create a lightweight retrieval router.

```text
Need information
      │
      ├── exact identifier/string/path?
      │      → rg / grep / find / direct read
      │
      ├── code history/change origin?
      │      → git log / diff / blame
      │
      ├── dependency/path/impact question?
      │      → Graphify
      │
      ├── design decision or project document?
      │      → full-text/BM25/qmd
      │
      ├── fuzzy conceptual memory?
      │      → semantic retrieval
      │
      └── uncertain/complex?
             → short read-only scout agent
```

This is more efficient than sending every question to an LLM or Graphify.

---

# 16. Graphify: Recommended, But as a Structural Index

Graphify is useful because it creates a persistent knowledge graph over code structure.

Current Graphify documentation describes local tree-sitter parsing for code and relationships including calls, imports, inheritance, cross-file relationships, communities, and highly connected “god nodes.” It produces a queryable graph rather than relying solely on vector similarity.

Use it for questions such as:

```text
What depends on AuthService?
How does Billing reach DatabaseClient?
What calls this function?
Which components are tightly connected?
What subsystem would this change affect?
```

Use exact source tools for questions such as:

```text
Where is MAX_RETRIES defined?
What does this exact function currently return?
Find every occurrence of FooBar.
```

## Graph freshness

Prefer maintaining Graphify against the integrated/orchestration branch.

```text
Wave of workers
      ↓
merge successful branches
      ↓
affected tests
      ↓
graphify update .
      ↓
next DAG wave
```

Do not necessarily rebuild every temporary worker worktree's graph unless that task specifically benefits from a local graph.

## Authority rule

Graphify is a navigation/relationship index, not canonical truth.

```text
Graphify says X
       ↓
locate source
       ↓
verify source/tests
       ↓
make high-impact decision
```

Graph edges may be extracted, inferred, or ambiguous, so high-impact changes should be confirmed against actual code.

---

# 17. Inter-Agent Communication: Possible, But Minimize It

Agents can communicate, but free-form all-to-all chat should **not** be the default.

Bad topology:

```text
A ↔ B ↔ C ↔ D
↕   ↕   ↕   ↕
E ↔ F ↔ G ↔ H
```

Better topology:

```text
             Supervisor
        ┌──────┼──────┐
        ▼      ▼      ▼
        A      B      C
```

Workers should first try:

1. Exact source search.
2. Git/history.
3. Graphify if structural.
4. Project memory/artifacts.
5. Dependency result files.
6. Then ask another agent if the answer truly exists only in its current work.

## Structured message types

Use a tiny schema:

```text
QUESTION
ANSWER
DISCOVERY
BLOCKED
UNBLOCKED
CONTRACT_CHANGE
DEPENDENCY_READY
REVIEW_REQUEST
REVIEW_RESULT
HANDOFF
```

Example:

```json
{
  "type": "CONTRACT_CHANGE",
  "sourceTask": "T021",
  "resource": "GET /api/user",
  "summary": "avatarUrl is now nullable",
  "artifact": ".agent/contracts/users.md",
  "affects": ["T024", "T027"]
}
```

Send a short structured summary plus a pointer to an artifact. Never send an entire worker transcript unless exceptional debugging requires it.

---

# 18. agent-comms: Optional Cross-Harness Layer

The Pi ecosystem's `agent-comms` package can provide DMs, rooms, discovery, and delivery timing such as `steer`, `followUp`, and `info` across multiple harness types.

Use it when the actual fleet spans systems such as:

```text
Pi
Claude Code
Codex
other MCP-compatible agents
```

If all workers live under one custom Pi Durable harness, prefer a simpler durable internal queue/document mechanism first.

Rule:

```text
single Pi control plane → internal durable messages
cross-harness fleet     → agent-comms becomes useful
```

---

# 19. Pi Subagents: Best for Specialists

Pi Subagents is particularly valuable for short-lived agents whose contexts should be isolated.

Good specialist roles:

```text
code-scout
security-reviewer
test-investigator
API-researcher
architecture-reviewer
performance-investigator
documentation-researcher
```

Recommended defaults:

```text
inherit_context: false
read-only whenever possible
minimal skills/extensions
worktree isolation only if writer privileges are needed
small turn/token budget
no recursive spawning by default
```

Do not allow uncontrolled agent trees such as:

```text
agent → agent → agent → agent → ...
```

The supervisor should be the normal spawning authority.

---

# 20. Codemode Is a Core Optimization

Pi Codemode lets the model generate a JavaScript script that calls other tools, performs calls in parallel, and filters results before returning output to the model.

Only the script's returned output reaches the model context.

This is ideal for:

```text
run tests
run lint
run typecheck
inspect git diff
search several symbols
query several APIs
```

Instead of:

```text
LLM → tool
LLM → tool
LLM → tool
LLM → tool
```

use:

```text
                 ┌─ tests
                 ├─ lint
LLM → Codemode ──┼─ typecheck
                 ├─ search
                 └─ git diff
                      │
                      ▼
                 compact result
                      │
                      ▼
                     LLM
```

Codemode supports `Promise.allSettled()` for concurrency and an explicit `max_output_tokens` budget.

### Recommended routine output cap

Pi currently defaults Codemode script output to up to 10,000 tokens. For routine inner loops, set a much smaller cap, commonly around 1,500-3,000 tokens, and save full logs to artifacts when needed.

Example principle:

```text
Return:
FAILED 2 / 318
billing cancellation integration failed
refresh token expiry failed

Do not return:
30,000 lines of passing-test output
```

---

# 21. Tool Schema Optimization and MCP Exposure

Tool schemas can consume a surprising portion of prompt context.

Pi's built-in MCP now supports exposure modes:

- `codemode` (default for MCP servers)
- `deferred`
- `direct`
- `hidden`

Recommended use:

```text
large/general MCP server → codemode
rare direct tool set     → deferred
small hot tool set       → direct
dangerous/irrelevant     → hidden
```

Example:

```json
{
  "mcpServers": {
    "github": {
      "exposure": "codemode"
    },
    "jira": {
      "exposure": "deferred"
    }
  }
}
```

Do not expose hundreds of tool schemas directly to every worker on every turn.

Pi's current implementation intentionally keeps non-direct MCP tools out of normal tool declarations and allows Codemode/tool search to discover them when necessary.

---

# 22. Model Routing: Route Once, Then Stay Sticky

Use different models for different roles, but avoid constantly switching a single conversation among providers/models.

Suggested roles:

```text
Planner/architect → strongest reasoning model
Implementation    → fast strong coding model
Scout             → cheaper/faster model
Summarizer        → cheaper/faster model
Reviewer          → strong model, preferably different family/provider
Merger/integrator → strong coding/reasoning model
```

Pi Virtual Models documentation specifically notes that switching models can lose prompt-cache benefits and recommends preserving the previous physical model for continuation/retry when appropriate.

Recommended pattern:

```text
task starts
   ↓
router classifies complexity/role
   ↓
physical model selected
   ↓
conversation stays sticky to that model
```

Cross-model review is cheap from a cache perspective because the reviewer is already a separate context.

---

# 23. Prompt Cache Stability Is a First-Class Design Goal

Avoid changing ambient prompt material every turn.

Cache-destabilizing patterns:

- Injecting new semantic memories on every prompt.
- Randomly changing system instructions.
- Constant model/provider switching.
- Directly declaring huge dynamic tool catalogs.
- Injecting real-time project state in the system prompt instead of retrieving it as needed.

Cache-friendly patterns:

- Stable system role.
- Stable pinned invariants.
- Stable tool declarations.
- On-demand retrieval as tool results.
- Sticky model per worker.
- `pi-memory` stable snapshots rather than per-turn automatic injection.

---

# 24. Test Strategy: Verification at Multiple Granularities

Running the complete monorepo test suite after every tiny worker edit can remove the wall-clock benefit of parallelism.

Use staged verification.

## Worker inner loop

```text
edit
 ↓
syntax/static quick check
 ↓
task-targeted tests
 ↓
commit checkpoint
```

## Merge-wave boundary

```text
merge independent tasks
 ↓
affected integration tests
 ↓
typecheck
 ↓
lint/build as appropriate
```

## Major milestone / final integration

```text
full test suite
full build
E2E
security checks
smoke/demo flow
```

Acceptance criteria should name the appropriate commands so the worker knows “done” deterministically.

---

# 25. Review Strategy

The reviewer should normally receive:

```text
task objective
hard constraints
acceptance criteria
git diff / commits
test summary
relevant contracts
```

It should not automatically receive:

```text
worker's entire conversation
entire repository
full raw test logs
all project history
```

The reviewer can retrieve individual files if necessary.

Review criteria should include:

- Functional correctness.
- Acceptance criteria.
- Test adequacy.
- Security issues.
- Architectural boundary violations.
- Public contract drift.
- Duplicate logic.
- Error handling.
- Performance regressions where relevant.
- Whether the change unnecessarily expanded task scope.

---

# 26. Durable Failure/Attempt Memory

Keep failed approaches so workers do not rediscover them, but store them compactly.

Bad:

```text
9,000-token transcript of a failed Redis design
```

Better:

```yaml
attempt: redis-session-cache
result: failed
reason: breaks horizontal session invalidation
evidence: tests/auth/session-cache.test.ts
commit: 17afb0
```

This creates high-value organizational memory at low token cost.

---

# 27. Budget Every Agent

Every job should have explicit limits.

Example:

```yaml
budget:
  max_turns: 30
  max_subagents: 3
  max_writer_agents: 1
  max_retries: 2
  max_review_cycles: 2
  max_context_soft_pct: 60
  max_context_hard_pct: 75
```

Wall-time and dollar/token budgets can be added once the harness records usage reliably.

Budgeting prevents recursive autonomy from becoming economically unpredictable.

---

# 28. Context Soft Limits

Do not interpret a very large model context window as a target to fill.

A practical initial policy:

```text
0-40% context   → normal operation
40-60%          → checkpoint at logical boundary
60-70%          → externalize state aggressively
70%+            → finish current atomic unit, handoff/compact/reset
```

These are engineering starting points, not universal constants. Benchmark and tune by model/provider/task type.

The system should prefer **fresh context + durable state** over endlessly growing context.

---

# 29. Autoresearch: Use After Functional Completion

For measurable optimization tasks, an autoresearch-style loop is valuable.

A current Pi autoresearch harness follows:

```text
edit
→ benchmark
→ measure
→ correctness backpressure checks
→ keep/revert
→ record result
→ repeat
```

Good objectives:

- Build time.
- Bundle size.
- Request latency.
- Benchmark score.
- Memory footprint.
- Test runtime.

Do not use an optimization loop as the primary application orchestrator. Use it after the application is functionally correct and the objective is measurable.

---

# 30. Systems to Avoid Stacking Together

For this specific goal:

```text
Taskplane + pi-spine       → unnecessary overlapping control planes
Taskplane + pi-long-task   → overlapping execution/state concepts
multiple memory systems injecting every turn → token/cache waste
multiple agent chat meshes → coordination noise
multiple project graph indexes without measured benefit → maintenance overhead
```

Pick one component for each responsibility.

---

# 31. Recommended Pi Configuration Baseline

Illustrative starting point:

```json
{
  "defaultTools": [
    "+codemode"
  ],
  "codemode": {
    "mode": "on",
    "inlineBudget": 2000
  },
  "cacheWarming": "streaming",
  "showCacheMissNotices": true,
  "compaction": {
    "enabled": true,
    "reserveTokens": 16384,
    "keepRecentTokens": 20000
  }
}
```

Treat `inlineBudget: 2000` as a benchmark starting point. Pi's Codemode documentation currently describes a 3,000-token declaration budget by default, so actual optimal values should be measured against the tools you install.

The more important rule is not the precise number. It is to **keep routine tool/context declarations bounded and stable**.

---

# 32. Recommended Component Matrix

| Component | Recommendation | Responsibility |
|---|---|---|
| Pi 1.0 | **Use** | Core runtime/harness |
| Taskplane | **Use now** | Main orchestration, DAG/workers/worktrees/review |
| Pi Durable | **Prototype / future core** | Crash-resumable durable control plane |
| Pi Codemode | **Use heavily** | Parallel deterministic tool calls + output filtering |
| Pi Subagents | **Use** | Short-lived specialists and bounded parallel research/review |
| Graphify | **Use selectively** | Structural code graph / dependency/path retrieval |
| pi-memory | **Optional, stable/global scope** | User/global preferences and reusable lessons |
| agent-comms | **Optional** | Cross-harness messaging |
| autoresearch harness | **Use for measurable optimization** | Autonomous benchmark/keep/revert loops |
| pi-spine | **Do not combine with Taskplane** | Alternative orchestrator |
| pi-long-task | **Not preferred for this goal** | Sequential long-task execution |

---

# 33. Recommended Worker Startup Sequence

Every implementation worker should approximately execute:

```text
1. Read relevant exact invariants
2. Read task PROMPT.md
3. Read STATUS.md if resuming
4. Read dependency RESULT.md artifacts
5. Run retrieval router to locate required source/context
6. Inspect only relevant code
7. Implement small logical unit
8. Run targeted validation
9. Commit checkpoint
10. Update STATUS
11. Continue or produce RESULT
12. Emit tiny structured summary to supervisor
```

A worker should not spend its first several turns browsing the entire repo unless the task is explicitly architectural.

---

# 34. Recommended Task Result Format

```yaml
task: T012-billing
status: completed
branch: agent/T012-billing
commits:
  - 7bc123a
  - 91ea030
changed_paths:
  - src/billing/**
  - tests/billing/**
validation:
  targeted_tests: pass
  typecheck: pass
  lint: pass
contracts_changed:
  - .agent/contracts/billing.md
memory_proposals:
  - .agent/discoveries/billing-webhook-order.md
risks:
  - "Stripe webhook ordering remains eventually consistent"
```

This is much cheaper and more machine-usable than a conversational handoff.

---

# 35. Recommended Communication Decision Tree

```text
Worker needs information
        │
        ▼
Can source/git answer it?
  ├── yes → retrieve directly
  └── no
       │
       ▼
Can project artifacts/Graphify answer it?
  ├── yes → retrieve
  └── no
       │
       ▼
Does another active task own the answer?
  ├── yes → structured QUESTION via supervisor
  └── no  → escalate to supervisor/user if truly ambiguous
```

This keeps communication sparse and purposeful.

---

# 36. Recommended Source-of-Truth Ordering

When information conflicts, prefer:

```text
1. Executable behavior/tests
2. Current source code
3. Current schemas/contracts
4. Git history/current commits
5. Current project docs/ADRs
6. Task STATUS/RESULT
7. Graph/retrieval indexes
8. Semantic/global memory
9. Old conversation summaries
```

Memory should help agents find truth, not become a competing truth database.

---

# 37. Observability: Measure the Harness, Not Just the App

Collect at minimum:

## Throughput

- task wall-clock duration
- milestone wall-clock duration
- merge/integration time
- queue/block time

## Token/cost

- input tokens per task
- output tokens per task
- cached vs uncached prompt usage when available
- tool output returned to model
- cost per completed task/milestone

## Agent effectiveness

- retries
- worker restarts
- reviewer rejection cycles
- subagents spawned
- subagent useful-result rate
- tasks completed without escalation

## Coordination quality

- merge conflicts
- dependency mistakes
- contract-change messages
- blocked time
- shared-file collisions

## Retrieval

- grep/read calls
- Graphify calls
- semantic-memory calls
- average retrieved tokens
- retrieval judged useful/not useful

## Testing

- targeted-test runtime
- integration-test runtime
- full-suite runtime
- failures introduced per merged task

This data should answer empirically:

```text
Does writer #4 reduce total completion time?
Does Graphify reduce source reads on this repo?
Do reviewer agents catch issues worth their token cost?
Which model gives the lowest cost per accepted task?
When should context be reset?
```

Do not rely on intuition for these once the harness is operational.

---

# 38. Phased Implementation Plan

## Phase 1: Practical high-performance baseline

Install/configure:

- Pi 1.0
- Taskplane
- Codemode
- Pi Subagents
- Graphify

Implement:

- `.agent/` memory/task layout
- exact `INVARIANTS.md`
- task/result schema
- targeted validation commands
- 3 writer lanes
- sticky model assignment
- orchestration branch

Avoid advanced cross-harness messaging initially.

## Phase 2: Context/token optimization

Add instrumentation for:

- prompt/token usage
- cache misses
- retrieved context volume
- tool output volume

Then tune:

- Codemode inline/output budgets
- compaction thresholds
- Graphify-vs-grep routing
- scout-agent thresholds
- number of writers

## Phase 3: Durable recovery

Prototype Pi Durable around one workflow first:

```text
supervisor + 2 workers + reviewer
```

Test deliberate failures:

- kill process during model response
- kill process during safe read tool
- kill during unsafe write/deploy action
- machine/container restart
- provider timeout

Verify exact resumption semantics.

## Phase 4: Containers / remote execution

Move workers into ephemeral environments with scoped credentials.

## Phase 5: Replace Taskplane only if warranted

Once the custom Durable scheduler has equivalent or better:

- task DAG behavior
- worker lifecycle
- review loops
- merge safety
- retries
- observability

then remove Taskplane and retain a single Pi Durable control plane.

---

# 39. Final Recommended V1

```text
PI 1.0
│
├── Taskplane
│   ├── supervisor
│   ├── dependency DAG
│   ├── 3 default writer lanes
│   ├── max 4 normal writers
│   ├── worktree isolation
│   ├── orchestration branch
│   ├── reviewer
│   └── merger
│
├── Pi Codemode
│   ├── parallel deterministic operations
│   ├── filtered tool output
│   └── strict output budgets
│
├── Pi Subagents
│   ├── inherit_context=false
│   ├── mostly read-only specialists
│   ├── scoped tools/extensions
│   └── bounded concurrency
│
├── Retrieval Router
│   ├── rg/read
│   ├── git
│   ├── Graphify
│   ├── project docs/BM25
│   └── semantic retrieval only when useful
│
├── Hierarchical Memory
│   ├── pinned exact invariants
│   ├── project ADR/contracts
│   ├── task PROMPT/STATUS/RESULT
│   ├── compact failure records
│   └── global pi-memory stable mode only if valuable
│
├── MCP Exposure
│   ├── codemode default
│   ├── deferred for rare direct tools
│   ├── direct for tiny hot tool sets
│   └── hidden for irrelevant/dangerous tools
│
├── Sticky Model Router
│   ├── strongest planner
│   ├── fast strong coder
│   ├── cheap scouts/summarizers
│   ├── independent strong reviewer
│   └── strong merger/debugger
│
├── Verification
│   ├── targeted worker checks
│   ├── merge-wave integration checks
│   └── full milestone/final suite
│
└── Telemetry
    ├── tokens/cost
    ├── wall-clock
    ├── cache
    ├── conflicts
    ├── retries
    └── retrieval/subagent effectiveness
```

---

# 40. Final Recommended V2

Once Pi Durable proves stable enough:

```text
                         Pi Durable
                              │
                   Durable Supervisor DB
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   Durable Worker A    Durable Worker B    Durable Worker C
          │                   │                   │
     container A          container B          container C
     worktree A           worktree B           worktree C
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                       merge/integration
                              │
                              ▼
                       durable reviewer
                              │
                              ▼
                         verification
```

Each durable conversation owns:

- model + thinking level
- tools
- instructions
- working directory/environment
- transcript
- usage state

The durable application owns:

- DAG
- task statuses
- artifact references
- agent ownership
- dependencies
- retries
- exact project metadata
- event journal

Git and executable tests remain canonical application truth.

---

# 41. Core Operating Rules

If only a small set of rules are retained, keep these:

1. **One orchestrator.**
2. **Three writers by default, four only when decomposition supports it.**
3. **Every writer gets an isolated worktree/container.**
4. **Workers start with fresh/minimal context.**
5. **The repository and durable state are truth; conversation is disposable.**
6. **Exact constraints are pinned, not repeatedly summarized.**
7. **Use retrieval, not giant context.**
8. **Use exact search before LLM retrieval for exact questions.**
9. **Use Graphify for structural questions, not everything.**
10. **Use tools/Codemode before spawning an agent when no independent reasoning is required.**
11. **Communicate with structured messages and artifact pointers, not transcript dumps.**
12. **Keep model selection sticky within a worker.**
13. **Do targeted validation inside workers; full validation at integration boundaries.**
14. **Review diffs and task contracts, not complete histories.**
15. **Curate memory through a single validated write path.**
16. **Budget turns, retries, agents, context, time, and cost.**
17. **Measure whether additional parallelism actually improves throughput.**
18. **Move to Pi Durable after proving the workflow, not before.**

---

# 42. Why This Design Should Outperform a Large Agent Swarm

A naive swarm tends to multiply:

- repeated code discovery
- duplicated context
- tool schemas
- overlapping implementation
- shared-file conflicts
- model calls
- merge/review burden
- stale assumptions
- communication messages

This architecture instead uses hierarchy:

```text
LEVEL 1: deterministic parallelism
Codemode, shell commands, searches, tests

LEVEL 2: read-only reasoning parallelism
scouts, reviewers, research specialists

LEVEL 3: isolated implementation parallelism
3-4 worktree writers

LEVEL 4: centralized coordination
supervisor + DAG + durable project state
```

It scales the cheapest and safest form of parallelism first.

That is the central performance strategy.

---

# 43. References and Primary Sources

Sources were checked on **October 2, 2026**.

## Pi

- Pi Codemode documentation: https://pi.dev/docs/latest/codemode
- Pi CLI / tool enabling: https://pi.dev/docs/latest/cli
- Pi compaction reference: https://pi.dev/docs/latest/compaction
- Pi Virtual Models: https://pi.dev/docs/latest/virtual-models
- Pi MCP server/tool exposure: https://pi.dev/docs/latest/mcp
- Pi extensions/tool exposure: https://pi.dev/docs/latest/extensions
- Pi changelog: https://pi.dev/changelog

## Pi Durable

- Earendil Engineering, **Pi Durable**, October 1, 2026: https://earendil.com/posts/pi-durable/

## Pi orchestration / agents

- Taskplane Pi package: https://pi.dev/packages/taskplane
- Pi Subagents: https://pi.dev/packages/%40tintinweb/pi-subagents
- Agent Comms: https://pi.dev/packages/agent-comms
- pi-memory: https://pi.dev/packages/pi-memory
- Current autonomous experiment-loop example: https://pi.dev/packages/pi-autoresearch-harness

## Graphify

- Graphify Labs: https://github.com/Graphify-Labs
- Graphify repository: https://github.com/Graphify-Labs/graphify
- How Graphify works: https://github.com/Graphify-Labs/graphify/blob/v8/docs/how-it-works.md
- Architecture/confidence tags: https://github.com/Graphify-Labs/graphify/blob/v8/ARCHITECTURE.md

## Long-running coding agents

- OpenAI, **Run long horizon tasks with Codex**, February 23, 2026: https://developers.openai.com/blog/run-long-horizon-tasks-with-codex

## Context/memory research

- Zerhoudi et al., **The Compaction Cliff in Long-Running AI Agent Memory**, 2026: https://arxiv.org/abs/2608.22752
- Nguyen et al., **CliffCompaction: Cost-Efficient Compaction for Long-Horizon Coding Agents**, 2026: https://arxiv.org/abs/2609.26779
- Li et al., **TiMem: Temporal-Hierarchical Memory Consolidation for Long-Horizon Conversational Agents**, 2026: https://arxiv.org/abs/2601.02845
- Tirmazi et al., **Context Compaction Theory**, 2026: https://arxiv.org/abs/2608.01326

---

# 44. Bottom Line

The best current configuration is not “spawn as many coding agents as possible.”

It is:

> **Pi 1.0 + one orchestrator + adaptive dependency-aware parallelism + worktree isolation + minimal private contexts + Codemode + selective Graphify retrieval + repo-local hierarchical memory + exact pinned invariants + sticky model routing + staged testing + telemetry.**

Use **Taskplane now** because it provides most of the required orchestration primitives without requiring a custom control plane.

Build toward **Pi Durable** as the long-term foundation because it directly addresses the hardest problems in genuine long-running autonomy: persistent conversations, durable task/application state, crash recovery, concurrent agents, restartable tool work, and external clients/steering.

The most important optimization is not any individual model or plugin. It is the separation of concerns:

```text
LLM context       = temporary working memory
Task files/DB     = execution memory
Project docs/ADRs = curated knowledge
Graphify          = structural retrieval index
Git/code/tests    = canonical truth
Pi Durable        = durable execution machinery
```

That separation is what allows the system to run longer, recover safely, spend fewer tokens, and add parallelism without collapsing under coordination overhead.
