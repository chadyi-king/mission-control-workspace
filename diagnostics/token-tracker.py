#!/usr/bin/env python3
"""
token-tracker.py - Track OpenAI API usage and costs

Tracks token usage and costs for OpenAI API calls.
Stores usage data in JSON format for analysis.

Usage:
    python token-tracker.py --log-api-call <model> <input_tokens> <output_tokens>
    python token-tracker.py --report daily
    python token-tracker.py --report weekly
    python token-tracker.py --report monthly
    python token-tracker.py --export csv
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Pricing per 1K tokens (as of 2025) - update as needed
MODEL_PRICING = {
    "gpt-4o": {"input": 0.0025, "output": 0.0100},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "o1-preview": {"input": 0.015, "output": 0.06},
    "o1-mini": {"input": 0.003, "output": 0.012},
    "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
    "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
    "default": {"input": 0.01, "output": 0.03},
}

DATA_DIR = Path(os.getenv("DIAGNOSTICS_DATA_DIR", "/home/chad-yi/.openclaw/workspace/diagnostics/data"))
USAGE_FILE = DATA_DIR / "token_usage.jsonl"


@dataclass
class APICall:
    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    operation: Optional[str] = None


def get_pricing(model: str) -> Dict[str, float]:
    """Get pricing for a model, falling back to default if unknown."""
    return MODEL_PRICING.get(model, MODEL_PRICING["default"])


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> Dict[str, float]:
    """Calculate cost for an API call."""
    pricing = get_pricing(model)
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    return {
        "input": round(input_cost, 6),
        "output": round(output_cost, 6),
        "total": round(input_cost + output_cost, 6),
    }


def log_api_call(
    model: str,
    input_tokens: int,
    output_tokens: int,
    session_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    operation: Optional[str] = None,
) -> APICall:
    """Log an API call to the usage file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    costs = calculate_cost(model, input_tokens, output_tokens)
    call = APICall(
        timestamp=datetime.now().isoformat(),
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost=costs["input"],
        output_cost=costs["output"],
        total_cost=costs["total"],
        session_id=session_id or os.getenv("OPENCLAW_SESSION_ID"),
        agent_id=agent_id or os.getenv("OPENCLAW_AGENT_ID"),
        operation=operation,
    )
    
    with open(USAGE_FILE, "a") as f:
        f.write(json.dumps(asdict(call)) + "\n")
    
    return call


