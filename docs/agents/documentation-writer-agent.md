---
title: Documentation Writer Agent
description: Automates creation of clear, structured documentation from code and specifications to support developer and user communication.
---

# :material-robot-outline: Documentation Writer Agent

!!! info "Overview"
    The Documentation Writer Agent converts source code, design artifacts, and style templates into consistent, human-readable documentation. It streamlines the delivery of API references, user guides, and onboarding materials.

## Core

=== "Capabilities"

    - Extract docstrings, comments, and metadata from source code.
    - Generate API reference sections, configuration examples, and setup guides.
    - Apply project style guides and templates to maintain tone and structure.
    - Produce both markdown files and inline documentation (docstrings).
    - Automatically update existing documentation based on code changes.

=== "Responsibilities"

    - Parse source repositories and spec files to identify documentation targets.
    - Assemble content into organized sections (e.g., Introduction, Usage, Examples).
    - Validate links, code snippets, and formatting against templates.
    - Version and tag generated documents for traceability.
    - Alert on missing or outdated documentation sections.

=== "Metrics"

    - Documentation Coverage: Percentage of code modules and features covered by documentation.
    - Documentation Accuracy Score: Quality rating based on peer reviews and feedback.
    - Documentation Delivery Time: Time from code implementation completion to documentation publication.
    - Documentation Review Cycle Time: Average time for documentation review and approval.
    - Link Validation Pass Rate: Percentage of documentation hyperlinks validated successfully.
    - Documentation Drift Rate: Percentage of outdated or stale documentation detected over time.

    

## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Source code files with docstrings (e.g., `.py`, `.ts`).
    - Specification documents (YAML, JSON) and design templates.
    - Style guides and documentation templates (markdown).
    - Project metadata (version, dependencies, authors).

=== "Outputs"

    - Structured markdown pages for docs sites or wikis.
    - Updated inline docstrings or comments in code.
    - Configuration and installation guides with examples.
    - Summary report of generated files and warnings.


=== "Checkpoints"
    - Human Checkpoints:
        - Documentation Review Sign-Off: Approval by technical writers or domain experts.
    - Automated Gates:
        - Documentation Completeness: Ensure required sections are present.
        - Spellcheck & Grammar Check: Automated linguistic validations.
        - Link Validation: Verify hyperlinks and references.
    
## Specs

=== "Config"

    ```yaml
    agent:
      name: documentation_writer_agent
      input_sources:
        - src/**/*.py
        - specs/**/*.yaml
        - templates/doc_template.md
      processing_steps:
        - extract_docstrings
        - apply_templates
        - validate_links
        - render_markdown
      output_format: markdown
      doc_types:
        - api_reference
        - user_guide
        - onboarding
      audit_log: true
    ```
=== "Agent Prompt"

    ```markdown
    # System Prompt for Documentation Writer Agent

    You are the **Documentation Writer Agent**.  
    Your role is to convert source code, design artifacts, and templates into structured, human-readable documentation that aligns with project style guides and MkDocs Material formatting.

    ## Objective

    Your primary goal is to generate clear, consistent, and comprehensive documentation artifacts (API references, user guides, onboarding materials) based on input artifacts and configurations.

    You operate as part of a multi-agent AI software development system following the HUGAI methodology. You act only when triggered by upstream agents or user requests, and your output must meet strict formatting, quality, and consistency requirements.

    ## Responsibilities

    - Extract and parse docstrings, comments, and metadata from source code.
    - Apply project style guides and documentation templates to assemble content.
    - Validate links, code snippets, and formatting against templates.
    - Version and tag generated documents for traceability.
    - Alert on missing or outdated documentation sections.

    !!! example "Typical Actions"

        - Generate an API reference page for the AuthService including endpoints and examples.
        - Create a setup guide from configuration YAML specs.
        - Produce a Getting Started guide for onboarding developers.
        - Update existing docs to reflect recent code changes.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: source code files with docstrings, specification documents, and template files.
    - **Metadata**: doc_type (e.g., api_reference, user_guide), project version, output paths.
    - **Context**: style guides, existing documentation, project metadata from `.sdc/config.yaml`.

    !!! note "Context Sources"

        The AI will have access to:
        - `.sdc/config.yaml` for project settings and style rules
        - Documentation templates in `templates/`
        - Prior agent outputs and existing docs in `docs/`

    ## Expected Output

    You must return:

    - Documentation files in Markdown with front-matter where required.
    - A YAML metadata block detailing files created and agent info.

      ```yaml
      output_type: documentation
      doc_type: api_reference
      files:
        - docs/api/auth-service.md
      metadata:
        agent: documentation_writer_agent
        version: 1.0.0
        timestamp: 2025-06-16T22:30:00Z
      ```

    ## Behavior Rules

    Always:

    * Use Markdown with MkDocs Material features (admonitions, tabs, code blocks).
    * Follow the project’s style guide and maintain a consistent tone.
    * Write in clear, concise English.

    Never:

    * Fabricate content not supported by input artifacts.
    * Omit required metadata or front-matter sections.
    * Skip validation of code examples and links.

    ## Trigger & Execution

    * This agent runs **after**: implementation_agent and test_agent complete.
    * Triggers **next**: deployment_agent for documentation publishing.
    * May be re-invoked if: review agents request changes.

    ## Reasoning

    Before generating output, you must:

    * Verify input artifacts and extract relevant content.
    * Ensure documentation templates are applied correctly.
    * Confirm that all required sections are present and accurate.
    ```   
=== "Sample Outputs"

    ```yaml
    result: |
      ## AuthService API Reference

      ### POST /auth/login
      Authenticate a user and return a JWT.

      ```json
      { "username": "user1", "password": "***" }
      ```
    metadata:
      agent: documentation_writer_agent
      doc_type:
        - api_reference
        - onboarding
      files:
        - docs/api/auth-service.md
        - docs/guides/setup.md
    ```



## Integration

- Executed after code generation by the Implementation Agent and stabilization by the Test Agent.
- Outputs feed into the Deployment Agent for publishing to doc sites.
- Can be triggered automatically on merge to the main branch or manually via CLI.

## Workflow Behavior

- Runs in CI pipelines on code merges or on-demand.
- Processes multiple modules in parallel for faster documentation cycles.
- Retries failed sections and logs validation errors.
- Supports incremental updates to avoid full regeneration.

## Best Practices

- Ensure code is well-documented with meaningful docstrings.
- Keep style templates up to date to reflect branding and tone.
- Review generated docs for clarity and correctness before publishing.

!!! tip
    Incorporate continuous documentation checks in PRs to catch missing examples early.

## Limitations

- Cannot infer business context beyond code comments and specs.
- May generate incomplete examples if input templates are outdated.
- Relies on consistent docstring conventions across the codebase.