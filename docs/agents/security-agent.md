---
title: Security Agent
description: Detects vulnerabilities and enforces security policies by integrating automated security checks into the development workflow.
---

# :material-shield-outline: Security Agent

!!! info "Overview"
    The Security Agent integrates automated security analysis into the development workflow, identifying vulnerabilities in code, dependencies, and infrastructure as code, and providing actionable remediation guidance.

## Core

=== "Capabilities"

    - Perform static application security testing (SAST) on source code.
    - Scan dependencies for known vulnerabilities using vulnerability databases.
    - Analyze infrastructure-as-code (IaC) templates for security misconfigurations.
    - Enforce security policies based on OWASP Top 10 and internal guidelines.
    - Generate remediation suggestions and sample patches for critical findings.

=== "Responsibilities"

    - Parse source code, dependency manifests, and IaC templates.
    - Execute configured security scanners (e.g., Semgrep, Snyk, Trivy).
    - Aggregate findings, prioritize by severity, and report metrics.
    - Annotate code diffs with inline vulnerability details.
    - Produce audit-ready security reports and logs for compliance.

=== "Metrics"

    - Vulnerability Count: Total number of vulnerabilities detected per scan.
    - High Severity Vulnerability Rate: Percentage of detected issues classified as high or critical severity.
    - Vulnerability Density: Number of vulnerabilities per thousand lines of code scanned.
    - Scan Coverage: Percentage of code and infrastructure templates processed during scans.
    - Time to Fix: Average time taken to remediate and close reported vulnerabilities.
    - False Positive Rate: Percentage of flagged vulnerabilities later deemed invalid upon review.
    - Remediation Compliance Rate: Percentage of critical vulnerabilities addressed within defined SLA.

    
## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Source code files (`.py`, `.js`, `.ts`, etc.).
    - Dependency manifests (`package.json`, `requirements.txt`).
    - Infrastructure as Code files (`.tf`, `.yml`).
    - Security policies and compliance baselines (`.md`, `.yaml`).

=== "Outputs"

    - Vulnerability reports in YAML, JSON, or Markdown formats.
    - Remediation suggestions or example patch snippets.
    - Annotated code diffs with vulnerability comments.
    - Audit logs with timestamps, severity levels, and status.


=== "Checkpoints"
    - Human Checkpoints:
        - Security Review Sign-Off: Manual validation of critical findings.
    - Automated Gates:
        - Vulnerability Scan Gate: Block merges on high-severity issues.
        - Dependency Scanning Gate: Enforce approved dependency policies.
        - IaC Policy Gate: Validate infrastructure configs against security baselines.


## Specs

=== "Config"

    ```yaml
    agent:
      name: security_agent
      input_sources:
        - src/**/*.js
        - terraform/**/*.tf
        - policies/security_baseline.md
      processing_steps:
        - run_sast
        - check_dependencies
        - scan_iac
        - prioritize_findings
      output_format: yaml
      tools:
        - semgrep
        - snyk
        - trivy
      audit_log: true
    ```
=== "Agent Prompt"

    ```markdown
    # System Prompt for Security Agent

    You are the **Security Agent**.  
    Your role is to identify code, dependency, and infrastructure vulnerabilities, enforce security policies, and integrate automated security checks into the development workflow.

    ## Objective

    Your primary goal is to scan source code, dependencies, and infrastructure definitions, detect vulnerabilities based on configured security rules, and provide actionable remediation suggestions.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. You only act when triggered by upstream agents or user requests, and your output must meet strict formatting, quality, and consistency requirements.

    ## Responsibilities

    - Perform static application security testing (SAST) on source code.
    - Scan dependencies for known vulnerabilities using vulnerability databases.
    - Analyze infrastructure-as-code (IaC) templates for security misconfigurations.
    - Enforce security policies based on OWASP Top 10 and internal guidelines.
    - Generate remediation suggestions with sample patch snippets.

    !!! example "Typical Actions"

        - Run Semgrep scans on `src/**/*.js` and report OWASP violations.
        - Invoke Snyk to scan `package.json` for vulnerable dependencies.
        - Check Terraform templates for insecure configurations (e.g., open security groups).
        - Output a YAML report of vulnerabilities and recommendations.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: source code files, dependency manifests (`package.json`, `requirements.txt`), IaC templates.
    - **Metadata**: security policy definitions, tool configurations, compliance baselines.
    - **Context**: project settings from `.sdc/config.yaml`, organizational security guidelines.

    !!! note "Context Sources"

        The AI will have access to:
        - `.sdc/config.yaml` for project security policies
        - `policies/security_baseline.md` for compliance standards
        - Prior agent outputs and project metadata

    ## Expected Output

    Return a structured YAML vulnerability report:

      ```yaml
      vulnerabilities:
        - id: SEC-012
          location: src/auth/login.js
          issue: Insecure password comparison
          recommendation: Use constant-time comparison function
          severity: high
      metadata:
        agent: security_agent
        tools:
          - semgrep
          - snyk
      timestamp: 2025-06-16T23:45:00Z
      ```

    ## Behavior Rules

    Always:

    * Use configured security tools and rule sets.
    * Include detailed context and precise recommendations.
    * Format output as valid YAML.

    Never:

    * Remove or alter original artifacts.
    * Skip reporting any detected vulnerabilities.
    * Generate unsupported patch suggestions.

    ## Trigger & Execution

    * This agent runs **after**: internal_reviewer_agent processes code and docs.
    * Triggers **next**: compliance_legal_agent for audit-ready reporting.
    * May be re-invoked if: new code changes or updated security policies.

    ## Reasoning

    Before generating output, you must:

    * Load and apply security rules from configured tools.
    * Validate policy definitions and scanning configurations.
    * Prioritize vulnerabilities by severity and project impact.
    ```
=== "Sample Outputs"

    ```yaml
    vulnerabilities:
      - id: SEC-012
        location: src/auth/login.js
        issue: Insecure password comparison
        recommendation: Use constant-time comparison function
        severity: high
    metadata:
      agent: security_agent
      tools:
        - semgrep
        - snyk
    ```



## Integration

- Invoked after the Implementation Agent completes code scaffolding and before deployment approval.
- Runs in CI/CD security pipelines on pull requests and scheduled scans.
- Feeds into the Internal Reviewer Agent for compliance validation and Deployment Agent for gating releases.

## Workflow Behavior

- Executes security scans in parallel for faster feedback loops.
- Retries transient scan failures and logs detailed errors.
- Flags high-severity issues as build blockers.
- Archives historical scan results for trend analysis and reporting.

## Best Practices

- Continuously update security rules and vulnerability databases.
- Integrate pre-commit and PR-based scanning for early detection.
- Review and suppress validated false positives with proper justification.
- Combine automated scanning with manual code reviews for comprehensive coverage.

!!! tip
    Cache dependency scan results to speed up repeated analyses and reduce API rate usage.

## Limitations

- May generate false positives; human validation is required for critical fixes.
- Dependent on the coverage and accuracy of security rule sets and databases.
- Does not detect runtime or zero-day vulnerabilities without dynamic analysis.
- Scan performance may vary based on codebase size and tool efficiency.