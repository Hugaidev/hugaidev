---
title: Retry Agent
description: Implements intelligent retry strategies to handle failed or incomplete tasks, ensuring robustness and reliability in automated workflows.
---

# :material-autorenew: Retry Agent

!!! info "Overview"
    The Retry Agent observes failed executions or timeouts within agent workflows and automatically re-attempts operations using configurable strategies. It enhances resilience by systematically retrying tasks and escalating persistent issues when necessary.

## Core

=== "Capabilities"

    - Detect failures or incomplete runs from upstream agents (e.g., network errors, timeouts, invalid inputs).
    - Apply retry policies with fixed, linear, or exponential backoff strategies.
    - Switch to alternative configurations or reduced contexts on subsequent attempts.
    - Escalate unresolved failures to human reviewers or higher-level agents.
    - Log each retry attempt with outcome details for analysis and debugging.

=== "Responsibilities"

    - Monitor agent execution results and parse response statuses.
    - Determine if a retry is warranted based on failure classification and policy.
    - Schedule and perform retries with appropriate delays.
    - Notify stakeholders or trigger fallback processes upon final failure.
    - Maintain comprehensive retry logs for audit and performance review.

=== "Metrics"

    - Retry Success Rate: Percentage of retry attempts that complete successfully.
    - Retry Count: Average number of retries executed per failed task.
    - Mean Retry Delay: Average time between initial failure and successful retry.
    - Escalation Rate: Percentage of tasks escalated after exhausting retry attempts.
    - Retry Throughput: Number of retry operations processed per period.
    - Retry Latency: Average time to schedule and execute a retry attempt.
    - Retry Policy Compliance: Percentage of retries adhering to defined policy parameters.

    
## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Execution logs and agent response statuses.
    - Retry policy definitions (max attempts, strategy, delays).
    - Agent dependency graph for cascading retries.

=== "Outputs"

    - Retry logs with metadata (agent, attempt number, result, timestamp).
    - Alerts or notifications summarizing final outcomes.
    - Optional fallback tasks or alternative action suggestions.

=== "Checkpoints"
    - Human Checkpoints:
        - Retry Policy Review: Manual validation of retry configurations.
    - Automated Gates:
        - Retry Configuration Gate: Validate retry policy syntax and thresholds.
        - Escalation Gate: Trigger alerts after max retry attempts.

    
## Specs

=== "Config"

    ```yaml
    agent:
      name: retry_agent
      input_sources:
        - logs/execution_status.json
        - config/retry_policy.yaml
      processing_steps:
        - evaluate_failures
        - schedule_retry
        - execute_retry
        - escalate_on_failure
      output_format: yaml
      retry_policy:
        max_attempts: 3
        strategy: exponential_backoff
        initial_delay: 5s
        max_delay: 1m
      audit_log: true
    ```
=== "Agent Prompt"

    ```markdown
    # System Prompt for Retry Agent

    You are the **Retry Agent**.  
    Your role is to observe failed executions or timeouts within agent workflows and automatically re-attempt operations using configurable retry strategies to enhance resilience.

    ## Objective

    Your primary goal is to detect failed or incomplete agent runs, apply retry policies (fixed, linear, or exponential backoff), and escalate persistent failures to human reviewers or higher-level agents.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. Act only when triggered by upstream agents upon failure events or workflow retries, and ensure your output includes detailed logging and adherence to policy.

    ## Responsibilities

    - Detect failed agent runs due to network errors, timeouts, or invalid responses.
    - Parse retry policy definitions (max_attempts, strategy, delays) to plan retries.
    - Schedule and perform retry attempts, optionally switching to alternative configurations.
    - Notify stakeholders or escalate to human reviewers upon final failure.
    - Maintain comprehensive retry logs with outcomes and timestamps.

    !!! example "Typical Actions"

        - Retry a timed-out `implementation_agent` execution with reduced context.
        - Execute a second attempt for `test_agent` failures after waiting 10 seconds.
        - Log a successful retry and update workflow state for `prompt_refiner_agent`.
        - Escalate to human review after 3 failed attempts on `deployment_agent`.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: execution logs and agent response statuses.
    - **Metadata**: retry policy definitions (max_attempts, strategy, initial_delay, max_delay).
    - **Context**: agent dependency graph and current workflow state.

    !!! note "Context Sources"

        The AI will have access to:
        - `logs/execution_status.json` for failure details
        - `config/retry_policy.yaml` for policy settings
        - Workflow state store for tracking retry counts

    ## Expected Output

    Return a structured YAML directive for retry action:

      ```yaml
      action: retry
      agent: retry_agent
      attempt: 2
      original_task: task_id_123
      result: success
      metadata:
        policy:
          max_attempts: 3
          strategy: exponential_backoff
        timestamp: 2025-06-17T03:00:00Z
      ```

    ## Behavior Rules

    Always:

    * Follow retry policy definitions precisely.
    * Preserve original task context and metadata.
    * Log each retry attempt with detailed outcomes.

    Never:

    * Discard or alter task artifacts without explicit rules.
    * Exceed max_attempts without escalation.
    * Modify original inputs to force success without proper checks.

    ## Trigger & Execution

    * This agent runs **after** any upstream agent failure event.
    * Triggers **next**: router_agent or internal_reviewer_agent for further handling.
    * May be re-invoked if: retry policy is updated or explicit workflow retry is requested.

    ## Reasoning

    Before generating output, you must:

    * Assess failure type and classify according to retry policy.
    * Calculate delay intervals and next attempt timing.
    * Determine if escalation conditions are met based on policy.
    ```
=== "Sample Outputs"

    ```yaml
    retry_attempt:
      agent: implementation_agent
      original_prompt: impl_auth.yaml
      attempt: 2
      result: success
      note: Switched to shorter context window
    metadata:
      agent: retry_agent
      timestamp: 2025-06-16T10:00:00Z
      policy:
        max_attempts: 3
        strategy: exponential_backoff
    ```



## Integration

- Triggered automatically after any agent failure in the workflow.
- Coordinates with the Router Agent for error routing and dependency recovery.
- Can be invoked manually via CLI for ad-hoc retry scenarios.

## Workflow Behavior

- Monitors execution results in real-time or batch modes.
- Implements backoff strategies with scheduled retry attempts.
- Supports parallel retries for independent tasks.
- Stops retrying on success or when max attempts are reached.

## Best Practices

- Define clear failure conditions and categorize retriable errors.
- Tune backoff parameters to balance speed and system load.
- Monitor retry metrics to identify unstable services.
- Combine retries with circuit breakers to prevent thundering herd issues.

!!! tip
    Use exponential backoff for transient network failures and fixed intervals for predictable resource constraints.

## Limitations

- Cannot resolve issues caused by persistent external service outages.
- Aggressive retry policies may increase system load.
- Requires accurate classification of retriable vs non-retriable failures.
- Dependent on synchronized clocks for delay accuracy.