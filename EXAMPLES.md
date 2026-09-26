# Examples

Real-world code examples demonstrating the five principles. Each example shows what LLMs commonly do wrong and how to fix it.

---

## 1. Think Before Coding

### Example 1: Hidden Assumptions

**User Request:** "Add a feature to export user data"

**❌ What LLMs Do (Wrong Assumptions)**

```python
def export_users(format='json'):
    """Export all users to a file."""
    users = User.query.all()
    
    if format == 'json':
        with open('users.json', 'w') as f:
            json.dump([u.to_dict() for u in users], f)
    elif format == 'csv':
        with open('users.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'email', 'name'])
            writer.writeheader()
            writer.writerows([u.to_dict() for u in users])
    
    return f"Exported {len(users)} users"
```

**Problems:**
- Assumed it should export ALL users (what about pagination? privacy?)
- Assumed file location without asking
- Assumed which fields to include
- Assumed CSV fieldnames without checking actual data structure

**✅ What Should Happen (Surface Assumptions)**

```
Before implementing, I need to clarify:

1. **Scope**: Export all users or filtered subset? (privacy implications)
2. **Format**: You mentioned "export" - did you mean:
   - Download file in browser?
   - Background job with email notification?
   - API endpoint returning data?
3. **Fields**: Which user fields? (some might be sensitive)
4. **Volume**: How many users typically? (affects approach)

Simplest approach: Add an API endpoint that returns paginated JSON.
Would need more info for file-based exports.

What's your preference?
```

### Example 2: Multiple Interpretations

**User Request:** "Make the search faster"

**❌ What LLMs Do (Pick Silently)**

```python
# Adds caching, database indexes, and async processing
# without asking which "faster" matters
@lru_cache(maxsize=1000)
async def search(query: str) -> List[Result]:
    # ... 200 lines of optimization code
```

**✅ What Should Happen**

```
"Make the search faster" could mean:

1. **Faster response time** (< 100ms instead of 500ms)
   - Add database indexes
   - Cache frequent queries
   - Estimated effort: 2 hours

2. **Handle more concurrent searches** (throughput)
   - Add async/await
   - Connection pooling
   - Estimated effort: 4 hours

3. **Faster perceived speed** (UX)
   - Show partial results immediately
   - Progressive loading
   - Estimated effort: 3 hours

Current search takes ~500ms for typical queries. 
Which aspect matters most for your use case?
```

---

## 2. Simplicity First

### Example 1: Over-abstraction

**User Request:** "Add a function to calculate discount"

**❌ What LLMs Do (Overengineered)**

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol, Union
from dataclasses import dataclass

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, amount: float) -> float:
        pass

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        self.percentage = percentage
    
    def calculate(self, amount: float) -> float:
        return amount * (self.percentage / 100)

class FixedDiscount(DiscountStrategy):
    def __init__(self, fixed_amount: float):
        self.fixed_amount = fixed_amount
    
    def calculate(self, amount: float) -> float:
        return min(self.fixed_amount, amount)

@dataclass
class DiscountConfig:
    strategy: DiscountStrategy
    min_purchase: float = 0.0
    max_discount: float = float('inf')

class DiscountCalculator:
    def __init__(self, config: DiscountConfig):
        self.config = config
    
    def apply_discount(self, amount: float) -> float:
        if amount < self.config.min_purchase:
            return 0
        discount = self.config.strategy.calculate(amount)
        return min(discount, self.config.max_discount)

# Usage requires 30+ lines of setup for a simple calculation
```

**✅ What Should Happen (Simple)**

```python
def calculate_discount(amount: float, percent: float) -> float:
    """Calculate discount amount. percent should be 0-100."""
    return amount * (percent / 100)

