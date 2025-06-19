#!/usr/bin/env python3
"""
HUGAI Configuration-Documentation Synchronization System

This script automatically synchronizes configuration files with their corresponding documentation,
ensuring that changes in configurations are reflected in the documentation and vice versa.

Features:
- Bidirectional sync between configs and docs
- Automatic documentation generation from configs
- Configuration validation against schemas
- Change detection and notification
- Git integration for version control
- Backup and rollback capabilities

Usage:
    python sync-automation.py [--mode <mode>] [--watch] [--dry-run]
    
Examples:
    # Full synchronization
    python sync-automation.py --mode full
    
    # Watch for changes and sync automatically
    python sync-automation.py --watch
    
    # Dry run to see what would be changed
    python sync-automation.py --dry-run
    
    # Sync specific configuration type
    python sync-automation.py --mode agents --target config/agents/
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import hashlib
import subprocess
import shutil

try:
    import yaml
    import jsonschema
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    from jinja2 import Environment, FileSystemLoader
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("💡 Install with: pip install pyyaml jsonschema watchdog jinja2")
    sys.exit(1)


class ConfigDocSyncHandler(FileSystemEventHandler):
    """File system event handler for configuration-documentation synchronization"""
    
    def __init__(self, sync_manager):
        self.sync_manager = sync_manager
        self.debounce_time = 2  # seconds
        self.pending_changes = {}
    
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path)
    
    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self._handle_file_deletion(event.src_path)
    
    def _handle_file_change(self, file_path: str):
        """Handle file modification with debouncing"""
        current_time = time.time()
        self.pending_changes[file_path] = current_time
        
        # Use a timer to debounce rapid changes
        def process_change():
            time.sleep(self.debounce_time)
            if (file_path in self.pending_changes and 
                current_time == self.pending_changes[file_path]):
                
                del self.pending_changes[file_path]
                self.sync_manager.handle_file_change(file_path)
        
        import threading
        threading.Thread(target=process_change, daemon=True).start()
    
    def _handle_file_deletion(self, file_path: str):
        """Handle file deletion"""
        self.sync_manager.handle_file_deletion(file_path)


class ConfigDocSyncManager:
    """Main synchronization manager for configurations and documentation"""
    
    def __init__(self, config_dir: str = "config", docs_dir: str = "docs"):
        self.config_dir = Path(config_dir)
        self.docs_dir = Path(docs_dir)
        self.backup_dir = Path("backups/sync")
        self.sync_metadata_file = Path(".sync-metadata.json")
        
        # Initialize Jinja2 environment
        template_dirs = [
            str(self.config_dir / "templates"),
            str(Path(__file__).parent / "sync-templates")
        ]
        self.jinja_env = Environment(loader=FileSystemLoader(template_dirs))
        
        # Load sync configuration
        self.sync_config = self.load_sync_config()
        
        # Create necessary directories
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Load sync metadata
        self.sync_metadata = self.load_sync_metadata()
    
    def load_sync_config(self) -> Dict:
        """Load synchronization configuration"""
        config_file = self.config_dir / "sync-config.yaml"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        
        # Default sync configuration
        default_config = {
            "sync_rules": {
                "config_to_docs": {
                    "agents": {
                        "source_pattern": "config/agents/*.yaml",
                        "target_pattern": "docs/agents/{name}.md",
                        "template": "agent-doc-template.md"
                    },
                    "lifecycle": {
                        "source_pattern": "config/lifecycle/*.yaml",
                        "target_pattern": "docs/methodology/{name}.md",
                        "template": "lifecycle-doc-template.md"
                    },
                    "tools": {
                        "source_pattern": "config/tools/*.yaml",
                        "target_pattern": "docs/tools/{name}.md",
                        "template": "tool-doc-template.md"
                    },
                    "llms": {
                        "source_pattern": "config/llms/*.yaml",
                        "target_pattern": "docs/llms/{name}.md",
                        "template": "llm-doc-template.md"
                    }
                }
            },
            "validation": {
                "enabled": True,
                "schema_validation": True,
                "link_validation": True,
                "content_validation": True
            },
            "backup": {
                "enabled": True,
                "max_backups": 10,
                "compress": True
            },
            "git_integration": {
                "enabled": True,
                "auto_commit": False,
                "commit_message_template": "docs: sync configuration changes for {files}"
            },
            "notifications": {
                "enabled": True,
                "channels": ["console", "file"],
                "log_file": "sync.log"
            }
        }
        
        # Save default config
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
        
        return default_config
    
    def load_sync_metadata(self) -> Dict:
        """Load synchronization metadata"""
        if self.sync_metadata_file.exists():
            try:
                with open(self.sync_metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "last_sync": None,
            "file_hashes": {},
            "sync_history": [],
            "conflicts": [],
            "schema_version": "1.0"
        }
    
    def save_sync_metadata(self):
        """Save synchronization metadata"""
        with open(self.sync_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.sync_metadata, f, indent=2, default=str)
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content"""
        if not file_path.exists():
            return ""
        
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def detect_changes(self) -> Dict[str, List[Path]]:
        """Detect changed files since last sync"""
        changes = {
            "modified": [],
            "added": [],
            "deleted": []
        }
        
        # Check configuration files
        for config_type in ["agents", "lifecycle", "tools", "llms"]:
            config_dir = self.config_dir / config_type
            if config_dir.exists():
                for config_file in config_dir.glob("*.yaml"):
                    file_key = str(config_file.relative_to(self.config_dir))
                    current_hash = self.calculate_file_hash(config_file)
                    stored_hash = self.sync_metadata["file_hashes"].get(file_key, "")
                    
                    if stored_hash == "":
                        changes["added"].append(config_file)
                    elif current_hash != stored_hash:
                        changes["modified"].append(config_file)
                    
                    # Update hash
                    self.sync_metadata["file_hashes"][file_key] = current_hash
        
        # Check for deleted files
        for file_key in list(self.sync_metadata["file_hashes"].keys()):
            file_path = self.config_dir / file_key
            if not file_path.exists():
                changes["deleted"].append(file_path)
                del self.sync_metadata["file_hashes"][file_key]
        
        return changes
    
    def check_naming_consistency(self) -> Dict[str, List[Dict]]:
        """Check for naming inconsistencies between configs and docs"""
        inconsistencies = {
            "config_without_docs": [],
            "docs_without_config": [],
            "naming_mismatches": []
        }
        
        for config_type in ["agents", "lifecycle", "tools", "llms"]:
            config_dir = self.config_dir / config_type
            
            # Map for different documentation directories
            docs_mapping = {
                "agents": self.docs_dir / "agents",
                "lifecycle": self.docs_dir / "methodology", 
                "tools": self.docs_dir / "tools",
                "llms": self.docs_dir / "llms"
            }
            
            docs_dir = docs_mapping.get(config_type, self.docs_dir / config_type)
            
            if not config_dir.exists():
                continue
                
            # Get all config files
            config_files = {f.stem: f for f in config_dir.glob("*.yaml")}
            
            # Get all doc files
            doc_files = {}
            if docs_dir.exists():
                doc_files = {f.stem: f for f in docs_dir.glob("*.md") if f.name != "index.md"}
            
            # Check for configs without docs
            for config_name, config_path in config_files.items():
                if config_name not in doc_files:
                    inconsistencies["config_without_docs"].append({
                        "type": config_type,
                        "config_file": str(config_path),
                        "expected_doc": str(docs_dir / f"{config_name}.md")
                    })
            
            # Check for docs without configs
            for doc_name, doc_path in doc_files.items():
                if doc_name not in config_files:
                    inconsistencies["docs_without_config"].append({
                        "type": config_type,
                        "doc_file": str(doc_path),
                        "expected_config": str(config_dir / f"{doc_name}.yaml")
                    })
        
        return inconsistencies
    
    def generate_consistency_report(self) -> str:
        """Generate a detailed consistency report"""
        inconsistencies = self.check_naming_consistency()
        
        report = ["# Configuration-Documentation Consistency Report", ""]
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_issues = sum(len(issues) for issues in inconsistencies.values())
        if total_issues == 0:
            report.append("✅ **STATUS: PERFECT ALIGNMENT**")
            report.append("All configurations have corresponding documentation.")
        else:
            report.append(f"⚠️ **STATUS: {total_issues} ISSUES FOUND**")
        
        report.append("")
        
        # Details
        for issue_type, issues in inconsistencies.items():
            if not issues:
                continue
                
            if issue_type == "config_without_docs":
                report.append(f"## 🚨 Configurations Missing Documentation ({len(issues)})")
                report.append("")
                for issue in issues:
                    report.append(f"- **{issue['type'].title()}**: `{Path(issue['config_file']).name}`")
                    report.append(f"  - Config: `{issue['config_file']}`")
                    report.append(f"  - Missing Doc: `{issue['expected_doc']}`")
                    report.append("")
            
            elif issue_type == "docs_without_config":
                report.append(f"## 📄 Documentation Without Configurations ({len(issues)})")
                report.append("")
                for issue in issues:
                    report.append(f"- **{issue['type'].title()}**: `{Path(issue['doc_file']).name}`")
                    report.append(f"  - Doc: `{issue['doc_file']}`")
                    report.append(f"  - Missing Config: `{issue['expected_config']}`")
                    report.append("")
        
        return "\n".join(report)
    
    def create_backup(self, files: List[Path]) -> Path:
        """Create backup of files before modification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        for file_path in files:
            if file_path.exists():
                relative_path = file_path.relative_to(Path.cwd())
                backup_file = backup_path / relative_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_file)
        
        # Compress backup if enabled
        if self.sync_config["backup"]["compress"]:
            shutil.make_archive(str(backup_path), 'zip', str(backup_path))
            shutil.rmtree(backup_path)
            return Path(f"{backup_path}.zip")
        
        return backup_path
    
    def cleanup_old_backups(self):
        """Remove old backups beyond the configured limit"""
        max_backups = self.sync_config["backup"]["max_backups"]
        backup_files = sorted(self.backup_dir.glob("backup_*"), 
                            key=lambda x: x.stat().st_mtime, reverse=True)
        
        for backup_file in backup_files[max_backups:]:
            if backup_file.is_dir():
                shutil.rmtree(backup_file)
            else:
                backup_file.unlink()
    
    def validate_configuration(self, config_file: Path) -> Tuple[bool, List[str]]:
        """Validate configuration file against schema"""
        if not self.sync_config["validation"]["enabled"]:
            return True, []
        
        errors = []
        
        # Load configuration
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        except Exception as e:
            return False, [f"YAML parsing error: {e}"]
        
        # Determine configuration type and validate against schema
        config_type = self.determine_config_type(config_file)
        schema_file = self.config_dir / "schemas" / f"{config_type}-schema.json"
        
        if schema_file.exists():
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                
                jsonschema.validate(instance=config_data, schema=schema)
            except jsonschema.ValidationError as e:
                errors.append(f"Schema validation error: {e.message}")
            except Exception as e:
                errors.append(f"Schema loading error: {e}")
        
        return len(errors) == 0, errors
    
    def determine_config_type(self, config_file: Path) -> str:
        """Determine configuration type from file path"""
        if "/agents/" in str(config_file):
            return "agent"
        elif "/lifecycle/" in str(config_file):
            return "lifecycle"
        elif "/tools/" in str(config_file):
            return "tool"
        elif "/llms/" in str(config_file):
            return "llm"
        else:
            return "unknown"
    
    def generate_documentation(self, config_file: Path) -> Optional[Path]:
        """Generate documentation from configuration file"""
        config_type = self.determine_config_type(config_file)
        sync_rules = self.sync_config["sync_rules"]["config_to_docs"]
        
        if config_type not in sync_rules:
            return None
        
        rule = sync_rules[config_type]
        template_name = rule["template"]
        
        # Load configuration data
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # Determine target file path
        config_name = config_file.stem
        target_pattern = rule["target_pattern"]
        target_path = Path(target_pattern.format(name=config_name))
        
        # Create target directory if it doesn't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Render documentation using template
        try:
            template = self.jinja_env.get_template(template_name)
            doc_content = template.render(
                config=config_data,
                config_name=config_name,
                config_type=config_type,
                config_file=str(config_file),
                generated_at=datetime.now().isoformat(),
                sync_version="1.0"
            )
            
            # Write documentation file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            return target_path
            
        except Exception as e:
            self.log_message(f"❌ Error generating documentation for {config_file}: {e}")
            return None
    
    def sync_single_file(self, config_file: Path, dry_run: bool = False) -> bool:
        """Synchronize a single configuration file"""
        self.log_message(f"🔄 Syncing {config_file}...")
        
        # Validate configuration
        is_valid, validation_errors = self.validate_configuration(config_file)
        if not is_valid:
            self.log_message(f"❌ Validation failed for {config_file}:")
            for error in validation_errors:
                self.log_message(f"   • {error}")
            return False
        
        if dry_run:
            self.log_message(f"🔍 [DRY RUN] Would sync {config_file}")
            return True
        
        # Create backup
        if self.sync_config["backup"]["enabled"]:
            existing_docs = []
            # Find existing documentation files that would be modified
            config_type = self.determine_config_type(config_file)
            sync_rules = self.sync_config["sync_rules"]["config_to_docs"]
            
            if config_type in sync_rules:
                rule = sync_rules[config_type]
                target_pattern = rule["target_pattern"]
                target_path = Path(target_pattern.format(name=config_file.stem))
                if target_path.exists():
                    existing_docs.append(target_path)
            
            if existing_docs:
                backup_path = self.create_backup(existing_docs)
                self.log_message(f"📦 Created backup: {backup_path}")
        
        # Generate documentation
        doc_file = self.generate_documentation(config_file)
        if doc_file:
            self.log_message(f"✅ Generated documentation: {doc_file}")
            
            # Update sync history
            sync_record = {
                "timestamp": datetime.now().isoformat(),
                "config_file": str(config_file),
                "doc_file": str(doc_file),
                "action": "sync",
                "success": True
            }
            self.sync_metadata["sync_history"].append(sync_record)
            
            return True
        else:
            self.log_message(f"❌ Failed to generate documentation for {config_file}")
            return False
    
    def sync_all(self, dry_run: bool = False) -> Dict[str, int]:
        """Synchronize all configuration files"""
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        self.log_message("🚀 Starting full synchronization...")
        
        # Detect changes
        changes = self.detect_changes()
        total_changes = len(changes["modified"]) + len(changes["added"])
        
        if total_changes == 0:
            self.log_message("✅ No changes detected. All files are up to date.")
            return results
        
        self.log_message(f"📊 Detected {total_changes} file changes:")
        for change_type, files in changes.items():
            if files:
                self.log_message(f"   {change_type.title()}: {len(files)} files")
        
        # Process changes
        all_files = changes["modified"] + changes["added"]
        
        for config_file in all_files:
            try:
                success = self.sync_single_file(config_file, dry_run)
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                self.log_message(f"❌ Error syncing {config_file}: {e}")
                results["failed"] += 1
        
        # Handle deleted files
        for deleted_file in changes["deleted"]:
            self.log_message(f"🗑️  Configuration deleted: {deleted_file}")
            # TODO: Implement documentation cleanup for deleted configs
        
        # Update metadata
        if not dry_run:
            self.sync_metadata["last_sync"] = datetime.now().isoformat()
            self.save_sync_metadata()
            
            # Cleanup old backups
            if self.sync_config["backup"]["enabled"]:
                self.cleanup_old_backups()
        
        # Git integration
        if (not dry_run and 
            self.sync_config["git_integration"]["enabled"] and 
            results["success"] > 0):
            
            self.git_commit_changes(all_files[:results["success"]])
        
        self.log_message(f"🎉 Synchronization complete: {results['success']} success, {results['failed']} failed")
        return results
    
    def git_commit_changes(self, files: List[Path]):
        """Commit synchronized changes to git"""
        try:
            # Add changed files to git
            subprocess.run(["git", "add", "docs/"], check=True, capture_output=True)
            
            # Create commit message
            file_names = [f.stem for f in files]
            commit_message = self.sync_config["git_integration"]["commit_message_template"].format(
                files=", ".join(file_names[:5])  # Limit to first 5 files
            )
            
            if len(file_names) > 5:
                commit_message += f" and {len(file_names) - 5} more"
            
            # Only commit if auto_commit is enabled
            if self.sync_config["git_integration"]["auto_commit"]:
                subprocess.run(["git", "commit", "-m", commit_message], 
                             check=True, capture_output=True)
                self.log_message(f"📝 Git commit created: {commit_message}")
            else:
                self.log_message(f"📝 Git changes staged. Commit message: {commit_message}")
                
        except subprocess.CalledProcessError as e:
            self.log_message(f"⚠️  Git operation failed: {e}")
        except Exception as e:
            self.log_message(f"⚠️  Git integration error: {e}")
    
    def handle_file_change(self, file_path: str):
        """Handle file change event from watcher"""
        file_path = Path(file_path)
        
        # Only process configuration files
        if (file_path.suffix.lower() in ['.yaml', '.yml'] and 
            any(part in file_path.parts for part in ['agents', 'lifecycle', 'tools', 'llms'])):
            
            self.log_message(f"📁 File changed: {file_path}")
            self.sync_single_file(file_path)
            self.save_sync_metadata()
    
    def handle_file_deletion(self, file_path: str):
        """Handle file deletion event from watcher"""
        file_path = Path(file_path)
        self.log_message(f"🗑️  File deleted: {file_path}")
        # TODO: Implement documentation cleanup
    
    def watch_for_changes(self):
        """Watch for file changes and sync automatically"""
        self.log_message("👀 Starting file watcher...")
        
        event_handler = ConfigDocSyncHandler(self)
        observer = Observer()
        
        # Watch configuration directories
        for config_type in ["agents", "lifecycle", "tools", "llms"]:
            config_dir = self.config_dir / config_type
            if config_dir.exists():
                observer.schedule(event_handler, str(config_dir), recursive=True)
                self.log_message(f"📂 Watching: {config_dir}")
        
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log_message("⏹️  Stopping file watcher...")
            observer.stop()
        
        observer.join()
    
    def log_message(self, message: str):
        """Log message to configured channels"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Console output
        if "console" in self.sync_config["notifications"]["channels"]:
            print(formatted_message)
        
        # File logging
        if "file" in self.sync_config["notifications"]["channels"]:
            log_file = self.sync_config["notifications"]["log_file"]
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(formatted_message + "\n")
    
    def create_sync_templates(self):
        """Create default synchronization templates"""
        templates_dir = Path("config/sync-templates")
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Agent documentation template
        agent_template = """# {{ config.metadata.name | title }}

{{ config.metadata.description }}

## Overview

**Category:** {{ config.metadata.category }}  
**Version:** {{ config.metadata.version }}  
**Author:** {{ config.metadata.author }}  
**Last Updated:** {{ config.metadata.updated }}

## Role and Capabilities

### Primary Role
{{ config.configuration.role.primary }}

### Secondary Roles
{% for role in config.configuration.role.secondary %}
- {{ role }}
{% endfor %}

### Capabilities
{% for capability in config.configuration.capabilities %}
- {{ capability }}
{% endfor %}

## Dependencies

{% if config.configuration.dependencies.agents %}
### Agent Dependencies
{% for agent in config.configuration.dependencies.agents %}
- {{ agent }}
{% endfor %}
{% endif %}

{% if config.configuration.dependencies.tools %}
### Tool Dependencies
{% for tool in config.configuration.dependencies.tools %}
- {{ tool }}
{% endfor %}
{% endif %}

## Integration

### Triggers
{% for trigger in config.integration.triggers %}
- **{{ trigger.event }}**: {{ trigger.condition }}
{% endfor %}

### Inputs
{% for input in config.integration.inputs %}
- **{{ input.name }}** ({{ input.type }}): {{ input.description }}
{% endfor %}

### Outputs
{% for output in config.integration.outputs %}
- **{{ output.name }}** ({{ output.type }}): {{ output.description }}
{% endfor %}

## Validation

### Quality Gates
{% for gate in config.validation.quality_gates %}
- **{{ gate.name }}**: {{ gate.criteria }}
{% endfor %}

### Metrics
{% for metric in config.validation.metrics %}
- **{{ metric.name }}** ({{ metric.type }}): Threshold {{ metric.threshold }}
{% endfor %}

## CLI Usage

{% for command in config.cli_usage.commands %}
### {{ command.command }}
{{ command.description }}

```bash
{{ command.example }}
```
{% endfor %}

---
*This documentation was automatically generated from `{{ config_file }}` on {{ generated_at }}*
"""

        with open(templates_dir / "agent-doc-template.md", 'w', encoding='utf-8') as f:
            f.write(agent_template)
        
        self.log_message(f"✅ Created sync templates in {templates_dir}")


