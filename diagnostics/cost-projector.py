#!/usr/bin/env python3
"""
cost-projector.py - Predict remaining API usage and costs

Analyzes usage patterns to predict when limits will be reached.
Provides cost forecasting and budget alerts.

Usage:
    python cost-projector.py --forecast daily
    python cost-projector.py --forecast weekly
    python cost-projector.py --budget 10.00
    python cost-projector.py --project-month
"""

import json
import os
import sys
import argparse
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

DATA_DIR = Path(os.getenv("DIAGNOSTICS_DATA_DIR", "/home/chad-yi/.openclaw/workspace/diagnostics/data"))
USAGE_FILE = DATA_DIR / "token_usage.jsonl"
PROJECTION_FILE = DATA_DIR / "cost_projections.json"

# Default budget settings
DEFAULT_BUDGETS = {
    "daily": 5.0,      # $5/day
    "weekly": 25.0,    # $25/week
    "monthly": 100.0,  # $100/month
}


@dataclass
class UsagePattern:
    period: str
    avg_cost: float
    avg_tokens: int
    avg_calls: int
    trend: str  # increasing, decreasing, stable
    confidence: float


def load_usage_data(days: int = 30) -> List[Dict]:
    """Load usage data for analysis."""
    if not USAGE_FILE.exists():
        return []
    
    cutoff = datetime.now() - timedelta(days=days)
    data = []
    
    with open(USAGE_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= cutoff:
                    data.append(entry)
            except (json.JSONDecodeError, KeyError):
                continue
    
    return data


def analyze_usage_patterns(data: List[Dict]) -> Dict[str, UsagePattern]:
    """Analyze usage patterns from historical data."""
    if not data:
        return {}
    
    # Group by day
    daily_usage = defaultdict(lambda: {"costs": [], "tokens": [], "calls": 0})
    
    for entry in data:
        day = entry["timestamp"][:10]  # YYYY-MM-DD
        daily_usage[day]["costs"].append(entry.get("total_cost", 0))
        daily_usage[day]["tokens"].append(entry.get("input_tokens", 0) + entry.get("output_tokens", 0))
        daily_usage[day]["calls"] += 1
    
    # Calculate daily averages
    daily_costs = [sum(d["costs"]) for d in daily_usage.values()]
    daily_tokens = [sum(d["tokens"]) for d in daily_usage.values()]
    daily_calls = [d["calls"] for d in daily_usage.values()]
    
    if not daily_costs:
        return {}
    
    # Determine trend
    if len(daily_costs) >= 3:
        first_half = statistics.mean(daily_costs[:len(daily_costs)//2])
        second_half = statistics.mean(daily_costs[len(daily_costs)//2:])
        
        if second_half > first_half * 1.2:
            trend = "increasing"
        elif second_half < first_half * 0.8:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    # Calculate confidence based on data volume
    confidence = min(len(data) / 100, 1.0)  # Max confidence at 100+ records
    
    patterns = {
        "daily": UsagePattern(
            period="daily",
            avg_cost=statistics.mean(daily_costs) if daily_costs else 0,
            avg_tokens=int(statistics.mean(daily_tokens)) if daily_tokens else 0,
            avg_calls=int(statistics.mean(daily_calls)) if daily_calls else 0,
            trend=trend,
            confidence=confidence,
        ),
        "weekly": UsagePattern(
            period="weekly",
            avg_cost=statistics.mean(daily_costs) * 7 if daily_costs else 0,
            avg_tokens=int(statistics.mean(daily_tokens) * 7) if daily_tokens else 0,
            avg_calls=int(statistics.mean(daily_calls) * 7) if daily_calls else 0,
            trend=trend,
            confidence=confidence,
        ),
        "monthly": UsagePattern(
            period="monthly",
            avg_cost=statistics.mean(daily_costs) * 30 if daily_costs else 0,
            avg_tokens=int(statistics.mean(daily_tokens) * 30) if daily_tokens else 0,
            avg_calls=int(statistics.mean(daily_calls) * 30) if daily_calls else 0,
            trend=trend,
            confidence=confidence,
        ),
    }
    
    return patterns


def get_current_period_usage(period: str) -> Tuple[float, int, int]:
    """Get current usage for the specified period."""
    if not USAGE_FILE.exists():
        return 0.0, 0, 0
    
    now = datetime.now()
    
    if period == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "weekly":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        return 0.0, 0, 0
    
    total_cost = 0.0
    total_tokens = 0
    total_calls = 0
    
    with open(USAGE_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= start:
                    total_cost += entry.get("total_cost", 0)
                    total_tokens += entry.get("input_tokens", 0) + entry.get("output_tokens", 0)
                    total_calls += 1
            except (json.JSONDecodeError, KeyError):
                continue
    
    return round(total_cost, 4), total_tokens, total_calls


def project_remaining(period: str, budget: float, patterns: Dict[str, UsagePattern]) -> Dict:
    """Project remaining usage for the period."""
    current_cost, current_tokens, current_calls = get_current_period_usage(period)
    
    pattern = patterns.get(period)
    if not pattern:
        return {
            "period": period,
            "budget": budget,
            "current_cost": current_cost,
            "remaining_budget": budget - current_cost,
            "projected_total": None,
            "projected_remaining": None,
            "status": "no_data",
        }
    
    # Calculate time elapsed in period
    now = datetime.now()
    if period == "daily":
        period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + timedelta(days=1)
    elif period == "weekly":
        period_start = now - timedelta(days=now.weekday())
        period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + timedelta(days=7)
    elif period == "monthly":
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if period_start.month == 12:
            period_end = period_start.replace(year=period_start.year + 1, month=1)
        else:
            period_end = period_start.replace(month=period_start.month + 1)
    else:
        return {"error": "Invalid period"}
    
    total_period_seconds = (period_end - period_start).total_seconds()
    elapsed_seconds = (now - period_start).total_seconds()
    remaining_seconds = total_period_seconds - elapsed_seconds
    
    progress = elapsed_seconds / total_period_seconds if total_period_seconds > 0 else 0
    
    # Project based on current rate
    if progress > 0:
        projected_total = current_cost / progress
    else:
        projected_total = pattern.avg_cost
    
    # Adjust based on trend
    if pattern.trend == "increasing":
        projected_total *= 1.1
    elif pattern.trend == "decreasing":
        projected_total *= 0.9
    
    projected_remaining = projected_total - current_cost
    remaining_budget = budget - current_cost
    
    # Determine status
    if projected_total > budget * 1.5:
        status = "critical"
    elif projected_total > budget:
        status = "over_budget"
    elif projected_total > budget * 0.8:
        status = "warning"
    else:
        status = "ok"
    
    days_remaining = remaining_seconds / 86400
    
    return {
        "period": period,
        "budget": budget,
        "current_cost": round(current_cost, 4),
        "current_tokens": current_tokens,
        "current_calls": current_calls,
        "progress_percent": round(progress * 100, 1),
        "projected_total": round(projected_total, 4),
        "projected_remaining": round(projected_remaining, 4),
        "remaining_budget": round(remaining_budget, 4),
        "days_remaining": round(days_remaining, 1),
        "daily_rate": round(current_cost / max(elapsed_seconds / 86400, 0.01), 4),
        "status": status,
        "confidence": pattern.confidence,
        "trend": pattern.trend,
    }


def generate_forecast(patterns: Dict[str, UsagePattern]) -> Dict:
    """Generate cost forecast for all periods."""
    forecast = {
        "generated_at": datetime.now().isoformat(),
        "patterns": {},
        "projections": {},
    }
    
    for period, pattern in patterns.items():
        forecast["patterns"][period] = {
            "avg_cost": round(pattern.avg_cost, 4),
            "avg_tokens": pattern.avg_tokens,
            "avg_calls": pattern.avg_calls,
            "trend": pattern.trend,
            "confidence": round(pattern.confidence, 2),
        }
        
        budget = DEFAULT_BUDGETS.get(period, 10.0)
        forecast["projections"][period] = project_remaining(period, budget, patterns)
    
    # Save forecast
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROJECTION_FILE, "w") as f:
        json.dump(forecast, f, indent=2)
    
    return forecast


def print_forecast(forecast: Dict):
    """Print formatted forecast."""
    print(f"\n{'='*70}")
    print(f"  Cost Forecast & Projections")
    print(f"{'='*70}")
    print(f"  Generated: {forecast['generated_at'][:19]}")
    print(f"{'-'*70}")
    
    for period in ["daily", "weekly", "monthly"]:
        proj = forecast["projections"].get(period)
        if not proj:
            continue
        
        print(f"\n  📊 {period.upper()} FORECAST")
        print(f"  {'─'*66}")
        
        if proj.get("status") == "no_data":
            print(f"     No usage data available yet")
            continue
        
        # Status indicator
        status_icons = {
            "ok": "✅",
            "warning": "⚠️",
            "over_budget": "🚨",
            "critical": "💥",
        }
        icon = status_icons.get(proj["status"], "❓")
        
        print(f"     Budget:           ${proj['budget']:.2f}")
        print(f"     Current Usage:    ${proj['current_cost']:.4f} ({proj['progress_percent']}% through period)")
        print(f"     Projected Total:  ${proj['projected_total']:.4f} {icon}")
        print(f"     Remaining Budget: ${proj['remaining_budget']:.4f}")
        print(f"     Trend:            {proj['trend']}")
        
        if proj["status"] in ["warning", "over_budget", "critical"]:
            print(f"\n     ⚠️  ALERT: Projected to exceed budget by ${proj['projected_total'] - proj['budget']:.2f}")
    
    # Patterns summary
    print(f"\n{'='*70}")
    print(f"  Usage Patterns (Historical)")
    print(f"{'='*70}")
    
    for period, pattern in forecast["patterns"].items():
        print(f"\n  {period.capitalize()}:")
        print(f"    Avg Cost:   ${pattern['avg_cost']:.4f}")
        print(f"    Avg Tokens: {pattern['avg_tokens']:,}")
        print(f"    Avg Calls:  {pattern['avg_calls']}")
        print(f"    Trend:      {pattern['trend']}")
        print(f"    Confidence: {pattern['confidence']*100:.0f}%")
    
    print(f"{'='*70}\n")


def print_budget_check(budget: float, period: str = "monthly"):
    """Check current usage against a specific budget."""
    data = load_usage_data(days=30)
    patterns = analyze_usage_patterns(data)
    
    proj = project_remaining(period, budget, patterns)
    
    print(f"\n{'='*60}")
    print(f"  Budget Check: ${budget:.2f} / {period}")
    print(f"{'='*60}")
    
    if proj.get("status") == "no_data":
        print("  No usage data available")
        return
    
    pct_used = (proj["current_cost"] / budget) * 100
    bar_width = 30
    filled = int(bar_width * min(pct_used, 100) / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    
    print(f"\n  Budget:     ${budget:.2f}")
    print(f"  Used:       ${proj['current_cost']:.4f} ({pct_used:.1f}%)")
    print(f"  Remaining:  ${proj['remaining_budget']:.4f}")
    print(f"  Progress:   [{bar}] {pct_used:.1f}%")
    
    if proj.get("projected_total"):
        projected_pct = (proj["projected_total"] / budget) * 100
        print(f"\n  Projected:  ${proj['projected_total']:.4f} ({projected_pct:.1f}% of budget)")
        
        if proj["status"] == "ok":
            print(f"  Status:     ✅ On track")
        elif proj["status"] == "warning":
            print(f"  Status:     ⚠️  Approaching limit")
        else:
            print(f"  Status:     🚨 Over budget projected")
    
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Predict API usage and costs")
    parser.add_argument("--forecast", choices=["daily", "weekly", "monthly", "all"],
                        help="Generate forecast for period")
    parser.add_argument("--budget", type=float,
                        help="Check against specific budget amount")
    parser.add_argument("--period", choices=["daily", "weekly", "monthly"], default="monthly",
                        help="Period for budget check (default: monthly)")
    parser.add_argument("--project-month", action="store_true",
                        help="Project end-of-month costs")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.budget:
        print_budget_check(args.budget, args.period)
    
    elif args.project_month:
        data = load_usage_data(days=30)
        patterns = analyze_usage_patterns(data)
        proj = project_remaining("monthly", DEFAULT_BUDGETS["monthly"], patterns)
        
        if args.json:
            print(json.dumps(proj, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  Monthly Projection")
            print(f"{'='*60}")
            print(f"  Current Usage:    ${proj['current_cost']:.4f}")
            print(f"  Projected Total:  ${proj['projected_total']:.4f}")
            print(f"  Days Remaining:   {proj['days_remaining']}")
            print(f"  Daily Rate:       ${proj['daily_rate']:.4f}")
            print(f"{'='*60}\n")
    
    else:
        # Default: generate all forecasts
        data = load_usage_data(days=30)
        patterns = analyze_usage_patterns(data)
        forecast = generate_forecast(patterns)
        
        if args.json:
            print(json.dumps(forecast, indent=2))
        else:
            print_forecast(forecast)


if __name__ == "__main__":
    main()
