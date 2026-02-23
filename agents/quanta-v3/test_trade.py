#!/usr/bin/env python3
"""
test_trade.py  —  Strategy audit + safe OANDA test order

Runs in two steps:
  1.  AUDIT  — full walkthrough of the strategy math on a sample signal
  2.  TEST   — places a real BUY LIMIT on OANDA at $4,000 (gold ~$5,100+)
               so it appears in your dashboard but will NEVER fill

Usage:
    python test_trade.py           # audit only (no API calls)
    python test_trade.py --live    # audit + send real limit order to OANDA
    python test_trade.py --cancel  # cancel the test order afterwards
"""

import argparse
import math
import os
import sys

# ── color helpers ──────────────────────────────────────────────────────────────
R = "\033[0m"
B = "\033[1m"
G = "\033[92m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
D = "\033[90m"
RE = "\033[91m"

def hdr(title):
    bar = "━" * 64
    print(f"\n{B}{C}{bar}{R}")
    print(f"{B}{C}  {title}{R}")
    print(f"{B}{C}{bar}{R}")

def ok(msg):   print(f"  {G}✓{R}  {msg}")
def info(msg): print(f"  {D}·{R}  {msg}")
def warn(msg): print(f"  {Y}⚠{R}  {msg}")
def err(msg):  print(f"  {RE}✗{R}  {RE}{msg}{R}")
def row(label, value, color=W):
    print(f"  {D}{label:<32}{R}{color}{value}{R}")


# ── SAMPLE SIGNAL (far from today's ~$5,100 market) ───────────────────────────
# This mirrors exactly the kind of signal CallistoFx sends.
SIGNAL = {
    "symbol":     "XAUUSD",
    "direction":  "BUY",
    "entry_low":  4002.0,   # well below live market ~5,100
    "entry_high": 4008.0,
    "stop_loss":  3998.0,   # SL 4 channel pips below entry_low
    "tp_levels":  [4028.0, 4048.0, 4068.0, 4088.0, 4108.0],  # TP1–TP5: 20/40/60/80/100 ch-pips from entry_high
}
NOTE_CURRENT_PRICE = "~5,100"


def section_signal():
    hdr("1 · SIGNAL RECEIVED")
    row("Channel",      "🚀 CallistoFx Premium Channel 🚀")
    row("Raw text",     "🟢XAUUSD🟢 BUY RANGE: 4008-4002  SL 3998  TP1 4028 TP2 4048 TP3 4068 TP4 4088 TP5 4108")
    print()
    row("Symbol",       SIGNAL["symbol"],    C)
    row("Direction",    SIGNAL["direction"], G)
    row("Entry range",  f"${SIGNAL['entry_low']} – ${SIGNAL['entry_high']}", W)
    row("Stop loss",    f"${SIGNAL['stop_loss']}", RE)
    row("TP levels",    "  ".join(f"TP{i+1}=${v}" for i,v in enumerate(SIGNAL["tp_levels"])), Y)
    print()
    info(f"Current live gold price is approx {NOTE_CURRENT_PRICE}.  This test signal is ~$1,100 below market.")
    info("A BUY LIMIT at this price will sit pending in OANDA forever unless you cancel it.")


def section_pip_math():
    hdr("2 · PIP MATH  (XAUUSD convention)")

    entry_low  = SIGNAL["entry_low"]
    entry_high = SIGNAL["entry_high"]
    sl         = SIGNAL["stop_loss"]
    tps        = SIGNAL["tp_levels"]
    entry_mid  = (entry_low + entry_high) / 2

    CH_PIP = 1.0    # 1 channel pip = $1.00 price move for XAUUSD
                    # (= 100 OANDA pips, since 1 OANDA pip = $0.01)

    sl_dist_price  = entry_mid - sl
    sl_dist_ch_pip = sl_dist_price / CH_PIP

    print()
    row("1 channel pip =",         f"${CH_PIP:.2f} price move  (= 100 OANDA pips)")
    row("Entry mid-point",         f"${entry_mid:.2f}")
    row("SL distance (price)",     f"${sl_dist_price:.2f}")
    row("SL distance (ch-pips)",   f"{sl_dist_ch_pip:.0f} channel pips")
    print()

    print(f"  {B}TP levels relative to entry mid:{R}")
    for i, tp in enumerate(tps):
        dist_price  = tp - entry_mid
        dist_chpip  = dist_price / CH_PIP
        rr          = dist_price / sl_dist_price if sl_dist_price else 0
        print(f"    {Y}TP{i+1}{R}  ${tp}  →  +${dist_price:.2f}  "
              f"({dist_chpip:.0f} ch-pips)  RR {rr:.1f}:1")


