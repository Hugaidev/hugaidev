---
title: Code Search & RAG
description: Retrieval-augmented generation and intelligent code search engines for contextual AI assistance.
---

# Code Search & RAG

Contextual code retrieval and retrieval-augmented generation (RAG) systems provide AI agents with precise, relevant codebase knowledge, enabling informed decision-making and maintaining consistency across large projects.

!!! info "Core Purpose"
    RAG-powered code search engines feed AI agents curated, contextually relevant code snippets and documentation, reducing hallucinations and improving code quality through informed context.

## Architecture Overview

=== "RAG Pipeline"
    ### Code Indexing & Embedding
    
    ```mermaid
    graph LR
        A[Source Code] --> B[Parser]
        B --> C[AST Analysis]
        C --> D[Semantic Chunking]
        D --> E[Vector Embeddings]
        E --> F[Vector Database]
        F --> G[Search API]
        G --> H[AI Agents]
    ```

    **Indexing Process:**
    ```typescript
    interface CodeChunk {
      id: string;
      filePath: string;
      content: string;
      type: 'function' | 'class' | 'interface' | 'comment' | 'documentation';
      language: string;
      embedding: number[];
      metadata: {
        dependencies: string[];
        complexity: number;
        lastModified: Date;
        author: string;
      };
    }
    
    async function indexCodebase(projectPath: string): Promise<void> {
      const files = await glob('**/*.{ts,js,py,java,go}', { cwd: projectPath });
      
      for (const file of files) {
        const content = await fs.readFile(file, 'utf-8');
        const ast = parseToAST(content, getLanguage(file));
        const chunks = semanticChunking(ast);
        
        for (const chunk of chunks) {
          const embedding = await generateEmbedding(chunk.content);
          await vectorDB.store({
            ...chunk,
            embedding,
            filePath: file
          });
        }
      }
    }
    ```

=== "Search Engine"
    ### Semantic Code Search
    
    ```typescript
    interface SearchQuery {
      query: string;
      contextType: 'implementation' | 'testing' | 'documentation' | 'architecture';
      fileTypes?: string[];
      maxResults?: number;
      similarityThreshold?: number;
    }
    
    interface SearchResult {
      chunk: CodeChunk;
      similarity: number;
      context: string;
      usageExamples?: string[];
    }
    
    class CodeSearchEngine {
      async search(query: SearchQuery): Promise<SearchResult[]> {
        const queryEmbedding = await this.generateEmbedding(query.query);
        
        const results = await this.vectorDB.similaritySearch({
          vector: queryEmbedding,
          limit: query.maxResults || 10,
          threshold: query.similarityThreshold || 0.7,
          filter: {
            language: query.fileTypes,
            type: query.contextType
          }
        });
        
        return results.map(result => ({
          chunk: result.chunk,
          similarity: result.similarity,
          context: this.buildContext(result.chunk),
          usageExamples: this.findUsageExamples(result.chunk)
        }));
      }
      
      private buildContext(chunk: CodeChunk): string {
        // Build contextual information around the code chunk
        return this.getFileContext(chunk.filePath) + 
               this.getDependencyContext(chunk.metadata.dependencies);
      }
    }
    ```

=== "Context Generation"
    ### RAG Context Builder
    
    ```typescript
    interface RAGContext {
      query: string;
      relevantCode: CodeChunk[];
      documentation: string[];
      examples: string[];
      bestPractices: string[];
      relatedPatterns: string[];
    }
    
    class RAGContextBuilder {
      async buildContext(
        userQuery: string, 
        agentType: string
      ): Promise<RAGContext> {
        // Multi-stage retrieval for comprehensive context
        const codeResults = await this.searchEngine.search({
          query: userQuery,
          contextType: 'implementation',
          maxResults: 5
        });
        
        const docResults = await this.searchEngine.search({
          query: userQuery,
          contextType: 'documentation',
          maxResults: 3
        });
        
        const examples = await this.findCodeExamples(userQuery);
        const patterns = await this.findRelatedPatterns(userQuery, agentType);
        
        return {
          query: userQuery,
          relevantCode: codeResults.map(r => r.chunk),
          documentation: docResults.map(r => r.chunk.content),
          examples: examples,
          bestPractices: await this.getBestPractices(userQuery),
          relatedPatterns: patterns
        };
      }
    }
    ```

## Implementation Strategies

