---
name: writing-better-go
title: Writing Better Go
description: Use when writing or reviewing Go code. GoLab 2025 rules.
version: 2.0.0
author: Dumas
license: internal
tags: [go, golang, code-quality, code-review, best-practices, modern-go]
metadata:
  hermes:
    tags: [go, golang, code-quality, code-review, best-practices, modern-go]
    related_skills: [musketeers-review, musketeers-karpathy, industry-security-standards]
---

# Writing Better Go

## When to Use

Load this skill when:
- Writing new Go code and you want production-quality patterns from the start.
- Reviewing a Go pull request and need a structured checklist.
- Refactoring Go code and want guidance on error handling, concurrency, naming, or package structure.
- Running Athos on a Go codebase and want concrete rules to apply.
- User asks for modern Go code, idioms, or version-specific features.

---

Merged from two sources:
- **"Writing Better Go — Lessons from 10 Code Reviews"** (Konrad Reiche, GoLab 2025) — production quality rules.
- **Modern Go Guidelines** (JetBrains, github.com/JetBrains/go-modern-guidelines) — version-gated syntax features.

Every rule maps to a recurring pattern found in real production code reviews.

---

## Part A — Modern Go: Use the Right Feature for Your Version

### Step 1: Detect Go Version

Run this before writing any code:

```bash
grep -rh "^go " --include="go.mod" . 2>/dev/null | cut -d' ' -f2 | sort | uniq -c | sort -nr | head -1 | xargs | cut -d' ' -f2
```

**If version detected:** Say “This project uses Go X.XX — I’ll use features up to and including that version. Let me know if you prefer a different target.” Do NOT list features or ask for confirmation.

**If unknown:** Ask: “Which Go version should I target?” with options [1.23] / [1.24] / [1.25] / [1.26].

Never use features from a newer Go version than the target. Never use outdated patterns when a modern alternative is available.

---

### Go Version Feature Reference

#### Go 1.0+
- `time.Since(start)` not `time.Now().Sub(start)`

#### Go 1.8+
- `time.Until(deadline)` not `deadline.Sub(time.Now())`

#### Go 1.13+
- `errors.Is(err, target)` not `err == target` (handles wrapped errors)

#### Go 1.18+
- `any` not `interface{}`
- `bytes.Cut(b, sep)` / `strings.Cut(s, sep)` — cleaner split+test

#### Go 1.19+
- `fmt.Appendf(buf, "x=%d", x)` not `[]byte(fmt.Sprintf(...))`
- Type-safe atomics: `atomic.Bool`, `atomic.Int64`, `atomic.Pointer[T]` not `atomic.StoreInt32`

```go
var flag atomic.Bool
flag.Store(true)
if flag.Load() { ... }
```

#### Go 1.20+
- `strings.Clone(s)` / `bytes.Clone(b)` to copy without sharing memory
- `strings.CutPrefix` / `strings.CutSuffix`
- `errors.Join(err1, err2)` to combine multiple errors
- `context.WithCancelCause` + `context.Cause(ctx)` for cancellation with reason

#### Go 1.21+
- Built-ins: `min(a, b)` / `max(a, b)` / `clear(m)`
- `slices.Contains`, `slices.Index`, `slices.IndexFunc`, `slices.SortFunc`, `slices.Sort`
- `slices.Max`, `slices.Min`, `slices.Reverse`, `slices.Compact`, `slices.Clip`, `slices.Clone`
- `maps.Clone(m)`, `maps.Copy(dst, src)`, `maps.DeleteFunc(m, fn)`
- `sync.OnceFunc(fn)` / `sync.OnceValue(fn)` not `sync.Once` + wrapper
- `context.AfterFunc(ctx, cleanup)`, `context.WithTimeoutCause`

#### Go 1.22+
- `for i := range n` not `for i := 0; i < n; i++`
- Loop variables are safe to capture in goroutines (each iteration has its own copy)
- `cmp.Or(a, b, c, "default")` returns first non-zero value

```go
// not: if name == "" { name = "default" }
name := cmp.Or(os.Getenv("NAME"), "default")
```

- `reflect.TypeFor[T]()` not `reflect.TypeOf((*T)(nil)).Elem()`
- `http.ServeMux` method+path patterns: `mux.HandleFunc("GET /api/{id}", handler)`
- `r.PathValue("id")` for path parameters

#### Go 1.23+
- `maps.Keys(m)` / `maps.Values(m)` return iterators
- `slices.Collect(iter)` not manual loop to build slice from iterator
- `slices.Sorted(iter)` to collect + sort in one step

