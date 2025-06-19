#!/usr/bin/env python3
"""
HUGAI Configuration Validator

This script validates all HUGAI configuration files against their JSON schemas.
It provides detailed error reporting and supports both individual file validation
and bulk validation of configuration directories.

Usage:
    python validate-config.py [--file <path>] [--directory <path>] [--schema <path>]
    
Examples:
    # Validate all configurations
    python validate-config.py
    
    # Validate specific file
    python validate-config.py --file config/agents/router-agent.yaml
    
    # Validate specific directory
    python validate-config.py --directory config/agents
    
    # Use custom schema
    python validate-config.py --file config.yaml --schema custom-schema.json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import jsonschema
    import yaml
    from jsonschema import validate, ValidationError, SchemaError
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("💡 Install with: pip install jsonschema pyyaml")
    sys.exit(1)


class ConfigValidator:
    """HUGAI Configuration Validator"""
    
    def __init__(self, config_dir: str = "config", schemas_dir: str = "config/schemas"):
        self.config_dir = Path(config_dir)
        self.schemas_dir = Path(schemas_dir)
        self.schemas = {}
        self.load_schemas()
    
    def load_schemas(self) -> None:
        """Load all JSON schemas from the schemas directory"""
        if not self.schemas_dir.exists():
            print(f"❌ Schemas directory not found: {self.schemas_dir}")
            sys.exit(1)
        
        schema_files = {
            'agent': 'agent-schema.json',
            'lifecycle': 'lifecycle-schema.json',
            'tool': 'tool-schema.json',
            'llm': 'llm-schema.json'
        }
        
        for schema_type, filename in schema_files.items():
            schema_path = self.schemas_dir / filename
            if schema_path.exists():
                try:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        self.schemas[schema_type] = json.load(f)
                    print(f"✅ Loaded {schema_type} schema")
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON in schema {filename}: {e}")
                    sys.exit(1)
            else:
                print(f"⚠️  Schema not found: {schema_path}")
    
    def detect_config_type(self, config_path: Path) -> Optional[str]:
        """Detect configuration type based on file path and content"""
        path_str = str(config_path)
        
        # Path-based detection
        if '/agents/' in path_str:
            return 'agent'
        elif '/lifecycle/' in path_str:
            return 'lifecycle'
        elif '/tools/' in path_str:
            return 'tool'
        elif '/llms/' in path_str:
            return 'llm'
        
        # Content-based detection
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if isinstance(content, dict) and 'metadata' in content:
                metadata = content['metadata']
                if 'category' in metadata:
                    if metadata['category'] in ['core', 'specialized', 'utility', 'governance']:
                        return 'agent'
                    elif metadata['category'] in ['development', 'testing', 'deployment', 'monitoring', 'security', 'collaboration']:
                        return 'tool'
                elif 'phase' in metadata:
                    return 'lifecycle'
                elif 'providers' in content.get('configuration', {}):
                    return 'llm'
        
        except Exception:
            pass
        
        return None
    
    def load_yaml_config(self, config_path: Path) -> Optional[Dict]:
        """Load and parse YAML configuration file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"❌ Invalid YAML in {config_path}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error reading {config_path}: {e}")
            return None
    
    def validate_config(self, config_path: Path, schema_type: Optional[str] = None) -> Tuple[bool, List[str]]:
        """Validate a single configuration file"""
        errors = []
        
        # Load configuration
        config_data = self.load_yaml_config(config_path)
        if config_data is None:
            return False, ["Failed to load configuration file"]
        
        # Detect schema type if not provided
        if schema_type is None:
            schema_type = self.detect_config_type(config_path)
        
        if schema_type is None:
            return False, ["Could not determine configuration type"]
        
        if schema_type not in self.schemas:
            return False, [f"No schema available for type: {schema_type}"]
        
        # Validate against schema
        try:
            validate(instance=config_data, schema=self.schemas[schema_type])
            return True, []
        except ValidationError as e:
            error_msg = f"Validation error at {e.json_path}: {e.message}"
            errors.append(error_msg)
            return False, errors
        except SchemaError as e:
            errors.append(f"Schema error: {e.message}")
            return False, errors
    
    def validate_directory(self, directory: Path) -> Dict[str, Tuple[bool, List[str]]]:
        """Validate all YAML files in a directory"""
        results = {}
        
        if not directory.exists():
            return {str(directory): (False, ["Directory does not exist"])}
        
        yaml_files = list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))
        
        for config_file in yaml_files:
            is_valid, errors = self.validate_config(config_file)
            results[str(config_file)] = (is_valid, errors)
        
        return results
    
    def validate_all(self) -> Dict[str, Tuple[bool, List[str]]]:
        """Validate all configuration files in the project"""
        results = {}
        
        # Define directories to validate
        directories = [
            self.config_dir / "agents",
            self.config_dir / "lifecycle", 
            self.config_dir / "tools",
            self.config_dir / "llms"
        ]
        
        for directory in directories:
            if directory.exists():
                dir_results = self.validate_directory(directory)
                results.update(dir_results)
        
        return results
    
    def print_results(self, results: Dict[str, Tuple[bool, List[str]]]) -> None:
        """Print validation results in a formatted way"""
        total_files = len(results)
        valid_files = sum(1 for is_valid, _ in results.values() if is_valid)
        invalid_files = total_files - valid_files
        
        print(f"\n📊 Validation Summary:")
        print(f"   Total files: {total_files}")
        print(f"   ✅ Valid: {valid_files}")
        print(f"   ❌ Invalid: {invalid_files}")
        
        if invalid_files > 0:
            print(f"\n❌ Validation Errors:")
            for file_path, (is_valid, errors) in results.items():
                if not is_valid:
                    print(f"\n📄 {file_path}:")
                    for error in errors:
                        print(f"   • {error}")
        
        if valid_files > 0:
            print(f"\n✅ Valid Files:")
            for file_path, (is_valid, _) in results.items():
                if is_valid:
                    print(f"   • {file_path}")


