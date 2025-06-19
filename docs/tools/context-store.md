---
title: Context Store
description: Central repository for sharing context, decisions, and artifact metadata across AI agents and human collaborators.
---

# Context Store

The context store serves as the central knowledge repository, maintaining shared context, decision history, and artifact metadata across all AI agents and human collaborators in the development workflow.

!!! info "Core Purpose"
    Centralized context management ensures consistency, enables knowledge sharing between agents, and maintains institutional memory across development cycles.

## Architecture Overview

=== "Storage Layer"
    ### Multi-tier Storage Strategy
    
    ```typescript
    interface ContextStore {
      metadata: MetadataStore;
      artifacts: ArtifactStore;
      decisions: DecisionStore;
      cache: CacheLayer;
    }
    
    interface StorageConfig {
      primary: StorageBackend;
      cache: CacheBackend;
      indexing: IndexingEngine;
      retention: RetentionPolicy;
    }
    
    class ContextStoreManager {
      private stores: Map<ContextType, ContextStore> = new Map();
      
      constructor(private config: StorageConfig) {
        this.initializeStores();
      }
      
      async storeContext(
        type: ContextType,
        context: ContextData,
        metadata: ContextMetadata
      ): Promise<string> {
        const store = this.stores.get(type);
        if (!store) {
          throw new Error(`No store configured for context type: ${type}`);
        }
        
        const contextId = generateId();
        const enrichedContext = await this.enrichContext(context, metadata);
        
        // Store in primary storage
        await store.metadata.store(contextId, enrichedContext.metadata);
        await store.artifacts.store(contextId, enrichedContext.data);
        
        // Update cache
        await store.cache.set(contextId, enrichedContext);
        
        // Index for search
        await this.config.indexing.index(contextId, enrichedContext);
        
        return contextId;
      }
      
      async retrieveContext(contextId: string): Promise<ContextData | null> {
        // Try cache first
        for (const store of this.stores.values()) {
          const cached = await store.cache.get(contextId);
          if (cached) {
            return cached;
          }
        }
        
        // Fallback to primary storage
        return await this.loadFromPrimaryStorage(contextId);
      }
    }
    ```

=== "Context Types"
    ### Structured Context Management
    
    ```typescript
    enum ContextType {
      PROJECT_METADATA = 'project_metadata',
      CODE_CONTEXT = 'code_context',
      DECISION_HISTORY = 'decision_history',
      HUMAN_FEEDBACK = 'human_feedback',
      AGENT_INTERACTIONS = 'agent_interactions',
      DOCUMENTATION = 'documentation',
      TEST_RESULTS = 'test_results',
      DEPLOYMENT_INFO = 'deployment_info'
    }
    
    interface ContextData {
      id: string;
      type: ContextType;
      content: any;
      relationships: ContextRelationship[];
      timestamp: Date;
      version: number;
    }
    
    interface ContextMetadata {
      source: string;
      tags: string[];
      priority: number;
      expiresAt?: Date;
      accessLevel: AccessLevel;
      dependencies: string[];
    }
    
    class TypedContextStore<T> {
      constructor(
        private contextType: ContextType,
        private validator: ContextValidator<T>,
        private storage: StorageBackend
      ) {}
      
      async store(data: T, metadata: ContextMetadata): Promise<string> {
        // Validate data structure
        const validation = await this.validator.validate(data);
        if (!validation.isValid) {
          throw new Error(`Invalid context data: ${validation.errors.join(', ')}`);
        }
        
        const contextData: ContextData = {
          id: generateId(),
          type: this.contextType,
          content: data,
          relationships: await this.detectRelationships(data),
          timestamp: new Date(),
          version: 1
        };
        
        return await this.storage.store(contextData, metadata);
      }
      
      async query(query: ContextQuery): Promise<T[]> {
        const results = await this.storage.query({
          ...query,
          type: this.contextType
        });
        
        return results.map(result => result.content as T);
      }
    }
    ```

## Knowledge Graph