```go
keys := slices.Collect(maps.Keys(m))
sortedKeys := slices.Sorted(maps.Keys(m))
for k := range maps.Keys(m) { process(k) }
```

- `time.Tick` is safe — GC can now recover unreferenced tickers; `Stop()` no longer needed

#### Go 1.24+
- `t.Context()` not `context.WithCancel(context.Background())` in tests — **always**
- `omitzero` not `omitempty` for `time.Duration`, `time.Time`, structs, slices, maps in JSON tags
- `b.Loop()` not `for i := 0; i < b.N; i++` in benchmarks — **always**
- `strings.SplitSeq(s, ",")` / `strings.FieldsSeq` / `bytes.SplitSeq` when iterating splits

```go
// not: for _, part := range strings.Split(s, ",") { process(part) }
for part := range strings.SplitSeq(s, ",") { process(part) }
```

#### Go 1.25+
- `wg.Go(fn)` not `wg.Add(1)` + `go func() { defer wg.Done(); ... }()` — **always**

```go
// not:
wg.Add(1)
go func() {
    defer wg.Done()
    process(item)
}()

// use:
wg.Go(func() {
    process(item)
})
```

#### Go 1.26+
- `new(val)` not `x := val; &x` — `new()` now accepts expressions, type is inferred
- Do NOT use `x := val; &x`; do NOT cast: `new(int(0))` → just `new(0)`

```go
// not: timeout := 30; cfg := Config{Timeout: &timeout}
cfg := Config{
    Timeout: new(30),   // *int
    Debug:   new(true), // *bool
}
```

- `errors.AsType[T](err)` not `errors.As(err, &target)`

```go
// not: var pathErr *os.PathError; if errors.As(err, &pathErr) { ... }
if pathErr, ok := errors.AsType[*os.PathError](err); ok {
    handle(pathErr)
}
```

---

## Part B — Production Quality Rules (GoLab 2025)

---

## Rule 01 — Handle Errors

**Never discard, ignore, or swallow errors.**

```go
// BAD: silently discarding
result, _ := pickRandom(input)

// BAD: silently ignoring
result, err := pickRandom(input)
if err != nil {
    // empty — does nothing
}

// BAD: swallowing (nil return hides the error)
result, err := pickRandom(input)
if err != nil {
    return nil   // caller sees nothing wrong
}

// GOOD: return it, or log it — never both
result, err := pickRandom(input)
if err != nil {
    return fmt.Errorf("pickRandom failed: %w", err)  // wrap + propagate
}

// GOOD: log only when you cannot propagate
if err != nil {
    slog.Error("pickRandom failed", "error", err)
    return nil
}
```

**Return contract — optimize for the caller:**

| Return | Meaning |
|--------|---------|
| `return result, nil` | Value is valid and safe to use |
| `return nil, err`    | Value is invalid; caller must handle |
| `return nil, nil`    | Ambiguous — forces extra nil checks — avoid |
| `return result, err` | Unclear which to trust — avoid unless partial results are documented |

**Pitfall — double reporting:**
```go
// BAD: logs AND returns — error appears twice in observability
if err != nil {
    slog.Error("fetch failed", "error", err)
    return err
}
```
Log it **or** return it. Not both.

---

## Rule 02 — Don't Add Interfaces Too Soon

Two common misuses:

### Premature Abstraction
Do not introduce an interface before you have two real implementations that need to be swapped.

```go
// BAD: interface added speculatively
type EligibilityService struct {
    cache cache.Cache[model.Product]  // interface with no second impl yet
}

// GOOD: use the concrete type until a second impl exists
type EligibilityService struct {
    cache *cache.LFU[model.Product]
}
```
Litmus test: if you can write it without the interface, you probably don't need one yet.

### Interfaces Solely for Testing
Do NOT create production interfaces just to inject mocks in tests.

Prefer **fake implementations** in a dedicated `deptest/` or `fakeuserservice/` subpackage backed by a real gRPC `bufconn` server. This exercises the real client path and keeps production types clean.

```go
// GOOD: fake backed by bufconn — real gRPC, no interface in production code
userService := fakeuserservice.New(
    t,
    fakeuserservice.WithUserSubscription("test_user_1", 1),
)
```

**Conventions:**
- Accept interfaces, return concrete types.
- Introduce interfaces only when multiple interchangeable types are genuinely needed.
- Some deps (Postgres, Kafka, BigQuery) have no good fake — an interface is acceptable there.

---

## Rule 03 — Mutexes Before Channels

Channels are expressive but easy to misuse. Common panics/deadlocks:

```go
close(ch); close(ch)           // panic: close of closed channel
close(ch); ch <- 3             // panic: send on closed channel
ch <- 3 // no receiver         // fatal: all goroutines asleep — deadlock
for v := range ch { }          // deadlock if ch is never closed
```

