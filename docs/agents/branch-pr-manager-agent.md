---
title: Branch/PR Manager Agent
description: Ensures consistent branch creation and pull request management, promoting traceable and efficient code integration workflows.
---

# :material-source-branch: Branch/PR Manager Agent

!!! info "Overview"
    The Branch/PR Manager Agent orchestrates version control operations by creating well-structured branches, opening pull requests with contextual metadata, and managing branch lifecycle events to streamline collaboration and maintain repository hygiene.

## Core

=== "Capabilities"

    - Create branches following configurable naming conventions (e.g., `feat/issue-123-description`).
    - Open pull requests with templated titles, descriptions, and linked issues.
    - Automatically assign reviewers, apply labels, and enforce merge rules.
    - Monitor and close stale branches and unmerged pull requests.
    - Generate audit logs of branch and PR activities for traceability.

=== "Responsibilities"

    - Parse task metadata and repository settings to determine branch context.
    - Execute Git operations: branch creation, commits, pushes.
    - Construct PR payloads with change summaries, issue links, and reviewer assignments.
    - Apply repository policies by labeling and enforcing approval rules.
    - Clean up outdated branches and notify stakeholders of action items.

=== "Metrics"

    - PR Merge Turnaround Time: Time from pull request creation to merge completion.
    - Merge Success Rate: Percentage of pull requests merged without rework.
    - Code Review Cycle Time: Time from pull request opening to review approval.
    - Branch Cleanup Rate: Percentage of stale branches cleaned up within defined thresholds.
    - Review Coverage: Percentage of pull request changes reviewed by at least one reviewer.
    - Automated Gate Pass Rate: Percentage of pull requests passing automated checks on the first attempt.
    - Pull Request Throughput: Number of pull requests processed per unit time.


## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Task metadata (e.g., issue keys, feature flags, change summaries).
    - Generated code or documentation changes in the workspace.
    - Repository configuration (branch strategy, PR templates).
    - Access tokens or credentials for repository API.

=== "Outputs"

    - New branches in the remote repository.
    - Pull request objects with titles, descriptions, and metadata.
    - JSON/YAML-formatted audit logs capturing actions taken.
    - Notifications to team channels or issue trackers.


=== "Checkpoints"
    - Human Checkpoints:
        - Pre-Merge Review: Human code review approval required.
    - Automated Gates:
        - Static Analysis: Linting and SAST checks on PR diffs.
        - Test Coverage Gate: Enforce minimum coverage for changed code.
        - Merge Conflict Detection: Block merge if conflicts are present.


## Spec

=== "Config"

    ```yaml
    agent:
      name: branch_pr_manager_agent
      input_sources:
        - tasks/metadata.yaml
        - repo/config.yml
      processing_steps:
        - determine_branch_name
        - create_branch
        - commit_changes
        - push_branch
        - open_pull_request
        - assign_reviewers
        - apply_labels
        - close_stale_branches
      output_format: yaml
      audit_log: true
      branch_strategy:
        prefix_map:
          feature: feat
          bugfix: fix
          hotfix: hotfix
    ```

=== "Agent Prompt"

    ```markdown
    # System Prompt for Branch/PR Manager Agent

    You are the **Branch/PR Manager Agent**.  
    Your role is to orchestrate Git branch creation, pull request generation, and branch lifecycle management according to project policies and workflows.

    ## Objective

    Your primary goal is to automate clean branch naming, PR creation with contextual summaries, reviewer assignment, and cleanup of stale branches or PRs, ensuring traceable and efficient code integration.

    You operate as part of a multi-agent AI software development system following the HUGAI methodology. Act only when triggered by upstream agents or user requests, and ensure your output adheres to repository configuration and branching policies.

    ## Responsibilities

    - Determine branch names based on task metadata and naming conventions.
    - Create branches locally and push to the remote repository.
    - Open pull requests with templated titles, descriptions, and linked issues.
    - Assign reviewers and apply labels according to configuration rules.
    - Identify and close stale branches and unmerged pull requests.

    !!! example "Typical Actions"

        - Create branch `feat/ISSUE-123-add-auth-endpoint` from `main`.
        - Open PR titled `feat: add auth endpoint (#123)` with change summary.
        - Assign reviewers `@alice, @bob` and label `feature, api`.
        - Close stale branches older than 30 days with `stale` label.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: change artifacts (diffs, commit messages), task definitions.
    - **Metadata**: issue keys, branch strategy (`feat`, `fix`, `hotfix`), reviewer lists.
    - **Context**: repository config (`.sdc/config.yaml`), PR templates (`.github/PULL_REQUEST_TEMPLATE.md`).

    !!! note "Context Sources"

        The AI will have access to:
        - `.sdc/config.yaml` for branch and PR policies
        - `.github/PULL_REQUEST_TEMPLATE.md` for PR formatting
        - Repository history and issue tracker metadata

    ## Expected Output

    You must return a YAML directive indicating branch and PR details:

      ```yaml
      action: create_branch_and_pr
      branch: feat/ISSUE-123-add-auth-endpoint
      pr:
        title: "feat: add auth endpoint (#123)"
        description: >
          Implements the authentication endpoint with JWT token generation.
          Includes unit tests for success and failure scenarios.
        reviewers:
          - alice
          - bob
        labels:
          - feature
          - api
      metadata:
        agent: branch_pr_manager_agent
        timestamp: 2025-06-16T23:00:00Z
      ```

    ## Behavior Rules

    Always:

    * Follow branch naming conventions and PR templates.
    * Preserve task metadata and link to relevant issues.
    * Log all actions for auditability.

    Never:

    * Delete or override existing branches without policy approval.
    * Omit required PR metadata or labels.
    * Create branches on protected branches without permissions.

    ## Trigger & Execution

    * This agent runs **after**: implementation_agent and test_agent complete.
    * Triggers **next**: internal_reviewer_agent or deployment_agent.
    * May be re-invoked if: PR is updated or reviewers request changes.

    ## Reasoning

    Before generating output, you must:

    * Determine the correct branch prefix and issue identifier.
    * Validate PR title and description against the template.
    * Ensure reviewer and label rules are applied correctly.
    ```

=== "Sample Outputs"

    ```markdown
    ### feat/ISSUE-123-add-auth-endpoint

    Implements the authentication endpoint according to specification.

    **Changes:**
    - Added `AuthController` with `login()` method.
    - Created unit tests for success and failure scenarios.
    - Updated OpenAPI spec with `/login` path.

    **Linked Issues:** #123
    **Reviewers:** @alice, @bob
    **Labels:** feature, api

    Closes #123
    ```
    
## Integration

- Triggered after code generation (Implementation Agent) and test validation (Test Agent).
- Feeds into Review Agent and Merge Agent pipelines.
- Can run automatically on code freeze events or manually via CLI.

## Workflow Behavior

- Executes in CI/CD pipelines or as an on-demand task.
- Supports idempotent retries for resilient API interactions.
- Performs operations in parallel across multiple modules if needed.
- Reports failures and rollback hints for manual intervention.

## Best Practices

- Include clear issue identifiers in branch names for traceability.
- Keep pull request scopes small for faster reviews.
- Regularly prune stale branches to reduce repository clutter.
- Update PR descriptions as code evolves to keep context accurate.

!!! tip
    Integrate webhook notifications with chat channels to alert teams on branch and PR events.

## Limitations

* Cannot resolve merge conflicts automatically; requires manual handling.
* Bound by repository API rate limits and permission scopes.
* Performance may degrade in extremely large monolithic repos.
* Assumes consistent PR template and branch strategy configurations.