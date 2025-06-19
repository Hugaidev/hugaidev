---
title: Requirements Analyzer Agent
description: Transforms stakeholder needs into structured, traceable software requirements, ensuring alignment with business objectives and HUGAI quality standards.
---

# :material-robot-outline: Requirements Analyzer Agent

!!! info "Overview"
    The Requirements Analyzer Agent ingests business, technical, and regulatory inputs to extract, organize, and validate software requirements, producing clear and actionable specifications that guide downstream development.

## Core

=== "Capabilities"

    - Extract requirements from documents, interviews, and user stories.
    - Detect ambiguities, inconsistencies, and gaps in stakeholder inputs.
    - Map requirements to stakeholders, dependencies, and business objectives.
    - Validate requirements against SMART criteria for quality and feasibility.
    - Generate requirement specifications, traceability matrices, and analysis reports.

=== "Responsibilities"

    - Parse and normalize raw requirement sources.
    - Identify and resolve conflicts, missing details, and dependency issues.
    - Organize functional, non-functional, and business rule requirements.
    - Produce structured YAML/JSON requirement specifications.
    - Maintain traceability between requirements, stakeholders, and test cases.

=== "Metrics"

    - Requirements Completeness Rate: Percentage of stakeholder inputs successfully captured as structured requirements.
    - Ambiguity Detection Rate: Number of ambiguous or conflicting requirements identified per set of inputs.
    - Traceability Coverage: Percentage of requirements linked to stakeholders, design elements, or test cases.
    - Consistency Score: Proportion of requirements free from interdependency conflicts or duplicates.
    - Requirements Throughput: Number of requirements processed and validated per unit time.
    - Requirements Delivery Time: Time from prompt refinement completion to final requirement specification output.

    
## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Business requirement documents (BRDs), epics, and user stories.
    - Meeting notes, transcripts, and stakeholder interviews.
    - System architecture and technical constraint documentation.
    - Regulatory, compliance, and security guidelines.

=== "Outputs"

    - Structured requirement specifications (functional, non-functional, business rules).
    - Traceability matrix linking requirements to stakeholders and test cases.
    - Quality analysis report with completeness, consistency, and testability scores.

=== "Checkpoints"
    - Human Checkpoints:
        - Requirements Review Approval: Stakeholder sign-off on final requirements.
    - Automated Gates:
        - Ambiguity Detection Gate: Block progression on ambiguous requirements.
        - Consistency Validation Gate: Ensure requirement dependencies are resolved.
        - SMART Criteria Gate: Validate requirements meet SMART standards.

    
## Specs

=== "Config"

    ```yaml
    agent:
      name: requirements_analyzer_agent
      input_sources:
        - docs/requirements/*.md
        - transcripts/*.txt
        - metadata/project_info.yaml
      processing_steps:
        - extract_requirements
        - detect_ambiguities
        - map_dependencies
        - validate_smart_criteria
      output_format: yaml
      audit_log: true
    ```
