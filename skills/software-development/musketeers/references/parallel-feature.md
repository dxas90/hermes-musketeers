# Parallel Feature Development — Full Procedure

Parallel feature implementation using Aramis agents via `delegate_task`, with optional Dumas orchestration for complex dependency chains.

## When to Use

When a feature can be decomposed into 2-4 work streams that don't share files. Parallelism pays off when each stream takes at least 30 minutes of sequential work.

**Prerequisites before spawning:**
- You have analyzed the feature requirements
- You have identified which files need modification
- You have split work into non-overlapping file ownership boundaries

## Step 1 — Analyze and Decompose

Read the codebase to understand:
- Which existing files need modification
- Which new files need creation
- Which patterns and conventions to follow
- Where integration points exist between streams

```bash
# Understand the codebase structure
find src/ -type f -name "*.py" | head -20
grep -r "similar_feature" src/ --include="*.py" -l

# Understand existing patterns
cat src/models/example.py
cat src/api/example.py
```

## Step 2 — Define Streams and Ownership

**Rule: One owner per file.** If two streams need the same file, one stream owns it, or you handle it sequentially.

Example decomposition for "Add user authentication":

| Stream | Owner | Files | Contract |
|---|---|---|---|
| backend-models | Aramis-1 | `src/models/user.py`, `src/db/migrations/002_users.py` | Exposes `User(id, email, password_hash, created_at)` |
| backend-api | Aramis-2 | `src/api/auth.py`, `tests/test_auth.py` | POST /auth/login → `{token, expires_at}`, POST /auth/register → `{id, email}` |
| frontend | Aramis-3 | `src/components/LoginForm.tsx`, `src/components/RegisterForm.tsx` | Calls the API contracts above |

Define interface contracts at boundaries BEFORE spawning. Contracts are immutable during the build.

## Step 3 — Spawn Aramis Agents in Parallel

```python
streams = [
    {
        "name": "backend-models",
        "owned_files": ["src/models/user.py", "src/db/migrations/002_users.py"],
        "contract_provides": "User model with fields: id (uuid), email (str, unique), password_hash (str), created_at (datetime). Method: User.from_credentials(email, password) -> User | None",
        "contract_depends": [],
        "task": "Implement User model and database migration for the authentication feature",
        "codebase_context": """Existing model pattern — see src/models/item.py for reference.
We use SQLAlchemy ORM. Migrations use Alembic.
Hash passwords with bcrypt (already a dependency in requirements.txt).""",
    },
    {
        "name": "backend-api",
        "owned_files": ["src/api/auth.py", "tests/test_auth.py"],
        "contract_provides": "POST /auth/login → 200 {token: str, expires_at: ISO8601} | 401. POST /auth/register → 201 {id: uuid, email: str} | 422.",
        "contract_depends": "User.from_credentials(email, password) from backend-models stream",
        "task": "Implement login and registration endpoints with JWT token generation and unit tests",
        "codebase_context": """Existing endpoint pattern — see src/api/items.py.
JWT library: python-jose (already installed). SECRET_KEY in config.py.
Test pattern: see tests/test_items.py.""",
    },
]

tasks = [
    {
        "goal": f"""You are Aramis, a parallel feature builder with STRICT file ownership.

STREAM: {s['name']}
OWNED FILES (modify ONLY these):
{chr(10).join('- ' + f for f in s['owned_files'])}

CONTRACT YOU MUST FULFILL:
{s['contract_provides']}

CONTRACTS YOU DEPEND ON:
{s['contract_depends'] if s['contract_depends'] else 'None — this stream is independent'}

TASK:
{s['task']}

CODEBASE CONTEXT:
{s['codebase_context']}

FILE OWNERSHIP RULES:
- Modify ONLY your owned files
- If you need a change in a file you don't own, describe it in SHARED_FILE_REQUESTS
- Implement exactly what is specified — no scope creep, no bonus features
- If a dependency contract seems wrong or incomplete, report it in BLOCKERS

When complete, report in EXACTLY this format:
FILES_CHANGED:
- filename.py: description of changes

INTERFACE_DELIVERED:
Describe what you implemented vs the contract. Note any deviations.

SHARED_FILE_REQUESTS:
(List any changes needed in files you don't own, or "None")

BLOCKERS:
(List any issues that require coordination, or "None")

TEST_RESULTS:
(pass/fail/skipped with counts, or "No tests applicable")""",
        "context": f"Build {s['name']} stream. File ownership is absolute. Return implementation report.",
        "toolsets": ["terminal", "file"],
    }
    for s in streams
]

build_results = delegate_task(
    goal="Parallel feature implementation across streams.",
    context="Feature build. Independent streams. Consolidate and verify after.",
    toolsets=["terminal", "file"],
    tasks=tasks,
)
```

