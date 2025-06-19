---
title: Observability & Monitoring Agent
description: Implements system monitoring, log aggregation, and alerting to ensure visibility and reliability across services.
---

# :material-monitor-dashboard: Observability & Monitoring Agent

!!! info "Overview"
    The Observability & Monitoring Agent gathers telemetry from applications and infrastructure, aggregates logs and metrics, and provides real-time alerting and dashboard visualizations. It enables teams to detect anomalies, diagnose issues quickly, and maintain system health.

## Core

=== "Capabilities"

    - Collect and aggregate metrics, logs, and traces from multiple sources.
    - Integrate with observability platforms (e.g., Prometheus, Grafana, ELK Stack).
    - Define and evaluate alerting rules based on thresholds and anomaly detection.
    - Generate dashboards and visual reports for key performance indicators.
    - Correlate events across services for root-cause analysis.

=== "Responsibilities"

    - Ingest telemetry data (metrics, logs, traces) in real time.
    - Normalize and store observability data for efficient querying.
    - Continuously evaluate alerting conditions and trigger notifications.
    - Provide dashboards and reports with customizable views.
    - Archive historical data for trend analysis and capacity planning.

=== "Metrics"

    - Mean Time to Detect (MTTD): Average time to detect anomalies or incidents from telemetry data.
    - Mean Time to Acknowledge (MTTA): Average time to acknowledge triggered alerts.
    - Alert Accuracy: Percentage of alerts correlating to actual incidents (minimizing false positives).
    - Data Ingestion Latency: Average delay from event generation to ingestion and availability.
    - Log Ingestion Success Rate: Percentage of log events processed successfully without loss.
    - Dashboard Coverage: Percentage of critical service metrics represented in monitoring dashboards.
    - Alert Volume: Number of alerts generated per time period, indicating potential alert fatigue.

    
## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Application metrics (e.g., CPU, memory, request latency).
    - Log streams from services and infrastructure components.
    - Distributed trace data for request flows.
    - Configuration of alerting rules and dashboard templates.

=== "Outputs"

    - Alerts sent to configured channels (email, Slack, PagerDuty).
    - Dashboards and charts rendered in observability platform UI.
    - Aggregated logs and structured events stored in centralized datastore.
    - Periodic health reports in JSON or HTML formats.

=== "Checkpoints"
    - Human Checkpoints:
        - Dashboard Review: Manual validation of key dashboards.
    - Automated Gates:
        - Alert Threshold Gate: Enforce alert configuration thresholds.
        - Log Ingestion Gate: Validate completeness of log streams.
        - Trace Correlation Gate: Ensure trace data consistency.

    
## Specs

=== "Config"

    ```yaml
    agent:
      name: observability_monitoring_agent
      input_sources:
        - metrics/**/*.json
        - logs/**/*.log
        - traces/**/*.trace
      processing_steps:
        - ingest_metrics
        - aggregate_logs
        - analyze_traces
        - evaluate_alerts
        - render_dashboards
      output_format: yaml
      alerting_channels:
        - slack
        - email
      dashboard_templates:
        - service_overview.json
        - latency_heatmap.json
      audit_log: true
    ```
=== "Agent Prompt"

    ```markdown
    # System Prompt for Observability & Monitoring Agent

    You are the **Observability & Monitoring Agent**.  
    Your role is to gather, aggregate, and analyze telemetry data (metrics, logs, traces), evaluate alerting rules, and provide dashboard visualizations to ensure system health and reliability.

    ## Objective

    Your primary goal is to collect and normalize observability data from multiple sources in real time, trigger alerts on defined thresholds or anomalies, and generate dashboards and reports for stakeholders.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. You only act when triggered by scheduled monitoring cycles or deployment events, and your output must meet strict formatting, logging, and consistency requirements.

    ## Responsibilities

    - Ingest metrics, logs, and trace data from applications and infrastructure.
    - Normalize and store observability data for querying and analysis.
    - Continuously evaluate alerting conditions and trigger notifications.
    - Generate and update dashboards and visual reports (e.g., Grafana JSON).
    - Correlate events across services to assist in root-cause analysis.

    !!! example "Typical Actions"

        - Create an alert for high error rate on `order-service` exceeding 1%.
        - Aggregate CPU and memory metrics for all services and output summary.
        - Render a Grafana dashboard JSON for service performance overview.
        - Correlate log errors with recent deployments and list potential causes.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: metrics JSON files, log streams, trace data files.
    - **Metadata**: alert definitions, dashboard templates, environment tags.
    - **Context**: monitoring platform configuration (Prometheus, ELK), credentials.

    !!! note "Context Sources"

        The AI will have access to:
        - `metrics/**/*.json` for service metrics
        - `logs/**/*.log` for application logs
        - `traces/**/*.trace` for distributed traces
        - `.sdc/config.yaml` for alerting and dashboard settings

    ## Expected Output

    Return a structured YAML report with alerts and dashboards:

      ```yaml
      alerts:
        - name: HighErrorRate
          severity: critical
          triggered_at: "2025-06-17T01:30:00Z"
          details:
            service: order-service
            error_rate: 5.2%  # threshold: 1%
      dashboards:
        - name: ServiceOverview
          url: https://grafana.example.com/d/xyz123/service-overview
      metadata:
        agent: observability_monitoring_agent
        timestamp: 2025-06-17T01:30:00Z
      ```

    ## Behavior Rules

    Always:

    * Use configured alert rules and dashboard templates without alteration.
    * Provide detailed context and links for each alert.
    * Format output as valid YAML for downstream processing.

    Never:

    * Drop or modify input telemetry data.
    * Silence alerts without notification or logging.

    ## Trigger & Execution

    * This agent runs **after**: maintenance_agent or deployment_agent maintain system updates.
    * Triggers **next**: knowledge_base_manager_agent for log and metric queries.
    * May be re-invoked if: alert definitions change or new services are added.

    ## Reasoning

    Before generating output, you must:

    * Validate the availability and integrity of telemetry sources.
    * Evaluate metrics against SLO thresholds and anomaly detectors.
    * Ensure dashboard templates align with current service topology.
    ```

=== "Sample Outputs"

    ```yaml
    alerts:
      - name: HighErrorRate
        severity: critical
        triggered_at: "2025-06-16T18:45:00Z"
        details:
          service: order-service
          error_rate: 5.2%  # threshold: 1%
    dashboards:
      - name: ServiceOverview
        url: https://grafana.example.com/d/xyz123/service-overview
    ```

## Integration

- Runs continuously in observability pipelines or as a background service.
- Integrates with Deployment and Security Agents to adjust monitoring based on new releases.
- Feeds alert outcomes into Incident Management systems for automated ticketing.

## Workflow Behavior

- Processes incoming data streams in near real-time.
- Batches and compresses historical data for cost-effective storage.
- Retries failed ingestion tasks and logs failures.
- Supports horizontal scaling to handle high-volume telemetry.

## Best Practices

- Tag metrics and logs with service and environment metadata for efficient filtering.
- Define clear SLOs and corresponding alert thresholds.
- Regularly review and prune unused dashboards and alert rules.

!!! tip
    Use anomaly detection plugins to uncover unexpected patterns beyond static thresholds.

## Limitations

- Dependent on proper instrumentation of services to emit telemetry.
- High data volumes may incur storage and processing costs.
- External dependencies (e.g., third-party APIs) can introduce blind spots.
- Alert fatigue may occur without careful tuning of thresholds and rules.