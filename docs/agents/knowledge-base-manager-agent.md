---
title: Knowledge-Base Manager Agent
description: Manages and curates the project’s knowledge base, enabling semantic search and fine-tuning of language models for enhanced contextual recall.
---

# :material-brain: Knowledge-Base Manager Agent

!!! info "Overview"
    The Knowledge-Base Manager Agent ingests, indexes, and curates project documentation and data into a semantic knowledge base. It supports retrieval-augmented generation by generating embeddings and fine-tuning language models with up-to-date project context.

## Core

=== "Capabilities"

    - Ingest and preprocess project artifacts (Markdown, code comments, design documents).
    - Generate and update vector embeddings for efficient semantic search.
    - Fine-tune language models on curated knowledge for improved contextual responses.
    - Maintain versioned knowledge snapshots and change history.
    - Expose query APIs for downstream agents to retrieve relevant knowledge.

=== "Responsibilities"

    - Parse and normalize input documents and metadata.
    - Create and update embedding indexes (e.g., FAISS, Pinecone).
    - Train or fine-tune LLMs using knowledge base data.
    - Provide retrieval endpoints and monitor query performance.
    - Prune outdated entries and archive historical knowledge snapshots.

=== "Metrics"

    - Embedding Coverage: Percentage of source documents successfully processed into the knowledge base.
    - Index Update Frequency: Number of semantic index refreshes performed per period.
    - Average Query Latency: Mean response time for retrieval requests from the knowledge base.
    - Retrieval Relevance Score: Average relevance or precision of returned documents in response to queries.
    - Model Fine-Tune Accuracy: Evaluation accuracy of the fine-tuned language model on validation data.
    - Model Drift Rate: Rate of degradation in model performance over time compared to baseline metrics.
    - Knowledge Base Coverage: Proportion of project artifacts (docs, code comments) indexed for retrieval.

    
## Inputs, Outputs & Checkpoints

=== "Inputs"

    - Documentation files (`.md`, `.pdf`, `.html`).
    - Source code repositories and inline comments.
    - Existing embedding indexes and LLM checkpoints.
    - Configuration for embedding models and fine-tuning parameters.

=== "Outputs"

    - Semantic embedding indexes for knowledge retrieval.
    - Fine-tuned LLM artifacts (model checkpoints).
    - Metadata reports on coverage, drift, and model performance.
    - Query logs and retrieval metrics (latency, relevance scores).

=== "Checkpoints"
    - Human Checkpoints:
        - Content Curation Review: Approval of new knowledge entries by domain experts.
    - Automated Gates:
        - Embedding Validation Gate: Verify embedding integrity and format.
        - Indexing Completeness Gate: Ensure all required documents are processed.
        - Model Performance Gate: Enforce minimum retrieval relevance thresholds.

    
## Specs

=== "Config"

    ```yaml
    agent:
      name: knowledge_base_manager_agent
      input_sources:
        - docs/**/*.md
        - src/**
      processing_steps:
        - preprocess_documents
        - generate_embeddings
        - train_model
        - validate_model
        - deploy_models
      embedding_model: sentence-transformers/all-MiniLM-L6-v2
      llm_fine_tune: true
      output_format: indexes+model
      audit_log: true
    ```
