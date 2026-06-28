# Engineering Manager's Log

> One page. This is where you show us how you *directed* the AI — it matters as much
> as the code. Be concrete. Bullet points are fine.

**Name:** Wani
**Time spent (be honest):** ~1 hour 25 mins

---

## How I broke the work down
I read the README and the triage_skill.py file first to understand what was actually needed. Then broke it into four pieces: core skill (classify, route, gate), interactive runner, tests, README section. One piece at a time. I didn't want the AI working on everything at once because that makes it hard to review.

## Where I ran things in parallel
I kept the mock server running in one terminal and the triage script in another while iterating. That way I could edit code and test it without restarting the server every time I made a change.

## One time the AI was wrong, and how I caught it
Claude hardcoded `gemini-2.0-flash` in the classifier. When I ran it, I got a 404 saying the model was deprecated. Had to update it to `gemini-2.5-flash`. 

## What I deliberately cut to fit the 2 hours
- A real logging system (I just print statements for now)


## The design decision I'm proudest of
The human-in-the-loop gate. `execute()` returns None immediately if `approved=False`, before any branch that could reach a write endpoint. On top of that, the write token is never passed to the client in dry-run mode, so even if the gate had a bug, there is no credential available to misuse. Two separate barriers, not one. The gate is not a convention you could forget to call, it is enforced inside the function itself.