=== "Vector Databases"
    ### Database Options
    
    **Pinecone Integration:**
    ```typescript
    import { PineconeClient } from '@pinecone-database/pinecone';
    
    class PineconeCodeSearch {
      private client: PineconeClient;
      
      constructor() {
        this.client = new PineconeClient();
        this.client.init({
          apiKey: process.env.PINECONE_API_KEY!,
          environment: process.env.PINECONE_ENVIRONMENT!
        });
      }
      
      async upsertCode(chunks: CodeChunk[]): Promise<void> {
        const index = this.client.Index('code-search');
        
        const vectors = chunks.map(chunk => ({
          id: chunk.id,
          values: chunk.embedding,
          metadata: {
            filePath: chunk.filePath,
            type: chunk.type,
            language: chunk.language,
            content: chunk.content.substring(0, 1000) // Metadata size limit
          }
        }));
        
        await index.upsert({ vectors });
      }
    }
    ```

    **Chroma DB Integration:**
    ```typescript
    import { ChromaClient } from 'chromadb';
    
    class ChromaCodeSearch {
      private client: ChromaClient;
      private collection: any;
      
      async initialize(): Promise<void> {
        this.client = new ChromaClient();
        this.collection = await this.client.createCollection({
          name: 'codebase',
          metadata: { 'hnsw:space': 'cosine' }
        });
      }
      
      async addDocuments(chunks: CodeChunk[]): Promise<void> {
        await this.collection.add({
          ids: chunks.map(c => c.id),
          embeddings: chunks.map(c => c.embedding),
          metadatas: chunks.map(c => c.metadata),
          documents: chunks.map(c => c.content)
        });
      }
    }
    ```

=== "Embedding Models"
    ### Model Selection
    
    **OpenAI Embeddings:**
    ```typescript
    import OpenAI from 'openai';
    
    class OpenAIEmbeddings {
      private client: OpenAI;
      
      constructor() {
        this.client = new OpenAI({
          apiKey: process.env.OPENAI_API_KEY
        });
      }
      
      async generateEmbedding(text: string): Promise<number[]> {
        const response = await this.client.embeddings.create({
          model: 'text-embedding-3-large',
          input: text
        });
        
        return response.data[0].embedding;
      }
    }
    ```

    **Local Embeddings (HuggingFace):**
    ```python
    from sentence_transformers import SentenceTransformer
    import numpy as np
    
    class LocalCodeEmbeddings:
        def __init__(self):
            # Specialized model for code
            self.model = SentenceTransformer('microsoft/codebert-base')
        
        def generate_embedding(self, code_text: str) -> np.ndarray:
            return self.model.encode(code_text, normalize_embeddings=True)
        
        def batch_encode(self, code_chunks: list) -> np.ndarray:
            return self.model.encode(code_chunks, normalize_embeddings=True)
    ```

=== "Hybrid Search"
    ### Combining Vector & Keyword Search
    
    ```typescript
    interface HybridSearchConfig {
      vectorWeight: number; // 0.7
      keywordWeight: number; // 0.3
      rerankThreshold: number; // 0.5
    }
    
    class HybridCodeSearch {
      async search(
        query: string,
        config: HybridSearchConfig = {
          vectorWeight: 0.7,
          keywordWeight: 0.3,
          rerankThreshold: 0.5
        }
      ): Promise<SearchResult[]> {
        // Vector similarity search
        const vectorResults = await this.vectorSearch(query);
        
        // Keyword/BM25 search
        const keywordResults = await this.keywordSearch(query);
        
        // Combine and rerank results
        const combined = this.combineResults(
          vectorResults,
          keywordResults,
          config
        );
        
        // Rerank with cross-encoder for final precision
        return await this.rerank(combined, query);
      }
      
      private combineResults(
        vector: SearchResult[],
        keyword: SearchResult[],
        config: HybridSearchConfig
      ): SearchResult[] {
        const scoreMap = new Map<string, number>();
        
        // Weighted vector scores
        vector.forEach(result => {
          scoreMap.set(
            result.chunk.id,
            result.similarity * config.vectorWeight
          );
        });
        
        // Add weighted keyword scores
        keyword.forEach(result => {
          const existing = scoreMap.get(result.chunk.id) || 0;
          scoreMap.set(
            result.chunk.id,
            existing + (result.similarity * config.keywordWeight)
          );
        });
        
        // Sort by combined score
        return Array.from(scoreMap.entries())
          .sort(([,a], [,b]) => b - a)
          .map(([id, score]) => 
            vector.find(r => r.chunk.id === id) || 
            keyword.find(r => r.chunk.id === id)!
          );
      }
    }
    ```

## Agent Integration