=== "Relationship Mapping"
    ### Context Relationships
    
    ```typescript
    interface ContextRelationship {
      type: RelationshipType;
      targetId: string;
      strength: number;
      metadata?: Record<string, any>;
    }
    
    enum RelationshipType {
      DEPENDS_ON = 'depends_on',
      REFERENCES = 'references',
      IMPLEMENTS = 'implements',
      TESTS = 'tests',
      DOCUMENTS = 'documents',
      SUPERSEDES = 'supersedes',
      INFLUENCES = 'influences'
    }
    
    class ContextRelationshipManager {
      private graph: Map<string, Set<ContextRelationship>> = new Map();
      
      addRelationship(
        sourceId: string,
        relationship: ContextRelationship
      ): void {
        if (!this.graph.has(sourceId)) {
          this.graph.set(sourceId, new Set());
        }
        
        this.graph.get(sourceId)!.add(relationship);
        
        // Add reverse relationship if applicable
        const reverseType = this.getReverseRelationshipType(relationship.type);
        if (reverseType) {
          this.addRelationship(relationship.targetId, {
            type: reverseType,
            targetId: sourceId,
            strength: relationship.strength,
            metadata: relationship.metadata
          });
        }
      }
      
      async findRelatedContext(
        contextId: string,
        relationshipTypes?: RelationshipType[],
        maxDepth: number = 2
      ): Promise<RelatedContext[]> {
        const visited = new Set<string>();
        const results: RelatedContext[] = [];
        
        await this.traverseRelationships(
          contextId,
          relationshipTypes,
          maxDepth,
          0,
          visited,
          results
        );
        
        return results.sort((a, b) => b.relevanceScore - a.relevanceScore);
      }
      
      private async traverseRelationships(
        currentId: string,
        relationshipTypes: RelationshipType[] | undefined,
        maxDepth: number,
        currentDepth: number,
        visited: Set<string>,
        results: RelatedContext[]
      ): Promise<void> {
        if (currentDepth >= maxDepth || visited.has(currentId)) {
          return;
        }
        
        visited.add(currentId);
        const relationships = this.graph.get(currentId) || new Set();
        
        for (const relationship of relationships) {
          if (relationshipTypes && !relationshipTypes.includes(relationship.type)) {
            continue;
          }
          
          const context = await this.contextStore.retrieveContext(relationship.targetId);
          if (context) {
            results.push({
              context: context,
              relationship: relationship,
              depth: currentDepth + 1,
              relevanceScore: this.calculateRelevanceScore(relationship, currentDepth)
            });
            
            await this.traverseRelationships(
              relationship.targetId,
              relationshipTypes,
              maxDepth,
              currentDepth + 1,
              visited,
              results
            );
          }
        }
      }
    }
    ```

=== "Semantic Search"
    ### Context Discovery
    
    ```typescript
    interface ContextQuery {
      text?: string;
      type?: ContextType;
      tags?: string[];
      timeRange?: TimeRange;
      similarTo?: string;
      minRelevance?: number;
    }
    
    interface SearchResult {
      context: ContextData;
      relevanceScore: number;
      matches: SearchMatch[];
    }
    
    class SemanticContextSearch {
      constructor(
        private vectorStore: VectorStore,
        private textSearch: TextSearchEngine,
        private embeddings: EmbeddingService
      ) {}
      
      async search(query: ContextQuery): Promise<SearchResult[]> {
        const searchTasks: Promise<SearchResult[]>[] = [];
        
        // Vector similarity search
        if (query.text || query.similarTo) {
          searchTasks.push(this.performVectorSearch(query));
        }
        
        // Full-text search
        if (query.text) {
          searchTasks.push(this.performTextSearch(query));
        }
        
        // Metadata filtering
        if (query.type || query.tags || query.timeRange) {
          searchTasks.push(this.performMetadataSearch(query));
        }
        
        const allResults = await Promise.all(searchTasks);
        return this.mergeAndRankResults(allResults.flat(), query);
      }
      
      private async performVectorSearch(query: ContextQuery): Promise<SearchResult[]> {
        let queryVector: number[];
        
        if (query.similarTo) {
          const similarContext = await this.contextStore.retrieveContext(query.similarTo);
          if (similarContext) {
            queryVector = await this.embeddings.embed(
              JSON.stringify(similarContext.content)
            );
          } else {
            return [];
          }
        } else if (query.text) {
          queryVector = await this.embeddings.embed(query.text);
        } else {
          return [];
        }
        
        const vectorResults = await this.vectorStore.similaritySearch(queryVector, {
          limit: 50,
          threshold: query.minRelevance || 0.7
        });
        
        return vectorResults.map(result => ({
          context: result.metadata.context,
          relevanceScore: result.similarity,
          matches: [{
            type: 'semantic',
            text: query.text || '',
            score: result.similarity
          }]
        }));
      }
      
      private mergeAndRankResults(
        results: SearchResult[],
        query: ContextQuery
      ): SearchResult[] {
        // Deduplicate by context ID
        const deduplicated = new Map<string, SearchResult>();
        
        for (const result of results) {
          const existing = deduplicated.get(result.context.id);
          if (existing) {
            // Merge results and combine scores
            existing.relevanceScore = Math.max(
              existing.relevanceScore,
              result.relevanceScore
            );
            existing.matches.push(...result.matches);
          } else {
            deduplicated.set(result.context.id, result);
          }
        }
        
        // Sort by relevance and apply additional ranking factors
        return Array.from(deduplicated.values())
          .map(result => ({
            ...result,
            relevanceScore: this.calculateFinalScore(result, query)
          }))
          .sort((a, b) => b.relevanceScore - a.relevanceScore);
      }
    }
    ```