# Usage
discount = calculate_discount(100.0, 10.0)  # $10 off
```

**When to add complexity:** Only when you actually need multiple discount types. If that requirement comes later, refactor then.

### Example 2: Speculative Features

**User Request:** "Save user preferences to database"

**❌ What LLMs Do (Unnecessary Features)**

```python
class PreferenceManager:
    def __init__(self, db, cache=None, validator=None):
        self.db = db
        self.cache = cache or InMemoryCache()
        self.validator = validator or DefaultValidator()
    
    def save(self, user_id: int, prefs: dict, 
             merge: bool = True, 
             validate: bool = True,
             notify: bool = False) -> bool:
        """Save preferences with optional merging, validation, and notifications."""
        
        if validate:
            errors = self.validator.validate(prefs)
            if errors:
                raise ValidationError(errors)
        
        existing = self.get(user_id) if merge else {}
        
        if merge:
            existing.update(prefs)
            prefs = existing
        
        self.db.execute(
            "UPDATE users SET preferences = ? WHERE id = ?",
            (json.dumps(prefs), user_id)
        )
        
        if self.cache:
            self.cache.set(f"prefs:{user_id}", prefs)
        
        if notify:
            self.notify_preference_change(user_id, prefs)
        
        return True
    
    def notify_preference_change(self, user_id: int, prefs: dict):
        # Another 30 lines for a feature nobody asked for
        pass
```

**✅ What Should Happen (Just What Was Asked)**

```python
def save_preferences(db, user_id: int, preferences: dict):
    """Save user preferences to database."""
    db.execute(
        "UPDATE users SET preferences = ? WHERE id = ?",
        (json.dumps(preferences), user_id)
    )
```

**Add later if needed:** Caching (when performance matters), validation (when bad data appears), merging (when requirement emerges).

---

## 3. Surgical Changes

### Example 1: Drive-by Refactoring

**User Request:** "Fix the bug where empty emails crash the validator"

**❌ What LLMs Do (Too Much)**

```diff
  def validate_user(user_data):
-     # Check email format
-     if not user_data.get('email'):
+     """Validate user data."""
+     email = user_data.get('email', '').strip()
+     
+     # Validate email
+     if not email:
          raise ValueError("Email required")
-     
-     # Basic email validation
-     if '@' not in user_data['email']:
+     if '@' not in email or '.' not in email.split('@')[1]:
          raise ValueError("Invalid email")
      
-     # Check username
-     if not user_data.get('username'):
+     # Validate username
+     username = user_data.get('username', '').strip()
+     if not username:
          raise ValueError("Username required")
+     if len(username) < 3:
+         raise ValueError("Username too short")
+     if not username.isalnum():
+         raise ValueError("Username must be alphanumeric")
      
      return True
```

**Problems:**
- "Improved" email validation beyond the bug fix
- Added username validation nobody asked for
- Changed comments
- Added docstring

**✅ What Should Happen (Surgical)**

```diff
  def validate_user(user_data):
      # Check email format
-     if not user_data.get('email'):
+     email = user_data.get('email', '')
+     if not email or not email.strip():
          raise ValueError("Email required")
      
      # Basic email validation
-     if '@' not in user_data['email']:
+     if '@' not in email:
          raise ValueError("Invalid email")
      
      # Check username
      if not user_data.get('username'):
          raise ValueError("Username required")
      
      return True
```

**Only changed:** The specific lines that fix empty email handling.

### Example 2: Style Drift

**User Request:** "Add logging to the upload function"

**❌ What LLMs Do (Reformat Everything)**

```diff
- def upload_file(file_path, destination):
+ def upload_file(file_path: str, destination: str) -> bool:
+     """Upload file to destination with logging."""
+     logger.info(f"Uploading {file_path} to {destination}")
+     
      try:
-         with open(file_path, 'rb') as f:
-             data = f.read()
-         
-         response = requests.post(destination, files={'file': data})
-         
-         if response.status_code == 200:
-             return True
-         else:
-             return False
+         with open(file_path, "rb") as f:
+             data = f.read()
+         response = requests.post(destination, files={"file": data})
+         success = response.status_code == 200
+         
+         if success:
+             logger.info(f"Upload successful: {file_path}")
+         else:
+             logger.error(f"Upload failed: {file_path}, status={response.status_code}")
+         
+         return success
      except Exception as e:
-         print(f"Error: {e}")
+         logger.exception(f"Upload error for {file_path}: {e}")
          return False
```

**Problems:**
- Changed quote style ('' to "")
- Added type hints nobody asked for
- Added docstring
- Reformatted whitespace
- Changed boolean return logic

**✅ What Should Happen (Match Existing Style)**

```diff
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
  def upload_file(file_path, destination):
+     logger.info(f'Starting upload: {file_path}')
      try:
          with open(file_path, 'rb') as f:
              data = f.read()
          
          response = requests.post(destination, files={'file': data})
          
          if response.status_code == 200:
+             logger.info(f'Upload successful: {file_path}')
              return True
          else:
+             logger.error(f'Upload failed: {file_path}, status={response.status_code}')
              return False
      except Exception as e:
-         print(f"Error: {e}")
+         logger.exception(f'Upload error: {file_path}')
          return False
```

**Matched:** Single quotes, no type hints, existing boolean pattern, spacing style.

---

## 4. Goal-Driven Execution

### Example 1: Vague vs. Verifiable

**User Request:** "Fix the authentication system"

**❌ What LLMs Do (Vague Approach)**

```
I'll fix the authentication system by:
1. Reviewing the code
2. Identifying issues
3. Making improvements
4. Testing the changes

[Proceeds to make changes without clear success criteria]
```

**✅ What Should Happen (Verifiable Goals)**

```
To "fix authentication," I need to define success criteria. 
What specific issue are we solving?

If the issue is "users stay logged in after password change":

Plan:
1. Write test: Change password → verify old session invalidated
   Verify: Test fails (reproduces bug)

2. Implement: Invalidate sessions on password change
   Verify: Test passes

3. Check edge cases: Multiple active sessions, concurrent changes
   Verify: Additional tests pass

4. Verify no regression: Existing auth tests still pass
   Verify: Full test suite green

Current test coverage for auth: [shows coverage]
What's the specific auth issue you're seeing?
```

### Example 2: Multi-Step with Verification

**User Request:** "Add rate limiting to the API"

**❌ What LLMs Do (All at Once)**

```python
# Implements full rate limiting with Redis, multiple strategies,
# configuration system, and monitoring in one 300-line commit
# No clear verification steps
```

**✅ What Should Happen (Incremental with Verification)**

```
Plan for rate limiting:

1. Add basic in-memory rate limiting (single endpoint)
   Verify: 
   - Test: 100 requests → first 10 succeed, rest get 429
   - Manual: curl endpoint 11 times, see rate limit error

2. Extract to middleware (apply to all endpoints)
   Verify:
   - Test: Rate limits apply to /users and /posts
   - Existing endpoint tests still pass

3. Add Redis backend (for multi-server)
   Verify:
   - Test: Rate limit persists across app restarts
   - Test: Two app instances share rate limit counter

4. Add configuration (rates per endpoint)
   Verify:
   - Test: /search allows 10/min, /users allows 100/min
   - Config file parsed correctly

Each step is independently verifiable and deployable.
Start with step 1?
```

### Example 3: Test-First Verification

**User Request:** "The sorting breaks when there are duplicate scores"

**❌ What LLMs Do (Fix Without Reproducing)**

```python
# Immediately changes sort logic without confirming the bug
def sort_scores(scores):
    return sorted(scores, key=lambda x: (-x['score'], x['name']))
```

**✅ What Should Happen (Reproduce First)**

```python
# 1. First, write a test that reproduces the issue
def test_sort_with_duplicate_scores():
    """Test sorting when multiple items have same score."""
    scores = [
        {'name': 'Alice', 'score': 100},
        {'name': 'Bob', 'score': 100},
        {'name': 'Charlie', 'score': 90},
    ]
    
    result = sort_scores(scores)
    
    # The bug: order is non-deterministic for duplicates
    # Run this test multiple times, it should be consistent
    assert result[0]['score'] == 100
    assert result[1]['score'] == 100
    assert result[2]['score'] == 90