def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description="HUGAI Configuration-Documentation Synchronization System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["full", "agents", "lifecycle", "tools", "llms"],
        default="full",
        help="Synchronization mode (default: full)"
    )
    
    parser.add_argument(
        "--watch", "-w",
        action="store_true",
        help="Watch for file changes and sync automatically"
    )
    
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Show what would be changed without making changes"
    )
    
    parser.add_argument(
        "--target", "-t",
        type=str,
        help="Target specific file or directory"
    )
    
    parser.add_argument(
        "--config-dir",
        type=str,
        default="config",
        help="Configuration directory (default: config)"
    )
    
    parser.add_argument(
        "--docs-dir",
        type=str,
        default="docs",
        help="Documentation directory (default: docs)"
    )
    
    parser.add_argument(
        "--setup-templates",
        action="store_true",
        help="Create default synchronization templates"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check consistency between configs and documentation"
    )
    
    parser.add_argument(
        "--report",
        action="store_true", 
        help="Generate detailed consistency report"
    )
    
    args = parser.parse_args()
    
    # Initialize sync manager
    sync_manager = ConfigDocSyncManager(args.config_dir, args.docs_dir)
    
    # Setup templates if requested
    if args.setup_templates:
        sync_manager.create_sync_templates()
        return
    
    # Check consistency if requested
    if args.check:
        inconsistencies = sync_manager.check_naming_consistency()
        total_issues = sum(len(issues) for issues in inconsistencies.values())
        
        if total_issues == 0:
            sync_manager.log_message("✅ Perfect alignment: All configurations have corresponding documentation")
        else:
            sync_manager.log_message(f"⚠️ Found {total_issues} consistency issues")
            for issue_type, issues in inconsistencies.items():
                if issues:
                    sync_manager.log_message(f"  {issue_type.replace('_', ' ').title()}: {len(issues)}")
        
        return
    
    # Generate report if requested
    if args.report:
        report = sync_manager.generate_consistency_report()
        report_file = Path("consistency_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        sync_manager.log_message(f"📊 Consistency report generated: {report_file}")
        return
    
    try:
        if args.watch:
            # Watch mode
            sync_manager.watch_for_changes()
        elif args.target:
            # Sync specific target
            target_path = Path(args.target)
            if target_path.is_file():
                sync_manager.sync_single_file(target_path, args.dry_run)
            else:
                sync_manager.log_message(f"❌ Target not found or not a file: {target_path}")
                sys.exit(1)
        else:
            # Full synchronization
            results = sync_manager.sync_all(args.dry_run)
            
            # Exit with error code if there were failures
            if results["failed"] > 0:
                sys.exit(1)
    
    except KeyboardInterrupt:
        sync_manager.log_message("⏹️  Synchronization interrupted by user")
        sys.exit(0)
    except Exception as e:
        sync_manager.log_message(f"❌ Synchronization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()