## Decision Tracking

=== "Decision History"
    ### Decision Management
    
    ```typescript
    interface Decision {
      id: string;
      title: string;
      description: string;
      context: string;
      alternatives: Alternative[];
      selectedAlternative: string;
      reasoning: string;
      decisionMaker: string;
      timestamp: Date;
      impact: ImpactAssessment;
      relatedDecisions: string[];
    }
    
    interface Alternative {
      id: string;
      name: string;
      description: string;
      pros: string[];
      cons: string[];
      estimatedCost: number;
      riskLevel: RiskLevel;
    }
    
    class DecisionTracker {
      constructor(private contextStore: ContextStoreManager) {}
      
      async recordDecision(decision: Decision): Promise<string> {
        // Validate decision data
        this.validateDecision(decision);
        
        // Store in context store
        const decisionId = await this.contextStore.storeContext(
          ContextType.DECISION_HISTORY,
          decision,
          {
            source: decision.decisionMaker,
            tags: this.extractTags(decision),
            priority: this.calculatePriority(decision.impact),
            accessLevel: AccessLevel.TEAM,
            dependencies: decision.relatedDecisions
          }
        );
        
        // Update decision relationships
        await this.updateDecisionRelationships(decisionId, decision);
        
        // Generate decision summary
        await this.generateDecisionSummary(decisionId, decision);
        
        return decisionId;
      }
      
      async getDecisionHistory(
        contextId?: string,
        timeRange?: TimeRange
      ): Promise<Decision[]> {
        const query: ContextQuery = {
          type: ContextType.DECISION_HISTORY,
          timeRange: timeRange
        };
        
        if (contextId) {
          // Find decisions related to specific context
          const relatedContexts = await this.relationshipManager.findRelatedContext(
            contextId,
            [RelationshipType.INFLUENCES, RelationshipType.DEPENDS_ON]
          );
          
          const relatedDecisionIds = relatedContexts
            .filter(rc => rc.context.type === ContextType.DECISION_HISTORY)
            .map(rc => rc.context.id);
          
          if (relatedDecisionIds.length > 0) {
            // Add related decision IDs to query
            query.similarTo = relatedDecisionIds[0];
          }
        }
        
        const results = await this.contextStore.query(query);
        return results.map(result => result.content as Decision);
      }
      
      async analyzeDecisionImpact(decisionId: string): Promise<DecisionImpactAnalysis> {
        const decision = await this.getDecision(decisionId);
        if (!decision) {
          throw new Error(`Decision not found: ${decisionId}`);
        }
        
        // Find all contexts affected by this decision
        const affectedContexts = await this.relationshipManager.findRelatedContext(
          decisionId,
          [RelationshipType.INFLUENCES],
          3
        );
        
        // Analyze actual vs. predicted outcomes
        const analysis: DecisionImpactAnalysis = {
          decisionId: decisionId,
          predictedImpact: decision.impact,
          actualImpact: await this.calculateActualImpact(decision, affectedContexts),
          affectedComponents: affectedContexts.map(ac => ac.context.id),
          followUpDecisions: await this.findFollowUpDecisions(decisionId),
          lessonsLearned: await this.extractLessonsLearned(decision, affectedContexts)
        };
        
        return analysis;
      }
    }
    ```

## Agent Memory Management