# Verify: Run test 10 times → fails with inconsistent ordering

# 2. Now fix with stable sort
def sort_scores(scores):
    """Sort by score descending, then name ascending for ties."""
    return sorted(scores, key=lambda x: (-x['score'], x['name']))

# Verify: Test passes consistently
```

---

## 5. Specific Tasks

### Example 1: The Broad Ask

**User Request:** "Fix the checkout"

**❌ What LLMs Do (Infinite Exploration)**

```
Let me understand how checkout works first.

[reads src/checkout/index.ts]
[reads src/checkout/cart.ts, totals.ts, tax.ts, shipping.ts]
[greps "checkout" across the repo — 187 matches]
[reads the Stripe webhook handler]
[reads src/api/routes/orders.ts]
[reads the Order and LineItem models]
[reads the React cart drawer, the address form, the confirmation page]
[reads the test suite to infer intended behavior]

...40 tool calls later, no failing test, and no idea which of the nine
things called "checkout" is actually broken.
```

**Problems:**
- "The checkout" names an *area*, not a *symptom* — so there's no stopping condition.
- Nothing said where the bug lives, so every file is equally plausible.
- Nothing said what "fixed" looks like, so there's no test to write.
- Anthropic lists this in their best practices as **infinite exploration**: investigation without a boundary, reading hundreds of files.

**✅ What Should Happen (Specific Task)**

```
Orders with a discount code total $0.00 at the payment step.
Look at src/checkout/totals.ts, especially how discounts are applied.
Write a failing test first.
```

```
[reads src/checkout/totals.ts — the named suspect]
[writes test: $80 cart + 10% code → expects $72.00, gets $0.00]
[runs it: fails, bug reproduced]
[fixes the discount math, reruns: passes]
```

**Same work — much less wandering around.** Three additions did it:

| What was added | Why it makes the task specific |
|---|---|
| "discount code totals $0.00 at the payment step" | A symptom with a trigger — reproducible, so verifiable |
| "src/checkout/totals.ts, especially discounts" | A file and a suspect — everything else is out of scope |
| "write a failing test first" | A first move, so the run starts by proving the bug, not by reading |

The same three additions turn any broad ask into a specific one:

| Broad | Specific |
|---|---|
| "Improve error handling" | "Uploads over 10MB fail with a generic 500. `api/upload.py` should return a 413 with the size limit. Test both sizes." |
| "Migrate us off moment.js" | "Replace moment in `src/lib/dates/` only — 6 call sites. Keep the existing format strings. Tests in `dates.test.ts` should pass unchanged." |
| "Add caching" | "`GET /reports/summary` recomputes on every hit and takes ~4s. Cache it for 5 minutes in the existing Redis client. Verify the second call is under 50ms." |

### Example 2: Making a Broad Ask Specific Before Exploring

**User Request:** "Something's wrong with our caching, can you look into it?"

**❌ What LLMs Do (Start Reading Anyway)**

```
[greps "cache" — 180 matches across 40 files]
[reads the Redis client, the HTTP cache headers, the React Query config,
 the CDN rules, the in-memory LRU, the service worker]
"I found several potential issues with your caching layer..."
```

Six plausible findings, none confirmed, and the actual bug — stale user
avatars — was never mentioned by the user or found in the sweep.

**✅ What Should Happen (Get Specific First)**

```
Before I start reading — "caching" spans at least five layers here
(CDN, HTTP headers, React Query, a Redis client, and a service worker),
so an open search would mean reading most of the repo.

Two questions to narrow it:

1. **What do you actually see going wrong?** (stale data? memory growth?
   cache misses? something slow?)
2. **Where do you see it?** (a specific page, endpoint, or deploy target)