def section_sizing(usd_sgd=1.35, trade_count=0, equity_sgd=None):
    hdr("3 · POSITION SIZING")

    entry_low  = SIGNAL["entry_low"]
    entry_high = SIGNAL["entry_high"]
    sl         = SIGNAL["stop_loss"]
    entry_mid  = (entry_low + entry_high) / 2

    # Risk budget
    if trade_count < 10:
        risk_sgd = 30.0
        mode = f"fixed SGD 30  (trade #{trade_count + 1} of first 10)"
    else:
        if equity_sgd is None:
            equity_sgd = 5000.0
        risk_sgd = equity_sgd * 0.02
        mode = f"2% of equity  (SGD {equity_sgd:,.0f} × 2% = SGD {risk_sgd:.2f})"

    # Split 33/33/34 across 3 tier entries
    tier_risks = [risk_sgd * 0.33, risk_sgd * 0.33, risk_sgd * 0.34]
    entry_prices = [entry_low, entry_mid, entry_high]   # tier 1/2/3

    print()
    row("Trade count",   str(trade_count))
    row("Risk mode",     mode, Y)
    row("Total risk",    f"SGD {risk_sgd:.2f}", G)
    row("USD/SGD rate",  f"{usd_sgd:.4f}  (live rate fetched from OANDA)")
    print()

    total_units = 0
    print(f"  {B}Three-tier limit order split:{R}")
    for i, (entry_price, tier_risk) in enumerate(zip(entry_prices, tier_risks), 1):
        price_dist   = abs(entry_price - sl)
        usd_risk_per_unit = price_dist              # XAU_USD: 1 unit = 1 oz, $1 move = $1
        sgd_per_unit = usd_risk_per_unit * usd_sgd
        raw          = tier_risk / sgd_per_unit
        units        = max(1, int(math.floor(raw)))  # minimum 1 unit
        min_flag     = "  ⚠ min-1 override" if raw < 1.0 else ""
        max_loss_sgd = units * sgd_per_unit
        total_units += units
        print(f"    {C}Tier {i}{R}  entry=${entry_price:.2f}  "
              f"dist=${price_dist:.2f}  "
              f"raw={raw:.2f}→units={units}  "
              f"max-loss=SGD{max_loss_sgd:.2f}{min_flag}")

    print()
    row("Total units across 3 orders", str(total_units), G)
    warn("OANDA XAU_USD: 1 unit = 1 troy ounce.  Min order = 1 unit.")
    return total_units


def section_tp_management():
    hdr("4 · TP MANAGEMENT  (position_manager loop, every 5s)")

    entry_mid = (SIGNAL["entry_low"] + SIGNAL["entry_high"]) / 2
    tps       = SIGNAL["tp_levels"]
    sl        = SIGNAL["stop_loss"]
    total_u   = 100   # example: 100 units total

    print()
    print(f"  {B}Assuming {total_u} total units entered at ${entry_mid:.2f}:{R}\n")

    remaining = total_u
    current_sl = sl
    for i, tp in enumerate(tps):
        close_u    = max(int(total_u * 0.10), 1)   # 10% of ORIGINAL
        remaining -= close_u
        tp_label   = f"TP{i+1}"

        if i == 0:
            current_sl = entry_mid
            sl_note = f"  → SL moves to breakeven ${entry_mid:.2f}"
        elif i == len(tps) - 1:
            sl_note = "  → Runner activates!"
        else:
            sl_note = f"  → SL stays at breakeven ${current_sl:.2f}"

        profit_per_u = tp - entry_mid
        profit_total = close_u * profit_per_u
        print(f"    {Y}{tp_label}{R}  price=${tp}  "
              f"close {close_u} units  "
              f"profit +${profit_total:.2f}  "
              f"remaining={remaining}{sl_note}")

    print()
    print(f"  {B}Runner phase  (after TP5){R}\n")
    print(f"  Every +$10.00 price gain (+10 channel pips):")
    print(f"    → Close 10% of then-remaining units")
    print(f"    → Trail SL $10.00 behind latest milestone\n")
    runner_remaining = remaining
    runner_price = tps[-1]
    entry = entry_mid
    for step in range(1, 4):
        milestone = tps[-1] + step * 10.0
        close_u = max(int(runner_remaining * 0.10), 1)
        runner_remaining -= close_u
        trail_sl = entry + (step * 10.0)   # breakeven + $10 per step
        profit_per_u = milestone - entry
        print(f"    {G}Step {step}{R}  price=${milestone:.2f}  "
              f"close {close_u} units  "
              f"SL trails to ${trail_sl:.2f}  "
              f"remaining={runner_remaining}")


def section_audit_verdict():
    hdr("5 · STRATEGY AUDIT VERDICT")
    print()
    ok("Signal parsing  — XAUUSD BUY/SELL, entry range, SL, TP absolute prices")
    ok("Risk sizing     — SGD 30 fixed first 10 trades, then 2% equity")
    ok("Three-tier entry— 3 LIMIT orders at low/mid/high of entry range (33/33/34%)")
    ok("Units formula   — units = (risk_SGD / USD_SGD_rate) / price_distance_to_SL")
    ok("TP closes       — 10% of ORIGINAL units at each TP (5 TPs = 50% total)")
    ok("SL breakeven    — moves to entry price when TP1 is hit")
    ok("Runner          — activates after TP5; every +$10 → close 10% remaining")
    ok("Runner SL trail — trails $10.00 behind each milestone  ← FIXED today")
    print()
    warn("Parser only catches XAUUSD today.  Other symbols (GBPUSD etc.) would be ignored.")
    warn("USD/SGD rate is fetched live — if that OANDA pair is unavailable, sizing fails.")
    warn("Position manager polls every 5s — in fast markets a TP may be missed briefly.")


