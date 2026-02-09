#!/usr/bin/env python3
"""
rate-limit-monitor.py - Monitor OpenAI API rate limits

Checks current rate limit status and warns when approaching limits.
Tracks daily and weekly usage against tier limits.

Usage:
    python rate-limit-monitor.py --check
    python rate-limit-monitor.py --status
    python rate-limit-monitor.py --set-tier <tier>
    python rate-limit-monitor.py --set-limit <rpm> <tpm> <rpd>
"""

import json
import os
import sys
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict

# Default tier limits (as of 2025) - update as needed
TIER_LIMITS = {
    "free": {
        "rpm": 3,           # Requests per minute
        "tpm": 40000,       # Tokens per minute
        "rpd": 200,         # Requests per day
        "tpd": 10000000,    # Tokens per day (10M)
        "context": 128000,
    },
    "tier1": {
        "rpm": 500,
        "tpm": 30000,
        "rpd": 10000,
        "tpd": None,        # No daily limit
        "context": 128000,
    },
    "tier2": {
        "rpm": 5000,
        "tpm": 450000,
        "rpd": None,
        "tpd": None,
        "context": 128000,
    },
    "tier3": {
        "rpm": 5000,
        "tpm": 800000,
        "rpd": None,
        "tpd": None,
        "context": 128000,
    },
    "tier4": {
        "rpm": 10000,
        "tpm": 2000000,
        "rpd": None,
        "tpd": None,
        "context": 128000,
    },
    "tier5": {
        "rpm": 10000,
        "tpm": 30000000,    # 30M
        "rpd": None,
        "tpd": None,
        "context": 200000,
    },
}

DATA_DIR = Path(os.getenv("DIAGNOSTICS_DATA_DIR", "/home/chad-yi/.openclaw/workspace/diagnostics/data"))
CONFIG_FILE = DATA_DIR / "rate_limit_config.json"
ALERT_FILE = DATA_DIR / "rate_limit_alerts.log"

# Warning thresholds
WARN_THRESHOLDS = {
    "rpm": 0.8,   # 80% of limit
    "tpm": 0.8,
    "rpd": 0.9,   # 90% of daily
    "tpd": 0.9,
}


@dataclass
class RateLimitConfig:
    tier: str = "free"
    custom_limits: Optional[Dict] = None
    last_updated: str = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()


def load_config() -> RateLimitConfig:
    """Load rate limit configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return RateLimitConfig(**data)
    return RateLimitConfig()


def save_config(config: RateLimitConfig):
    """Save rate limit configuration."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.last_updated = datetime.now().isoformat()
    with open(CONFIG_FILE, "w") as f:
        json.dump(asdict(config), f, indent=2)


def get_limits(config: RateLimitConfig) -> Dict:
    """Get current limits based on tier or custom settings."""
    if config.custom_limits:
        return config.custom_limits
    return TIER_LIMITS.get(config.tier, TIER_LIMITS["free"])


