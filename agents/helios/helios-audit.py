#!/usr/bin/env python3
"""
Helios Audit Script v2.0
The COO - Expanded monitoring for all agents
"""

import json
import os
import subprocess
import glob
from datetime import datetime, timedelta

class HeliosAuditor:
    def __init__(self):
        self.base_dir = "/home/chad-yi/.openclaw/workspace"
        self.agents_dir = os.path.join(self.base_dir, "agents")
        self.findings = []
        self.agent_status = {}
        
    def audit_data_json(self):
        """Check mission-control-dashboard/data.json directly"""
        try:
            data_path = os.path.join(self.base_dir, "mission-control-dashboard", "data.json")
            with open(data_path) as f:
                data = json.load(f)
            
            issues = []
            
            # Check lastUpdated is recent (within 4 hours)
            if 'lastUpdated' in data:
                last_updated_str = data['lastUpdated'].replace('Z', '+00:00')
                # Handle timezone-aware datetime
                if '+' in last_updated_str or '-' in last_updated_str[:-5]:
                    last_updated = datetime.fromisoformat(last_updated_str)
                else:
                    last_updated = datetime.fromisoformat(last_updated_str).replace(tzinfo=None)
                    
                now = datetime.now()
                if last_updated.tzinfo:
                    now = now.replace(tzinfo=last_updated.tzinfo)
                else:
                    last_updated = last_updated.replace(tzinfo=None)
                    
                age_hours = (now - last_updated).total_seconds() / 3600
                if age_hours > 4:
                    issues.append(f"data.json stale: {age_hours:.1f}h old")
            
            # Check stats match workflow
            if 'stats' in data and 'workflow' in data:
                workflow_pending = len(data['workflow'].get('pending', []))
                workflow_active = len(data['workflow'].get('active', []))
                stats_pending = data['stats'].get('pending', 0)
                stats_active = data['stats'].get('active', 0)
                
                if workflow_pending != stats_pending or workflow_active != stats_active:
                    issues.append(f"Stats mismatch: workflow shows {workflow_pending}p/{workflow_active}a, stats says {stats_pending}p/{stats_active}a")
            
            # Check tasks object exists and has items
            if 'tasks' not in data or len(data['tasks']) == 0:
                issues.append("Empty or missing tasks object")
            
            # Check urgent deadlines
            if 'tasks' in data:
                today = datetime.now().date()
                overdue_tasks = []
                due_today_tasks = []
                
                for task_id, task in data['tasks'].items():
                    if task.get('deadline') and task.get('status') != 'done':
                        deadline = datetime.strptime(task['deadline'], '%Y-%m-%d').date()
                        if deadline < today:
                            overdue_tasks.append(task_id)
                        elif deadline == today:
                            due_today_tasks.append(task_id)
                
                if overdue_tasks:
                    issues.append(f"Overdue tasks: {', '.join(overdue_tasks[:3])}")
                if due_today_tasks:
                    issues.append(f"Due today: {', '.join(due_today_tasks[:3])}")
            
            for issue in issues:
                self.findings.append({
                    "severity": "warning" if "stale" in issue else "critical" if "Empty" in issue else "warning",
                    "category": "data_integrity",
                    "issue": issue
                })
            
            return {"passed": len(issues) == 0, "issues": issues}
            
        except json.JSONDecodeError as e:
            self.findings.append({
                "severity": "critical",
                "category": "data_integrity",
                "issue": f"data.json invalid JSON: {e}"
            })
            return {"passed": False, "error": str(e)}
        except Exception as e:
            self.findings.append({
                "severity": "critical",
                "category": "data_integrity",
                "issue": f"Cannot read data.json: {e}"
            })
            return {"passed": False, "error": str(e)}
    
    def audit_agent_inbox(self, agent_name):
        """Check agent inbox for unread messages"""
        inbox_dir = os.path.join(self.agents_dir, agent_name, "inbox")
        outbox_dir = os.path.join(self.agents_dir, agent_name, "outbox")
        
        result = {"inbox_count": 0, "outbox_count": 0, "unread_recent": False, "no_response": False}
        
        # Check inbox
        if os.path.exists(inbox_dir):
            inbox_files = glob.glob(os.path.join(inbox_dir, "*"))
            result["inbox_count"] = len(inbox_files)
            
            # Check for recent messages (within 24h)
            for f in inbox_files:
                try:
                    mtime = os.path.getmtime(f)
                    age_hours = (datetime.now().timestamp() - mtime) / 3600
                    if age_hours < 24:
                        result["unread_recent"] = True
                        break
                except:
                    pass
        
        # Check outbox
        if os.path.exists(outbox_dir):
            outbox_files = glob.glob(os.path.join(outbox_dir, "*"))
            result["outbox_count"] = len(outbox_files)
        
        # Flag if agent has unread messages but no recent outbox activity
        if result["unread_recent"] and result["outbox_count"] == 0:
            result["no_response"] = True
            self.findings.append({
                "severity": "warning",
                "category": "agent_comms",
                "agent": agent_name,
                "issue": f"Has unread inbox messages but no outbox activity"
            })
        
        return result
    
    def audit_agent_git(self, agent_name):
        """Check agent's git activity"""
        agent_dir = os.path.join(self.agents_dir, agent_name)
        
        try:
            result = subprocess.run(
                ["git", "log", "--since=24 hours ago", "--oneline"],
                cwd=agent_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
                return {
                    "has_commits": len(commits) > 0,
                    "commit_count": len(commits),
                    "commits": commits[:3]  # Last 3 commits
                }
            else:
                return {"has_commits": False, "error": "Not a git repo or no commits"}
                
        except Exception as e:
            return {"has_commits": False, "error": str(e)}
    
    def audit_agent_logs(self, agent_name):
        """Check agent logs for errors"""
        logs_dir = os.path.join(self.agents_dir, agent_name, "logs")
        
        if not os.path.exists(logs_dir):
            return {"exists": False, "errors": []}
        
        error_patterns = ["error", "exception", "failed", "crash", "fatal"]
        recent_errors = []
        
        # Check last log file for errors
        log_files = glob.glob(os.path.join(logs_dir, "*"))
        if log_files:
            latest_log = max(log_files, key=os.path.getmtime)
            try:
                with open(latest_log, 'r') as f:
                    lines = f.readlines()
                    # Check last 50 lines for errors
                    for line in lines[-50:]:
                        line_lower = line.lower()
                        if any(pattern in line_lower for pattern in error_patterns):
                            recent_errors.append(line.strip()[:100])  # Truncate long lines
            except:
                pass
        
        if recent_errors:
            self.findings.append({
                "severity": "warning",
                "category": "agent_health",
                "agent": agent_name,
                "issue": f"Recent errors in logs: {len(recent_errors)} found"
            })
        
        return {"exists": True, "errors": recent_errors[:3]}
    
    def audit_agent_service(self, agent_name):
        """Check if agent systemd service is running"""
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", agent_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {"running": True, "status": "active"}
            else:
                return {"running": False, "status": result.stdout.strip()}
        except Exception as e:
            return {"running": False, "error": str(e)}
    
    def audit_agent_state(self, agent_name):
        """Check agent state.json is fresh"""
        state_path = os.path.join(self.agents_dir, agent_name, "state.json")
        
        if not os.path.exists(state_path):
            return {"exists": False, "fresh": False}
        
        try:
            with open(state_path) as f:
                state = json.load(f)
            
            # Check timestamp
            if 'timestamp' in state:
                last_update = datetime.fromisoformat(state['timestamp'].replace('Z', '+00:00'))
                age_minutes = (datetime.now() - last_update).total_seconds() / 60
                
                return {
                    "exists": True,
                    "fresh": age_minutes < 30,
                    "age_minutes": age_minutes,
                    "status": state.get('status', 'unknown')
                }
            else:
                return {"exists": True, "fresh": False, "reason": "No timestamp"}
                
        except Exception as e:
            return {"exists": True, "valid": False, "error": str(e)}
    
    def audit_agent_memory(self, agent_name):
        """Check if agent MEMORY.md is recent"""
        memory_path = os.path.join(self.agents_dir, agent_name, "MEMORY.md")
        
        if not os.path.exists(memory_path):
            return {"exists": False, "current": False}
        
        mtime = os.path.getmtime(memory_path)
        age_hours = (datetime.now().timestamp() - mtime) / 3600
        
        return {
            "exists": True,
            "current": age_hours < 4,
            "age_hours": age_hours
        }
    
    def audit_agent_full(self, agent_name):
        """Full audit of a single agent"""
        agent_dir = os.path.join(self.agents_dir, agent_name)
        
        if not os.path.exists(agent_dir):
            return {"name": agent_name, "status": "not_created"}
        
        # Run all checks
        service = self.audit_agent_service(agent_name)
        state = self.audit_agent_state(agent_name)
        memory = self.audit_agent_memory(agent_name)
        inbox = self.audit_agent_inbox(agent_name)
        git = self.audit_agent_git(agent_name)
        logs = self.audit_agent_logs(agent_name)
        
        status = {
            "name": agent_name,
            "service_running": service.get("running", False),
            "state_fresh": state.get("fresh", False),
            "memory_current": memory.get("current", False),
            "inbox_unread": inbox.get("inbox_count", 0),
            "inbox_has_recent": inbox.get("unread_recent", False),
            "no_response": inbox.get("no_response", False),
            "git_active_24h": git.get("has_commits", False),
            "git_commits": git.get("commit_count", 0),
            "log_errors": len(logs.get("errors", []))
        }
        
        # Flag issues
        if not service.get("running", False) and agent_name in ["quanta", "helios"]:
            self.findings.append({
                "severity": "warning",
                "category": "agent_health",
                "agent": agent_name,
                "issue": f"Service not running: {service.get('status', 'unknown')}"
            })
        
        if inbox.get("no_response", False):
            # Already flagged in inbox audit
            pass
        
        if not git.get("has_commits", False) and agent_name not in ["helios"]:
            # Not a warning, just info - agents don't commit every day
            pass
        
        return status
    
    def audit_chad_yi(self):
        """Audit CHAD_YI with all checks"""
        base_status = self.audit_agent_full("chad-yi")
        
        # Check daily log
        today = datetime.now().strftime('%Y-%m-%d')
        log_path = os.path.join(self.base_dir, "memory", f"{today}.md")
        daily_log_exists = os.path.exists(log_path)
        
        # Check BUILD_TRACKING.md
        bt_path = os.path.join(self.base_dir, "BUILD_TRACKING.md")
        if os.path.exists(bt_path):
            bt_age = (datetime.now().timestamp() - os.path.getmtime(bt_path)) / 3600
            build_tracking_fresh = bt_age < 4
        else:
            build_tracking_fresh = False
        
        base_status.update({
            "role": "CEO/Brain",
            "daily_log_exists": daily_log_exists,
            "build_tracking_fresh": build_tracking_fresh
        })
        
        # Flag issues
        if not daily_log_exists:
            self.findings.append({
                "severity": "warning",
                "category": "agent_health",
                "agent": "chad-yi",
                "issue": f"Daily log missing: memory/{today}.md"
            })
        
        return base_status
    
    def audit_all_agents(self):
        """Audit all agents in the system"""
        agents_to_audit = ["chad-yi", "quanta", "escritor", "mensamusa", "helios", "forger", "autour"]
        
        for agent_name in agents_to_audit:
            if agent_name == "chad-yi":
                self.agent_status[agent_name] = self.audit_chad_yi()
            else:
                self.agent_status[agent_name] = self.audit_agent_full(agent_name)
    
    def generate_report(self):
        """Generate complete audit report"""
        # Count findings by severity
        critical = len([f for f in self.findings if f.get("severity") == "critical"])
        warning = len([f for f in self.findings if f.get("severity") == "warning"])
        
        # Get urgent deadlines
        urgent_deadlines = [f for f in self.findings if "Overdue" in f.get("issue", "") or "Due today" in f.get("issue", "")]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "auditor": "helios",
            "audit_id": f"audit-{datetime.now().strftime('%Y%m%d-%H%M')}",
            "summary": {
                "total_findings": len(self.findings),
                "critical": critical,
                "warning": warning,
                "agents_audited": len(self.agent_status),
                "urgent_deadlines": len(urgent_deadlines)
            },
            "data_integrity": self.audit_data_json(),
            "agents": self.agent_status,
            "findings": self.findings,
            "recommendations": self.generate_recommendations()
        }
    
    def generate_recommendations(self):
        """Generate actionable recommendations"""
        recs = []
        
        for finding in self.findings:
            if finding["severity"] == "critical":
                recs.append({
                    "priority": "immediate",
                    "category": finding.get("category", "general"),
                    "action": finding["issue"]
                })
            elif finding["severity"] == "warning":
                recs.append({
                    "priority": "soon",
                    "category": finding.get("category", "general"),
                    "agent": finding.get("agent", "system"),
                    "action": finding["issue"]
                })
        
        return recs
    
    def run_audit(self):
        """Run complete audit cycle"""
        print("=" * 50)
        print("Helios Audit v2.0 Starting...")
        print("=" * 50)
        
        # 1. Data.json
        print("\n[1/3] Checking data.json...")
        self.audit_data_json()
        
        # 2. All agents (expanded)
        print("[2/3] Auditing agents (service, state, memory, inbox, git, logs)...")
        self.audit_all_agents()
        
        # 3. Generate report
        print("[3/3] Generating report...")
        report = self.generate_report()
        
        # 4. Write to outbox
        outbox_dir = os.path.join(self.agents_dir, "helios", "outbox")
        os.makedirs(outbox_dir, exist_ok=True)
        
        report_file = os.path.join(outbox_dir, f"audit-{datetime.now().strftime('%Y%m%d-%H%M')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # 5. Print summary
        print("\n" + "=" * 50)
        print("AUDIT COMPLETE")
        print("=" * 50)
        print(f"Report: {report_file}")
        print(f"\nFindings: {report['summary']['total_findings']}")
        print(f"  Critical: {report['summary']['critical']}")
        print(f"  Warning: {report['summary']['warning']}")
        print(f"  Urgent Deadlines: {report['summary']['urgent_deadlines']}")
        print(f"\nAgents Audited: {report['summary']['agents_audited']}")
        
        if report['findings']:
            print("\nTop Issues:")
            for finding in report['findings'][:5]:
                severity = finding['severity'].upper()
                agent = f"[{finding.get('agent', 'system')}] " if 'agent' in finding else ""
                print(f"  [{severity}] {agent}{finding['issue'][:60]}")
        
        print("=" * 50)
        
        return report

if __name__ == "__main__":
    auditor = HeliosAuditor()
    report = auditor.run_audit()
    
    # Exit with error if critical findings
    if report['summary']['critical'] > 0:
        exit(1)
    exit(0)