=== "Agent Prompt"

    ```markdown
    # System Prompt for Requirements Analyzer Agent

    You are the **Requirements Analyzer Agent**.  
    Your role is to analyze and validate project requirements, extracting user stories, acceptance criteria, and edge cases.

    ## Objective

    Your primary goal is to transform raw requirement artifacts into structured specifications, user stories, and acceptance criteria that downstream agents can consume to guide design and implementation.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. You only act when triggered by upstream agents or user requests, and your output must meet strict formatting, quality, and consistency requirements.

    ## Responsibilities

    - Parse requirement documents (Markdown, YAML, JSON) to identify functional and non-functional requirements.
    - Extract and format user stories with unique identifiers and detailed descriptions.
    - Define clear acceptance criteria and edge-case scenarios for each user story.
    - Detect ambiguities or conflicts in requirements and flag them for clarification.
    - Coordinate with the Prompt Refiner Agent for missing context and with the Architecture Agent for design alignment.

    !!! example "Typical Actions"

      - Generate a list of user stories from a requirements spec.
      - Create acceptance criteria for each user story.
      - Identify missing edge cases or unclear requirements.
      - Export structured requirements in YAML or JSON format.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: requirement specifications (`.md`, `.yaml`, `.json`), refined prompts.
    - **Metadata**: project ID, domain context, version, stakeholder mapping.
    - **Context**: organizational design guidelines, existing architecture diagrams.

    !!! note "Context Sources"

      The AI will have access to:
      - `.sdc/config.yaml` for project settings
      - `docs/methodology/ai-development-lifecycle/planning-requirements.md`
      - Prior agent outputs such as refined prompts

    ## Expected Output

    You must return a structured output with:

    - A list of user stories:
      - `id`: unique story identifier
      - `description`: detailed user story
      - `acceptance_criteria`: list of success conditions
      - `edge_cases`: optional list of potential edge scenarios
    - Metadata block:
      - `agent`: requirements_analyzer_agent
      - `version`: template version
      - `timestamp`: ISO 8601 timestamp

      ```yaml
      user_stories:
        - id: US-001
          description: >
            As a user, I want to reset my password via email so that I can regain account access.
          acceptance_criteria:
            - A reset link is sent to the registered email.
            - The link expires after 24 hours.
          edge_cases:
            - Email address not registered.
            - Reset link reused after expiration.
      metadata:
        agent: requirements_analyzer_agent
        version: 1.0.0
        timestamp: 2025-06-16T21:00:00Z
      ```

    ## Behavior Rules

    Always:

    * Use consistent user story formatting and identifiers.
    * Validate that each story has acceptance criteria.
    * Highlight any ambiguous or missing requirement details.

    Never:

    * Fabricate requirements not present in input.
    * Omit edge-case analysis for complex flows.
    * Assume default behaviors without explicit definitions.

    ## Trigger & Execution

    * This agent runs **after**: prompt_refiner_agent.
    * Triggers **next**: architecture_agent.
    * May be re-invoked if: downstream validation flags missing or conflicting requirements.

    ## Reasoning

    Before generating output, you must:

    * Ensure all functional and non-functional requirements are captured.
    * Assign unique identifiers and maintain consistent formatting.
    * Check for requirement completeness and logical consistency.
    ```
=== "Sample Outputs"

    ```yaml
    result:
      project: "User Authentication"
      requirements:
        - id: FR-001
          title: "Email/Password Authentication"
          description: "Authenticate users with email and password."
          priority: high
          acceptance_criteria:
            - "Valid credentials return JWT token"
            - "Error shown on invalid credentials"
      traceability_matrix:
        - requirement_id: FR-001
          stakeholder: product_manager
          test_cases: [TC-101, TC-102]
    metadata:
      agent: requirements_analyzer_agent
      tags:
        - requirements_spec
        - traceability
    ```



## Integration

- Runs immediately after ideation and planning to formalize requirements.
- Feeds structured specifications to the Architecture Agent for design.
- Cooperates with Prompt Refiner and Documentation Writer Agents in the pipeline.
- Triggered on new requirement submissions or manual review requests.

## Workflow Behavior

- Executes synchronously, offering immediate feedback on requirement quality.
- Supports iterative refinement loops until quality gates are met.
- Logs all analysis steps and validation outcomes for auditing.

## Best Practices

- Supply comprehensive and organized input artifacts for best results.
- Engage stakeholders early and iteratively to refine requirements.
- Store requirements in a central, version-controlled repository.
- Use traceability matrices to monitor coverage and changes.

!!! tip
    Tune `detect_ambiguities` sensitivity and completeness thresholds to adapt analysis depth to project needs.

## Limitations

- Dependent on the quality and completeness of input sources; missing context can lead to gaps.
- Requires domain-specific tuning for specialized industries or regulations.
- Human review is recommended for critical or ambiguous requirements.
- Does not support real-time collaborative editing; analysis must be re-run after updates.