=== "Context Injection"
    ### Agent Prompt Enhancement
    
    ```typescript
    interface AgentPromptBuilder {
      buildPrompt(userQuery: string, agentType: string): Promise<string>;
    }
    
    class RAGPromptBuilder implements AgentPromptBuilder {
      async buildPrompt(userQuery: string, agentType: string): Promise<string> {
        const context = await this.ragBuilder.buildContext(userQuery, agentType);
        
        return `
    ## Task Context
    ${userQuery}
    
    ## Relevant Code Examples
    ${context.relevantCode.map(chunk => `
    **${chunk.filePath}** (${chunk.type}):
    \`\`\`${chunk.language}
    ${chunk.content}
    \`\`\`
    `).join('\n')}
    
    ## Documentation References
    ${context.documentation.join('\n\n')}
    
    ## Best Practices
    ${context.bestPractices.join('\n- ')}
    
    ## Related Patterns
    ${context.relatedPatterns.join('\n- ')}
    
    Please implement the requested functionality following the patterns and practices shown above.
        `.trim();
      }
    }
    ```

=== "Real-time Updates"
    ### Live Context Refresh
    
    ```typescript
    class LiveRAGUpdater {
      private fileWatcher: chokidar.FSWatcher;
      
      async startWatching(projectPath: string): Promise<void> {
        this.fileWatcher = chokidar.watch('**/*.{ts,js,py,java}', {
          cwd: projectPath,
          ignored: ['node_modules', '.git', 'dist']
        });
        
        this.fileWatcher
          .on('change', this.handleFileChange.bind(this))
          .on('add', this.handleFileAdd.bind(this))
          .on('unlink', this.handleFileDelete.bind(this));
      }
      
      private async handleFileChange(filePath: string): Promise<void> {
        // Re-index the changed file
        const content = await fs.readFile(filePath, 'utf-8');
        const chunks = await this.parseAndChunk(content, filePath);
        
        // Update vector database
        await this.vectorDB.updateChunks(filePath, chunks);
        
        // Notify active agents of context changes
        await this.notifyAgents(filePath, 'updated');
      }
    }
    ```

## Performance Optimization

=== "Caching Strategies"
    ### Multi-level Caching
    
    ```typescript
    class RAGCacheManager {
      private l1Cache = new Map<string, SearchResult[]>(); // In-memory
      private l2Cache: Redis; // Redis for shared cache
      
      async getCachedResults(query: string): Promise<SearchResult[] | null> {
        // L1 Cache check
        if (this.l1Cache.has(query)) {
          return this.l1Cache.get(query)!;
        }
        
        // L2 Cache check
        const cached = await this.l2Cache.get(`search:${query}`);
        if (cached) {
          const results = JSON.parse(cached);
          this.l1Cache.set(query, results); // Populate L1
          return results;
        }
        
        return null;
      }
      
      async cacheResults(query: string, results: SearchResult[]): Promise<void> {
        // Cache in both levels
        this.l1Cache.set(query, results);
        await this.l2Cache.setex(
          `search:${query}`, 
          3600, // 1 hour TTL
          JSON.stringify(results)
        );
      }
    }
    ```

=== "Query Optimization"
    ### Smart Query Processing
    
    ```typescript
    class QueryOptimizer {
      async optimizeQuery(originalQuery: string): Promise<string> {
        // Extract code-specific terms
        const codeTerms = this.extractCodeTerms(originalQuery);
        
        // Expand with synonyms and related terms
        const expanded = await this.expandQuery(originalQuery, codeTerms);
        
        // Add language-specific context if detected
        const languageContext = this.detectLanguage(originalQuery);
        
        return this.buildOptimizedQuery(expanded, languageContext);
      }
      
      private extractCodeTerms(query: string): string[] {
        const codePatterns = [
          /function\s+(\w+)/g,
          /class\s+(\w+)/g,
          /interface\s+(\w+)/g,
          /import.*from\s+['"]([^'"]+)['"]/g
        ];
        
        const terms: string[] = [];
        codePatterns.forEach(pattern => {
          const matches = query.matchAll(pattern);
          for (const match of matches) {
            terms.push(match[1]);
          }
        });
        
        return terms;
      }
    }
    ```

## Best Practices

!!! tip "Index Optimization"
    - **Chunking Strategy**: Use semantic chunking based on AST structure rather than fixed-size chunks
    - **Update Frequency**: Implement incremental indexing for large codebases
    - **Metadata Enrichment**: Include dependency graphs, usage patterns, and code complexity metrics

!!! warning "Common Pitfalls"
    - **Stale Context**: Ensure real-time updates for rapidly changing codebases
    - **Over-retrieval**: Limit context size to prevent prompt token overflow
    - **Relevance Drift**: Regularly evaluate and tune similarity thresholds

!!! success "Performance Tips"
    - Use approximate nearest neighbor (ANN) indices for large codebases
    - Implement query result caching with TTL-based invalidation
    - Pre-compute embeddings for frequently accessed code patterns