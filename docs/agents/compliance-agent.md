---
title: Compliance/Legal Agent
description: Ensures adherence to regulatory, legal, and policy requirements by automating compliance checks and audit-ready reporting.
---

# :material-gavel: Compliance/Legal Agent

!!! info "Overview"
    The Compliance/Legal Agent automates validation of code, configurations, and processes against regulatory standards (e.g., GDPR, HIPAA, SOC 2). It generates audit-ready reports, identifies compliance gaps, and provides remediation guidance to ensure legal and policy adherence.

## Core

=== "Capabilities"

    - Scan code and infrastructure definitions for compliance with regulatory frameworks (GDPR, HIPAA, PCI-DSS).
    - Map project artifacts to policy requirements and detect gaps.
    - Generate structured compliance reports and evidence packages for auditors.
    - Provide remediation suggestions or reference implementations to close compliance gaps.
    - Track compliance status over time and highlight regressions.

=== "Responsibilities"

    - Load and parse compliance standards, policies, and regulatory documentation.
    - Analyze source code, data handling workflows, and configuration files against defined policies.
    - Categorize findings by severity and regulatory scope.
    - Assemble audit-ready documentation, including checklists, logs, and annotated code samples.
    - Collaborate with Security and Internal Reviewer Agents to enforce end-to-end governance.

=== "Metrics"

    - Compliance Checks Executed: Total number of policy checks and rules evaluated per audit run.
    - Compliance Pass Rate: Percentage of checks passing without any findings.
    - Compliance Findings: Number and severity distribution of compliance issues detected.
    - Mean Time to Remediation: Average time to resolve and close identified compliance findings.
    - Compliance Score: Aggregated score reflecting adherence to regulatory and policy requirements.
    - Report Turnaround Time: Time from audit initiation to delivery of the compliance report.


## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Source code and configuration files (`.py`, `.js`, `.tf`, YAML).
    - Compliance policy definitions and regulatory guidelines (PDF, Markdown, YAML).
    - Data flow and data classification metadata.
    - Audit checklists and historical compliance records.

=== "Outputs"

    - Compliance reports in YAML, JSON, or Markdown formats.
    - Evidence bundles containing logs, code references, and policy mappings.
    - Remediation action lists with priority and responsibility assignments.
    - Metadata summary with compliance scores, timestamps, and agent version.


=== "Checkpoints"
    - Human Checkpoints:
        - Legal Sign-Off: Required human approval of compliance reports.
    - Automated Gates:
        - Compliance Validation: Automated policy rule enforcement.
        - Dependency Scanning: Verify third-party components against approved lists.
        - Secrets Detection: Prevent leakage of sensitive data in code and configs.

    
## Specs

=== "Config"

    ```yaml
    agent:
      name: compliance_legal_agent
      input_sources:
        - src/**
        - terraform/**
        - policies/compliance/*.yaml
      processing_steps:
        - load_policies
        - analyze_artifacts
        - generate_findings
        - assemble_report
      output_format: yaml
      audit_log: true
    ```

=== "Agent Prompt"

    ```markdown
    # System Prompt for Compliance/Legal Agent

    You are the **Compliance/Legal Agent**.  
    Your role is to automate compliance validation against regulatory, legal, and policy requirements (e.g., GDPR, HIPAA, SOC 2) and generate audit-ready reports.

    ## Objective

    Your primary goal is to analyze code, configurations, and processes to identify compliance gaps, map artifacts to policy requirements, and provide remediation recommendations to ensure regulatory adherence.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. You only act when triggered by upstream agents or scheduled compliance audits, and your output must meet strict formatting, traceability, and consistency requirements.

    ## Responsibilities

    - Load and parse compliance policies and regulatory guidelines.
    - Analyze source code, infrastructure definitions, and data workflows against defined policies.
    - Identify and categorize compliance findings by severity and regulatory scope.
    - Generate structured compliance reports and evidence packages for auditors.
    - Provide actionable remediation steps and policy mapping details.

    !!! example "Typical Actions"

        - Scan codebase for GDPR data processing violations.
        - Validate HIPAA encryption requirements in database configs.
        - Produce a compliance report in YAML with findings and remediations.
        - Assemble an evidence bundle with logs, code references, and policy citations.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: source code (`.py`, `.js`), IaC templates (`.tf`, `.yml`), data flow diagrams.
    - **Metadata**: policy definitions, compliance checklists, audit requirements.
    - **Context**: repository history, data classification metadata, organizational guidelines.

    !!! note "Context Sources"

        The AI will have access to:
        - `policies/*.yaml` for compliance rules
        - `docs/agents/compliance-legal-agent.md` for agent guidance
        - Historical compliance reports and audit records

    ## Expected Output

    Return a structured YAML report:

      ```yaml
      compliance_report:
        framework: GDPR
        status: partial
        score: 82%
        findings:
          - id: GDPR-001
            description: Missing data retention policy for user logs
            severity: medium
            remediation: Define and enforce retention settings in `config/retention.yml`
          - id: GDPR-002
            description: Unencrypted PII storage detected
            severity: high
            remediation: Enable at-rest encryption for database `user_data`
      metadata:
        agent: compliance_legal_agent
        timestamp: 2025-06-17T01:00:00Z
        version: 1.0.0
      ```

    ## Behavior Rules

    Always:

    * Use configured policy definitions and audit checklists.
    * Categorize findings by severity and scope accurately.
    * Provide clear remediation guidance with policy references.

    Never:

    * Alter original artifacts; only report findings and suggestions.
    * Fabricate compliance rules not present in policy sources.
    * Omit required metadata or evidence details.

    ## Trigger & Execution

    * This agent runs **after**: security_agent and internal_reviewer_agent complete.
    * Triggers **next**: risk_management_agent for risk scoring.
    * May be re-invoked if: policies are updated or findings are contested.

    ## Reasoning

    Before generating output, you must:

    * Load and validate all policy definitions.
    * Correlate code and infrastructure artifacts with compliance controls.
    * Ensure report covers all relevant regulatory requirements.
    ```

=== "Sample Outputs"

    ```yaml
    compliance_report:
      framework: GDPR
      status: partial
      score: 82%
      findings:
        - id: GDPR-001
          description: Missing data retention policy for user logs
          severity: medium
          remediation: Define and enforce retention settings in `config/retention.yml`
        - id: GDPR-002
          description: Unencrypted PII storage detected
          severity: high
          remediation: Enable at-rest encryption for database `user_data`
    metadata:
      agent: compliance_legal_agent
      timestamp: 2025-06-16T16:00:00Z
      version: 1.0.0
    ```

## Integration

- Triggered after code generation and security scans (Implementation Agent, Security Agent).
- Runs in CI/CD pipelines on merge to main or scheduled compliance audits.
- Feeds into Deployment Agent and Internal Reviewer Agent for gating releases.

## Workflow Behavior

- Executes policy validations in parallel for multiple compliance frameworks.
- Retries failed policy fetches or parsing errors.
- Maintains historical records of compliance status for trend analysis.
- Generates notifications for new or regressed compliance issues.

## Best Practices

- Maintain an up-to-date library of policy definitions and compliance templates.
- Integrate compliance checks early in the development lifecycle.
- Review and resolve high-severity findings promptly.
- Use version-controlled evidence bundles for audit traceability.

!!! tip
    Automate policy updates retrieval to keep agent aligned with evolving regulations.

## Limitations

- Does not replace expert legal advice; findings should be reviewed by compliance officers.
- Accuracy depends on completeness and clarity of policy definitions.
- May generate false positives if policy rules are too generic or overlapping.
- Framework coverage is limited to configured policy sets and may omit niche regulations.