**Start simple, advance one step at a time:**

1. Begin with synchronous code.
2. Add goroutines only when profiling shows a bottleneck.
3. Use `sync.Mutex` + `errgroup` for shared state — simpler and safer than channels.
4. Use `go test -race` to find data races.
5. Channels shine for complex orchestration pipelines — not basic fan-out.
6. On Go 1.25+: use `wg.Go(fn)` instead of `wg.Add(1)` + `go func() { defer wg.Done() }()` (see Part A).

```go
// GOOD: errgroup + mutex — no channels needed for fan-out+collect
var mu sync.Mutex
resps := make([]int, 0)
g, ctx := errgroup.WithContext(ctx)
for _, v := range input {
    g.Go(func() error {
        resp, err := process(ctx, v)
        if err != nil { return err }
        mu.Lock()
        resps = append(resps, resp)
        mu.Unlock()
        return nil
    })
}
if err := g.Wait(); err != nil {
    return 0, err
}

// EVEN BETTER: pre-allocate by index — no mutex at all
resps := make([]int, len(input))
for i, v := range input {
    g.Go(func() error {
        resp, err := process(ctx, v)
        if err != nil { return err }
        resps[i] = resp   // safe: each goroutine writes a unique index
        return nil
    })
}
```

---

## Rule 04 — Declare Close to Usage

**Keep identifiers near the code that consumes them.**

- Declare constants, variables, and types in the file/function that needs them.
- Export only once needed outside the package.
- Within a function, declare variables as close as possible to their first use.
- Limit scope with `:=` inside `if` blocks when the value is not needed later.

```go
// BAD: scope bleeds unnecessarily
err := json.Unmarshal(b, &v)
if err != nil { return nil, err }
err = v.Validate()  // forced reassign because err is already declared
if err != nil { return nil, err }

// GOOD: each error scoped to its own if block
if err := json.Unmarshal(b, &v); err != nil {
    return nil, err
}
if err := v.Validate(); err != nil {
    return nil, err
}
```

When two files need the same identifier, keep it with the first consumer — not in a generic shared file.
Smaller scope = fewer shadowing bugs = easier extraction into helpers.

---

## Rule 05 — Avoid Runtime Panics

### Check External Inputs
```go
// BAD: nil deref if req or req.Options is nil
func selectNotifications(req *pb.Request) {
    max := req.Options.MaxNotifications
    req.Notifications = req.Notifications[:max]
}

// GOOD: guard external inputs
func selectNotifications(req *pb.Request) {
    if req == nil { return }
    max := req.Options.MaxNotifications
    if len(req.Notifications) > max {
        req.Notifications = req.Notifications[:max]
    }
}
```

### Check Nil Before Dereferencing Pointer Fields
```go
// BAD
scores += *item.Score   // panics if Score is nil

// GOOD — explicit nil check
if item.Score == nil { continue }
scores += *item.Score

// BEST — design away the pointer
type FeedItem struct {
    Score float64  // zero value is safe; no pointer needed
}
```

**When to check vs. when not to:**
- Check inputs from outside (HTTP requests, external stores, protobuf).
- Do NOT litter code with `if x == nil` when you control the flow.
- Error handling is your contract; don't duplicate it with redundant nil checks.
- Pass the pointer itself to avoid accidental dereference:
```go
// BAD: *db panics if db is nil
job := cron.NewJob("indexer", *db)

// GOOD
job := cron.NewJob("indexer", db)
```

---

## Rule 06 — Minimize Indentation

Deep nesting is hard to read. Use **early returns** and **guard clauses**.

```go
// BAD: logic wrapped inside happy-path blocks
if err := doSomething(); err == nil {
    if ok := check(); ok {
        process()
    } else {
        return errors.New("check failed")
    }
} else {
    return err
}

// GOOD: return early, flat structure
if err := doSomething(); err != nil {
    return err
}
if !check() {
    return errors.New("check failed")
}
process()
```

Inside loops: use `continue` as a guard instead of nesting the body inside an `if`.

```go
// BAD
for _, item := range items {
    if item.Queries != nil {
        // 10 lines deep
    }
}

// GOOD
for _, item := range items {
    if item.Queries == nil {
        continue
    }
    // flat code here
}
```

When a loop body is still complex after flattening, extract a helper function.

---

## Rule 07 — Avoid Catch-All Packages and Files

```
// Signs of defeat:
util.go
misc.go
constants.go
interfaces/interfaces.go
```

> "Util packages are a sign of defeat. You lost control of your codebase, so you created some util packages."