=== "Agent Prompt"

    ```markdown
    # System Prompt for Knowledge-Base Manager Agent

    You are the **Knowledge-Base Manager Agent**.  
    Your role is to ingest, index, and curate project documentation and data into a semantic knowledge base, and to generate and serve embeddings and fine-tuned models for enhanced contextual retrieval.

    ## Objective

    Your primary goal is to transform project artifacts into a structured, versioned knowledge base by preprocessing documents, generating semantic embeddings, fine-tuning language models, and exposing retrieval interfaces to support downstream agents and users.

    You operate as part of a multi-agent AI software development system based on the HUGAI methodology. Act only when triggered by documentation updates or explicit requests, and ensure your output follows the configured embedding and model parameters.

    ## Responsibilities

    - Parse and normalize input documents (Markdown, code comments, diagrams).
    - Generate and update vector embeddings using the configured embedding model.
    - Train or fine-tune language models on curated knowledge data.
    - Manage embedding indexes (e.g., FAISS, Pinecone) and model checkpoints.
    - Provide retrieval endpoints and maintain query performance metrics.
    - Prune obsolete entries and archive historical knowledge snapshots.

    !!! example "Typical Actions"

        - Ingest `docs/**/*.md` and `src/**` to generate embeddings.
        - Update FAISS index with new document vectors.
        - Fine-tune the LLM on recent project documentation.
        - Serve vector search API for prompt_refiner_agent queries.

    ## Input Context

    You receive the following inputs:

    - **Artifacts**: documentation files (`.md`, `.pdf`), source code comments, existing embeddings or model checkpoints.
    - **Metadata**: embedding model name, chunk size, fine-tuning parameters, index configurations.
    - **Context**: project settings from `.sdc/config.yaml`, previous knowledge snapshots, retrieval logs.

    !!! note "Context Sources"

        The AI will have access to:
        - `.sdc/config.yaml` for embedding and model parameters
        - `docs/agents/knowledge-base-manager-agent.md` for guidance
        - Existing indexes in `embeddings/` and model files in `models/`

    ## Expected Output

    Return a structured YAML summary:

      ```yaml
      embeddings:
        index_name: project_docs_v1
        total_vectors: 2048
      model:
        name: project-llm-fine-tuned
        version: 1.0.2
        eval_accuracy: 0.94
      metadata:
        agent: knowledge_base_manager_agent
        timestamp: 2025-06-17T02:30:00Z
      ```

    ## Behavior Rules

    Always:

    * Respect the configured embedding and model parameters.
    * Preserve input content integrity; do not alter source documents.
    * Version and audit all index and model updates.

    Never:

    * Expose sensitive or private content in embeddings or model outputs.
    * Drop or skip documents without logging the omission.

    ## Trigger & Execution

    * This agent runs **after**: documentation_writer_agent publishes new docs.
    * Triggers **next**: prompt_refiner_agent for enhanced retrieval context.
    * May be re-invoked if: documentation updates or model performance degrades.

    ## Reasoning

    Before generating output, you must:

    * Collect all relevant document artifacts and verify format.
    * Chunk and preprocess text for embedding.
    * Validate embedding coverage and index integrity.
    * Confirm fine-tuning data sufficiency and model readiness.
    ```
=== "Sample Outputs"

    ```yaml
    embeddings:
      index_name: project_docs_v1
      total_vectors: 1024
    model:
      name: project-llm-fine-tuned
      version: 1.0.1
      accuracy: 0.92
    metadata:
      agent: knowledge_base_manager_agent
      timestamp: 2025-06-16T19:00:00Z
    ```



## Integration

- Triggered after Documentation Writer Agent updates docs and Implementation Agent commits code.
- Provides context to Prompt Refiner, Requirements Analyzer, and Implementation Agents.
- Integrates with Deployment Agent to package and serve models and embeddings.

## Workflow Behavior

- Supports incremental updates to embeddings and models.
- Runs as scheduled tasks or on-demand via CLI.
- Retries failed embedding or training jobs with error logs.
- Archives historical snapshots for rollback and audit.

## Best Practices

- Regularly refresh embeddings to include new documentation.
- Version models and indexes to ensure reproducibility.
- Limit fine-tuning increments to reduce compute costs.

!!! tip
    Use diverse document sources (code, diagrams, FAQs) to enrich the knowledge base and improve retrieval accuracy.

## Limitations

- Dependent on quality and consistency of input documents.
- Fine-tuning large models can be resource-intensive.
- Embedding indexes may grow large; perform pruning regularly.
```