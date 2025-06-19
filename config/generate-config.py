#!/usr/bin/env python3
"""
HUGAI Configuration Generator

This script generates configuration files from templates using the Jinja2 templating engine.
It supports creating new configurations based on predefined templates and custom parameters.

Usage:
    python generate-config.py --type <type> --name <name> [--template <template>] [--params <params>]
    
Examples:
    # Generate agent configuration
    python generate-config.py --type agent --name security-scanner --params security-agent-params.yaml
    
    # Generate lifecycle configuration
    python generate-config.py --type lifecycle --name testing --params testing-phase-params.json
    
    # Generate tool configuration with custom template
    python generate-config.py --type tool --name custom-tool --template custom-tool-template.yaml
    
    # Interactive mode
    python generate-config.py --interactive
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("💡 Install with: pip install jinja2 pyyaml")
    sys.exit(1)


class ConfigGenerator:
    """HUGAI Configuration Generator"""
    
    def __init__(self, templates_dir: str = "config/templates", output_dir: str = "config"):
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['to_yaml'] = self._to_yaml
        self.env.filters['current_date'] = self._current_date
        
        # Verify templates directory exists
        if not self.templates_dir.exists():
            print(f"❌ Templates directory not found: {self.templates_dir}")
            sys.exit(1)
    
    def _to_yaml(self, value: Any) -> str:
        """Convert value to YAML string"""
        if value is None:
            return ""
        return yaml.dump(value, default_flow_style=False, sort_keys=False).strip()
    
    def _current_date(self, value: Any = None) -> str:
        """Get current date in YYYY-MM-DD format"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_available_templates(self) -> Dict[str, list]:
        """Get list of available templates by type"""
        templates = {
            'agent': [],
            'lifecycle': [],
            'tool': [],
            'llm': [],
            'custom': []
        }
        
        for template_file in self.templates_dir.glob("*.yaml"):
            name = template_file.stem
            if name.endswith('-template'):
                template_type = name.replace('-template', '')
                if template_type in templates:
                    templates[template_type].append(name)
                else:
                    templates['custom'].append(name)
        
        return templates
    
    def load_parameters(self, params_file: Path) -> Dict[str, Any]:
        """Load parameters from file"""
        if not params_file.exists():
            print(f"❌ Parameters file not found: {params_file}")
            return {}
        
        try:
            with open(params_file, 'r', encoding='utf-8') as f:
                if params_file.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"❌ Error loading parameters from {params_file}: {e}")
            return {}
    
    def generate_config(self, 
                       config_type: str, 
                       name: str, 
                       template_name: Optional[str] = None,
                       parameters: Optional[Dict[str, Any]] = None,
                       output_file: Optional[Path] = None) -> bool:
        """Generate configuration file from template"""
        
        # Determine template name
        if template_name is None:
            template_name = f"{config_type}-template.yaml"
        
        # Check if template exists
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            print(f"❌ Template not found: {template_path}")
            return False
        
        # Load template
        try:
            template = self.env.get_template(template_name)
        except Exception as e:
            print(f"❌ Error loading template {template_name}: {e}")
            return False
        
        # Prepare parameters
        if parameters is None:
            parameters = {}
        
        # Add default parameters
        default_params = {
            'name': name,
            'current_date': datetime.now().strftime("%Y-%m-%d"),
            'component_type': config_type
        }
        
        # Merge parameters (user params override defaults)
        render_params = {**default_params, **parameters}
        
        # Render template
        try:
            rendered_content = template.render(**render_params)
        except Exception as e:
            print(f"❌ Error rendering template: {e}")
            return False
        
        # Determine output file
        if output_file is None:
            output_subdir = self.output_dir / f"{config_type}s"
            output_subdir.mkdir(parents=True, exist_ok=True)
            output_file = output_subdir / f"{name}.yaml"
        
        # Write output file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered_content)
            print(f"✅ Generated configuration: {output_file}")
            return True
        except Exception as e:
            print(f"❌ Error writing output file {output_file}: {e}")
            return False
    
    def interactive_mode(self):
        """Interactive configuration generation"""
        print("🔧 HUGAI Configuration Generator - Interactive Mode")
        print("=" * 50)
        
        # Get available templates
        templates = self.get_available_templates()
        
        # Select configuration type
        print("\n📋 Available configuration types:")
        for i, config_type in enumerate(templates.keys(), 1):
            if templates[config_type]:
                print(f"  {i}. {config_type}")
        
        while True:
            try:
                choice = input("\nSelect configuration type (number): ").strip()
                choice_idx = int(choice) - 1
                config_types = list(templates.keys())
                if 0 <= choice_idx < len(config_types):
                    config_type = config_types[choice_idx]
                    if templates[config_type]:
                        break
                print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a number.")
        
        # Get configuration name
        while True:
            name = input(f"\nEnter {config_type} name (kebab-case): ").strip()
            if name and name.replace('-', '').replace('_', '').isalnum():
                break
            print("❌ Name must be alphanumeric with dashes/underscores only.")
        
        # Get optional parameters file
        params_file = input("\nEnter parameters file path (optional): ").strip()
        parameters = {}
        if params_file:
            params_path = Path(params_file)
            parameters = self.load_parameters(params_path)
        
        # Generate configuration
        success = self.generate_config(config_type, name, parameters=parameters)
        
        if success:
            print(f"\n🎉 Successfully generated {config_type} configuration for '{name}'!")
            print(f"📁 Location: {self.output_dir}/{config_type}s/{name}.yaml")
            print(f"🔧 Next steps:")
            print(f"   1. Review and customize the generated configuration")
            print(f"   2. Validate with: python config/validate-config.py --file {self.output_dir}/{config_type}s/{name}.yaml")
            print(f"   3. Test with: hugai {config_type} start {name}")
        else:
            print(f"\n❌ Failed to generate configuration for '{name}'")
    
    def create_sample_parameters(self, config_type: str, output_file: Path):
        """Create sample parameters file for a configuration type"""
        sample_params = {
            'agent': {
                'primary_role': 'Specialized AI assistant',
                'capabilities': ['analysis', 'generation', 'validation'],
                'llm_model': 'gpt-4',
                'temperature': 0.7,
                'timeout': 300,
                'inputs': [
                    {'name': 'task_description', 'type': 'string', 'required': True},
                    {'name': 'context', 'type': 'object', 'required': False}
                ],
                'outputs': [
                    {'name': 'result', 'type': 'object'},
                    {'name': 'confidence', 'type': 'number'}
                ]
            },
            'lifecycle': {
                'phase': 'implementation',
                'objectives': ['Implement features', 'Ensure code quality'],
                'deliverables': [
                    {'name': 'source_code', 'type': 'code', 'description': 'Implementation code'},
                    {'name': 'unit_tests', 'type': 'code', 'description': 'Test suite'}
                ],
                'agents': [
                    {'name': 'implementation-agent', 'role': 'primary', 'responsibilities': ['Code development']},
                    {'name': 'test-agent', 'role': 'secondary', 'responsibilities': ['Test creation']}
                ]
            },
            'tool': {
                'purpose': 'Development productivity tool',
                'capabilities': ['code_analysis', 'automation', 'reporting'],
                'interfaces': [
                    {'type': 'cli', 'endpoint': 'tool-command'},
                    {'type': 'api', 'endpoint': 'http://localhost:8080/api'}
                ],
                'health_checks': [
                    {'name': 'api_health', 'endpoint': '/health', 'interval': 30}
                ]
            },
            'llm': {
                'providers': [
                    {'name': 'openai', 'type': 'openai', 'endpoint': 'https://api.openai.com/v1'}
                ],
                'models': [
                    {
                        'id': 'gpt-4',
                        'provider': 'openai',
                        'capabilities': {'max_tokens': 4000, 'context_window': 8192},
                        'cost': {'input_cost': 0.03, 'output_cost': 0.06}
                    }
                ],
                'routing_rules': [
                    {'condition': {'task_type': 'code'}, 'target_model': 'gpt-4'}
                ]
            }
        }
        
        if config_type in sample_params:
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(sample_params[config_type], f, default_flow_style=False, sort_keys=False)
            print(f"✅ Created sample parameters file: {output_file}")
        else:
            print(f"❌ No sample parameters available for type: {config_type}")


