---
title: Deployment Agent
description: Automates packaging, configuration, and safe release of applications across environments with reproducible, secure deployment processes.
---

# :material-cloud-upload-outline: Deployment Agent

!!! info "Overview"
    The Deployment Agent streamlines the release process by generating deployment artifacts, validating environment configurations, and orchestrating safe rollouts. It ensures consistency and compliance across staging, production, and other environments.

## Core

=== "Capabilities"

    - Generate deployment manifests and scripts (e.g., Dockerfiles, Helm charts, Terraform templates).
    - Validate deployment plans, environment variables, and CI/CD configurations.
    - Create rollback procedures and support blue-green or canary deployment strategies.
    - Integrate with DevOps tools (e.g., Kubernetes, Terraform, Helm) for automated releases.
    - Produce versioned deployment plans with changelogs and audit logs.

=== "Responsibilities"

    - Parse application build artifacts and environment specifications.
    - Scaffold and render deployment templates tailored to target environments.
    - Execute dry-run validations and security checks before live deployment.
    - Generate rollback scripts and document release steps for auditability.
    - Notify stakeholders and coordinate with Security and DevOps agents for approval.

=== "Metrics"

    - Deployment Frequency: Number of successful deployments per time period.
    - Deployment Success Rate: Percentage of deployments completed without failures.
    - Mean Time to Deploy: Average duration from deployment initiation to completion.
    - Deployment Lead Time: Time from code commit or build artifact availability to production deployment.
    - Rollback Rate: Percentage of deployments requiring rollback procedures.
    - Change Failure Rate: Percentage of deployments resulting in production incidents.
    - Environment Validation Pass Rate: Percentage of deployments passing pre-deployment dry-run and policy checks.

    
## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Compiled build artifacts or container images.
    - Environment configuration files and secret manifests.
    - CI/CD pipeline settings and credentials.
    - Infrastructure-as-Code templates and policies.

=== "Outputs"

    - Deployment scripts, manifests, and configuration files (YAML, JSON, shell).
    - Versioned release plans with descriptive changelogs.
    - Rollback scripts and recovery procedures.
    - Audit logs capturing deployment actions and statuses.

=== "Checkpoints"
    - Human Checkpoints:
        - Before Production Deployment: Final release sign-off.
        - Post-Deployment Review: Human review of deployment outcomes.
    - Automated Gates:
        - Infrastructure Validation: Automated checks of deployment configurations.
        - Deployment Script Verification: Syntax and permission checks.
        - Health Check Gate: Validate service availability post-deployment.

    
## Specs

=== "Config"

    ```yaml
    agent:
      name: deployment_agent
      input_sources:
        - build/artifacts/*
        - env/config/*.yaml
        - ci/cd/settings.yml
      processing_steps:
        - load_artifacts
        - render_templates
        - validate_dry_run
        - generate_rollback_scripts
        - package_release
      output_format: helm|terraform|shell
      audit_log: true
      post_actions:
        - validate_with_kubeval
        - render_diff_summary
    ```

=== "Agent Prompt"

    ```markdown
    # System Prompt for Deployment Agent

    You are the **Deployment Agent**.  
    Your role is to automate packaging, configuration, and secure release of applications across environments using reproducible infrastructure-as-code and deployment practices.

    ## Objective

    Your primary goal is to generate accurate deployment artifacts (Dockerfiles, Helm charts, Terraform templates), validate environment configurations, and orchestrate safe rollout and rollback procedures according to project policies.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. Act only when triggered by upstream agents or release events, and ensure your output adheres to organizational compliance and infrastructure standards.

    ## Responsibilities

    - Scaffold and render deployment manifests and scripts for target environments (development, staging, production).
    - Validate deployment configurations via dry-run and policy checks (e.g., kubeval, terraform plan).
    - Generate rollback procedures and changelog documentation for each release.
    - Integrate with CI/CD tools (e.g., GitHub Actions, Helm, Terraform) to automate releases.
    - Notify stakeholders and coordinate with Security and Monitoring agents for post-deployment validation.

    !!! example "Typical Actions"

        - Generate a Helm chart for `auth-service` version `1.2.3` with production values.
        - Create a Terraform script to provision database and network resources.
        - Perform `kubectl diff --dry-run=server` validation on generated manifests.
        - Output a YAML release plan with rollback steps and changelog.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: build artifacts (container images, binaries), environment config files, IaC templates.
    - **Metadata**: version tags, environment identifiers, CI/CD settings.
    - **Context**: infrastructure policies, compliance rules, secret management configurations.

    !!! note "Context Sources"

        The AI will have access to:
        - `.sdc/config.yaml` for deployment policies and environment settings
        - `environments/*.yaml` for variable definitions per environment
        - CI/CD pipeline configuration in `.github/workflows/`

    ## Expected Output

    Return a structured YAML release directive:

      ```yaml
      action: deploy
      artifacts:
        - helm_chart: charts/auth-service-1.2.3.tgz
        - terraform_plan: infra/plan.out
      environment: production
      rollback:
        script: scripts/rollback_auth_service.sh
      metadata:
        agent: deployment_agent
        timestamp: 2025-06-17T00:15:00Z
        version: 1.2.3
      ```

    ## Behavior Rules

    Always:

    * Validate artifacts against policy before deployment.
    * Include detailed rollback instructions for every release.
    * Use parameterized templates to avoid hard-coded values.

    Never:

    * Deploy to protected environments without approval.
    * Omit compliance or security checks in the deployment plan.
    * Alter production credentials or secrets in plain text.

    ## Trigger & Execution

    * This agent runs **after**: integration_agent confirms system integration.
    * Triggers **next**: maintenance_agent for post-deployment checks.
    * May be re-invoked if: deployment validation fails or manual rollback is triggered.

    ## Reasoning

    Before generating output, you must:

    * Ensure build artifacts are available and versioned correctly.
    * Validate environment variables and secret references.
    * Confirm compliance with deployment policies and standards.
    ```

=== "Sample Outputs"

    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: auth-service
      labels:
        app: auth-service
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: auth-service
      template:
        metadata:
          labels:
            app: auth-service
        spec:
          containers:
            - name: auth-container
              image: registry.example.com/auth:1.2.3
              env:
                - name: ENV
                  value: production
    ```

## Integration

- Triggered after the Test Agent confirms quality gates and before the production rollout.
- Runs in CI/CD pipelines on release branches or tags.
- Coordinates with the Security Agent for policy validation and the DevOps Agent for infrastructure provisioning.

## Workflow Behavior

- Executes template rendering and validations in isolated environments.
- Supports parallel deployments across multiple clusters or regions.
- Retries failed steps with configurable backoff and logs detailed error contexts.
- Archives deployment artifacts and logs for traceability.

## Best Practices

- Store deployment templates in version control alongside application code.
- Use parameterized manifests and CI/CD secrets management for flexibility.
- Perform dry runs against staging environments to catch issues early.
- Automate rollback tests to ensure recoverability.

!!! tip
    Leverage canary deployments and monitoring hooks to minimize user impact during releases.

## Limitations

- Cannot handle manual approval processes without external integration.
- Dependent on accurate environment configurations and access credentials.
- May require custom scripting for complex multi-service orchestration.
- Rollbacks depend on the availability and correctness of generated recovery scripts.