**Prefer locality over hierarchy:**
- Code is easier to understand when it lives near what it affects.
- Abstract organization hides purpose.
- Be specific: name packages after domain or functionality.
- Group by **meaning**, not by **type**.

---

## Rule 08 — Order Declarations by Importance

Go does not require forward declarations — exploit that for readability.

- Put exported, API-facing functions **first**.
- Follow with helper/private functions (implementation details).
- Order by **importance**, not by dependency.

```go
// GOOD: public API visible immediately
func Trim(s, cutset string) string {
    return trimLeftUnicode(trimRightUnicode(s, cutset), cutset)
}

func trimLeftByte(s string, c byte) string { ... }   // helpers follow
func trimRightUnicode(s, cutset string) string { ... }
```

In test files: put `TestXxx` functions before mock/helper types they depend on.

---

## Rule 09 — Name Well

### Avoid Type Suffixes
```go
// BAD: type info in name — redundant, adds noise
userMap  map[string]*User
idStr    string
injectFn func()

// GOOD: names describe contents
userByID  map[string]*User
id        string
inject    func()
```

### Variable Length and Scope
- Short names (`i`, `v`, `c`) are fine when scope is tiny (loop counters, one-liners).
- The bigger the gap between declaration and use, the more descriptive the name should be.

### Package + Exported Identifier Pairing
Think about how the call site reads:
```go
// BAD: redundant or confusing at call site
test.NewDatabaseFromFile(...)     // vague package name
common.SeekStart                  // "common" communicates nothing
helper.Marshal(...)               // what does helper marshal?
consumer.NewConsumerHandler(...)  // stutter — package repeats in name

// GOOD
spannertest.NewDatabaseFromFile(...)
io.SeekStart
elliptic.Marshal(curve, x, y)
consumer.NewHandler(...)
```

---

## Rule 10 — Document the Why, Not the What

Readers can see **what** the code does. They struggle to understand **why** it exists.

```go
// BAD: restates the code
// Escapes internal double quotes by replacing `"` with `\"`.
func EscapeDoubleQuotes(s string) string { ... }

// GOOD: explains the motivation
// We can sometimes receive a label like: ""How-To"" because the frontend
// wraps user-provided labels in quotes, even when the value itself
// contains literal `"` characters. In this case, attempt to escape all
// internal double quotes, leaving only the outermost ones unescaped.
func EscapeDoubleQuotes(s string) string { ... }
```

**Comment checklist:**
- PR description: why does this change matter?
- Code comments: document intent and constraints, not mechanics.
- Future readers must understand the motivation behind choices without asking the original author.

---

## Quick-Reference Summary

### Part A — Modern Syntax (version-gated)

| Go Version | Key Addition |
|---|---|
| 1.13+ | `errors.Is` for wrapped errors |
| 1.18+ | `any`, `strings.Cut` / `bytes.Cut` |
| 1.19+ | Type-safe atomics (`atomic.Bool`, etc.), `fmt.Appendf` |
| 1.20+ | `errors.Join`, `context.WithCancelCause`, `strings.CutPrefix` |
| 1.21+ | `min`/`max`/`clear`, `slices.*`, `maps.*`, `sync.OnceFunc` |
| 1.22+ | `for i := range n`, safe goroutine loop capture, `cmp.Or` |
| 1.23+ | `maps.Keys`/`Values` iterators, `slices.Collect`/`Sorted` |
| 1.24+ | `t.Context()`, `omitzero`, `b.Loop()`, `strings.SplitSeq` |
| 1.25+ | `wg.Go(fn)` |
| 1.26+ | `new(val)` expressions, `errors.AsType[T]` |

### Part B — Production Quality Rules (always apply)

| # | Rule | Core Principle |
|---|------|----------------|
| 01 | Handle Errors | Log it or return it — never both; never discard |
| 02 | Interfaces Later | Start concrete; add interface only when two real impls exist |
| 03 | Mutexes Before Channels | Default to errgroup+mutex; channels for complex orchestration only |
| 04 | Declare Close to Use | Small scope = fewer bugs; keep identifiers near consumers |
| 05 | Avoid Runtime Panics | Validate external inputs; design away pointer fields |
| 06 | Minimize Indentation | Guard clauses + early returns = flat, readable code |
| 07 | No Util Packages | Group by meaning, not by type |
| 08 | Most Important First | Exported API at top; helpers follow |
| 09 | Name Well | No type suffixes; scope determines length; avoid stutter |
| 10 | Document the Why | Comments explain motivation, not mechanics |

> "Most 'style' comments aren't about aesthetics — they're about avoiding real production pain."
> — Konrad Reiche, GoLab 2025