def get_token_usage_minute() -> Tuple[int, int]:
    """Get token usage in the last minute from usage data."""
    token_tracker_path = DATA_DIR / "token_usage.jsonl"
    if not token_tracker_path.exists():
        return 0, 0
    
    one_minute_ago = datetime.now() - timedelta(minutes=1)
    requests = 0
    tokens = 0
    
    with open(token_tracker_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= one_minute_ago:
                    requests += 1
                    tokens += entry.get("input_tokens", 0) + entry.get("output_tokens", 0)
            except (json.JSONDecodeError, KeyError):
                continue
    
    return requests, tokens


def get_token_usage_day() -> Tuple[int, int]:
    """Get token usage for today."""
    token_tracker_path = DATA_DIR / "token_usage.jsonl"
    if not token_tracker_path.exists():
        return 0, 0
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    requests = 0
    tokens = 0
    
    with open(token_tracker_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= today:
                    requests += 1
                    tokens += entry.get("input_tokens", 0) + entry.get("output_tokens", 0)
            except (json.JSONDecodeError, KeyError):
                continue
    
    return requests, tokens


def check_rate_limits() -> Dict:
    """Check current rate limit status."""
    config = load_config()
    limits = get_limits(config)
    
    rpm_used, tpm_used = get_token_usage_minute()
    rpd_used, tpd_used = get_token_usage_day()
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "tier": config.tier,
        "limits": limits,
        "current_usage": {
            "rpm": rpm_used,
            "tpm": tpm_used,
            "rpd": rpd_used,
            "tpd": tpd_used,
        },
        "alerts": [],
        "warnings": [],
    }
    
    # Check RPM
    if limits.get("rpm"):
        rpm_pct = rpm_used / limits["rpm"]
        status["rpm_percentage"] = round(rpm_pct * 100, 1)
        if rpm_pct >= WARN_THRESHOLDS["rpm"]:
            status["warnings"].append(f"RPM at {status['rpm_percentage']}% of limit")
        if rpm_pct >= 1.0:
            status["alerts"].append(f"RPM LIMIT EXCEEDED: {rpm_used}/{limits['rpm']}")
    
    # Check TPM
    if limits.get("tpm"):
        tpm_pct = tpm_used / limits["tpm"]
        status["tpm_percentage"] = round(tpm_pct * 100, 1)
        if tpm_pct >= WARN_THRESHOLDS["tpm"]:
            status["warnings"].append(f"TPM at {status['tpm_percentage']}% of limit")
        if tpm_pct >= 1.0:
            status["alerts"].append(f"TPM LIMIT EXCEEDED: {tpm_used}/{limits['tpm']}")
    
    # Check RPD
    if limits.get("rpd"):
        rpd_pct = rpd_used / limits["rpd"]
        status["rpd_percentage"] = round(rpd_pct * 100, 1)
        if rpd_pct >= WARN_THRESHOLDS["rpd"]:
            status["warnings"].append(f"RPD at {status['rpd_percentage']}% of limit")
        if rpd_pct >= 1.0:
            status["alerts"].append(f"RPD LIMIT EXCEEDED: {rpd_used}/{limits['rpd']}")
    
    # Check TPD
    if limits.get("tpd"):
        tpd_pct = tpd_used / limits["tpd"]
        status["tpd_percentage"] = round(tpd_pct * 100, 1)
        if tpd_pct >= WARN_THRESHOLDS["tpd"]:
            status["warnings"].append(f"TPD at {status['tpd_percentage']}% of limit")
        if tpd_pct >= 1.0:
            status["alerts"].append(f"TPD LIMIT EXCEEDED: {tpd_used}/{limits['tpd']}")
    
    return status


def log_alerts(status: Dict):
    """Log any alerts to file."""
    if status["alerts"] or status["warnings"]:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(ALERT_FILE, "a") as f:
            timestamp = datetime.now().isoformat()
            for alert in status["alerts"]:
                f.write(f"[ALERT] {timestamp}: {alert}\n")
            for warning in status["warnings"]:
                f.write(f"[WARNING] {timestamp}: {warning}\n")


def print_status(status: Dict):
    """Print formatted status to console."""
    print(f"\n{'='*60}")
    print(f"  Rate Limit Status - {status['tier'].upper()} Tier")
    print(f"{'='*60}")
    print(f"  Checked at: {status['timestamp'][:19]}")
    print(f"{'-'*60}")
    
    limits = status["limits"]
    usage = status["current_usage"]
    
    # RPM
    if limits.get("rpm"):
        pct = status.get("rpm_percentage", 0)
        bar = _progress_bar(pct)
        print(f"  RPM:  {usage['rpm']:5} / {limits['rpm']:<5} [{bar}] {pct:5.1f}%")
    
    # TPM
    if limits.get("tpm"):
        pct = status.get("tpm_percentage", 0)
        bar = _progress_bar(pct)
        print(f"  TPM:  {usage['tpm']:7,} / {limits['tpm']:<7,} [{bar}] {pct:5.1f}%")
    
    # RPD
    if limits.get("rpd"):
        pct = status.get("rpd_percentage", 0)
        bar = _progress_bar(pct)
        print(f"  RPD:  {usage['rpd']:6} / {limits['rpd']:<6} [{bar}] {pct:5.1f}%")
    
    # TPD
    if limits.get("tpd"):
        pct = status.get("tpd_percentage", 0)
        bar = _progress_bar(pct)
        tpd_display = f"{usage['tpd'] / 1000000:.2f}M"
        tpd_limit = f"{limits['tpd'] / 1000000:.0f}M"
        print(f"  TPD:  {tpd_display:>6} / {tpd_limit:<6} [{bar}] {pct:5.1f}%")
    
    print(f"{'='*60}")
    
    if status["alerts"]:
        print("\n  🚨 ALERTS:")
        for alert in status["alerts"]:
            print(f"     • {alert}")
    
    if status["warnings"]:
        print("\n  ⚠️  WARNINGS:")
        for warning in status["warnings"]:
            print(f"     • {warning}")
    
    if not status["alerts"] and not status["warnings"]:
        print("\n  ✅ All limits within safe range")
    
    print()


def _progress_bar(percentage: float, width: int = 20) -> str:
    """Create a text progress bar."""
    filled = int(width * min(percentage, 100) / 100)
    bar = "█" * filled + "░" * (width - filled)
    if percentage > 100:
        bar = "█" * width
    return bar


def check_openai_headers():
    """Attempt to check actual rate limit headers from OpenAI (if API key available)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    
    try:
        import requests
        
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        
        headers = response.headers
        return {
            "x-ratelimit-limit-requests": headers.get("x-ratelimit-limit-requests"),
            "x-ratelimit-limit-tokens": headers.get("x-ratelimit-limit-tokens"),
            "x-ratelimit-remaining-requests": headers.get("x-ratelimit-remaining-requests"),
            "x-ratelimit-remaining-tokens": headers.get("x-ratelimit-remaining-tokens"),
            "x-ratelimit-reset-requests": headers.get("x-ratelimit-reset-requests"),
            "x-ratelimit-reset-tokens": headers.get("x-ratelimit-reset-tokens"),
        }
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Monitor OpenAI API rate limits")
    parser.add_argument("--check", action="store_true",
                        help="Check current rate limit status")
    parser.add_argument("--status", action="store_true",
                        help="Show detailed status")
    parser.add_argument("--set-tier", choices=list(TIER_LIMITS.keys()),
                        help="Set your OpenAI tier")
    parser.add_argument("--set-limit", nargs=3, metavar=("RPM", "TPM", "RPD"),
                        help="Set custom limits (use 0 for unlimited)")
    parser.add_argument("--headers", action="store_true",
                        help="Check actual OpenAI API headers")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.set_tier:
        config = load_config()
        config.tier = args.set_tier
        config.custom_limits = None
        save_config(config)
        print(f"Set tier to: {args.set_tier}")
        print(f"Limits: {TIER_LIMITS[args.set_tier]}")
    
    elif args.set_limit:
        rpm, tpm, rpd = args.set_limit
        config = load_config()
        config.custom_limits = {
            "rpm": int(rpm) if int(rpm) > 0 else None,
            "tpm": int(tpm) if int(tpm) > 0 else None,
            "rpd": int(rpd) if int(rpd) > 0 else None,
            "tpd": None,
            "context": 128000,
        }
        save_config(config)
        print(f"Set custom limits: {config.custom_limits}")
    
    elif args.headers:
        headers = check_openai_headers()
        if headers:
            print(json.dumps(headers, indent=2))
        else:
            print("Could not fetch headers. OPENAI_API_KEY not set or request failed.")
    
    elif args.check or args.status:
        status = check_rate_limits()
        log_alerts(status)
        
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        else:
            print_status(status)
        
        # Exit with error code if limits exceeded
        if status["alerts"]:
            sys.exit(1)
    
    else:
        # Default: show status
        status = check_rate_limits()
        log_alerts(status)
        print_status(status)


if __name__ == "__main__":
    main()