def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate HUGAI configuration files from templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--type", "-t",
        type=str,
        choices=['agent', 'lifecycle', 'tool', 'llm'],
        help="Configuration type to generate"
    )
    
    parser.add_argument(
        "--name", "-n",
        type=str,
        help="Name for the configuration (kebab-case)"
    )
    
    parser.add_argument(
        "--template",
        type=str,
        help="Template file to use (default: <type>-template.yaml)"
    )
    
    parser.add_argument(
        "--params", "-p",
        type=str,
        help="Parameters file (YAML or JSON)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--sample-params",
        type=str,
        help="Generate sample parameters file for given type"
    )
    
    parser.add_argument(
        "--templates-dir",
        type=str,
        default="config/templates",
        help="Templates directory (default: config/templates)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="config",
        help="Output directory (default: config)"
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = ConfigGenerator(args.templates_dir, args.output_dir)
    
    # Handle sample parameters generation
    if args.sample_params:
        output_file = Path(f"sample-{args.sample_params}-params.yaml")
        generator.create_sample_parameters(args.sample_params, output_file)
        return
    
    # Handle interactive mode
    if args.interactive:
        generator.interactive_mode()
        return
    
    # Validate required arguments for non-interactive mode
    if not args.type or not args.name:
        print("❌ Both --type and --name are required for non-interactive mode")
        print("💡 Use --interactive for guided configuration generation")
        sys.exit(1)
    
    # Load parameters if provided
    parameters = {}
    if args.params:
        params_path = Path(args.params)
        parameters = generator.load_parameters(params_path)
    
    # Set output file if provided
    output_file = Path(args.output) if args.output else None
    
    # Generate configuration
    success = generator.generate_config(
        args.type,
        args.name,
        args.template,
        parameters,
        output_file
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()