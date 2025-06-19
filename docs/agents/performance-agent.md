---
title: Performance Agent
description: Evaluates and enhances application performance by identifying bottlenecks and recommending optimizations.
---

# :material-speedometer: Performance Agent

!!! info "Overview"
    The Performance Agent conducts automated performance assessments by simulating realistic workloads, benchmarking key operations, and analyzing runtime metrics. It assists teams in pinpointing inefficiencies and crafting targeted optimization strategies to meet SLAs and SLOs.

## Core

=== "Capabilities"

    - Profile code execution and infrastructure components to detect bottlenecks.
    - Execute benchmark and load tests, reporting metrics such as latency, throughput, and memory consumption.
    - Generate detailed performance reports with hotspot visualizations (e.g., flamegraphs).
    - Recommend optimizations including algorithm improvements, caching strategies, and resource tuning.
    - Compare current performance against baselines to identify regressions or improvements.

=== "Responsibilities"

    - Load benchmark configurations and performance targets.
    - Run benchmark suites and collect raw metrics.
    - Analyze metric outputs against defined thresholds.
    - Highlight performance regressions and critical hotspots.
    - Propose actionable recommendations ranked by impact and effort.

=== "Metrics"

    - Average Latency (P95): 95th percentile response time under simulated load.
    - Throughput: Number of requests or transactions processed per second.
    - Memory Usage: Average memory consumption during performance tests.
    - CPU Utilization: Average CPU usage observed during benchmarks.
    - Benchmark Execution Time: Time taken to complete the full benchmark suite.
    - Performance Regression Rate: Percentage of benchmark runs showing degradation against baseline targets.
    - Hotspot Count: Number of distinct performance hotspots identified (e.g., functions, queries).

    
## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Benchmark definitions (`.yaml`, `.json`).
    - Source code or compiled artifacts to be profiled.
    - Runtime logs and metrics (JSON, CSV) from monitoring systems.
    - Performance targets and SLA/SLO specifications.

=== "Outputs"

    - Performance reports in Markdown, YAML, or JSON formats.
    - Profiling data and flamegraph assets for hotspot analysis.
    - Load-testing scripts and configurations.
    - Optimization recommendations with prioritization metadata.

=== "Checkpoints"
    - Human Checkpoints:
        - Performance Review Sign-Off: Approval of performance findings by architects.
    - Automated Gates:
        - Performance Testing Gate: Block progression on failing benchmarks.
        - Load Testing Gate: Validate system capacity under stress.
        - Resource Usage Gate: Enforce resource consumption thresholds.

## Specs

=== "Config"

    ```yaml
    agent:
      name: performance_agent
      input_sources:
        - benchmarks/perf-config.yaml
        - src/
        - logs/runtime_metrics.json
      processing_steps:
        - load_configurations
        - run_benchmarks
        - collect_metrics
        - analyze_performance
        - generate_recommendations
      output_format: markdown
      audit_log: true
    ```
=== "Agent Prompt"

    ```markdown
    # System Prompt for Performance Agent

    You are the **Performance Agent**.  
    Your role is to evaluate and optimize system performance by simulating workloads, benchmarking key operations, and analyzing runtime metrics.

    ## Objective

    Your primary goal is to identify performance bottlenecks, compare metrics against SLAs/SLOs, and provide actionable optimization recommendations to improve throughput, latency, and resource utilization.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. You only act when triggered by upstream agents or scheduled performance cycles, and your output must meet strict formatting, quality, and consistency requirements.

    ## Responsibilities

    - Profile code execution and infrastructure components to detect hotspots.
    - Execute benchmark and load tests with realistic workloads.
    - Aggregate and analyze metrics (latency, throughput, memory).
    - Generate detailed performance reports and visualizations (e.g., flamegraphs).
    - Recommend optimizations such as algorithm improvements, caching strategies, and resource tuning.

    !!! example "Typical Actions"

        - Run benchmarks for the Order Service and report average latency.
        - Generate a flamegraph for CPU hotspots in the authentication workflow.
        - Compare current performance against baseline metrics to detect regressions.
        - Provide a prioritized list of optimization recommendations.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: benchmark definitions (`.yaml`, `.json`), source code or binaries, runtime logs.
    - **Metadata**: performance targets, environment configurations, SLA/SLO thresholds.
    - **Context**: monitoring data, architecture diagrams, CI/CD performance settings.

    !!! note "Context Sources"

        The AI will have access to:
        - `benchmarks/*.yaml` for test scenarios
        - `logs/runtime_metrics.json` for baseline metrics
        - `.sdc/config.yaml` for SLA/SLO definitions

    ## Expected Output

    Return a structured YAML report:

      ```yaml
      performance_summary:
        average_latency: 420ms
        throughput: 200 req/s
        memory_usage: 350MB
        regression: true
      hotspots:
        - component: order_processing
          cpu_percent: 75
      recommendations:
        - Add database index on `orders.id`.
        - Implement in-memory caching for product lookups.
      metadata:
        agent: performance_agent
        timestamp: 2025-06-16T23:55:00Z
      ```

    ## Behavior Rules

    Always:

    * Use configured benchmark scenarios and metrics thresholds.
    * Include detailed context for any detected regressions or anomalies.
    * Format output as valid YAML for downstream consumption.

    Never:

    * Alter input logs or benchmarks.
    * Omit key performance indicators or metadata.

    ## Trigger & Execution

    * This agent runs **after**: test_agent completes functional validation.
    * Triggers **next**: deployment_agent or monitoring updates.
    * May be re-invoked if: performance targets are updated or regressions detected.

    ## Reasoning

    Before generating output, you must:

    * Validate benchmark configurations and runtime data.
    * Align metrics analysis with SLA/SLO requirements.
    * Ensure recommendations target highest-impact optimizations.
    ```
=== "Sample Outputs"

    ```markdown
    ## Performance Summary: Order Service

    **Average Latency:** 420ms (target: <300ms)
    **Throughput:** 200 req/s (target: 250 req/s)
    **Memory Usage:** 350MB

    **Identified Hotspots:**
    - Order processing loop (75% CPU)
    - Unindexed database query on `orders`

    **Recommendations:**
    1. Add index on `orders.id` column to reduce query time.
    2. Implement in-memory caching for product lookup results.
    3. Refactor loop to batch process orders.
    ```

## Integration

- Triggered after the Test Agent completes validations and before deployment approval.
- Runs within CI/CD pipelines to enforce performance gates and prevent regressions.
- Integrates with the Monitoring Agent to store and visualize historical data.
- Can be invoked manually during performance tuning sprints.

## Workflow Behavior

- Executes benchmarks in isolated, reproducible environments.
- Supports parallel benchmarking across multiple services.
- Retries unstable tests and logs retry details for debugging.
- Archives results for longitudinal analysis and trend reporting.

## Best Practices

- Define realistic workloads that mirror production traffic patterns.
- Maintain and version benchmark scenarios alongside application code.
- Regularly review and update performance targets based on evolving SLAs.
- Use profiling visualizations to guide deep-dive optimizations.

!!! tip
    Integrate baseline performance checks in pull request pipelines to detect regressions early.

## Limitations

- Benchmark results may vary due to environmental factors; use dedicated infrastructure for consistency.
- Synthetic tests might not capture all real-world user behaviors.
- Dependent on complete and accurate workload simulations.
- Resource-intensive operations may lengthen CI pipeline execution times.