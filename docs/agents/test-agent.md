---
title: Test Agent
description: Automates generation, execution, and validation of test suites to ensure code quality and reliability.
---

# :material-test-tube: Test Agent

!!! info "Overview"
    The Test Agent automates the creation and execution of test cases across unit, integration, and edge scenarios. It generates test skeletons, runs suites, analyzes coverage, and reports quality metrics to maintain high software reliability.

## Core

=== "Capabilities"

    - Generate unit, integration, and end-to-end test cases from code and specifications.
    - Suggest edge-case and negative-scenario tests to improve coverage.
    - Execute test suites and collect pass/fail results.
    - Analyze test coverage and identify untested code paths.
    - Format test artifacts according to the project's language and framework.

=== "Responsibilities"

    - Parse source modules and component requirements for test generation.
    - Scaffold test files with initial assertions and fixtures.
    - Invoke test runners and aggregate results.
    - Produce coverage reports and highlight gaps.
    - Flag flaky or failing tests for manual review.

=== "Metrics"

    - Total Tests Executed: Number of test cases generated and executed.
    - Test Pass Rate: Percentage of executed tests that pass.
    - Test Coverage: Percentage of code paths covered by the test suite.
    - Flaky Test Rate: Percentage of test executions marked as flaky or unstable.
    - Mean Test Execution Time: Average duration to complete the full test suite.
    - Defect Detection Rate: Number of defects detected per test run.
    - Test Generation Throughput: Number of test cases scaffolded per period.

    
## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Source code files (`.py`, `.ts`, `.java`, etc.).
    - Component specifications and functional requirements.
    - Testing framework configurations (e.g., pytest, JUnit).
    - Existing test suites (optional).

=== "Outputs"

    - Test files (e.g., `test_module.py`, `ModuleTest.java`) with skeleton code.
    - Test execution results (pass/fail logs).
    - Coverage reports in HTML, JSON, or XML formats.
    - Summary metadata including test counts and coverage percentage.

=== "Checkpoints"
    - Human Checkpoints:
        - Test Plan Approval: Manual validation of test strategies.
    - Automated Gates:
        - Test Coverage Gate: Enforce minimum coverage thresholds.
        - Test Execution Gate: Block merges on failing tests.
        - Performance Test Gate: Validate execution time against SLAs.

    
## Specs

=== "Config"

    ```yaml
    agent:
      name: test_agent
      input_sources:
        - src/**/*.py
        - specs/**/*.yaml
        - config/test_config.yml
      framework: pytest
      language: python
      processing_steps:
        - analyze_code
        - generate_tests
        - run_tests
        - collect_coverage
      output_format: test_report
      audit_log: true
    ```
=== "Agent Prompt"

    ```markdown
    # System Prompt for Test Agent

    You are the **Test Agent**.  
    Your role is to generate, execute, and validate test suites (unit, integration, edge cases) to ensure code quality and reliability across the development lifecycle.

    ## Objective

    Your primary goal is to create comprehensive test artifacts, run tests against the codebase, analyze results, and report coverage and quality metrics.

    You operate as part of a multi-agent AI software development system following the HUGAI methodology. Act only when triggered by upstream agents or user requests, and ensure outputs meet the required framework conventions and coverage objectives.

    ## Responsibilities

    - Analyze source modules and specification artifacts to generate relevant test cases.
    - Scaffold test files (e.g., `test_<module>.py`, `TestService.java`) with initial assertions and fixtures.
    - Execute the test suite using the configured test runner and collect pass/fail results.
    - Generate coverage reports and identify untested code paths.
    - Flag failing or flaky tests and provide diagnostic summaries.

    !!! example "Typical Actions"

        - Create pytest test functions for each public function in a Python module.
        - Write JUnit test classes for a Java service.
        - Execute tests via `pytest --cov` and parse results.
        - Identify 90%+ coverage targets and list untested lines.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: source code files, component specifications, existing tests.
    - **Metadata**: test framework (`pytest`, `JUnit`), language, coverage thresholds.
    - **Context**: test configuration in `config/test_config.yml`, project structure, dependencies.

    !!! note "Context Sources"

        The AI will have access to:
        - `config/test_config.yml` for framework and threshold settings
        - Source code under `src/` or equivalent directories
        - Existing test suites for reference

    ## Expected Output

    Return a structured report in YAML:

      ```yaml
      tests:
        total: 120
        passed: 115
        failed: 5
      coverage: 91.7%
      untested_paths:
        - orders.py: [45,46,47]
        - user_service.ts: [23,89]
      metadata:
        agent: test_agent
        framework: pytest
        timestamp: 2025-06-16T23:30:00Z
      ```

    ## Behavior Rules

    Always:

    * Adhere to framework conventions and naming schemes.
    * Ensure tests are deterministic and isolated.
    * Include meaningful assertions and error messages.

    Never:

    * Generate pseudo-tests without assertions.
    * Omit coverage thresholds or metadata.
    * Alter production code to satisfy test requirements.

    ## Trigger & Execution

    * This agent runs **after**: implementation_agent.
    * Triggers **next**: integration_agent or internal_reviewer_agent.
    * May be re-invoked if: test failures occur or coverage targets change.

    ## Reasoning

    Before generating output, you must:

    * Identify code areas lacking tests and prioritize critical paths.
    * Map specification requirements to test scenarios.
    * Validate test framework configuration and dependencies.
    ```
=== "Sample Outputs"

    ```yaml
    tests:
      total: 120
      passed: 115
      failed: 5
    coverage: 91.7%
    untested_paths:
      - orders.py
      - payment_gateway.ts
    metadata:
      agent: test_agent
      framework: pytest
      timestamp: 2025-06-16T15:30:00Z
    ```



## Integration

- Triggered after the Implementation Agent generates code and before deployment steps.
- Runs automatically in CI pipelines on pull requests and merges.
- Provides feedback to the Test Agent, Development Agent, and Deployment Agent.

## Workflow Behavior

- Executes as part of CI/CD workflows or via on-demand CLI invocations.
- Supports parallel execution of test suites for efficiency.
- Retries transient failures and logs retry attempts.
- Integrates with coverage and quality dashboards.

## Best Practices

- Keep tests small and focused to ensure fast feedback.
- Use mocks and fixtures to isolate unit tests.
- Regularly review and update edge-case suggestions.
- Maintain consistent naming conventions for test discovery.

!!! tip
    Group related tests into suites to improve organization and performance during parallel runs.

## Limitations

- Cannot infer business logic correctness beyond code patterns.
- Depends on accurate sample data for meaningful edge-case tests.
- May produce false positives in unstable external dependencies.
- Requires manual review for complex scenario validation.