def load_usage_data() -> List[Dict]:
    """Load all usage data from file."""
    if not USAGE_FILE.exists():
        return []
    
    data = []
    with open(USAGE_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def get_date_range(period: str) -> tuple:
    """Get start and end dates for a period."""
    now = datetime.now()
    
    if period == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif period == "weekly":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    elif period == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
    else:
        raise ValueError(f"Unknown period: {period}")
    
    return start, end


def generate_report(period: str) -> Dict:
    """Generate usage report for a period."""
    data = load_usage_data()
    start, end = get_date_range(period)
    
    # Filter data by date range
    filtered = []
    for entry in data:
        entry_time = datetime.fromisoformat(entry["timestamp"])
        if start <= entry_time < end:
            filtered.append(entry)
    
    # Aggregate stats
    stats = {
        "period": period,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "total_calls": len(filtered),
        "total_input_tokens": sum(e["input_tokens"] for e in filtered),
        "total_output_tokens": sum(e["output_tokens"] for e in filtered),
        "total_cost": sum(e["total_cost"] for e in filtered),
        "by_model": {},
        "by_agent": {},
        "by_operation": {},
    }
    
    for entry in filtered:
        # By model
        model = entry.get("model", "unknown")
        if model not in stats["by_model"]:
            stats["by_model"][model] = {"calls": 0, "tokens": 0, "cost": 0}
        stats["by_model"][model]["calls"] += 1
        stats["by_model"][model]["tokens"] += entry["input_tokens"] + entry["output_tokens"]
        stats["by_model"][model]["cost"] += entry["total_cost"]
        
        # By agent
        agent = entry.get("agent_id") or "unknown"
        if agent not in stats["by_agent"]:
            stats["by_agent"][agent] = {"calls": 0, "tokens": 0, "cost": 0}
        stats["by_agent"][agent]["calls"] += 1
        stats["by_agent"][agent]["tokens"] += entry["input_tokens"] + entry["output_tokens"]
        stats["by_agent"][agent]["cost"] += entry["total_cost"]
        
        # By operation
        op = entry.get("operation") or "unknown"
        if op not in stats["by_operation"]:
            stats["by_operation"][op] = {"calls": 0, "tokens": 0, "cost": 0}
        stats["by_operation"][op]["calls"] += 1
        stats["by_operation"][op]["tokens"] += entry["input_tokens"] + entry["output_tokens"]
        stats["by_operation"][op]["cost"] += entry["total_cost"]
    
    # Round costs
    stats["total_cost"] = round(stats["total_cost"], 4)
    for category in ["by_model", "by_agent", "by_operation"]:
        for key in stats[category]:
            stats[category][key]["cost"] = round(stats[category][key]["cost"], 4)
    
    return stats


def print_report(stats: Dict):
    """Print formatted report to console."""
    print(f"\n{'='*60}")
    print(f"  Token Usage Report - {stats['period'].upper()}")
    print(f"{'='*60}")
    print(f"  Period: {stats['start'][:10]} to {stats['end'][:10]}")
    print(f"{'-'*60}")
    print(f"  Total API Calls:     {stats['total_calls']}")
    print(f"  Input Tokens:        {stats['total_input_tokens']:,}")
    print(f"  Output Tokens:       {stats['total_output_tokens']:,}")
    print(f"  Total Tokens:        {stats['total_input_tokens'] + stats['total_output_tokens']:,}")
    print(f"{'-'*60}")
    print(f"  TOTAL COST:          ${stats['total_cost']:.4f}")
    print(f"{'='*60}")
    
    if stats["by_model"]:
        print("\n  By Model:")
        for model, data in sorted(stats["by_model"].items(), key=lambda x: -x[1]["cost"]):
            print(f"    {model:25} {data['calls']:4} calls  ${data['cost']:.4f}")
    
    if stats["by_agent"] and len(stats["by_agent"]) > 1:
        print("\n  By Agent:")
        for agent, data in sorted(stats["by_agent"].items(), key=lambda x: -x[1]["cost"]):
            agent_short = agent[:20] if len(agent) > 20 else agent
            print(f"    {agent_short:25} {data['calls']:4} calls  ${data['cost']:.4f}")


def export_to_csv(output_path: Optional[str] = None):
    """Export usage data to CSV."""
    data = load_usage_data()
    
    if not output_path:
        output_path = DATA_DIR / f"token_usage_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    import csv
    with open(output_path, "w", newline="") as f:
        if data:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    print(f"Exported {len(data)} records to {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Track OpenAI API token usage and costs")
    parser.add_argument("--log-api-call", nargs=3, metavar=("MODEL", "INPUT_TOKENS", "OUTPUT_TOKENS"),
                        help="Log a new API call")
    parser.add_argument("--report", choices=["daily", "weekly", "monthly", "all"],
                        help="Generate usage report")
    parser.add_argument("--export", choices=["csv", "json"],
                        help="Export usage data")
    parser.add_argument("--output", help="Output path for export")
    parser.add_argument("--session-id", help="Session ID for the API call")
    parser.add_argument("--agent-id", help="Agent ID for the API call")
    parser.add_argument("--operation", help="Operation type for the API call")
    
    args = parser.parse_args()
    
    if args.log_api_call:
        model, input_toks, output_toks = args.log_api_call
        call = log_api_call(
            model=model,
            input_tokens=int(input_toks),
            output_tokens=int(output_toks),
            session_id=args.session_id,
            agent_id=args.agent_id,
            operation=args.operation,
        )
        print(f"Logged: {call.model} - ${call.total_cost:.6f}")
    
    elif args.report:
        if args.report == "all":
            for period in ["daily", "weekly", "monthly"]:
                stats = generate_report(period)
                print_report(stats)
        else:
            stats = generate_report(args.report)
            print_report(stats)
    
    elif args.export:
        if args.export == "csv":
            export_to_csv(args.output)
        elif args.export == "json":
            output_path = args.output or DATA_DIR / f"token_usage_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            data = load_usage_data()
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Exported {len(data)} records to {output_path}")
    
    else:
        # Default: show today's usage
        stats = generate_report("daily")
        print_report(stats)


if __name__ == "__main__":
    main()
