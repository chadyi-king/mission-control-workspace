#!/usr/bin/env python3
"""
Conflict Resolver for Git Sync
Handles merge conflicts automatically
"""

import json
import os
import shutil
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configuration
LOG_DIR = Path("/root/.openclaw/workspace/logs")
CONFLICT_DIR = Path("/root/.openclaw/workspace/sync/conflicts")
BACKUP_DIR = Path("/root/.openclaw/workspace/sync/backups")

# Setup logging
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "conflict_resolver.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("conflict_resolver")


class ConflictResolver:
    def __init__(self, repo_path="/root/.openclaw/workspace"):
        self.repo_path = Path(repo_path)
        self.conflict_dir = CONFLICT_DIR
        self.backup_dir = BACKUP_DIR
        
        # Ensure directories exist
        self.conflict_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def run_git(self, args, check=True):
        """Run a git command"""
        cmd = ["git", "-C", str(self.repo_path)] + args
        logger.debug(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, result.stdout, result.stderr
            )
        
        return result
    
    def has_conflicts(self):
        """Check if there are merge conflicts"""
        try:
            result = self.run_git(["diff", "--name-only", "--diff-filter=U"], check=False)
            return len(result.stdout.strip()) > 0
        except Exception as e:
            logger.error(f"Failed to check for conflicts: {e}")
            return False
    
    def get_conflicted_files(self):
        """Get list of files with conflicts"""
        try:
            result = self.run_git(["diff", "--name-only", "--diff-filter=U"], check=False)
            files = result.stdout.strip().split('\n')
            return [f for f in files if f]
        except Exception as e:
            logger.error(f"Failed to get conflicted files: {e}")
            return []
    
    def backup_file(self, filepath):
        """Create a backup of a file before resolving"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{filepath.name}.{timestamp}.backup"
        backup_path = self.backup_dir / backup_name
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(filepath, backup_path)
        
        logger.info(f"Backed up {filepath} to {backup_path}")
        return backup_path
    
    def resolve_conflict_keep_both(self, filepath):
        """
        Resolve conflict by keeping both versions with timestamps.
        Original file gets merged content, conflict versions saved separately.
        """
        file_path = self.repo_path / filepath
        
        if not file_path.exists():
            logger.warning(f"File does not exist: {filepath}")
            return False
        
        # Backup first
        self.backup_file(file_path)
        
        # Read the conflicted file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Extract both versions
        ours = []
        theirs = []
        current = None
        
        for line in content.split('\n'):
            if line.startswith('<<<<<<<'):
                current = 'ours'
            elif line.startswith('======='):
                current = 'theirs'
            elif line.startswith('>>>>>>>'):
                current = None
            else:
                if current == 'ours':
                    ours.append(line)
                elif current == 'theirs':
                    theirs.append(line)
                else:
                    # Common lines go to both
                    ours.append(line)
                    theirs.append(line)
        
        # Save both versions with timestamps
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        ours_path = self.conflict_dir / f"{filepath}.{timestamp}.ours"
        theirs_path = self.conflict_dir / f"{filepath}.{timestamp}.theirs"
        
        ours_path.parent.mkdir(parents=True, exist_ok=True)
        theirs_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(ours_path, 'w') as f:
            f.write('\n'.join(ours))
        
        with open(theirs_path, 'w') as f:
            f.write('\n'.join(theirs))
        
        # For messages, merge by appending (don't lose messages)
        if 'messages' in filepath or filepath.endswith('.json'):
            merged = self.merge_json_files(ours, theirs)
            with open(file_path, 'w') as f:
                f.write(merged)
        else:
            # For other files, take ours and append theirs
            merged_content = '\n'.join(ours) + '\n\n' + '='*40 + '\n' + 'MERGED FROM REMOTE:\n' + '='*40 + '\n\n' + '\n'.join(theirs)
            with open(file_path, 'w') as f:
                f.write(merged_content)
        
        # Stage the resolved file
        self.run_git(["add", filepath])
        
        logger.info(f"Resolved conflict in {filepath} - both versions saved")
        return True
    
    def merge_json_files(self, ours_lines, theirs_lines):
        """Merge JSON files (like messages) without losing data"""
        try:
            ours_content = '\n'.join(ours_lines)
            theirs_content = '\n'.join(theirs_lines)
            
            # Try to parse as JSON array
            ours_data = json.loads(ours_content) if ours_content.strip() else []
            theirs_data = json.loads(theirs_content) if theirs_content.strip() else []
            
            # Ensure both are lists
            if not isinstance(ours_data, list):
                ours_data = [ours_data] if ours_data else []
            if not isinstance(theirs_data, list):
                theirs_data = [theirs_data] if theirs_data else []
            
            # Merge by ID or content to avoid duplicates
            seen_ids = set()
            merged = []
            
            for item in ours_data + theirs_data:
                item_id = item.get('id') if isinstance(item, dict) else str(item)
                if item_id not in seen_ids:
                    seen_ids.add(item_id)
                    merged.append(item)
            
            return json.dumps(merged, indent=2)
            
        except json.JSONDecodeError:
            # If not valid JSON, just concatenate
            return '\n'.join(ours_lines) + '\n' + '\n'.join(theirs_lines)
    
    def resolve_all_conflicts(self):
        """Resolve all conflicts in the repository"""
        if not self.has_conflicts():
            logger.info("No conflicts to resolve")
            return True
        
        conflicted_files = self.get_conflicted_files()
        logger.info(f"Found {len(conflicted_files)} conflicted files")
        
        resolved = []
        failed = []
        
        for filepath in conflicted_files:
            try:
                if self.resolve_conflict_keep_both(filepath):
                    resolved.append(filepath)
                else:
                    failed.append(filepath)
            except Exception as e:
                logger.error(f"Failed to resolve {filepath}: {e}")
                failed.append(filepath)
        
        # Create a merge commit if all resolved
        if not failed and resolved:
            try:
                self.run_git(["commit", "-m", f"Auto-resolved conflicts: {', '.join(resolved)}"])
                logger.info("Created merge commit for resolved conflicts")
            except Exception as e:
                logger.error(f"Failed to create merge commit: {e}")
        
        return len(failed) == 0
    
    def abort_merge(self):
        """Abort the current merge"""
        try:
            self.run_git(["merge", "--abort"])
            logger.info("Merge aborted")
            return True
        except Exception as e:
            logger.error(f"Failed to abort merge: {e}")
            return False
    
    def get_conflict_report(self):
        """Generate a report of current conflicts"""
        if not self.has_conflicts():
            return {"status": "clean", "conflicts": []}
        
        conflicted_files = self.get_conflicted_files()
        
        return {
            "status": "conflicted",
            "conflicts": conflicted_files,
            "count": len(conflicted_files),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Conflict Resolver")
    parser.add_argument("--check", action="store_true",
                       help="Check for conflicts only")
    parser.add_argument("--resolve", action="store_true",
                       help="Resolve all conflicts")
    parser.add_argument("--abort", action="store_true",
                       help="Abort current merge")
    parser.add_argument("--report", action="store_true",
                       help="Generate conflict report")
    
    args = parser.parse_args()
    
    resolver = ConflictResolver()
    
    if args.check:
        has_conflicts = resolver.has_conflicts()
        print(json.dumps({"has_conflicts": has_conflicts}, indent=2))
        return 1 if has_conflicts else 0
    
    elif args.resolve:
        success = resolver.resolve_all_conflicts()
        return 0 if success else 1
    
    elif args.abort:
        success = resolver.abort_merge()
        return 0 if success else 1
    
    elif args.report:
        report = resolver.get_conflict_report()
        print(json.dumps(report, indent=2))
        return 0
    
    else:
        # Default: check and resolve if needed
        if resolver.has_conflicts():
            print("Conflicts detected, resolving...")
            success = resolver.resolve_all_conflicts()
            return 0 if success else 1
        else:
            print("No conflicts")
            return 0


if __name__ == "__main__":
    exit(main())