If you'd rather I just pick, I'll start with the Redis client in
src/lib/cache/ and stop there — tell me if that's the wrong layer.
```

**The rule:** when the ask arrives broad, make it specific *before* exploring. If you
do have to explore, name the boundary out loud and stop at it — and if the
boundary turns out to be wrong, say so and ask rather than silently widening.

---

## 6. Work in Checkpoints

### Example 1: One Big Build vs. Stacked Checkpoints

**User Request:** "Build a tool that counts shots and labels forehands and backhands from tennis broadcast video"

**❌ What LLMs Do (Build It All, Show It at the End)**

```
[writes video I/O, court detection, player tracking, pose, ball tracking,
 hit detection and stroke classification]
[one 3,000-line change, one final run]

"Done! It detected 90 hits: 41 near, 49 far. Forehand: 34, backhand: 34."   <- illustrative output
```

**Problems:**
- The first thing the user can *look at* is the last thing built, so every layer has to be right at once.
- When the output is wrong, nothing says which layer is to blame. (Here the "far player" was a stationary bystander standing off-court, and the pose, hits and strokes were all computed on the wrong person.)
- Every layer's thresholds were tuned against the layer above's mistakes.
- One giant diff: nothing can be reviewed, reverted or bisected on its own.

**✅ What Should Happen (Stack Reviewed Layers)**

Each checkpoint reads the last one's output, adds one layer, ends with something to look at, and stops:

| Checkpoint | Deliverable the user looks at | Review question |
|---|---|---|
| **A** | A clip decoded and re-exported with audio; each model smoke-tested; the rally segmented | Do timings and the segmenter make sense? |
| **B** | Boxes and skeletons over the players | Are the *right* two people boxed? |
| **C** | A fading ball trail | Does it follow the ball, and ignore the scoreboard? |
| **D** | Hit counters in the corner of the video | Do counts match what happened in the rally? |
| **E** | An `FH`/`BH` tag above the hitter | Are the labels right, and how often does it abstain? |
| **F** | Five different clips plus a metrics report | Is this ready to build on? |

The payoff shows up at B. The near player was tracked correctly, but the orange "FAR" box sat on a
bystander for all 103 seconds while `status` said `ok`. Because B was reviewed *before* C and D were
built, it was fixed once, with a speed threshold calibrated on real per-track data (bystanders measured
0.33 and 0.65 m/s of jitter; real players 1.7 to 2.9 m/s), instead of surfacing as "why are the hit counts
wrong?" three layers later.

Each checkpoint also ends with an honest entry in `docs/limitations.md`: what was verified and how, and
what was *not*. For E that meant: "the plan's 90% accuracy gate is not verified, there are no
ground-truth labels" rather than a number that only looked like one.

### Example 2: How a Review Correction Flows Back to the Right Layer

**User Request (during review of D):** "72 hits is 34 near, 38 far. In a rally that shouldn't be possible. The hitters alternate."

**❌ What LLMs Do (Tune Where the Symptom Is)**

```
The far player has more hits, so I'll raise the hit threshold for the far player
and lower it for the near player until the counts match.
```

Counts now match, nothing is fixed, and the timing of the wrong hits is still wrong.

**✅ What Should Happen (Trace to the Layer That Causes It)**

```
Alternation means near and far can differ by at most 1, so at least 3-4 near shots
are missing. Let me find out why, one layer at a time:

1. Look at frames around the missing shots.
   -> the ball is tracked... until the near player runs wide, then it jumps to a
      fixed point at (665, 564) and back. A ball is lying on the court.
   -> ROOT CAUSE, in the *ball* stage: the static-object filter counts frames per
      6px bin, and the stray ball drifts slowly across the frame (consistent with the camera pan), so it never piles up in one bin.
2. Wrist-only guesses beat real contacts because the duplicate rule keeps the *earlier* hit.
   -> EVENT stage, fixed test-first.
3. Bounce kinks count as reversals.
   -> EVENT stage, fixed test-first.
