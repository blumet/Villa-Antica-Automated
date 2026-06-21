# Villa Antica Barcelona — Session Handoff

Paste this whole file into a new chat to resume with full context.

## Project

80-room Barcelona boutique hotel automation POC. 1 orchestrator + 5 specialist agents (guest_comms, revenue, housekeeping, maintenance, fb), each a `BaseAgent` subclass calling Claude Haiku (`claude-haiku-4-5-20251001`) via the Anthropic API with tool use. CSV-backed mock-PMS, no transaction isolation, real permanent mutations. FastAPI + activity feed (`/api/activity?limit=N`, in-memory, rolls over). Frontend not built yet — plan is a Lovable-generated React UI styled after (not copying) Shiji PMS.

Local path: `/Users/blumet/Desktop/Claude Cowork/Outputs/Hotel_Villa_Antica`

**Claude has no direct filesystem/terminal access to this Mac.** Every fact must come from pasted terminal output. Never assume paths or file contents — verify with grep/cat/curl.

## Hard rules to carry forward

- Always state which terminal tab a command goes in. **Server tab** runs ONLY `python3 main.py`, never touched except for explicit restarts. **Curl/test tab** runs everything else (edits, curl, grep, scripts).
- Never declare something "ready" / "fixed" / "verified" without actual pasted command output as evidence.
- One self-contained copy-paste command block at a time — not multi-step instructions.
- Heredocs (`cat > file <<'EOF' ... EOF`) corrupt on paste in this user's zsh/Terminal — **never use them**. For delivering any multi-line file/script: base64-encode it, verify the round-trip, then give one unbroken line: `echo '<base64>' | openssl base64 -d -A > path` (or `| python3 -` to run directly). Use `openssl base64 -d -A`, not `base64 -D`/`-d` (macOS/Linux flag mismatch) — `openssl` is consistent across both.
- Never ask the user to print/echo a secret value to chat. Only check presence/absence (`[ -n "$VAR" ]`, `bool(os.environ.get(...))`).
- If a message is ambiguous or compressed, ask a short clarifying question — don't guess.

## Task status

1. ✅ Verified — scenario B runs twice back-to-back with no state drift (room/ticket status correctly reverts via baseline auto-reset before every scenario run).
2. ✅ Done — extracted final guest-facing message text + maintenance ticket number from a real run (delivered earlier in session).
3. ⬜ **Not started** — git init + push to GitHub. `.gitignore` already exists and excludes `.env`. No `git init` run yet.
4. ⬜ **Not started** — first phased Lovable prompt for the React frontend.
5. ✅ **Just completed this session** — two real bugs found and fixed, both verified with real evidence:
   - **Fix A** (`scenarios/scenario_b.py`): closing log message was hardcoded to "Zero human involvement" regardless of what actually happened. Replaced with a message computed from the real escalation count. Verified live: a real run produced "1 escalation(s) flagged for human review."
   - **Fix B** (`agents/maintenance.py`): maintenance agent's escalation text could falsely claim/imply a guest room-reassignment was pending or done — something it has no visibility into (guest_comms runs in parallel). Added a scope-limit line to its system prompt. Verified via a deterministic standalone test (see below): output explicitly states *"I cannot verify the outcome of the Guest Comms agent's parallel actions... outside my system visibility."* No false claim. Confirmed fixed.

## How Fix B was verified (reusable pattern)

Scenario B's escalation trigger is an ambiguous LLM judgment call, not a deterministic keyword match — retrying scenario B hoping for an escalation wastes time and may never converge. Built a standalone direct-agent test instead:

- Script imports `MaintenanceAgent` directly, bypassing the orchestrator and guest_comms entirely.
- Event description uses "gas leak" — a real entry in `config.py`'s `ESCALATION["safety_keywords"]` list (`flood, fire, water leak, electrical, gas, injury, blood, smoke detector, structural, unsafe`) — guarantees `escalate=True` deterministically via `BaseAgent._check_escalation()`.
- Because guest_comms never runs, any claim in the maintenance agent's output about a reassignment having happened/being pending would be unambiguous proof the bug isn't fixed.
- Result: `escalate=True`, output correctly disclaimed reassignment visibility. Bug confirmed fixed.

This pattern (direct single-agent invocation with a guaranteed-trigger event) is the right way to test any other agent's escalation logic too — don't rely on full scenario runs for that.

## Auth troubleshooting saga (resolved — keep this if it recurs)

**Root cause:** `python-dotenv`'s `load_dotenv()` with no arguments searches upward from the *calling script's own file location*, not the current working directory. `main.py` lives in the project root, so it finds `.env` immediately. A script run from elsewhere (e.g. `/tmp/test_escalation.py`) searches upward from `/tmp` and never finds the project's `.env` — so `ANTHROPIC_API_KEY` never reaches the environment, producing:

```
TypeError: "Could not resolve authentication method. Expected one of api_key, auth_token, or credentials..."
```

**Fix used (no script edit required):** export the key into the current shell from `.env` before running the script:

```bash
export $(grep ANTHROPIC_API_KEY .env | xargs) && python3 /tmp/test_escalation.py
```

This never prints the key's value. Useful for any future standalone script that lives outside the project root.

**Diagnostic sequence that got us here** (useful if a similar auth error shows up again):

```bash
# 1. Confirm .env exists and contains the key name (never prints the value)
cd "/Users/blumet/Desktop/Claude Cowork/Outputs/Hotel_Villa_Antica" && \
[ -f .env ] && echo ".env file: EXISTS" || echo ".env file: MISSING" && \
(grep -q "ANTHROPIC_API_KEY" .env 2>/dev/null && echo ".env has ANTHROPIC_API_KEY: YES" || echo ".env has ANTHROPIC_API_KEY: NO") && \
([ -n "$ANTHROPIC_API_KEY" ] && echo "shell env var SET in this tab" || echo "shell env var NOT SET in this tab") && \
(python3 -c "import dotenv" 2>/dev/null && echo "python-dotenv: INSTALLED" || echo "python-dotenv: NOT INSTALLED")

# 2. Test load_dotenv() in isolation from the project root
python3 -c "from dotenv import load_dotenv; print('dotenv_loaded:', load_dotenv()); import os; print('key_present:', bool(os.environ.get('ANTHROPIC_API_KEY')))"

# 3. Find every place the key/client is actually referenced in the codebase
grep -rn "ANTHROPIC_API_KEY\|api_key\|Anthropic(" --include="*.py" .
```

If step 2 says `True`/`True` but a script elsewhere still fails, compare where that script's `.py` file lives vs. where `.env` lives — that mismatch is the bug.

## Known accepted limitations (explicitly NOT being fixed, by user's choice)

- `agents/maintenance.py`'s escalation trigger has a hardcoded "Room 108" reference baked into its system prompt — same code smell as an earlier hardcode bug elsewhere. Flagged, not fixed.
- Ticket creation vs. reuse on repeated scenario B runs is non-deterministic (agent sometimes creates a new ticket instead of reusing the seeded `TKT0035`). De-risked because baseline reset wipes it before the next run, but the root cause is unfixed.
- `/api/escalations` endpoint exists in `dashboard/app.py` but always returns `[]` — escalation data doesn't persist past the activity buffer's rollover/reset cycle. Don't rely on it; check `/api/activity` immediately after a single run if an escalation needs inspecting.

## Immediate next step — before touching git

The last verification test (`/tmp/test_escalation.py`) created a **real mutation**: ticket `TKT0037` and room 108 set to "maintenance" status in the live CSVs. This must not get committed as the project's baseline state. Was mid-way through finding the reset route when this session ended — next action, curl tab:

```bash
grep -n "reset" dashboard/app.py
```

Then call whatever reset endpoint that reveals (confirm method — GET vs POST — from the route decorator before calling it) to restore clean baseline CSVs, before doing anything with git.

## Task #3 outline — git push (not started, no commands run yet)

- First: confirm CSVs are back to clean baseline (see above).
- Confirm `.gitignore` still excludes `.env`: `cat .gitignore`.
- No git repo initialized yet (`git init` never run on this project).
- Sequence still to do: `git init` → `git status` (eyeball that `.env` and any CSV-mutation artifacts aren't staged) → first commit → create GitHub repo (ask user: via `gh` CLI or web UI) → push.
- Per the hard rule above: don't declare "pushed" without pasted proof (`git log`, `git remote -v`, the actual GitHub URL).

## Task #4 outline — Lovable prompt (not started)

- Frontend not built yet. Plan: Lovable-generated React, styled after (not copying) Shiji PMS's visual language.
- `dashboard/app.py` reportedly already has CORS wide open for local-only Lovable preview use (confirmed in an earlier session, not re-verified this session) — worth a quick sanity check before drafting the prompt: `grep -n "CORS\|allow_origins" dashboard/app.py`.
- Deliver the first prompt as **phase 1 only**, not the whole app in one shot — exact phase-1 scope not yet drafted.

## Operating rules to keep using

- Single self-contained copy-paste command blocks, one at a time, always state which tab.
- Verify, don't assert — every "fixed"/"working"/"ready" claim needs pasted terminal evidence.
- Ask a short clarifying question on ambiguous input rather than guessing.
