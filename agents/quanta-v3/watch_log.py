#!/usr/bin/env python3
"""
watch_log.py  —  colorized live tail for quanta-v3/logs/quanta.log

Usage:
    python watch_log.py              # auto-finds log, follows from beginning
    python watch_log.py logs/quanta.log --since  # only lines since now
"""

import sys
import time
import os
import argparse
from pathlib import Path

# ── ANSI color helpers ─────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

# Block background-ish tones using foreground colors (works in all terminals)
GREEN  = "\033[92m"   # bright green  → PUBLISHED / executed
YELLOW = "\033[93m"   # yellow        → PARSE_FAIL (fuzzy but couldn't parse)
CYAN   = "\033[96m"   # cyan          → BACKFILL signal (seen before, skipped)
WHITE  = "\033[97m"   # white         → ALREADY_SEEN / generic skip
GREY   = "\033[90m"   # dark grey     → not a signal at all
RED    = "\033[91m"   # bright red    → ERROR / NO_REDIS

def _color_for_block(lines: list[str]) -> str:
    """Decide the ANSI color for a whole block based on its └─ ACTION line."""
    for line in lines:
        if "└─ ACTION" in line:
            if "✅ PUBLISHED"   in line: return GREEN
            if "NO_REDIS"       in line: return RED
            if "⚠  IGNORED"     in line: return YELLOW   # fuzzy parse fail
            if "PARSE_FAIL"     in line: return YELLOW
            if "─  IGNORED"     in line: return GREY      # plain not-a-signal
            if "NO_SIGNAL"      in line: return GREY
            if "⏭ SKIPPED"      in line:
                # distinguish backfill-signal (cyan) from non-signal skip (white)
                for l in lines:
                    if "SIGNAL : ✓" in l: return CYAN
                    if "SIGNAL : ~" in l: return CYAN
                return WHITE
    return RESET   # fallback: separator / status lines

def _print_block(lines: list[str], color: str) -> None:
    if not lines:
        return
    for line in lines:
        # Timestamp prefix stays dim so it doesn't compete with the message
        if line.startswith("20") and " INFO " in line:
            # split "2026-02-23 21:05:45,015 INFO quanta-v3 <rest>"
            parts = line.split(" ", 4)
            if len(parts) == 5:
                ts   = f"{DIM}{parts[0]} {parts[1]}{RESET}"
                rest = parts[4].rstrip("\n")
                print(f"{ts} {color}{rest}{RESET}")
                continue
        # ━━ banners and box lines get the full color + bold
        stripped = line.rstrip("\n")
        if stripped.startswith(("━━", "┌─", "│", "└─")):
            print(f"{BOLD}{color}{stripped}{RESET}")
        elif stripped == "":
            print()
        else:
            print(f"{color}{stripped}{RESET}")

def tail_follow(log_path: Path, from_start: bool = True) -> None:
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:

        if not from_start:
            f.seek(0, 2)          # jump to end — only new lines

        pending_block: list[str] = []

        while True:
            line = f.readline()

            if not line:
                # no new data — if we have a pending block with no closing └─
                # yet, don't print it yet; just wait
                if pending_block:
                    # flush if the last line was a non-block status line
                    last = pending_block[-1]
                    if not any(x in last for x in ("┌─", "│  ", "└─", "━━")):
                        color = _color_for_block(pending_block)
                        _print_block(pending_block, color)
                        pending_block = []
                time.sleep(0.2)
                continue

            # Blank line = block separator → flush current block then print blank
            if line.strip() == "":
                if pending_block:
                    color = _color_for_block(pending_block)
                    _print_block(pending_block, color)
                    pending_block = []
                print()
                continue

            pending_block.append(line)

            # ┌─ starts a new block — flush whatever was before it
            if "┌─ MSG" in line and len(pending_block) > 1:
                color = _color_for_block(pending_block[:-1])
                _print_block(pending_block[:-1], color)
                pending_block = [line]

            # └─ closes a block — flush immediately
            if "└─ ACTION" in line:
                color = _color_for_block(pending_block)
                _print_block(pending_block, color)
                pending_block = []


def main() -> None:
    parser = argparse.ArgumentParser(description="Colorized live tail for quanta-v3 log")
    parser.add_argument("logfile", nargs="?", default=None,
                        help="Path to quanta.log (auto-detected if omitted)")
    parser.add_argument("--since", action="store_true",
                        help="Only show lines from NOW onward (skip backfill)")
    args = parser.parse_args()

    if args.logfile:
        log_path = Path(args.logfile)
    else:
        # auto-detect relative to this script
        log_path = Path(__file__).parent / "logs" / "quanta.log"

    if not log_path.exists():
        print(f"Log not found: {log_path}", file=sys.stderr)
        sys.exit(1)

    from_start = not args.since

    print(f"{DIM}── Watching {log_path}  {'(from beginning)' if from_start else '(from now)'}  Ctrl-C to stop ──{RESET}")
    print()

    try:
        tail_follow(log_path, from_start=from_start)
    except KeyboardInterrupt:
        print(f"\n{DIM}── stopped ──{RESET}")


if __name__ == "__main__":
    main()