def main():
    """Main function to handle command line arguments and run validation"""
    parser = argparse.ArgumentParser(
        description="Validate HUGAI configuration files against JSON schemas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Validate a specific configuration file"
    )
    
    parser.add_argument(
        "--directory", "-d", 
        type=str,
        help="Validate all YAML files in a specific directory"
    )
    
    parser.add_argument(
        "--schema", "-s",
        type=str,
        help="Use a specific schema file for validation"
    )
    
    parser.add_argument(
        "--config-dir",
        type=str,
        default="config",
        help="Configuration directory (default: config)"
    )
    
    parser.add_argument(
        "--schemas-dir",
        type=str, 
        default="config/schemas",
        help="Schemas directory (default: config/schemas)"
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = ConfigValidator(args.config_dir, args.schemas_dir)
    
    if not validator.schemas:
        print("❌ No schemas loaded. Cannot proceed with validation.")
        sys.exit(1)
    
    # Run validation based on arguments
    results = {}
    
    if args.file:
        # Validate single file
        file_path = Path(args.file)
        schema_type = None
        
        if args.schema:
            # Load custom schema
            try:
                with open(args.schema, 'r', encoding='utf-8') as f:
                    custom_schema = json.load(f)
                validator.schemas['custom'] = custom_schema
                schema_type = 'custom'
            except Exception as e:
                print(f"❌ Error loading custom schema: {e}")
                sys.exit(1)
        
        is_valid, errors = validator.validate_config(file_path, schema_type)
        results[str(file_path)] = (is_valid, errors)
        
    elif args.directory:
        # Validate directory
        directory = Path(args.directory)
        results = validator.validate_directory(directory)
        
    else:
        # Validate all configurations
        results = validator.validate_all()
    
    # Print results
    validator.print_results(results)
    
    # Exit with error code if any files are invalid
    if any(not is_valid for is_valid, _ in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()