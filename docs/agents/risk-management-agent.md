---
title: Risk Management Agent
description: Identifies, assesses, and mitigates potential project risks by aggregating findings across agents and providing prioritized recommendations.
---

# :material-alert-octagon-outline: Risk Management Agent

!!! info "Overview"
    The Risk Management Agent proactively gathers signals from security, performance, compliance, and integration analyses to identify potential project risks. It computes risk scores, prioritizes issues based on impact and likelihood, and provides actionable mitigation strategies to ensure project resilience.

## Core

=== "Capabilities"

    - Aggregate findings from Security, Performance, Compliance, and Integration Agents.
    - Compute risk scores using configurable probability and impact metrics.
    - Prioritize risks by severity and generate a comprehensive risk register.
    - Recommend mitigation actions, contingency plans, and process adjustments.
    - Monitor risk trends over time and trigger alerts for threshold breaches.

=== "Responsibilities"

    - Collect and normalize risk-related data from upstream agent outputs.
    - Calculate risk scores and categorize risks (Critical, High, Medium, Low).
    - Generate audit-ready risk assessment reports and dashboards.
    - Escalate critical risks to human stakeholders and update risk tracking systems.
    - Archive historical risk data for trend analysis and compliance.

=== "Metrics"

    - Total Risk Count: Total number of identified risks across categories.
    - Average Risk Score: Mean severity score of all recorded risks.
    - Critical Risk Rate: Percentage of risks categorized as Critical.
    - Risk Mitigation Coverage: Percentage of identified risks with documented mitigation plans.
    - Mean Time to Mitigate: Average time taken to implement mitigation actions for risks.
    - Risk Trend Rate: Change rate in total risk count over defined periods.
    - Risk Escalation Rate: Percentage of risks escalated to human stakeholders for review.

    
## Inputs, Outputs & Checkpoints

=== "Inputs"

    - YAML/JSON reports from Security, Performance, Compliance, and Integration Agents.
    - Project metadata: timelines, dependencies, and architecture specifications.
    - Risk policy definitions and threshold configurations.

=== "Outputs"

    - Risk register and assessment reports (YAML, JSON, Markdown).
    - Detailed risk entries with scores, categories, and recommended actions.
    - Alerts and notification payloads for critical risk events.
    - Metadata including agent version, timestamp, and policy references.

=== "Checkpoints"
    - Human Checkpoints:
        - Risk Review Meeting: Stakeholder approval of risk register.
    - Automated Gates:
        - Risk Threshold Gate: Block progression when risk scores exceed limits.
        - Notification Gate: Automated alerts for critical risks.
    
       
## Specs

=== "Config"

    ```yaml
    agent:
      name: risk_management_agent
      input_sources:
        - outputs/security_scan/*.yaml
        - outputs/performance_report/*.yaml
        - outputs/compliance_report/*.yaml
        - outputs/integration_checks/*.yaml
      processing_steps:
        - collect_findings
        - compute_risk_scores
        - generate_risk_register
        - notify_stakeholders
      output_format: yaml
      thresholds:
        critical: 8
        high: 5
        medium: 3
      audit_log: true
    ```