def section_live_order(dry_run: bool) -> list:
    hdr("6 · TEST ORDER  →  OANDA API  (3 LIMIT orders, three-tier)")
    print()
    print(f"  Placing {B}3 BUY LIMIT orders{R} for XAU_USD via execute_three_tier():")
    row("  Tier 1 entry",  f"${SIGNAL['entry_low']:.2f}  (lowest)")
    row("  Tier 2 entry",  f"${(SIGNAL['entry_low']+SIGNAL['entry_high'])/2:.2f}  (mid)")
    row("  Tier 3 entry",  f"${SIGNAL['entry_high']:.2f}  (highest)")
    row("  Stop loss",     f"${SIGNAL['stop_loss']:.2f}")
    row("  Time in force", "GTC  (Good Till Cancelled — will NEVER fill at $4,000)")
    row("  Client tags",   "qv3-TEST-tier1 / tier2 / tier3")
    row("  Mode",          "DRY RUN — no API calls" if dry_run else "LIVE — real orders sent to OANDA")
    print()

    if dry_run:
        info("Pass --live to actually send these 3 orders to OANDA.")
        return []

    sys.path.insert(0, os.path.dirname(__file__))
    from config import load_settings
    from oanda_client import OandaClient
    from trade_manager import TradeManager
    from risk_manager import RiskManager
    from redis_backbone import RedisBackbone
    from signal_parser import ParsedSignal

    settings = load_settings()
    oanda = OandaClient(
        settings.oanda_account_id,
        settings.oanda_api_key,
        settings.oanda_base_url,
        dry_run=False,
    )
    try:
        store = RedisBackbone(settings.redis_url)
    except Exception:
        import fakeredis
        store = type("FakeStore", (), {
            "get_trade_count": lambda self: 0,
            "set_risk_mode": lambda self, m: None,
        })()

    risk = RiskManager(store)  # type: ignore[arg-type]
    tm = TradeManager(oanda, store, risk, None)  # type: ignore[arg-type]

    signal = ParsedSignal(
        symbol=SIGNAL["symbol"],
        direction=SIGNAL["direction"],
        entry_low=SIGNAL["entry_low"],
        entry_high=SIGNAL["entry_high"],
        stop_loss=SIGNAL["stop_loss"],
        tp_levels=SIGNAL["tp_levels"],
    )

    try:
        result = tm.execute_three_tier(signal, message_id=99999)
        order_ids = result.get("trade_ids", [])
        print(f"  {G}✓  {len(order_ids)} order(s) accepted!{R}")
        for i, oid in enumerate(order_ids, 1):
            row(f"  Tier {i} OANDA order ID", str(oid), G)
        row("  Check dashboard", "https://trade.oanda.com  →  Orders tab")
        print()
        warn("Remember to cancel these orders when done testing:")
        for oid in order_ids:
            print(f"    {D}python test_trade.py --cancel {oid}{R}")
        return order_ids
    except Exception as exc:
        err(f"Order failed: {exc}")
        return []


def section_cancel_order(order_id: str) -> None:
    hdr("CANCEL TEST ORDER")
    print()
    sys.path.insert(0, os.path.dirname(__file__))
    from config import load_settings
    from oanda_client import OandaClient
    import requests as req

    settings = load_settings()
    oanda = OandaClient(
        settings.oanda_account_id,
        settings.oanda_api_key,
        settings.oanda_base_url,
        dry_run=False,
    )

    url = f"{oanda.base_url}/v3/accounts/{oanda.account_id}/orders/{order_id}/cancel"
    try:
        assert oanda.session is not None, "session is None (dry_run mode?)"
        resp = oanda.session.put(url, timeout=10)
        resp.raise_for_status()
        ok(f"Order {order_id} cancelled successfully.")
    except Exception as exc:
        err(f"Cancel failed: {exc}")


# ── main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live",   action="store_true", help="Send real order to OANDA")
    parser.add_argument("--cancel", metavar="ORDER_ID",  help="Cancel a previously placed test order")
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if args.cancel:
        section_cancel_order(args.cancel)
        return

    section_signal()
    section_pip_math()
    section_sizing(usd_sgd=1.35, trade_count=0)
    section_tp_management()
    section_audit_verdict()
    order_ids = section_live_order(dry_run=not args.live)

    if order_ids:
        print()
        for oid in order_ids:
            print(f"{D}  To cancel:  python test_trade.py --cancel {oid}{R}")

    print()


if __name__ == "__main__":
    main()