```

Then the discipline that makes it a checkpoint and not just a bug hunt:
- Each fix is a failing test first, then the fix, then its own commit.
- Re-run downstream and **diff**: hits went from 72 (34/38, 4 alternation breaks) to 72 (36/36, 0 breaks).
- Verify a way that does not share the suspect data (a frame-by-frame audit of every hit, plus a
  separate ball-path count) rather than only re-reading the same numbers.
- Record it as a correction in the checkpoint's `docs/limitations.md` entry, including what is *still* wrong.

**The rule:** fix a defect at the earliest layer that causes it. A threshold nudged in a later layer
hides the problem and breaks the next clip.

### Example 3: One Stacked Branch per Checkpoint

**User Request:** "Start Checkpoint B (players and pose) now that A is reviewed."

**❌ What LLMs Do (One Long-Lived Branch)**

```bash
git switch -c rally-tracker main
# ...100+ commits mixing decoding, players, ball, hits, strokes...
# the user reviews the whole thing, or nothing, at the end
```

**Problems:**
- A review has to cover every layer at once.
- One bad layer can't be reverted without touching the others.
- `main` gets everything or nothing.

**✅ What Should Happen (Stack, Review, Merge in Order)**

```bash
git switch -c checkpoint-a-video-io-segments-court main
# ...tests-first commits, docs/limitations.md entry... user reviews A

git switch -c checkpoint-b-players-and-skeleton-overlay checkpoint-a-video-io-segments-court   # cut from A, not from main
# ...B's commits only... user reviews B

git switch -c checkpoint-c-ball-detection-and-trail checkpoint-b-players-and-skeleton-overlay
# ... and so on: checkpoint-d-hit-detection-and-counts, checkpoint-e-forehand-backhand-labels ...
#
# the branch name says which checkpoint it is AND what it adds, so the branch list reads like the plan

# after each is reviewed and accepted, in order:
git switch main && git merge --ff-only checkpoint-a-video-io-segments-court
git merge --ff-only checkpoint-b-players-and-skeleton-overlay   # fast-forward: it already contains A
```

Because the branches are a chain (`main` → a → b → c → d → e), each contains everything before it,
so the merges are fast-forwards and `main` is only ever at a state the user has accepted.

| Benefit | Why |
|---|---|
| Review = one layer's diff | `git diff checkpoint-c-ball-detection-and-trail..checkpoint-d-hit-detection-and-counts` is the work done for D and nothing else |
| A bad layer reverts alone | Revert or drop one branch; earlier layers are untouched |
| History reads like the plan | Small tests-first commits, one per component |
| Bisect works across layers | "It broke somewhere between C and D" is a two-branch search |

If a checkpoint is **squash-merged** instead, the later branches would replay its commits, so move
them across: `git rebase --onto main checkpoint-a-video-io-segments-court checkpoint-b-players-and-skeleton-overlay`. And as always: push only the branch
you are on.

---

## Anti-Patterns Summary

| Principle | Anti-Pattern | Fix |
|-----------|-------------|-----|
| Think Before Coding | Silently assumes file format, fields, scope | List assumptions explicitly, ask for clarification |
| Simplicity First | Strategy pattern for single discount calculation | One function until complexity is actually needed |
| Surgical Changes | Reformats quotes, adds type hints while fixing bug | Only change lines that fix the reported issue |
| Goal-Driven | "I'll review and improve the code" | "Write test for bug X → make it pass → verify no regressions" |
| Specific Tasks | "Fix the checkout" → reads 200 files looking for the bug | Name the symptom, the file, and the first move |
| Checkpoints | Builds every layer in one pass, or tunes a late layer to hide an early layer's bug | Stack reviewed checkpoints on their own branches; fix each defect at the layer that causes it |

## Key Insight

The "overcomplicated" examples aren't obviously wrong—they follow design patterns and best practices. The problem is **timing**: they add complexity before it's needed, which:

- Makes code harder to understand
- Introduces more bugs
- Takes longer to implement
- Harder to test

The "simple" versions are:
- Easier to understand
- Faster to implement
- Easier to test
- Can be refactored later when complexity is actually needed

**Good code is code that solves today's problem simply, not tomorrow's problem prematurely.**
