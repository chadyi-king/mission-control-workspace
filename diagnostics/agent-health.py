#!/usr/bin/env python3
"""
agent-health.py - Monitor agent health and detect conflicts

Tracks agent processes, detects conflicts, and monitors for crashes.
Integrates with OpenClaw session tracking.

Usage:
    python agent-health.py --check
    python agent-health.py --list
    python agent-health.py --watch
    python agent-health.py --report
"""

import json
import os
import sys
import argparse
import subprocess
import psutil
import time
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict

DATA_DIR = Path(os.getenv("DIAGNOSTICS_DATA_DIR", "/home/chad-yi/.openclaw/workspace/diagnostics/data"))
AGENT_STATE_FILE = DATA_DIR / "agent_state.json"
CRASH_LOG_FILE = DATA_DIR / "agent_crashes.log"
HEALTH_LOG_FILE = DATA_DIR / "health_checks.log"
CONFLICT_LOG_FILE = DATA_DIR / "agent_conflicts.log"

# Health check thresholds
HEALTH_THRESHOLDS = {
    "max_cpu_percent": 90,
    "max_memory_percent": 85,
    "max_runtime_hours": 24,
    "stale_session_minutes": 30,
}


@dataclass
class AgentInfo:
    pid: int
    session_id: str
    agent_id: str
    start_time: str
    last_heartbeat: str
    status: str  # active, idle, stale, crashed
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    operations_count: int = 0
    errors_count: int = 0


def load_agent_state() -> Dict:
    """Load current agent state."""
    if AGENT_STATE_FILE.exists():
        with open(AGENT_STATE_FILE, "r") as f:
            return json.load(f)
    return {"agents": {}, "last_updated": datetime.now().isoformat()}


def save_agent_state(state: Dict):
    """Save agent state to file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now().isoformat()
    with open(AGENT_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def get_openclaw_processes() -> List[Dict]:
    """Find OpenClaw agent processes."""
    processes = []
    
    for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time", "cpu_percent", "memory_info"]):
        try:
            cmdline = " ".join(proc.info.get("cmdline") or [])
            name = proc.info.get("name", "")
            
            # Look for openclaw, python with agent, or relevant processes
            if any(x in cmdline.lower() for x in ["openclaw", "agent", "python"]):
                # Check environment for session info
                proc_obj = psutil.Process(proc.info["pid"])
                environ = proc_obj.environ() if hasattr(proc_obj, "environ") else {}
                
                processes.append({
                    "pid": proc.info["pid"],
                    "name": name,
                    "cmdline": cmdline[:200],  # Truncate for storage
                    "create_time": datetime.fromtimestamp(proc.info["create_time"]).isoformat(),
                    "cpu_percent": proc_obj.cpu_percent(interval=0.1),
                    "memory_mb": proc_obj.memory_info().rss / 1024 / 1024,
                    "session_id": environ.get("OPENCLAW_SESSION_ID", f"pid_{proc.info['pid']}"),
                    "agent_id": environ.get("OPENCLAW_AGENT_ID", "unknown"),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return processes


def detect_conflicts(processes: List[Dict]) -> List[Dict]:
    """Detect potential agent conflicts."""
    conflicts = []
    
    # Group by session_id
    sessions = defaultdict(list)
    for proc in processes:
        sessions[proc["session_id"]].append(proc)
    
    # Detect multiple agents in same session
    for session_id, procs in sessions.items():
        if len(procs) > 1:
            conflicts.append({
                "type": "multiple_agents_same_session",
                "session_id": session_id,
                "agents": procs,
                "severity": "warning",
                "message": f"Multiple agents ({len(procs)}) detected in session {session_id[:8]}...",
            })
    
    # Detect zombie processes (high CPU or memory with no recent activity)
    for proc in processes:
        runtime_hours = (datetime.now() - datetime.fromisoformat(proc["create_time"].replace("Z", "+00:00").replace("+00:00", ""))).total_seconds() / 3600
        
        if runtime_hours > HEALTH_THRESHOLDS["max_runtime_hours"]:
            conflicts.append({
                "type": "long_running_process",
                "pid": proc["pid"],
                "runtime_hours": round(runtime_hours, 1),
                "severity": "info",
                "message": f"Process {proc['pid']} running for {runtime_hours:.1f} hours",
            })
        
        if proc["cpu_percent"] > HEALTH_THRESHOLDS["max_cpu_percent"]:
            conflicts.append({
                "type": "high_cpu_usage",
                "pid": proc["pid"],
                "cpu_percent": proc["cpu_percent"],
                "severity": "warning",
                "message": f"Process {proc['pid']} using {proc['cpu_percent']:.1f}% CPU",
            })
        
        if proc["memory_mb"] > 2048:  # > 2GB
            conflicts.append({
                "type": "high_memory_usage",
                "pid": proc["pid"],
                "memory_mb": round(proc["memory_mb"], 1),
                "severity": "warning",
                "message": f"Process {proc['pid']} using {proc['memory_mb']:.0f} MB memory",
            })
    
    return conflicts


def check_crashes() -> List[Dict]:
    """Check for recent crashes from logs."""
    crashes = []
    
    # Check OpenClaw logs if available
    log_paths = [
        Path.home() / ".openclaw" / "logs" / "openclaw.log",
        Path("/var/log/openclaw.log"),
        Path("/tmp/openclaw.log"),
    ]
    
    for log_path in log_paths:
        if log_path.exists():
            try:
                with open(log_path, "r") as f:
                    lines = f.readlines()
                    
                # Look for crash/error patterns in last 1000 lines
                for line in lines[-1000:]:
                    line_lower = line.lower()
                    if any(x in line_lower for x in ["crash", "fatal", "panic", "error", "exception", "killed"]):
                        crashes.append({
                            "timestamp": datetime.now().isoformat(),
                            "log_line": line.strip()[:200],
                            "log_source": str(log_path),
                        })
                        break  # Just capture most recent
                        
            except Exception:
                continue
    
    return crashes


def log_crash(crash_info: Dict):
    """Log a crash to file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CRASH_LOG_FILE, "a") as f:
        f.write(json.dumps(crash_info) + "\n")


