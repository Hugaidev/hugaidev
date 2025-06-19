# HUGAI Configuration Templates

This directory contains reusable templates for generating HUGAI configuration files. The templates use the Jinja2 templating engine to provide a DRY (Don't Repeat Yourself) approach to configuration management.

## 📋 Template Structure

### Base Templates

**Common building blocks used across all configuration types:**

- `base-metadata.yaml` - Standard metadata fields (name, version, author, etc.)
- `base-integration.yaml` - Integration patterns (triggers, inputs, outputs)
- `base-validation.yaml` - Validation and monitoring configurations
- `base-cli-usage.yaml` - CLI command patterns and examples

### Type-Specific Templates

**Complete templates for each configuration type:**

- `agent-template.yaml` - Agent configuration template
- `lifecycle-template.yaml` - Lifecycle phase configuration template
- `tool-template.yaml` - Tool configuration template
- `llm-template.yaml` - LLM model configuration template

## 🚀 Usage

### Command Line Generation

```bash
# Generate agent configuration
python config/generate-config.py --type agent --name security-scanner

# Generate with parameters file
python config/generate-config.py --type agent --name test-agent --params agent-params.yaml

# Interactive mode
python config/generate-config.py --interactive

# Custom template
python config/generate-config.py --type tool --name custom-tool --template my-custom-template.yaml
```

### Creating Parameter Files

```bash
# Generate sample parameters file
python config/generate-config.py --sample-params agent

# Creates: sample-agent-params.yaml
```

## 📝 Template Syntax

Templates use Jinja2 syntax with custom filters and functions:

### Variable Substitution
```yaml
metadata:
  name: "{{name}}"
  version: "{{version | default('1.0.0')}}"
  author: "{{author | default('HUGAI Team')}}"
```

### Conditional Blocks
```yaml
{% if custom_parameters %}
custom: {{custom_parameters | to_yaml}}
{% endif %}
```

### Loops
```yaml
capabilities:
  {% for capability in capabilities %}
  - "{{capability}}"
  {% endfor %}
```

### Template Includes
```yaml
# Include base metadata template
{% include 'base-metadata.yaml' %}
```

### Custom Filters

- `to_yaml` - Convert Python objects to YAML format
- `current_date` - Get current date in YYYY-MM-DD format
- `default(value)` - Provide default value if variable is undefined

## 🔧 Creating New Templates

1. **Create template file** in `config/templates/`
2. **Use Jinja2 syntax** for variables and logic
3. **Include base templates** to reduce duplication
4. **Document required parameters** in comments
5. **Validate against schemas** using the validation system

### Template Example

```yaml
# My Custom Template
# Required parameters: name, purpose, capabilities

# Include base metadata
{% set category = 'custom' %}
{% include 'base-metadata.yaml' %}

# Custom configuration
configuration:
  purpose: "{{purpose}}"
  capabilities: {{capabilities | to_yaml}}
  
  {% if optional_setting %}
  optional_setting: "{{optional_setting}}"
  {% endif %}

# Include base integration
{% include 'base-integration.yaml' %}
```

## 📊 Parameter Files

Parameter files provide values for template variables. Support both YAML and JSON formats.

### YAML Parameter File Example
```yaml
# agent-params.yaml
name: "security-scanner"
description: "AI-powered security vulnerability scanner"
primary_role: "Security analysis and vulnerability detection"
capabilities:
  - "static_code_analysis"
  - "dependency_scanning"
  - "vulnerability_assessment"
llm_model: "gpt-4"
temperature: 0.3
inputs:
  - name: "source_code"
    type: "string"
    required: true
    description: "Source code to analyze"
outputs:
  - name: "vulnerabilities"
    type: "array"
    description: "Detected security vulnerabilities"
  - name: "recommendations"
    type: "array"
    description: "Security improvement recommendations"
```

### JSON Parameter File Example
```json
{
  "name": "performance-optimizer",
  "description": "Performance optimization agent",
  "capabilities": ["profiling", "optimization", "monitoring"],
  "llm_model": "claude-3-sonnet",
  "custom_parameters": {
    "optimization_targets": ["latency", "throughput", "memory"]
  }
}
```

## 🎯 Best Practices

### Template Design
- ✅ **Use base templates** to maintain consistency
- ✅ **Provide sensible defaults** with the `default()` filter
- ✅ **Document required parameters** in template comments
- ✅ **Validate template logic** before committing
- ✅ **Keep templates focused** on specific configuration types

### Parameter Management
- ✅ **Use descriptive parameter names** (snake_case preferred)
- ✅ **Group related parameters** in nested objects
- ✅ **Provide example values** in sample parameter files
- ✅ **Validate parameter types** in templates when possible

### Version Control
- ✅ **Version templates** alongside configurations
- ✅ **Document breaking changes** in template updates
- ✅ **Test template changes** with existing parameter files
- ✅ **Maintain backward compatibility** when possible

## 🔍 Validation Integration

Templates integrate with the JSON schema validation system:

```bash
# Generate and validate in one step
python config/generate-config.py --type agent --name test-agent --params params.yaml
python config/validate-config.py --file config/agents/test-agent.yaml
```

## 🛠️ Advanced Features

### Dynamic Content Generation

Templates can generate different content based on parameters:

```yaml
configuration:
  {% if deployment_mode == 'production' %}
  replicas: 3
  resources:
    limits:
      cpu: "2"
      memory: "4Gi"
  {% else %}
  replicas: 1
  resources:
    limits:
      cpu: "500m"
      memory: "1Gi"
  {% endif %}
```

### Template Inheritance

Create specialized templates that extend base templates:

```yaml
# specialized-agent-template.yaml
{% extends "agent-template.yaml" %}

{% block agent_extensions %}
{{ super() }}

# Additional specialized configuration
specialized_config:
  domain: "{{domain}}"
  expertise_level: "{{expertise_level | default('intermediate')}}"
{% endblock %}
```

### Custom Filters

Add custom filters for specific formatting needs:

```python
# In generate-config.py
def custom_filter(value):
    # Custom processing logic
    return processed_value

env.filters['custom_filter'] = custom_filter
```

## 🧪 Testing Templates

### Unit Testing
```bash
# Test template rendering with different parameters
python -c "
from config.generate_config import ConfigGenerator
gen = ConfigGenerator()
result = gen.generate_config('agent', 'test', parameters={'test_param': 'value'})
print('✅ Test passed' if result else '❌ Test failed')
"
```

### Integration Testing
```bash
# Generate and validate configuration
python config/generate-config.py --type agent --name test-agent --params test-params.yaml
python config/validate-config.py --file config/agents/test-agent.yaml
```

## 📚 Examples

### Minimal Agent Configuration
```bash
# Create minimal parameters
echo "
name: simple-agent
description: A simple AI agent
primary_role: Basic assistance
capabilities: [analysis]
" > simple-agent-params.yaml

# Generate configuration
python config/generate-config.py --type agent --name simple-agent --params simple-agent-params.yaml
```

### Complex LLM Configuration
```bash
# Create comprehensive LLM parameters
python config/generate-config.py --sample-params llm
# Edit sample-llm-params.yaml with your values
python config/generate-config.py --type llm --name production-llm --params sample-llm-params.yaml
```

## 🔮 Future Enhancements

- [ ] **Template marketplace** for community-contributed templates
- [ ] **Visual template builder** with web interface
- [ ] **Template testing framework** with automated validation
- [ ] **Template versioning** with migration tools
- [ ] **IDE integration** with syntax highlighting and autocomplete
- [ ] **Template analytics** to track usage and identify improvements