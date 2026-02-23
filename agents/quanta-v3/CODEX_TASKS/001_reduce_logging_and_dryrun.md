Task: 001 - Reduce noisy logging & add `--dry-run` support
Timebox: 45-60 minutes
Priority: high (safety first)

Objective
---------
Make minimal, safe changes to QUANTA v3 so that:
- Only true signals and errors are logged to stdout/file (reduce noisy "Message (not signal)" logs).
- A global `DRY_RUN` mode exists, defaulting to `true` for safety, controllable via `--dry-run` (CLI) or `DRY_RUN` env var.
- All order placement code respects `DRY_RUN` and never sends live orders when enabled. Instead it returns simulated order responses and emits the same events to Redis streams for downstream testing.

Files to modify
---------------
- `main.py` — add `--dry-run` CLI flag and pass setting into the app initializer.
- `config.py` or `load_settings()` — ensure `dry_run` boolean is read from env and CLI.
- `telegram_listener.py` — stop printing/logging every message; only log when `tolerant_signal_check` is True (signal detected) or on errors. Publish `signal_ignored` events for ignored messages.
- `oanda_client.py` (or `oanda_client` module) — add `dry_run` check in order placement methods and return simulated responses when `dry_run` True.
- `redis_backbone.py` (or `redis_backbone` helpers) — ensure `publish_event(event_type, payload)` exists and is used for `signal_detected`, `signal_ignored`, and `signal_executed`.

Acceptance Criteria
-------------------
1. `python3 -m py_compile *.py` in `agents/quanta-v3` passes with no syntax errors.
2. Existing unit tests still pass: `python3 -m unittest -v` (the 2 current parser tests must remain OK).
3. Default behaviour is safe: DRY_RUN enabled by default. Running `python3 main.py --role listener` should not send any live orders.
4. On receiving a non-signal message the code does NOT print the full message but does write a `signal_ignored` event to Redis stream `quanta.events` with the correct schema.
5. On receiving a valid signal: print a concise `✅ SIGNAL DETECTED: {...}` line and publish `signal_detected` to `quanta.events`.
6. When `--dry-run` is false (explicitly passed), the system will call `oanda_client` order methods but `oanda_client` will still respect `dry_run` flag (for safety this task keeps a default true). Live order placement is explicitly gated and will not run unless user sets `DRY_RUN=false` in env and `--dry-run false` on CLI.

Implementation Notes
--------------------
- Keep changes minimal and well-tested. Do NOT change trading logic (tier sizes, TP steps) in this task.
- Use `redis_backbone.publish_stream` or add `publish_event(event_type, payload)` wrapper to write JSON to `quanta.events` (XADD or Upstash REST equivalent) — prefer existing helper functions if present.
- Logging: use `logger.info(...)` for signals and `logger.error(...)` for exceptions. Avoid `print(...)` for routine non-signal messages.
- Tests: add a small unit test `test_dry_run_prevents_orders` that simulates a `ParsedSignal` and verifies `oanda_client.create_order` is NOT called when `dry_run` True (use monkeypatch/mocks).

Test Commands
-------------
From `agents/quanta-v3` run:
```
python3 -m py_compile *.py
python3 -m unittest -v
```

Patch Output Required
---------------------
- A short patch (git diff) with only the minimal code changes.
- A new or updated unit test demonstrating dry-run behaviour.
- A brief note in `CHANGELOG.md` under `agents/quanta-v3/` describing the safety change.

Notes for Codex
---------------
- Scope the task to the exact files listed. If `config.py` is not present, add a small `config.py` with `load_settings()` that supports env + CLI override for `dry_run`.
- Ensure `DRY_RUN` default is `true` (string 'true' / '1' should be accepted).
- Keep all changes reversible and documented in the patch message.
