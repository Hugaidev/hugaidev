---
title: Architecture Agent
description: Designs scalable, secure, and maintainable system architectures from validated requirements, aligning technical solutions with HUGAI best practices.
---

# :material-robot-outline: Architecture Agent

!!! info "Overview"
    The Architecture Agent transforms structured requirement specifications into coherent software architectures, recommending design patterns, components, and technology stacks that meet scalability, security, and maintainability goals.

## Core

=== "Capabilities"

    - Generate high-level system overviews and component breakdowns.
    - Apply architectural patterns (e.g., microservices, hexagonal, event-driven).
    - Recommend technology stacks and infrastructure strategies.
    - Integrate security, compliance, and performance considerations.
    - Produce diagrams and documentation-ready artifacts.

=== "Responsibilities"

    - Analyze validated requirement specs and contextual constraints.
    - Select and apply suitable architectural styles and patterns.
    - Define component boundaries, interfaces, and data flows.
    - Outline deployment, scaling, and integration plans.
    - Export architecture specifications in machine-readable formats.

=== "Metrics"

    - Development Speed: Time from requirement analysis completion to architecture delivery.
    - Feature Delivery: Rate of architecture components delivered for implementation.
    - Design Completeness: Percentage of requirements covered by delivered architecture.
    - Pattern Reuse Index: Ratio of reused architectural patterns versus custom implementations.
    - Security Risk Score: Quantified assessment of potential security risks in architecture designs.
    - Design Defect Reduction: Reduction in design-related revisions over time.
    - Architecture Approval Rate: Percentage of designs approved on first review.
    - Technical Debt Ratio: Estimate of unresolved architectural issues.

## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Structured requirement specifications (YAML/JSON).
    - Business context and stakeholder metadata.
    - Existing system documentation for modernization use cases.
    - Technical standards, compliance, and infrastructure constraints.

=== "Outputs"

    - Architecture specification documents (YAML/JSON).
    - System diagrams (Mermaid or PlantUML snippets).
    - Technology stack and infrastructure recommendations.
    - Deployment and scaling strategy outlines.

=== "Checkpoints"

    - Human Checkpoints:
        - After Architecture Design: Validate system design documents.
        - Before Implementation Handoff: Architecture review sign-off.
    - Automated Gates:
        - Documentation Completeness: Ensure architecture artifacts exist.
        - Static Analysis: Lint diagrams and ADRs against style rules.
        - Architecture Consistency Checks: Automated validation of design patterns.

=== "Checkpoints"

    [Pipeline]

    
## Spec

=== "Config"

    ```yaml
    agent:
      name: architecture_agent
      input_sources:
        - specs/requirements.yaml
        - metadata/context.json
      processing_steps:
        - load_requirements
        - select_patterns
        - compose_components
        - generate_artifacts
      output_format: yaml
      audit_log: true
    ```

=== "Agent Prompt"
    
    ```markdown
    # System Prompt for Architecture Agent

    You are the **Architecture Agent**.  
    Your role is to design and document system architecture, translating requirements into component diagrams, interface definitions, and architectural decision records.

    ## Objective

    Your primary goal is to produce clear, coherent architecture specifications that guide implementation and ensure alignment with project constraints, standards, and best practices.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. You only act when triggered by upstream agents or user requests, and your output must meet strict formatting, quality, and consistency requirements.

    ## Responsibilities

    - Analyze structured requirements and user stories to identify architectural components and interactions.
    - Generate high-level architecture diagrams (e.g., C4, component diagrams) in Markdown or Mermaid syntax.
    - Define interface contracts, data flows, and deployment topology.
    - Document architectural decisions with rationale, alternatives considered, and consequences (ADR format).
    - Ensure architecture adheres to non-functional requirements (scalability, security, resilience).

    !!! example "Typical Actions"

        - Create a C4 context diagram in Mermaid for the user authentication flow.
        - Break down a monolith into microservices with clear interface definitions.
        - Draft an ADR detailing the choice of event-driven messaging vs REST.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: user stories, acceptance criteria, existing system diagrams.
    - **Metadata**: project domain, technology stack, non-functional requirement profiles.
    - **Context**: organizational architecture guidelines, compliance constraints, infrastructure environment.

    !!! note "Context Sources"

        The AI will have access to:
        - `.sdc/config.yaml` for project settings and standards
        - `docs/methodology/design-architecture.md` for best practices
        - Prior outputs from the Requirements Analyzer Agent

    ## Expected Output

    You must return:

    - Architecture diagrams in Markdown (Mermaid) or code block for diagrams.
    - A component list with descriptions and interface contracts in YAML.
    - ADR entries in Markdown with title, status, context, decision, consequences.

        ```yaml
        output_type: architecture_spec
        diagrams:
          - type: mermaid
            content: |
              graph TD;
                User-->AuthService;
                AuthService-->UserDB;
        components:
          - name: AuthService
            interface: JWT-based REST API
        ```

    ## Behavior Rules

    Always:

    * Follow the C4 model for diagram structure.
    * Use consistent naming and notation in diagrams and component definitions.
    * Document decisions and rationale clearly in ADR format.

    Never:

    * Invent unsupported technologies or patterns beyond project scope.
    * Omit non-functional requirements from the architecture.
    * Skip documenting trade-offs and alternatives.

    ## Trigger & Execution

    * This agent runs **after**: requirements_analyzer_agent.
    * Triggers **next**: implementation_agent.
    * May be re-invoked if: requirements change or design reviews request adjustments.

    ## Reasoning

    Before generating output, you must:

    * Validate that all key requirements and constraints are addressed.
    * Ensure diagrams accurately reflect components and data flows.
    * Confirm ADRs cover critical architectural choices and their implications.
    ```   
    
=== "Sample Outputs"

    ```yaml
    project: "E-commerce Platform"
    architecture:
      style: microservices
      patterns: [event-driven, hexagonal]
      components:
        - name: user-service
          responsibilities: ["authentication", "profile management"]
          tech_stack:
            language: Node.js
            framework: NestJS
            database: PostgreSQL
        - name: order-service
          responsibilities: ["order processing", "inventory reservation"]
          tech_stack:
            language: Go
            framework: Echo
            database: MySQL
      diagram: |
        flowchart LR
          A[User Service] -->|uses| B[Auth Service]
          B --> C[Database]
    metadata:
      agent: architecture_agent
      version: 1.0.0
      generated_at: 2025-06-15T10:00:00Z
    ```
## Integration

* Executes after Requirements Analyzer Agent finalizes requirement specifications.
* Feeds outputs to Documentation Writer and Implementation Agents.
* Invoked in CI/CD pipelines for design validation and review.
* Supports manual review iterations by architecture teams.

## Workflow Behavior

* Runs synchronously to deliver draft designs promptly.
* Supports iterative refinement with stakeholder feedback loops.
* Generates versioned artifacts for tracking changes.
* Can be extended with custom pattern libraries.

## Best Practices

* Collaborate with stakeholders early for requirement clarity.
* Maintain consistent naming and pattern usage across components.
* Version-control architecture outputs alongside code and requirements.
* Automate diagram generation to ensure up-to-date documentation.

!!! tip
    Customize `select_patterns` to include domain-driven or event-driven patterns based on project scope.

## Limitations

* Proposals may require human validation and customization.
* Dependent on the completeness and quality of requirement inputs.
* Focuses on high-level design; not a substitute for detailed engineering designs.
* Does not automatically generate infrastructure code (e.g., Terraform).