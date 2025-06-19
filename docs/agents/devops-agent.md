---
title: DevOps Agent
description: Automates infrastructure provisioning, CI/CD pipeline configuration, and operational tooling to support reliable application delivery.
---

# :material-server-network-outline: DevOps Agent

!!! info "Overview"
    The DevOps Agent automates key operational tasks, including provisioning infrastructure, configuring CI/CD pipelines, and setting up observability tooling to ensure consistent, reproducible, and secure application deployments.

## Core

=== "Capabilities"

    - Scaffold and validate CI/CD pipeline configurations (GitHub Actions, GitLab CI, etc.).
    - Provision infrastructure templates (Terraform, Pulumi, CloudFormation).
    - Configure monitoring, logging, and alerting setups.
    - Suggest improvements based on build/test/deploy history and metrics.

=== "Responsibilities"

    - Parse repository and project configurations to determine pipeline and infrastructure requirements.
    - Generate and validate CI/CD workflows and infrastructure-as-code templates.
    - Integrate monitoring and alerting configurations into deployment artifacts.
    - Provide recommendations for pipeline optimizations and infrastructure hardening.

=== "Metrics"

    - Pipeline Success Rate: Percentage of CI/CD pipeline runs completing successfully.
    - Average Pipeline Duration: Mean time taken for CI/CD pipeline executions.
    - Provisioning Time: Average duration to provision infrastructure resources.
    - Provisioning Success Rate: Percentage of infrastructure provisioning runs without errors.
    - Infrastructure Drift Detection Rate: Percentage of resources detected out of declared state.
    - Provisioning Frequency: Number of infrastructure changes applied per period.
    - Secrets Compliance Rate: Percentage of secrets managed and rotated according to policy.

    
## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Repository structure and source code.
    - Project YAML or JSON configuration files.
    - Deployment and infrastructure policy definitions.
    - Build artifacts and version metadata.

=== "Outputs"

    - CI/CD pipeline files (e.g., `.github/workflows/ci.yml`).
    - Infrastructure-as-code templates (`main.tf`, `pulumi.yaml`).
    - Observability configuration (dashboards, alert rules).
    - Change logs and configurable runbooks.

=== "Checkpoints"
    - Human Checkpoints:
        - Infrastructure Design Review: Approval of provisioning configurations.
    - Automated Gates:
        - CI/CD Gate Enforcement: Block progression on pipeline failures.
        - Environment Compliance Check: Validate infrastructure against policies.
        - Secrets Management Gate: Verify proper handling of credentials.

    
## Specs

=== "Config"

    ```yaml
    agent:
      name: devops_agent
      input_sources:
        - repo/config.yaml
        - build/spec.yaml
        - policies/infra/*.yaml
      processing_steps:
        - scaffold_ci_cd
        - provision_infra
        - configure_observability
        - suggest_improvements
      ci_cd_tool: github
      infra_tool: terraform
      prompt_type: pipeline+infra_provision
      output_format: yaml
      audit_log: true
      post_actions:
        - run_config_linter
        - simulate_pipeline_dryrun
    ```
=== "Agent Prompt"

    ```markdown
    # System Prompt for DevOps Agent

    You are the **DevOps Agent**.  
    Your role is to automate infrastructure provisioning, CI/CD pipeline configuration, and operational tooling to support reliable application delivery.

    ## Objective

    Your primary goal is to scaffold and validate CI/CD workflows, provision infrastructure-as-code templates, and set up observability and alerting configurations according to project policies and best practices.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. You only act when triggered by upstream agents or user requests, and your output must adhere to repository configuration, security policies, and infrastructure standards.

    ## Responsibilities

    - Generate and validate CI/CD pipeline configurations (e.g., GitHub Actions, GitLab CI).
    - Provision infrastructure templates (Terraform, Pulumi, CloudFormation) for target environments.
    - Configure monitoring, logging, and alerting resources.
    - Suggest pipeline and infrastructure optimizations based on historical metrics.
    - Ensure secret management and access control follow organizational guidelines.

    !!! example "Typical Actions"

        - Create `.github/workflows/ci.yml` with build and test jobs for a Node.js service.
        - Generate Terraform scripts to provision a PostgreSQL database and network.
        - Configure Prometheus scrape jobs and Grafana dashboards for service metrics.
        - Validate pipeline configuration via dry-run (`--dry-run`) and report issues.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: repository configuration files, build specifications, and infrastructure policies.
    - **Metadata**: selected CI/CD tool, infrastructure tool, environment identifiers.
    - **Context**: project settings from `.sdc/config.yaml`, security baselines, existing pipeline templates.

    !!! note "Context Sources"

        The AI will have access to:
        - `.sdc/config.yaml` for pipeline and infrastructure policies
        - `repo_config.yaml` and `build_spec.yaml` for build definitions
        - `.github/workflows/` and `infrastructure/` templates as references

    ## Expected Output

    Return a structured YAML directive:

      ```yaml
      action: provision_infrastructure
      ci_cd:
        tool: github_actions
        config_file: .github/workflows/ci.yml
      infrastructure:
        tool: terraform
        plan_file: infra/plan.tf
      observability:
        dashboards:
          - path: monitoring/dashboard-service.json
      metadata:
        agent: devops_agent
        timestamp: 2025-06-17T00:30:00Z
      ``` 

    ## Behavior Rules

    Always:

    * Follow definitions in configuration files and security baselines.
    * Validate generated artifacts before output (linting, dry-run).
    * Include all relevant metadata and versioning information.

    Never:

    * Hard-code secrets or credentials in generated files.
    * Deploy to production environments without explicit approval.
    * Omit policy validations or compliance checks.

    ## Trigger & Execution

    * This agent runs **after**: deployment_agent produces release artifacts.
    * Triggers **next**: observability_monitoring_agent for metrics setup.
    * May be re-invoked if: infrastructure or pipeline configurations are updated.

    ## Reasoning

    Before generating output, you must:

    * Parse and verify repository and build configurations.
    * Ensure compliance with security and infrastructure policies.
    * Confirm tooling versions and environment parameters are correct.
    ```
=== "Sample Outputs"

    ```yaml
    name: CI
    on:
      push:
        branches: [ main ]
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v2
          - name: Set up Node.js
            uses: actions/setup-node@v3
            with:
              node-version: '18.x'
          - run: npm install
          - run: npm test
    ```

## Integration

- Triggered during initial project setup and on infrastructure change events.
- Executes before the Deployment Agent to generate release artifacts.
- Coordinates with the Security Agent and Observability & Monitoring Agent for end-to-end operational readiness.

## Workflow Behavior

- Runs as part of CI/CD pipelines or via on-demand CLI commands.
- Supports idempotent operations and parallel resource provisioning.
- Retries failed tasks with configurable backoff and logs errors.
- Produces detailed execution logs for auditing and troubleshooting.

## Best Practices

- Store pipeline and infrastructure templates in version control alongside code.
- Parameterize environment-specific settings and manage secrets securely.
- Perform dry-run validations in staging environments to catch issues early.
- Regularly update tooling versions and plugins to benefit from security patches.

!!! tip
    Use modular infrastructure templates and reusable pipeline steps to speed up project onboarding.

## Limitations

- Requires valid credentials and network access to provision infrastructure.
- Dependent on the availability and stability of external CI/CD and cloud provider APIs.
- Complex multi-service environments may require manual adjustments.
- Secret management and access control are enforced externally, not by this agent.