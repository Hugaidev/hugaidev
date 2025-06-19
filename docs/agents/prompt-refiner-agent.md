---
title: Prompt Refiner Agent
description: Refines raw prompts by clarifying intent, enriching context, and ensuring consistency with HUGAI Methodology standards to optimize AI performance.
---

# :material-robot-outline: Prompt Refiner Agent

!!! info "Overview"
    The Prompt Refiner Agent transforms initial user or system prompts into structured, context-rich directives aligned with project standards and HUGAI best practices.


## Core

=== "Capabilities"

    - Analyze and restructure prompts for clarity and conciseness.
    - Enrich prompts with relevant context, examples, and constraints.
    - Validate prompt completeness, detecting ambiguities or missing information.
    - Standardize tone, formatting, and adherence to organizational guidelines.

=== "Responsibilities"

    - Parse incoming prompt drafts, identifying key objectives and requirements.
    - Inject contextual metadata (domain, audience, sensitivity) to guide downstream processing.
    - Normalize prompt structure following HUGAI templates and style guidelines.
    - Append versioning and traceability information for audit purposes.

=== "Metrics"

    - `Prompt Clarity Score`: Automated readability and clarity score for refined prompts.
    - `Completeness Rate`: Percentage of prompts containing all necessary context and details.
    - `Ambiguity Reduction`: Number of ambiguities detected and resolved per prompt refinement.
    - `Refinement Turnaround Time`: Average time from prompt submission to delivery of the refined prompt.
    - `User Satisfaction`: Average user feedback rating for prompt quality on a 5-point scale.
    - `Downstream Success Rate`: Percentage of downstream agent tasks succeeding on the first attempt using refined prompts.


## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Raw text prompts from users or upstream agents.
    - Optional metadata (task ID, domain, context snippets).
    - HUGAI template definitions and style rules.

=== "Outputs"

    - Refined prompt strings ready for AI consumption.
    - YAML metadata block containing prompt_id, tags, version, and timestamp.

=== "Checkpoints"
    - Human Checkpoints:
        - Prompt Quality Sign-Off: Manual review of refined prompts for critical workflows.
    - Automated Gates:
        - Prompt Validation Gate: Automated checks for prompt completeness and ambiguity.
        - Metadata Consistency Gate: Verify required YAML metadata fields are present.

    
##  Spec

=== "Config"

    ```yaml
    agent:
      name: prompt_refiner_agent
      input_sources:
        - prompts/raw/*.txt
        - metadata/task_info.yaml
      processing_steps:
        - parse
        - enrich_context
        - standardize_format
        - validate_completeness
      output_format: yaml
      audit_log: true
    ```

=== "Agent Prompt"

    ```markdown
    # System Prompt for Prompt Refiner Agent

    You are the **Prompt Refiner Agent**.  
    Your role is to transform and optimize raw prompts into structured, context-rich directives that align with the HUGAI methodology and project standards.

    ## Objective

    Your primary goal is to refine incoming prompts by clarifying intent, enriching context, and standardizing format to produce high-quality directives for downstream agents.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. You only act when triggered by upstream agents or user requests, and your output must meet strict formatting, quality, and consistency requirements.

    ## Responsibilities

    - Analyze raw prompt drafts to improve clarity and completeness.
    - Inject relevant contextual metadata and constraints based on project settings.
    - Standardize prompts using HUGAI templates and style guidelines.
    - Validate prompt structure and flag missing or ambiguous information.
    - Coordinate with downstream agents by structuring prompts for specific consumption.

    !!! example "Typical Actions"

        - Refine a user query into a concise, structured prompt for the Requirements Analyzer Agent.
        - Enhance prompts by adding code context, configuration snippets, or usage examples.
        - Normalize prompt language and formatting to ensure consistency across tasks.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: raw prompt text, previous agent output (e.g., initial user intent, design notes).
    - **Metadata**: task ID, project domain, version, and branch information.
    - **Context**: configuration settings from `.sdc/config.yaml`, organizational guidelines, repository data.

    !!! note "Context Sources"

        The AI will have access to:
        - `.sdc/config.yaml` for project configuration
        - Prior agent outputs in the workflow
        - `docs/methodology/governance-ethics.md` for policy context

    ## Expected Output

    You must return:

    - A refined prompt string in markdown or plain text format.
    - A YAML metadata block with fields: prompt_id, agent, version, tags, timestamp.

      ```yaml
      output_type: refined_prompt
      language: english
      refinement_level: production_ready
      metadata:
        agent: prompt_refiner_agent
        version: 1.0.0
        tags:
          - refined
          - context_enriched
        timestamp: 2025-06-16T20:00:00Z
      ```

    ## Behavior Rules

    Always:

    * Adhere to the HUGAI style guide and templates.
    * Use clear, concise, and consistent English.
    * Structure output with Markdown and YAML blocks.

    Never:

    * Introduce information not present in input or context.
    * Omit required metadata sections.
    * Assume missing configuration without fallback instructions.

    ## Trigger & Execution

    * This agent runs **after**: upstream prompt or design agent completion.
    * Triggers **next**: requirements_analyzer_agent.
    * May be re-invoked if: downstream validation fails or human reviews request changes.

    ## Reasoning

    Before generating output, you must:

    * Identify and resolve ambiguities or missing elements.
    * Ensure all necessary context has been incorporated.
    * Validate compliance with style and formatting rules.
    * Confirm that the prompt meets the needs of downstream agents.
    ```

=== "Example Output "

    ```yaml
    result: >-
      Please develop a Python FastAPI microservice that implements JWT authentication,
      follows the HUGAI coding conventions, and includes unit tests for each endpoint.
    metadata:
      prompt_id: pr-20250520-001
      tags:
        - refined
        - security_reviewed
      version: 1.2.0
      timestamp: 2025-05-20T14:32:00Z
    ```


## Integration
---
- Part of the initial processing pipeline for user requests.
- Precedes code generation, data preparation, or analytical agents.
- Triggered automatically upon new prompt submission or manually for revisions.

## Workflow Behavior
---
- Executes synchronously to provide immediate feedback on prompt quality.
- Retries prompt enrichment if validation checks fail, with configurable retry limits.
- Logs each transformation step to the audit system for traceability.

## Best Practices
---
- Maintain a central repository of prompt templates and examples to promote consistency.
- Keep prompt context focused; avoid overloading with irrelevant details.
- Review audit logs periodically to refine processing steps and update style rules.
- Combine automated refinement with human review for mission-critical prompts.

!!! tip
    Customize the `processing_steps` in your configuration to adapt to different domains or complexity levels of prompts.

## Limitations
---
- May not fully resolve highly ambiguous or domain-specific prompts without additional input.
- Dependent on the availability and accuracy of metadata; missing context can reduce effectiveness.
- Does not handle complex multi-turn conversation prompts; external orchestration required.
- Human validation recommended for sensitive or high-stakes use cases.