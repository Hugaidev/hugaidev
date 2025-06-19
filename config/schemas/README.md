# HUGAI Configuration Schemas

This directory contains JSON Schema definitions for validating HUGAI configuration files. These schemas ensure consistency, catch errors early, and provide IDE support with autocompletion and validation.

## 📋 Available Schemas

### 🤖 Agent Schema (`agent-schema.json`)
Validates agent configuration files in `config/agents/`.

**Key Features:**
- Metadata validation (name, version, description, category)
- Role and capability definitions
- Dependency management
- Integration specifications (triggers, inputs, outputs)
- Quality gates and metrics
- CLI usage examples

**Categories:** `core`, `specialized`, `utility`, `governance`

### 🔄 Lifecycle Schema (`lifecycle-schema.json`)
Validates lifecycle phase configurations in `config/lifecycle/`.

**Key Features:**
- Phase metadata and objectives
- Deliverable specifications
- Agent assignments and responsibilities
- Tool requirements
- Workflow definitions
- Human checkpoints and automated gates

**Phases:** `planning`, `design`, `implementation`, `testing`, `deployment`, `maintenance`, `governance`

### 🛠️ Tool Schema (`tool-schema.json`)
Validates tool configurations in `config/tools/`.

**Key Features:**
- Tool purpose and capabilities
- System requirements and dependencies
- Interface definitions (API, CLI, webhook, GUI, library)
- Authentication methods
- Health checks and performance metrics

**Categories:** `development`, `testing`, `deployment`, `monitoring`, `security`, `collaboration`

### 🧠 LLM Schema (`llm-schema.json`)
Validates LLM model configurations in `config/llms/`.

**Key Features:**
- Multi-provider support (OpenAI, Anthropic, Azure, HuggingFace, local)
- Model capability definitions
- Cost optimization strategies
- Intelligent routing rules
- Performance monitoring
- Budget management

## 🚀 Usage

### Command Line Validation

```bash
# Validate all configurations
python config/validate-config.py

# Validate specific file
python config/validate-config.py --file config/agents/router-agent.yaml

# Validate specific directory
python config/validate-config.py --directory config/agents

# Use custom schema
python config/validate-config.py --file config.yaml --schema custom-schema.json
```

### IDE Integration

Most modern IDEs support JSON Schema validation. Configure your IDE to use these schemas:

#### VS Code (`settings.json`)
```json
{
  "yaml.schemas": {
    "./config/schemas/agent-schema.json": ["config/agents/*.yaml"],
    "./config/schemas/lifecycle-schema.json": ["config/lifecycle/*.yaml"],
    "./config/schemas/tool-schema.json": ["config/tools/*.yaml"],
    "./config/schemas/llm-schema.json": ["config/llms/*.yaml"]
  }
}
```

#### JetBrains IDEs
1. Go to Settings → Languages & Frameworks → Schemas and DTDs → JSON Schema Mappings
2. Add mappings for each schema file and corresponding file patterns

### Pre-commit Validation

The project includes a pre-commit hook that automatically validates configurations:

```bash
# Install the hook (already done if you cloned the repo)
chmod +x .git/hooks/pre-commit

# Test the hook
git add config/agents/new-agent.yaml
git commit -m "Add new agent"
# Hook will validate the file before allowing the commit
```

### CI/CD Integration

GitHub Actions automatically validate configurations on:
- Push to main branch
- Pull requests affecting configuration files

See `.github/workflows/validate-configs.yml` for details.

## 📝 Schema Structure

All schemas follow a consistent structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hugai.dev/schemas/{type}-schema.json",
  "title": "Schema Title",
  "description": "Schema description",
  "type": "object",
  "required": ["metadata", "configuration", "integration", "validation"],
  "properties": {
    "metadata": { /* Common metadata fields */ },
    "configuration": { /* Type-specific configuration */ },
    "integration": { /* Integration specifications */ },
    "validation": { /* Quality gates and metrics */ },
    "cli_usage": { /* CLI command examples */ }
  }
}
```

### Common Metadata Fields

All configuration files must include:

```yaml
metadata:
  name: "kebab-case-name"           # Required, kebab-case
  version: "1.0.0"                 # Required, semantic version
  description: "Brief description" # Required, 10-200 chars
  author: "Author Name"            # Required
  created: "2024-01-01"           # Required, YYYY-MM-DD
  updated: "2024-01-01"           # Required, YYYY-MM-DD
```

## 🔧 Validation Features

### Error Reporting
- Detailed error messages with JSON path location
- Multiple error detection in single validation run
- Suggested fixes for common issues

### Type Detection
- Automatic detection based on file path (`/agents/`, `/tools/`, etc.)
- Content-based detection using metadata fields
- Manual override with `--schema` parameter

### Format Validation
- Semantic versioning validation
- Date format validation (YYYY-MM-DD)
- URL format validation
- Email format validation

## 🆕 Adding New Schemas

1. Create new schema file in `config/schemas/`
2. Follow the common structure pattern
3. Add validation rules in `validate-config.py`
4. Update this README
5. Add IDE integration examples

## 🐛 Troubleshooting

### Common Issues

**Invalid YAML syntax**
```
❌ Invalid YAML in config/agents/test-agent.yaml: found character '\t' that cannot start any token
```
*Solution: Use spaces instead of tabs for indentation*

**Missing required fields**
```
❌ Validation error at .metadata: 'version' is a required property
```
*Solution: Add the missing required field*

**Invalid enumeration value**
```
❌ Validation error at .metadata.category: 'invalid' is not one of ['core', 'specialized', 'utility', 'governance']
```
*Solution: Use one of the allowed values*

### Getting Help

- Check the schema files for detailed property definitions
- Run validation with `--verbose` flag for detailed output
- Review existing configuration files for examples
- Consult the main configuration documentation in `config/README.md`

## 📊 Validation Statistics

The validation system tracks:
- ✅ Total files validated
- ❌ Validation errors found
- 🔧 Schema compliance percentage
- ⚡ Validation performance metrics

## 🔮 Future Enhancements

- [ ] Custom validation rules for business logic
- [ ] Integration with external validation services
- [ ] Real-time validation in configuration editors
- [ ] Automatic schema generation from examples
- [ ] Multi-language schema support
- [ ] Performance optimization for large configuration sets