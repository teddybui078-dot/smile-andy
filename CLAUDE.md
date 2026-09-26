# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Specific Tasks

**A broad ask makes the run drag. Make the task specific before it starts.**

Most slow runs aren't slow because the work is hard - they're slow because the request was broad, so Claude reads half the repo trying to work out what you meant. Anthropic names this failure pattern **infinite exploration**: ask it to investigate something without a boundary, and it will happily read hundreds of files before writing a line.

A specific task carries three things:
- **The symptom, not the area** - what actually goes wrong, and when.
- **Where to look** - the directory or file, and the specific suspect within it.
- **What to do first** - usually "write a failing test before fixing."

Broad asks name an area. Specific tasks name a failure:

| Broad (drags) | Specific (doesn't) |
|---|---|
| "Clean up the API" | "`/orders` returns 500 on empty carts. Check the serializer in `api/orders/`. Reproduce it in a test first." |
| "The dashboard feels slow" | "The dashboard makes ~40 requests on load. Look at the data fetching in `components/Dashboard/`, starting with the widget hooks." |
| "Our tests are flaky" | "`test_sync_retry` fails maybe 1 in 5 runs in CI. Look at `workers/sync.py` and the sleep-based waits. Run it 20 times to confirm before changing anything." |

Same work in each case - much less wandering around.

When an ask arrives broad, don't start reading - make it specific first:
- Ask for the symptom and the entry point before exploring.
- If you must explore, name the boundary out loud ("checking `workers/` only") and stop there.
- If the boundary turns out wrong, say so and ask - don't silently widen the search.

## 6. Work in Checkpoints

**Build big things as a stack of small, reviewable layers. Each layer ends with something the user can look at, and then you stop.**

A checkpoint is a lettered deliverable (A, B, C...) with three parts:
- **A thing to look at** - an annotated video, an overlay, a JSON file, a contact sheet. Not "the tests pass".
- **A review question** - what the user should judge (e.g. "is the right player boxed?", "do counts match a rally?").
- **A limitations note** - what it does, what was checked and how, and what was *not* verified, written into `docs/limitations.md`. Don't claim a target you couldn't measure.

Each checkpoint reads the previous one's outputs and adds one layer. From the RallyVision build:

| | Adds | Builds on | What review caught |
|---|---|---|---|
| **A** | Decode/re-export with audio, models smoke-tested, point segmenter, court fit | nothing | Thresholds untuned; a planned replay warning would fire on almost every clip |
| **B** | Two-player boxes and skeletons | A's segments and court | Far player's box locked onto a stationary bystander for the whole rally while `status` said "ok" |
| **C** | Ball trail with static-graphic suppression | A + B | Scoreboard, clock and speed radar did *not* false-trigger; far-baseline visibility unchecked |
| **D** | Hits, hitter, HUD counters | ball + players + pose | "Counts must alternate" exposed 34 near vs 38 far: a stray ball on court hijacked the ball stage, plus two event-rule bugs |
| **E** | Forehand / backhand / other | events + pose + ball | Wrong `--far-hand`; a running shot and a hidden contact were mislabelled |
| **F** | Five clips + metrics | everything | (next) |

How to work them:
- **Order by dependency.** Earlier layers feed later ones, so an error there poisons everything after it. Each stage gets a small interface, one implementation and a cached artifact keyed on its config, so re-tuning a late stage re-runs in seconds, not minutes.
- **Verify on real input, not just unit tests.** B's read-only-frame crash only appeared on the real clip. Say in the note which it was.
- **Stop for review, then turn feedback into tests first.** Every fix follows Section 4: reproduce, fix, re-run.
- **Fix a defect at the earliest layer that causes it**, not where you noticed it (D's biggest fix went in the ball stage, not in more event thresholds). Re-run downstream, diff the result, and record it as a *correction* in the earlier checkpoint's entry.
- **Don't start N+1 until N is reviewed.**

### Git: one stacked branch per checkpoint

- Name each branch `checkpoint-<letter>-<what-it-adds>` (e.g. `checkpoint-b-players-and-skeleton-overlay`) so the branch list reads like the plan, and cut each one from the previous: `checkpoint-a-video-io-segments-court` from `main`, `checkpoint-b-players-and-skeleton-overlay` from `checkpoint-a-video-io-segments-court`, and so on. Each holds only its own layer's commits.
- Commit in small, tests-first steps (Section 4), one per component, so a checkpoint's history reads like its plan.
- Push only the branch you are on. Merge into `main` **in order, after the user has reviewed that checkpoint**; until then `main` stays at the last accepted state.
- The payoff: the diff for each review is exactly one layer, a bad layer reverts alone, and you can `git bisect` across layers.
- If a checkpoint is squash-merged, rebase the next branch onto `main` (`git rebase --onto main checkpoint-a-video-io-segments-court checkpoint-b-players-and-skeleton-overlay`) so it doesn't replay merged commits.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, clarifying questions come before implementation rather than after mistakes, runs finish without reading files that were never relevant, and each checkpoint ends with a reviewable artifact, an honest limitations note, and its own branch.