## Step 4 — Handle Dependencies

If Stream B depends on Stream A's output, run them sequentially — pass Stream A's result as context to Stream B:

```python
# Run independent streams first
foundation_result = delegate_task(
    goal="""Aramis stream: backend-models. [full prompt as above]""",
    context="Build foundation stream.",
    toolsets=["terminal", "file"],
)

# Pass the delivered contract to the dependent stream
dependent_result = delegate_task(
    goal=f"""Aramis stream: backend-api.
...
The backend-models stream has completed and delivered:
{foundation_result}

Use the above contract. Do not re-implement — import from src/models/user.py.""",
    context="Build api stream. Foundation already complete.",
    toolsets=["terminal", "file"],
)
```

## Step 5 — Integration Verification

After all streams complete:

```bash
# Verify build
python -m pytest tests/ -q

# Or for other stacks:
npm test
go test ./...
cargo test
```

If tests fail, assign a single fix agent to the failing test file:

```python
delegate_task(
    goal="""Fix ONLY the failing tests listed below. Do not change passing tests.
Do not change implementation files unless the test reveals an implementation bug.

Failing tests:
{paste test output}

Changed files for context:
{paste git diff}""",
    context="Fix failing tests from integration. Minimal changes only.",
    toolsets=["terminal", "file"],
)
```

## Step 6 — Shared File Conflicts

If two streams requested changes to the same file (reported in SHARED_FILE_REQUESTS), handle sequentially:

```python
delegate_task(
    goal="""Apply the following changes to {shared_file}. These were requested by parallel streams that don't own this file.

Changes requested:
Stream backend-api: {request_1}
Stream frontend: {request_2}

Apply both changes. If they conflict, apply the more conservative change and note the conflict.
Current file content: [read and paste the file]""",
    context="Merge shared file changes from parallel streams.",
    toolsets=["terminal", "file"],
)
```

## Orchestrator Pattern (Dumas) for Complex Features

For features with 3+ streams and complex dependency chains, use `role="orchestrator"`:

```python
delegate_task(
    goal="""You are Dumas, a team orchestrator.
Decompose and coordinate parallel implementation of: {feature_description}

Available codebase context:
{codebase_summary}

Your job:
1. Decompose the feature into 2-4 independent streams with non-overlapping file ownership
2. Define interface contracts at stream boundaries
3. Identify dependencies between streams (which must run before others)
4. Spawn Aramis agents in parallel (or sequentially for dependent streams)
5. Collect results and verify integration
6. Report: files changed, tests passing, remaining issues

Spawn Aramis agents using delegate_task with role="leaf". Include full context in each agent's goal.
Do not spawn more than 4 parallel agents at once.""",
    context="Feature orchestration. Decompose then coordinate parallel builds.",
    toolsets=["terminal", "file"],
    role="orchestrator",
)
```

## Common Pitfalls

1. **Overlapping file ownership** — Two Aramis agents touching the same file is the most common failure. Map ALL files to be changed before spawning.

2. **Underspecified contracts** — "Exposes User model" is not a contract. "Exposes `User.from_credentials(email: str, password: str) -> User | None`" is.

3. **Spawning before decomposing** — Spend 10 minutes decomposing well. Rework from a bad decomposition costs more than the upfront analysis.

4. **Too many dependent streams** — If every stream depends on the previous one, parallelism offers no benefit. Restructure to maximize independent work.

5. **Skipping integration verification** — Parallel builds with clean individual results can still fail integration. Always run tests after merging.