=== "Working Memory"
    ### Agent Context Isolation
    
    ```typescript
    interface AgentMemory {
      agentId: string;
      workingMemory: Map<string, any>;
      episodicMemory: EpisodicMemory[];
      semanticMemory: SemanticMemory;
      proceduralMemory: ProceduralMemory;
    }
    
    interface EpisodicMemory {
      id: string;
      timestamp: Date;
      event: string;
      context: any;
      outcome: any;
      significance: number;
    }
    
    class AgentMemoryManager {
      private agentMemories = new Map<string, AgentMemory>();
      private memoryCapacity = 1000; // items per agent
      
      getAgentMemory(agentId: string): AgentMemory {
        if (!this.agentMemories.has(agentId)) {
          this.agentMemories.set(agentId, this.createEmptyMemory(agentId));
        }
        return this.agentMemories.get(agentId)!;
      }
      
      async storeEpisode(
        agentId: string,
        event: string,
        context: any,
        outcome: any
      ): Promise<void> {
        const memory = this.getAgentMemory(agentId);
        
        const episode: EpisodicMemory = {
          id: generateId(),
          timestamp: new Date(),
          event: event,
          context: context,
          outcome: outcome,
          significance: this.calculateSignificance(event, outcome)
        };
        
        memory.episodicMemory.push(episode);
        
        // Maintain memory capacity
        if (memory.episodicMemory.length > this.memoryCapacity) {
          await this.consolidateMemory(memory);
        }
        
        // Update semantic memory with patterns
        await this.updateSemanticMemory(memory, episode);
      }
      
      async retrieveRelevantMemories(
        agentId: string,
        currentContext: any,
        limit: number = 10
      ): Promise<EpisodicMemory[]> {
        const memory = this.getAgentMemory(agentId);
        
        // Calculate relevance scores for all episodes
        const scoredEpisodes = memory.episodicMemory.map(episode => ({
          episode: episode,
          relevance: this.calculateRelevance(episode, currentContext)
        }));
        
        // Sort by relevance and significance
        return scoredEpisodes
          .sort((a, b) => 
            (b.relevance * b.episode.significance) - 
            (a.relevance * a.episode.significance)
          )
          .slice(0, limit)
          .map(scored => scored.episode);
      }
      
      private async consolidateMemory(memory: AgentMemory): Promise<void> {
        // Identify less significant memories for removal
        const sortedBySignificance = memory.episodicMemory
          .sort((a, b) => a.significance - b.significance);
        
        const toRemove = sortedBySignificance.slice(0, 100); // Remove oldest 100
        const toKeep = sortedBySignificance.slice(100);
        
        // Extract patterns from removed memories
        const patterns = await this.extractPatterns(toRemove);
        
        // Update semantic memory with patterns
        memory.semanticMemory.patterns.push(...patterns);
        
        // Update episodic memory
        memory.episodicMemory = toKeep;
      }
    }
    ```

## Performance Optimization

=== "Caching Strategy"
    ### Multi-level Caching
    
    ```typescript
    interface CacheConfiguration {
      l1: MemoryCacheConfig;
      l2: DistributedCacheConfig;
      l3: PersistentCacheConfig;
    }
    
    class HierarchicalContextCache {
      private l1Cache: MemoryCache; // In-process memory
      private l2Cache: RedisCache;  // Distributed cache
      private l3Cache: FileCache;   // Persistent cache
      
      constructor(config: CacheConfiguration) {
        this.l1Cache = new MemoryCache(config.l1);
        this.l2Cache = new RedisCache(config.l2);
        this.l3Cache = new FileCache(config.l3);
      }
      
      async get(key: string): Promise<any | null> {
        // Try L1 cache first (fastest)
        let value = await this.l1Cache.get(key);
        if (value !== null) {
          return value;
        }
        
        // Try L2 cache (distributed)
        value = await this.l2Cache.get(key);
        if (value !== null) {
          // Populate L1 cache
          await this.l1Cache.set(key, value, this.l1Cache.defaultTTL);
          return value;
        }
        
        // Try L3 cache (persistent)
        value = await this.l3Cache.get(key);
        if (value !== null) {
          // Populate L2 and L1 caches
          await this.l2Cache.set(key, value, this.l2Cache.defaultTTL);
          await this.l1Cache.set(key, value, this.l1Cache.defaultTTL);
          return value;
        }
        
        return null;
      }
      
      async set(key: string, value: any, ttl?: number): Promise<void> {
        // Write to all cache levels
        const tasks = [
          this.l1Cache.set(key, value, ttl || this.l1Cache.defaultTTL),
          this.l2Cache.set(key, value, ttl || this.l2Cache.defaultTTL),
          this.l3Cache.set(key, value, ttl || this.l3Cache.defaultTTL)
        ];
        
        await Promise.all(tasks);
      }
      
      async invalidate(key: string): Promise<void> {
        await Promise.all([
          this.l1Cache.delete(key),
          this.l2Cache.delete(key),
          this.l3Cache.delete(key)
        ]);
      }
    }
    ```

## Best Practices

!!! tip "Context Management"
    - **Granular Storage**: Store context at appropriate granularity to balance detail and performance
    - **Relationship Modeling**: Maintain rich relationship graphs for effective context discovery
    - **Version Control**: Track context evolution to understand decision reasoning over time

!!! warning "Common Pitfalls"
    - **Context Bloat**: Avoid storing excessive low-value context that clutters the store
    - **Stale Data**: Implement proper TTL and invalidation strategies for time-sensitive context
    - **Access Patterns**: Optimize storage layout based on actual access patterns

!!! success "Performance Tips"
    - **Indexing Strategy**: Create appropriate indices for common query patterns
    - **Caching Layers**: Implement multi-level caching for frequently accessed context
    - **Batch Operations**: Use bulk operations for loading and storing related context items