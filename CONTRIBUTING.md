# Contributing

Two (or more) people are working on this repo now, so a lightweight
process beats everyone pushing straight to `main` and hoping for the best.
If you're an AI session (Claude or otherwise) picking up work here, read
[`CLAUDE.md`](CLAUDE.md) in full first — this file is just the workflow,
`CLAUDE.md` is the actual project context.

## Workflow

1. **Pick an issue.** All remaining work is tracked on the
   [Issues tab](../../issues), with dependencies noted on each one (also
   mirrored in `CLAUDE.md` §10). Check an issue isn't already claimed —
   an open PR, an existing branch named after it, or an assignee — before
   starting.
2. **Pull first:** `git pull origin main`.
3. **Branch per issue:** `git checkout -b issue-<n>-<short-slug>`, e.g.
   `issue-5-csv-loader`.
4. **Make the change.** Keep it scoped to the issue — if you spot
   something unrelated worth fixing, file a new issue for it instead of
   folding it in.
5. **Test before you push:**
   ```
   pytest
   ```
   All tests should pass. If you touched `exam_timetable/cost.py`'s delta
   functions specifically, see `CLAUDE.md` §5.1 — there's a property test
   that must pass, not just the hand-picked ones.
6. **Commit.** See the conventions below before you do.
7. **Open a PR** referencing the issue (e.g. `Closes #5` in the
   description, so it auto-closes on merge).
8. **Update `CLAUDE.md`** in the same PR if your change makes any part of
   it stale (most commonly §3's status table). Don't leave that for later
   — the next session (human or AI) trusts that file by default.

## Commit conventions

- **No AI co-author/attribution lines.** If you're committing from an AI
  session, don't add `Co-Authored-By` or similar lines for the AI tool —
  this is an explicit project convention, not a default to assume
  otherwise.
- **Commit message body, not just a one-liner**, for anything beyond a
  trivial change — explain *why*, not just *what* (the diff already shows
  what). Look at `git log` for the existing style.
- **Windows users: watch your quotes.** Pasting a commit message that
  uses smart/curly quotes (`"..."`) into `cmd.exe` silently breaks
  argument parsing (see `CLAUDE.md` §5.5 for what that looked like when it
  happened). Prefer a heredoc for multi-line messages:
  ```bash
  git commit -m "$(cat <<'EOF'
  Short summary line

  Longer explanation if needed.
  EOF
  )"
  ```

## Code conventions

- No external optimization/metaheuristic libraries (DEAP, PyGAD,
  scipy.optimize, etc.) — see `CLAUDE.md` §9 for why this is a hard rule,
  not a preference.
- Don't change `cost.py`'s `HARD_WEIGHT`/`SOFT_WEIGHT` or any algorithm's
  default hyperparameters as a side effect of unrelated work — tuning is
  its own tracked issue (#2), with its own documentation of what changed
  and why.
- Follow the existing module boundaries (`models.py` / `state.py` /
  `cost.py` / `operators.py` / `algorithms/*.py`) — see `CLAUDE.md` §4 for
  what each owns. A CSV loader, for example, only needs to produce a
  `ProblemInstance`; it shouldn't need to touch `cost.py` or any
  algorithm at all.
