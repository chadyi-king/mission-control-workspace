#!/usr/bin/env python3
"""
Helios Audit Script
The COO - Audits all agents including CHAD_YI
"""

import json
import os
import subprocess
from datetime import datetime, timedelta

class HeliosAuditor:
    def __init__(self):
        self.base_dir = "/home/chad-yi/.openclaw/workspace"
        self.findings = []
        self.agent_status = {}
        
    def audit_data_integrity(self):
        """Check DATA/data.json is valid and consistent"""
        try:
            data_path = os.path.join(self.base_dir, "DATA", "data.json")
            with open(data_path) as f:
                data = json.load(f)
            
            # Check tasks exist
            if 'tasks' not in data:
                self.findings.append({
                    "severity": "critical",
                    "category": "data_integrity",
                    "issue": "Missing 'tasks' key in data.json"
                })
                return False
            
            task_count = len(data['tasks'])
            
            # Check workflow consistency
            if 'workflow' in data:
                workflow_tasks = set()
                for status, ids in data['workflow'].items():
                    workflow_tasks.update(ids)
                
                if len(workflow_tasks) != len(list(workflow_tasks)):
                    self.findings.append({
                        "severity": "critical",
                        "category": "data_integrity",
                        "issue": "Duplicate task IDs in workflow arrays"
                    })
            
            # Check agents exist
            if 'agents' not in data:
                self.findings.append({
                    "severity": "warning",
                    "category": "data_integrity",
                    "issue": "Missing 'agents' section"
                })
            
            return {
                "passed": True,
                "task_count": task_count,
                "agent_count": len(data.get('agents', {}))
            }
            
        except json.JSONDecodeError as e:
            self.findings.append({
                "severity": "critical",
                "category": "data_integrity",
                "issue": f"Invalid JSON: {e}"
            })
            return {"passed": False}
        except Exception as e:
            self.findings.append({
                "severity": "critical",
                "category": "data_integrity",
                "issue": f"Cannot read data.json: {e}"
            })
            return {"passed": False}
    
    def audit_agent_service(self, agent_name):
        """Check if agent systemd service is running"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", agent_name],
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
        state_path = os.path.join(self.base_dir, "agents", agent_name, "state.json")
        
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
                    "fresh": age_minutes < 30,  # Fresh if updated in last 30 min
                    "age_minutes": age_minutes,
                    "status": state.get('status', 'unknown')
                }
            else:
                return {"exists": True, "fresh": False, "reason": "No timestamp"}
                
        except Exception as e:
            return {"exists": True, "valid": False, "error": str(e)}
    
    def audit_agent_memory(self, agent_name):
        """Check if agent MEMORY.md is recent"""
        memory_path = os.path.join(self.base_dir, "agents", agent_name, "MEMORY.md")
        
        if not os.path.exists(memory_path):
            return {"exists": False, "current": False}
        
        mtime = os.path.getmtime(memory_path)
        age_hours = (datetime.now().timestamp() - mtime) / 3600
        
        return {
            "exists": True,
            "current": age_hours < 4,  # Current if updated in last 4 hours
            "age_hours": age_hours
        }
    
    def audit_chad_yi(self):
        """Audit CHAD_YI (me) - Check my compliance"""
        # Check my state
        state = self.audit_agent_state("chad-yi")
        
        # Check my memory
        memory = self.audit_agent_memory("chad-yi")
        
        # Check daily log exists
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
        
        status = {
            "name": "chad-yi",
            "role": "CEO/Brain",
            "state_fresh": state.get("fresh", False),
            "memory_current": memory.get("current", False),
            "daily_log_exists": daily_log_exists,
            "build_tracking_fresh": build_tracking_fresh
        }
        
        # Flag issues
        if not memory.get("current", False):
            self.findings.append({
                "severity": "warning",
                "category": "agent_health",
                "agent": "chad-yi",
                "issue": f"MEMORY.md stale: {memory.get('age_hours', 0):.1f} hours old"
            })
        
        if not daily_log_exists:
            self.findings.append({
                "severity": "warning",
                "category": "agent_health",
                "agent": "chad-yi",
                "issue": f"Daily log missing: memory/{today}.md"
            })
        
        return status
    
    def audit_all_agents(self):
        """Audit all agents in the system"""
        agents_dir = os.path.join(self.base_dir, "agents")
        
        agents_to_audit = ["chad-yi", "quanta", "escritor", "mensamusa", "helios"]
        
        for agent_name in agents_to_audit:
            agent_dir = os.path.join(agents_dir, agent_name)
            
            if not os.path.exists(agent_dir):
                self.agent_status[agent_name] = {
                    "name": agent_name,
                    "status": "not_created"
                }
                continue
            
            if agent_name == "chad-yi":
                self.agent_status[agent_name] = self.audit_chad_yi()
            else:
                # Generic agent audit
                service = self.audit_agent_service(agent_name)
                state = self.audit_agent_state(agent_name)
                memory = self.audit_agent_memory(agent_name)
                
                self.agent_status[agent_name] = {
                    "name": agent_name,
                    "service_running": service.get("running", False),
                    "state_fresh": state.get("fresh", False),
                    "memory_current": memory.get("current", False)
                }
                
                # Flag issues
                if not service.get("running", False) and agent_name in ["quanta", "helios"]:
                    self.findings.append({
                        "severity": "warning",
                        "category": "agent_health",
                        "agent": agent_name,
                        "issue": f"Service not running: {service.get('status', 'unknown')}"
                    })
    
    def generate_report(self):
        """Generate complete audit report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "auditor": "helios",
            "audit_id": f"audit-{datetime.now().strftime('%Y%m%d-%H%M')}",
            "summary": {
                "total_findings": len(self.findings),
                "critical": len([f for f in self.findings if f.get("severity") == "critical"]),
                "warning": len([f for f in self.findings if f.get("severity") == "warning"]),
                "agents_audited": len(self.agent_status)
            },
            "data_integrity": self.audit_data_integrity(),
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
                    "action": f"Fix {finding['category']}: {finding['issue']}"
                })
            elif finding["severity"] == "warning":
                recs.append({
                    "priority": "soon",
                    "action": f"Address {finding.get('agent', 'system')}: {finding['issue']}"
                })
        
        return recs
    
    def run_audit(self):
        """Run complete audit cycle"""
        print("Helios Audit Starting...")
        
        # 1. Data integrity
        print("  Checking data integrity...")
        self.audit_data_integrity()
        
        # 2. All agents
        print("  Auditing agents...")
        self.audit_all_agents()
        
        # 3. Generate report
        print("  Generating report...")
        report = self.generate_report()
        
        # 4. Write to outbox
        outbox_dir = os.path.join(self.base_dir, "agents", "helios", "outbox")
        os.makedirs(outbox_dir, exist_ok=True)
        
        report_file = os.path.join(outbox_dir, f"audit-{datetime.now().strftime('%Y%m%d-%H%M')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # 5. Print summary
        print(f"\nAudit Complete: {report_file}")
        print(f"Findings: {report['summary']['total_findings']}")
        print(f"  Critical: {report['summary']['critical']}")
        print(f"  Warning: {report['summary']['warning']}")
        
        return report

if __name__ == "__main__":
    auditor = HeliosAuditor()
    report = auditor.run_audit()
    
    # Exit with error if critical findings
    if report['summary']['critical'] > 0:
        exit(1)
