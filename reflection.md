# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- I created the Owner, Pet, Task, and Scheduler classes.
- I came up with the initial attributes and methods for each class and asked AI for the UML diagram and to make sure it looks correct. The AI fixed some class by adding some attributes like time_avaiable for the Owner class.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

**Tradeoff: Greedy scheduling (fast, readable) vs. optimal task packing (correct but complex)**

The `create_plan` method uses a greedy algorithm: it sorts tasks by priority then shortest duration, then adds each task to the plan as long as it fits within `owner.time_available`. This is fast (O(n log n) to sort, O(n) to fit) and easy to explain to a user — "high-priority, shorter tasks go first."

However, greedy scheduling does not always produce the maximum number of tasks. Consider: a 90-minute budget with one 50-minute task and two 45-minute tasks. The greedy algorithm picks the 50-minute task first (same priority), leaving only 40 minutes — neither 45-minute task fits. The optimal solution would skip the 50-minute task and schedule both 45-minute tasks instead.

The true optimal solution is the 0/1 Knapsack problem, which is NP-hard. For a pet care app with 5–10 tasks, that level of complexity is unnecessary. The greedy approach is fast, predictable, and produces a good-enough plan for the real-world use case. The tradeoff is correctness for edge cases in exchange for simplicity and performance.

**A second tradeoff: time conflict detection checks pending tasks only**

The `detect_conflicts` method filters out completed tasks before checking for time overlaps. This prevents false warnings from recurring tasks (which clone themselves with the same `start_time`), but it means a conflict between a completed task and a pending one goes undetected. This is the right tradeoff here — a completed task is already done and can't cause a real scheduling problem.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
