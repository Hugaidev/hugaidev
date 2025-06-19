---
title: Router Agent
description: Dispatches tasks to appropriate HUGAI agents based on metadata, context, and configured strategies, with fallback and retry logic.
---

# :material-robot-outline: Router Agent

!!! info "Overview"
    The Router Agent functions as the central dispatcher within the HUGAI agent network, orchestrating task flow by determining the best agent(s) for each request based on context, priority, and configuration.

## Core

=== "Capabilities"

    - Determine optimal target agent(s) for each task based on metadata and agent capabilities.
    - Chain or parallelize multiple agents to fulfill complex workflows.
    - Apply fallback rules and retry mechanisms for handling failures.
    - Log all routing decisions and maintain audit trails for transparency.
    - Adapt routing strategies dynamically based on performance metrics and project configuration.

=== "Responsibilities"

    - Parse and interpret task metadata (type, priority, source) and available agent registry.
    - Evaluate routing strategies (e.g., priority-first, round-robin, load-based).
    - Dispatch tasks to designated agents and monitor execution outcomes.
    - Handle failures by rerouting tasks according to fallback policies or enqueueing retries.
    - Record routing logs for audit, debugging, and optimization.

=== "Metrics"

    - Routing Accuracy: Percentage of tasks routed to the correct agent on the first attempt.
    - Routing Latency: Average time taken to evaluate and dispatch tasks to target agents.
    - Routing Throughput: Number of routing decisions processed per time period.
    - Fallback Invocation Rate: Percentage of routing operations that trigger fallback logic.
    - Retry Invocation Rate: Percentage of tasks rerouted due to downstream failures.
    - Routing Error Rate: Percentage of routing operations resulting in errors or misroutes.
    - Capability Mismatch Rate: Percentage of tasks dispatched to agents without required capabilities.

    
## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Task definitions (YAML/JSON) including action, payload, and metadata.
    - Agent capability registry (supported task types per agent).
    - Project configuration (routing rules, fallback settings, retry policies).

=== "Outputs"

    - Routing decisions specifying target agent(s), fallback chain, and retry parameters.
    - Task delegation logs with timestamps and routing metadata.
    - Retry queue entries for tasks requiring reprocessing.

=== "Checkpoints"
    - Human Checkpoints:
        - Routing Strategy Approval: Manual validation of routing rules.
    - Automated Gates:
        - Fallback Gate: Enforce fallback policies on task failures.
        - Retry Gate: Verify retry parameters before re-dispatching.
        - Capability Validation Gate: Ensure target agents support dispatched tasks.

    
## Specs

=== "Config"

    ```yaml
    agent:
      name: router_agent
      input_sources:
        - tasks/*.yaml
        - agents/*.yaml
        - config/routing_rules.yaml
      processing_steps:
        - load_capabilities
        - evaluate_rules
        - dispatch_task
        - handle_failures
      strategy: priority_first   # Options: priority_first, round_robin, load_based
      fallbacks_enabled: true
      retry_policy:
        max_attempts: 2
        delay_seconds: 5
      audit_log: true
    ```
=== "Agent Prompt"

    ```markdown
    # System Prompt for Router Agent

    You are the **Router Agent**.  
    Your role is to evaluate incoming tasks, determine the appropriate specialized agent to handle each task, and forward context and artifacts accordingly.

    ## Objective

    Your primary goal is to orchestrate workflow by routing prompts, artifacts, and metadata to the correct downstream agents based on task type, context, and configuration rules.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. You only act when triggered by upstream agents or user requests, and your output must meet strict routing, logging, and consistency requirements.

    ## Responsibilities

    - Inspect task metadata and content to classify task type.
    - Select the target agent (e.g., implementation_agent, test_agent) from the registry.
    - Forward artifacts and context to the chosen agent with required metadata.
    - Handle routing failures by applying fallback rules or escalating to human operators.
    - Maintain routing logs and update workflow state for traceability.

    !!! example "Typical Actions"

        - Route a refined prompt to the Requirements Analyzer Agent.
        - Dispatch code artifacts to the Internal Reviewer Agent after implementation.
        - Forward test results to the Deployment Agent for gating releases.
        - Escalate tasks with no matching agent to a human review queue.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: refined prompts, code modules, documentation, test results.
    - **Metadata**: task ID, domain, pipeline stage, agent registry definitions.
    - **Context**: workflow configuration from `.sdc/config.yaml`, agent capabilities mapping.

    !!! note "Context Sources"

        The AI will have access to:
        - `.sdc/config.yaml` for routing rules and pipeline settings
        - `docs/agents/overview.md` for agent capability summaries
        - Prior agent outputs and workflow state logs

    ## Expected Output

    You must return a YAML routing directive with fields:

      ```yaml
      next_agent: requirements_analyzer_agent
      artifacts:
        - prompt: ref_prompt_123.md
      metadata:
        agent: router_agent
        routed_at: 2025-06-16T22:00:00Z
        reason: matched on task_type 'requirement_analysis'
      ```

    ## Behavior Rules

    Always:

    * Follow routing rules defined in project configuration.
    * Preserve all input metadata and context.
    * Log routing decisions for auditability.

    Never:

    * Drop or alter the task content without explicit rules.
    * Route to an agent without verifying its capabilities.
    * Lose track of workflow execution order.

    ## Trigger & Execution

    * This agent runs **after**: prompt_refiner_agent, requirements_analyzer_agent, or any agent producing new artifacts.
    * Triggers **next**: the agent specified in `next_agent` of your output.
    * May be re-invoked if: downstream agent fails or workflow is retried.

    ## Reasoning

    Before generating output, you must:

    * Evaluate task_type and context against routing rules.
    * Confirm the selected agent supports the required capabilities.
    * Ensure metadata integrity and workflow continuity.
    ```
=== "Sample Outputs"

    ```yaml
    task_id: task-12345
    action: analyze_requirements
    routed_to: requirements_analyzer_agent
    fallbacks:
      - prompt_refiner_agent
    retry_policy:
      max_attempts: 2
      delay_seconds: 5
    metadata:
      agent: router_agent
      tags:
        - routing_decision
        - audit_log
    ```



## Integration

* Positioned at the start of multi-agent workflows to orchestrate task delegation.
* Precedes specialized agents (e.g., Requirements Analyzer, Implementation Agent).
* Works with orchestration tools (CLI, pipelines, event-driven systems).
* Triggered automatically on new task submissions or manually for maintenance.

## Workflow Behavior

* Executes synchronously to provide immediate routing feedback.
* Supports asynchronous dispatch with non-blocking I/O for scalability.
* Applies retry and fallback logic per task or globally.
* Scales horizontally to handle high-throughput routing scenarios.

## Best Practices

* Define clear routing rules that align with project priorities and agent capabilities.
* Maintain centralized, version-controlled routing configurations.
* Monitor routing performance metrics (latency, success rate) to refine strategies.
* Use audit logs to identify bottlenecks and optimize fallback policies.

!!! tip
    Adjust `strategy` and `retry_policy` settings to balance performance, reliability, and latency requirements.

## Limitations

* Dependent on accurate and up-to-date agent capability metadata.
* Complex routing rules can introduce processing overhead and latency.
* Not designed for multi-turn conversational flows without external orchestration.
* Human oversight recommended for critical, high-risk workflows.