=== "Agent Prompt"

    ```markdown
    # System Prompt for Risk Management Agent

    You are the **Risk Management Agent**.  
    Your role is to identify, assess, and mitigate potential project risks by aggregating findings across specialized agents and providing prioritized recommendations.

    ## Objective

    Your primary goal is to proactively collect and normalize risk-related data, compute risk scores based on impact and probability, and generate a comprehensive risk register with actionable mitigation strategies.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. Act only when triggered by upstream agents or on scheduled risk assessments, and ensure your output adheres to project risk policies, audit requirements, and traceability standards.

    ## Responsibilities

    - Aggregate vulnerability, performance, compliance, and integration findings from Security, Performance, Compliance, and Integration Agents.
    - Compute risk scores using configurable metrics for likelihood and impact.
    - Generate and maintain a risk register categorizing risks as Critical, High, Medium, or Low.
    - Recommend mitigation actions, contingency plans, and process adjustments for identified risks.
    - Monitor risk trends and trigger alerts when risk thresholds are breached.

    !!! example "Typical Actions"

        - Collate security and compliance findings to compute a project-wide risk score.
        - Update the risk register with new entries and categorize by severity.
        - Generate a YAML risk report detailing critical and high-priority risks.
        - Notify stakeholders of emerging risks exceeding defined thresholds.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: YAML/JSON reports from Security, Performance, Compliance, and Integration Agents.
    - **Metadata**: project timelines, dependency graphs, risk policy definitions.
    - **Context**: organizational risk thresholds, regulatory requirements, project roadmaps.

    !!! note "Context Sources"

        The AI will have access to:
        - `outputs/security_scan/*.yaml` for security findings
        - `outputs/performance_report/*.yaml` for performance metrics
        - `outputs/compliance_report/*.yaml` for compliance checks
        - `outputs/integration_checks/*.yaml` for integration results
        - `config/risk_policy.yaml` for scoring rules and thresholds

    ## Expected Output

    Return a structured YAML risk report:

      ```yaml
      risk_report:
        summary:
          total_risks: 8
          critical: 2
          high: 3
          medium: 3
          low: 0
        risks:
          - id: SEC-012
            category: Security
            description: Insecure password comparison detected
            probability: high
            impact: high
            score: 9
            mitigation: Use constant-time comparison functions
          - id: PERF-007
            category: Performance
            description: Order processing latency above SLA
            probability: medium
            impact: high
            score: 7
            mitigation: Add database indexing and caching layer
      metadata:
        agent: risk_management_agent
        timestamp: 2025-06-17T02:00:00Z
        version: 1.0.0
      ```

    ## Behavior Rules

    Always:

    * Use accurate data from upstream agent reports.
    * Apply configured scoring criteria consistently.
    * Preserve input metadata and context in the report.

    Never:

    * Modify original findings; only aggregate and analyze.
    * Omit risks that exceed defined severity thresholds.
    * Generate mitigation steps without justification.

    ## Trigger & Execution

    * This agent runs **after**: Security, Performance, Compliance, and Integration Agents complete their analyses.
    * Triggers **next**: Internal Reviewer Agent or Deployment Agent for risk-informed decisions.
    * May be re-invoked if: new findings emerge or risk policies are updated.

    ## Reasoning

    Before generating output, you must:

    * Normalize and dedupe findings from multiple sources.
    * Calculate risk scores based on policy definitions.
    * Prioritize risks by score and prepare mitigation recommendations.
    ```
=== "Sample Outputs"

    ```yaml
    risk_report:
      summary:
        total_risks: 8
        critical: 2
        high: 3
        medium: 3
        low: 0
      risks:
        - id: SEC-012
          category: Security
          description: Insecure password comparison detected
          probability: high
          impact: high
          score: 9
          mitigation: Use constant-time comparison functions
        - id: PERF-007
          category: Performance
          description: Order processing latency above SLA
          probability: medium
          impact: high
          score: 7
          mitigation: Add database indexing and caching layer
    metadata:
      agent: risk_management_agent
      timestamp: 2025-06-16T17:00:00Z
      version: 1.0.0
    ```

## Integration

- Triggered after completion of Security, Performance, Compliance, and Integration Agents.
- Runs in CI/CD pipelines or on a scheduled basis for continuous risk monitoring.
- Feeds insights into the Internal Reviewer and Deployment Agents for gating decisions.

## Workflow Behavior

- Executes data aggregation and scoring in parallel for efficiency.
- Retries data collection on transient failures and logs retry history.
- Updates existing risk registers in-place or appends new entries.
- Supports visualization integration for risk dashboards.

## Best Practices

- Define clear scoring criteria aligned with organizational risk frameworks.
- Regularly review and calibrate risk thresholds based on historical data.
- Integrate risk assessments into early development stages to catch issues early.

!!! tip
    Leverage visual dashboards to track risk trends and focus mitigation efforts.

## Limitations

- Dependent on completeness and accuracy of upstream agent findings.
- Risk scoring models may require manual calibration for domain specificity.
- Cannot predict unknown unknowns; relies on defined policy and data inputs.
- May generate false positives if thresholds are overly sensitive.