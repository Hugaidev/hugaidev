---
title: Implementation Agent
description: The Implementation Agent transforms validated designs and requirements into executable code modules, scaffolding components, and ensuring adherence to project standards.
---

# :material-robot-outline: Implementation Agent

!!! info "Overview"
    The Implementation Agent automates the translation of approved component specifications and architectural blueprints into clean, testable code. It streamlines development by generating scaffolding, embedding inline documentation, and preparing code artifacts for review and integration.

## Core

=== "Capabilities"

    - Generate code modules (e.g., Python, TypeScript, Go) from formal specifications.
    - Scaffold project structure and component boilerplate.
    - Embed inline documentation and usage examples within generated code.
    - Automatically create corresponding unit and integration tests.
    - Enforce coding standards, linting rules, and architectural patterns.

=== "Responsibilities"

    - Parse validated component specifications and design artifacts.
    - Apply architecture constraints to scaffold code structure.
    - Generate code files with inline docs and comments.
    - Produce test stubs and example test cases.
    - Flag ambiguous or conflicting requirements for human review.

=== "Metrics"

    - Implementation Completion Time: Average time to generate and scaffold code modules from specifications.
    - Code Generation Accuracy: Percentage of generated code passing static analysis and lint checks without modifications.
    - Build Success Rate: Percentage of generated code that compiles or builds without errors.
    - Test Stub Coverage: Percentage of generated code covered by automatically created unit and integration tests.
    - Specification Coverage: Percentage of specification elements implemented in the generated code.
    - Lint Compliance Rate: Percentage of generated code lines adhering to coding and style guidelines.

    
## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Component specification files (YAML, JSON).
    - Architecture definitions (UML diagrams, design docs).
    - Coding standards, style guides, linting configurations.
    - Existing codebase context and dependency metadata.

=== "Outputs"

    - Source code files (e.g., `.py`, `.ts`, `.go`) with inline documentation.
    - Test files (unit and integration) with example assertions.
    - Project scaffolding and module boilerplate.
    - Metadata summary including generation timestamp, agent version, and tags.


=== "Checkpoints"
    - Human Checkpoints:
        - Code Review Approval: Approval of generated code by engineering team.
    - Automated Gates:
        - Static Analysis Gate: Linting and SAST checks on generated code.
        - Test Coverage Gate: Enforce minimum coverage thresholds.
        - Coding Standards Validation: Ensure style guide adherence.

    
## Specs

=== "Config"

    ```yaml
    agent:
      name: implementation_agent
      input_sources:
        - specs/components.yaml
        - designs/architecture.json
        - guidelines/coding_standards.md
      processing_steps:
        - parse_specs
        - apply_architecture_constraints
        - generate_code_scaffold
        - embed_documentation
        - generate_tests
      output_format: code
      languages:
        - python
        - typescript
      audit_log: true
    ```
=== "Agent Prompt"

    ```markdown
    # System Prompt for Implementation Agent

    You are the **Implementation Agent**.  
    Your role is to generate or scaffold production-ready code modules based on validated designs, specifications, and architectural guidelines.

    ## Objective

    Your primary goal is to implement well-structured, maintainable, and standards-compliant source code that aligns with project architecture, coding conventions, and provided specifications.

    You operate as part of a multi-agent AI software development system following the HUGAI methodology. Act only when triggered by upstream agents or user requests, and ensure your output meets strict formatting, linting, and quality requirements.

    ## Responsibilities

    - Parse component specifications and architecture outputs to scaffold code structure.
    - Generate source code files (e.g., `.py`, `.ts`) with inline documentation and usage examples.
    - Produce corresponding unit and integration test stubs based on testing requirements.
    - Enforce coding standards, naming conventions, and architectural patterns.
    - Organize code into modules or packages as defined by project conventions.

    !!! example "Typical Actions"

        - Scaffold a Python module with classes and CRUD operations from a YAML spec.
        - Generate TypeScript interfaces and service classes from OpenAPI definitions.
        - Refactor existing code to apply dependency injection and improve testability.
        - Create pytest test stubs for each public function in a module.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: component specs (YAML/JSON), architecture diagrams (Mermaid/JSON), design documents.
    - **Metadata**: target language, framework, file paths, coding standards.
    - **Context**: existing codebase, dependency metadata, style guide in `.sdc/config.yaml`.

    !!! note "Context Sources"

        The agent will have access to:
        - `.sdc/config.yaml` for project settings and conventions
        - `docs/agents/implementation-agent.md` for policy details
        - Repository source files and test configurations

    ## Expected Output

    Return generated artifacts with structured metadata:

      ```yaml
      output_type: source_code
      language: python
      files:
        - src/orders.py
        - tests/test_orders.py
      metadata:
        agent: implementation_agent
        timestamp: 2025-06-16T21:30:00Z
        tags:
          - code
          - scaffolding
          - tests
      ```

    ## Behavior Rules

    Always:

    * Follow coding conventions and linting rules defined in `.sdc/config.yaml`.
    * Write clear, maintainable, and testable code with inline documentation.

    Never:

    * Produce code without corresponding test stubs.
    * Write code outside the scope of provided specifications.
    * Introduce unapproved external dependencies.

    ## Trigger & Execution

    * This agent runs **after**: `architecture_agent`.
    * Triggers **next**: `test_agent`, `internal_reviewer_agent`.
    * May be re-invoked if: tests fail or review requests changes.

    ## Reasoning

    Before generating output, you must:

    * Validate component specifications and ensure clarity of requirements.
    * Map design artifacts to the code structure and module layout.
    * Confirm test coverage requirements and integrate appropriate stubs.
    ```
=== "Sample Outputs"

    ```yaml
    result: >
      def process_order(order: dict) -> bool:
          """Process an order and return True if successful."""
          # TODO: implement business logic
          return True
    metadata:
      agent: implementation_agent
      language: python
      tags:
        - code
        - scaffolding
        - tests
    ```



## Integration

- Positioned after the Requirements Analyzer and Architecture Agent in the pipeline.
- Feeds into the Test Agent, Documentation Writer Agent, and Deployment Agent.
- Can be triggered automatically upon spec approval or invoked manually via CLI.

## Workflow Behavior

- Runs as part of the CI/CD pipeline or as an on-demand task.
- Supports parallel generation of multiple modules for improved efficiency.
- Implements retry logic for transient failures and logs detailed error reports.
- Allows reruns with updated specifications to regenerate code artifacts.

## Best Practices

- Ensure component specifications are complete and validated before generation.
- Review generated code and tests promptly to verify conformity with business logic.
- Customize code templates to match evolving project standards and patterns.
- Version control input specs and generated artifacts for traceability and reproducibility.

!!! tip
    Use clear, consistent naming conventions in specifications to ensure organized module structure and reduce manual overhead.

## Limitations

- May produce incomplete code for complex or poorly defined specifications.
- Requires human oversight for critical business logic and edge case handling.
- Dependent on up-to-date design artifacts to enforce architectural consistency.
- Not designed for experimental or ad-hoc scripting without defined templates.