def log_conflict(conflict: Dict):
    """Log a conflict to file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFLICT_LOG_FILE, "a") as f:
        f.write(json.dumps(conflict) + "\n")


def perform_health_check() -> Dict:
    """Perform a full health check."""
    processes = get_openclaw_processes()
    conflicts = detect_conflicts(processes)
    crashes = check_crashes()
    
    # Load previous state
    state = load_agent_state()
    
    # Update state with current processes
    current_pids = {p["pid"] for p in processes}
    previous_pids = set(state.get("agents", {}).keys())
    
    # Detect new and dead agents
    new_agents = current_pids - previous_pids
    dead_agents = previous_pids - current_pids
    
    health_report = {
        "timestamp": datetime.now().isoformat(),
        "active_agents": len(processes),
        "agents": processes,
        "new_agents": list(new_agents),
        "dead_agents": list(dead_agents),
        "conflicts": conflicts,
        "crashes": crashes,
        "system_health": {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
        },
    }
    
    # Log issues
    for conflict in conflicts:
        log_conflict(conflict)
    
    for crash in crashes:
        log_crash(crash)
    
    # Update state
    state["agents"] = {str(p["pid"]): p for p in processes}
    save_agent_state(state)
    
    # Log health check
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HEALTH_LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": health_report["timestamp"],
            "active_agents": health_report["active_agents"],
            "conflicts_count": len(conflicts),
            "crashes_count": len(crashes),
        }) + "\n")
    
    return health_report


def print_health_report(report: Dict):
    """Print formatted health report."""
    print(f"\n{'='*70}")
    print(f"  Agent Health Report")
    print(f"{'='*70}")
    print(f"  Checked at: {report['timestamp'][:19]}")
    print(f"{'-'*70}")
    
    # System health
    sys_health = report["system_health"]
    print(f"  System Health:")
    print(f"    CPU Usage:     {sys_health['cpu_percent']:.1f}%")
    print(f"    Memory Usage:  {sys_health['memory_percent']:.1f}%")
    print(f"    Disk Usage:    {sys_health['disk_percent']:.1f}%")
    print(f"{'-'*70}")
    
    # Agents
    print(f"  Active Agents: {report['active_agents']}")
    if report["agents"]:
        print(f"  {'PID':<8} {'Session':<20} {'CPU%':<8} {'Mem(MB)':<10} {'Runtime':<15}")
        for agent in report["agents"]:
            session_short = agent.get("session_id", "unknown")[:18]
            runtime = "unknown"
            try:
                start = datetime.fromisoformat(agent["create_time"].replace("Z", "+00:00").replace("+00:00", ""))
                runtime_mins = (datetime.now() - start).total_seconds() / 60
                runtime = f"{runtime_mins:.0f}m"
            except:
                pass
            print(f"  {agent['pid']:<8} {session_short:<20} {agent['cpu_percent']:<8.1f} {agent['memory_mb']:<10.0f} {runtime:<15}")
    
    print(f"{'-'*70}")
    
    # Conflicts
    if report["conflicts"]:
        print(f"  ⚠️  Detected Conflicts ({len(report['conflicts'])}):")
        for conflict in report["conflicts"]:
            icon = "🚨" if conflict["severity"] == "error" else "⚠️" if conflict["severity"] == "warning" else "ℹ️"
            print(f"     {icon} [{conflict['severity'].upper()}] {conflict['message']}")
    else:
        print(f"  ✅ No conflicts detected")
    
    # Crashes
    if report["crashes"]:
        print(f"\n  🚨 Recent Crashes ({len(report['crashes'])}):")
        for crash in report["crashes"][:3]:  # Show max 3
            print(f"     • {crash['log_line'][:80]}...")
    else:
        print(f"  ✅ No recent crashes detected")
    
    print(f"{'='*70}\n")


def watch_mode():
    """Run continuous health monitoring."""
    print("🔍 Agent Health Monitor - Watching for issues...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            report = perform_health_check()
            
            # Only print if there are issues or every 10 checks
            if report["conflicts"] or report["crashes"]:
                print_health_report(report)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Healthy - {report['active_agents']} agents")
            
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\n\n👋 Stopped monitoring")


def generate_summary(days: int = 7) -> Dict:
    """Generate health summary for the past N days."""
    since = datetime.now() - timedelta(days=days)
    
    summary = {
        "period_days": days,
        "total_conflicts": 0,
        "total_crashes": 0,
        "conflicts_by_type": defaultdict(int),
        "peak_agents": 0,
    }
    
    # Process health logs
    if HEALTH_LOG_FILE.exists():
        with open(HEALTH_LOG_FILE, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    if entry_time >= since:
                        summary["peak_agents"] = max(summary["peak_agents"], entry.get("active_agents", 0))
                except:
                    continue
    
    # Process conflict logs
    if CONFLICT_LOG_FILE.exists():
        with open(CONFLICT_LOG_FILE, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_time = datetime.fromisoformat(entry.get("timestamp", datetime.now().isoformat()))
                    if entry_time >= since:
                        summary["total_conflicts"] += 1
                        summary["conflicts_by_type"][entry.get("type", "unknown")] += 1
                except:
                    continue
    
    # Process crash logs
    if CRASH_LOG_FILE.exists():
        with open(CRASH_LOG_FILE, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_time = datetime.fromisoformat(entry.get("timestamp", datetime.now().isoformat()))
                    if entry_time >= since:
                        summary["total_crashes"] += 1
                except:
                    continue
    
    return dict(summary)


def main():
    parser = argparse.ArgumentParser(description="Monitor agent health and detect conflicts")
    parser.add_argument("--check", action="store_true",
                        help="Perform single health check")
    parser.add_argument("--list", action="store_true",
                        help="List active agents")
    parser.add_argument("--watch", action="store_true",
                        help="Watch mode - continuous monitoring")
    parser.add_argument("--report", action="store_true",
                        help="Generate summary report")
    parser.add_argument("--days", type=int, default=7,
                        help="Days for summary report (default: 7)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.watch:
        watch_mode()
    
    elif args.list:
        processes = get_openclaw_processes()
        print(f"\n{'='*70}")
        print(f"  Active OpenClaw Agents")
        print(f"{'='*70}")
        for proc in processes:
            print(f"\n  PID:       {proc['pid']}")
            print(f"  Session:   {proc.get('session_id', 'unknown')}")
            print(f"  Agent:     {proc.get('agent_id', 'unknown')}")
            print(f"  Started:   {proc['create_time']}")
            print(f"  CPU:       {proc['cpu_percent']:.1f}%")
            print(f"  Memory:    {proc['memory_mb']:.1f} MB")
            print(f"  Command:   {proc['cmdline'][:60]}...")
        if not processes:
            print("  No active agents found")
        print(f"{'='*70}\n")
    
    elif args.report:
        summary = generate_summary(args.days)
        if args.json:
            print(json.dumps(summary, indent=2, default=str))
        else:
            print(f"\n{'='*60}")
            print(f"  Health Summary (Last {args.days} days)")
            print(f"{'='*60}")
            print(f"  Total Conflicts:  {summary['total_conflicts']}")
            print(f"  Total Crashes:    {summary['total_crashes']}")
            print(f"  Peak Agents:      {summary['peak_agents']}")
            if summary['conflicts_by_type']:
                print(f"\n  Conflicts by Type:")
                for conflict_type, count in summary['conflicts_by_type'].items():
                    print(f"    • {conflict_type}: {count}")
            print(f"{'='*60}\n")
    
    else:
        # Default: health check
        report = perform_health_check()
        if args.json:
            print(json.dumps(report, indent=2, default=str))
        else:
            print_health_report(report)


if __name__ == "__main__":
    main()
