---
title: Containerization
description: Docker environments and Kubernetes orchestration for consistent AI-assisted development and deployment.
---

# Containerization

Containerized environments ensure consistent development, testing, and deployment across all stages of the AI-assisted development lifecycle, providing isolation for agent tasks and reproducible infrastructure.

!!! info "Core Purpose"
    Docker-based containerization provides isolated, reproducible environments for AI agents to work safely while maintaining consistency across development, testing, and production environments.

## Docker Architecture

=== "Development Containers"
    ### AI Agent Environments
    
    ```dockerfile
    # Dockerfile.agent-dev
    FROM node:18-alpine
    
    # Install AI development tools
    RUN npm install -g @hugai/cli typescript ts-node
    
    # Create agent workspace
    WORKDIR /workspace
    
    # Install system dependencies for AI tools
    RUN apk add --no-cache git python3 py3-pip
    RUN pip3 install huggingface_hub openai
    
    # Copy project files
    COPY package*.json ./
    RUN npm ci --only=production
    
    # Create non-root user for security
    RUN addgroup -g 1001 -S hugai && \
        adduser -S hugai -u 1001 -G hugai
    
    USER hugai
    
    # Health check for agent readiness
    HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
      CMD hugai-cli health-check || exit 1
    
    CMD ["npm", "run", "dev"]
    ```

    ### Multi-stage Build Optimization
    ```dockerfile
    # Dockerfile.optimized
    # Stage 1: Build dependencies
    FROM node:18-alpine AS builder
    WORKDIR /app
    COPY package*.json ./
    RUN npm ci --only=production && npm cache clean --force
    
    # Stage 2: Development image
    FROM node:18-alpine AS development
    WORKDIR /app
    COPY --from=builder /app/node_modules ./node_modules
    COPY . .
    CMD ["npm", "run", "dev"]
    
    # Stage 3: Production image
    FROM node:18-alpine AS production
    WORKDIR /app
    COPY --from=builder /app/node_modules ./node_modules
    COPY dist ./dist
    COPY package.json ./
    USER node
    CMD ["npm", "start"]
    ```

=== "Service Architecture"
    ### Docker Compose Configuration
    
    ```yaml
    # docker-compose.dev.yml
    version: '3.8'
    
    services:
      hugai-orchestrator:
        build:
          context: .
          dockerfile: Dockerfile.orchestrator
        environment:
          - NODE_ENV=development
          - HUGAI_CONFIG=/config/hugai.yml
        volumes:
          - ./config:/config:ro
          - hugai-workspace:/workspace
        networks:
          - hugai-network
        depends_on:
          - redis
          - postgres
    
      hugai-agent-implementation:
        build:
          context: .
          dockerfile: Dockerfile.agent-dev
        environment:
          - AGENT_TYPE=implementation
          - WORKSPACE_PATH=/workspace
        volumes:
          - hugai-workspace:/workspace
          - ./src:/app/src:ro
        networks:
          - hugai-network
        scale: 3
    
      hugai-agent-testing:
        build:
          context: .
          dockerfile: Dockerfile.agent-dev
        environment:
          - AGENT_TYPE=testing
          - TEST_ENVIRONMENT=isolated
        volumes:
          - hugai-workspace:/workspace
          - ./tests:/app/tests:ro
        networks:
          - hugai-network
    
      redis:
        image: redis:7-alpine
        volumes:
          - redis-data:/data
        networks:
          - hugai-network
    
      postgres:
        image: postgres:15-alpine
        environment:
          POSTGRES_DB: hugai_dev
          POSTGRES_USER: hugai
          POSTGRES_PASSWORD: dev_password
        volumes:
          - postgres-data:/var/lib/postgresql/data
        networks:
          - hugai-network
    
    volumes:
      hugai-workspace:
      redis-data:
      postgres-data:
    
    networks:
      hugai-network:
        driver: bridge
    ```

=== "Security Configuration"
    ### Container Security Best Practices
    
    ```dockerfile
    # Dockerfile.secure
    FROM node:18-alpine
    
    # Security: Update base packages
    RUN apk upgrade --no-cache
    
    # Security: Create non-root user
    RUN addgroup -g 1001 -S hugai && \
        adduser -S hugai -u 1001 -G hugai
    
    # Security: Set secure file permissions
    WORKDIR /app
    COPY --chown=hugai:hugai package*.json ./
    
    # Security: Install only production dependencies
    RUN npm ci --only=production && \
        npm cache clean --force
    
    # Security: Remove unnecessary packages
    RUN apk del npm
    
    # Copy application code with proper ownership
    COPY --chown=hugai:hugai . .
    
    # Security: Run as non-root user
    USER hugai
    
    # Security: Expose only necessary port
    EXPOSE 3000
    
    # Security: Use exec form for CMD
    CMD ["node", "dist/index.js"]
    ```

## Kubernetes Orchestration

=== "Deployment Configuration"
    ### Agent Deployment Manifests
    
    ```yaml
    # k8s/hugai-agent-deployment.yml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: hugai-implementation-agents
      namespace: hugai-system
      labels:
        app: hugai-agent
        type: implementation
    spec:
      replicas: 5
      selector:
        matchLabels:
          app: hugai-agent
          type: implementation
      template:
        metadata:
          labels:
            app: hugai-agent
            type: implementation
        spec:
          serviceAccountName: hugai-agent-sa
          securityContext:
            runAsNonRoot: true
            runAsUser: 1001
            fsGroup: 1001
          containers:
          - name: hugai-agent
            image: hugai/agent:latest
            imagePullPolicy: Always
            env:
            - name: AGENT_TYPE
              value: "implementation"
            - name: NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            resources:
              requests:
                memory: "256Mi"
                cpu: "250m"
              limits:
                memory: "512Mi"
                cpu: "500m"
            livenessProbe:
              httpGet:
                path: /health
                port: 8080
              initialDelaySeconds: 30
              periodSeconds: 10
            readinessProbe:
              httpGet:
                path: /ready
                port: 8080
              initialDelaySeconds: 5
              periodSeconds: 5
            volumeMounts:
            - name: workspace
              mountPath: /workspace
            - name: config
              mountPath: /config
              readOnly: true
          volumes:
          - name: workspace
            persistentVolumeClaim:
              claimName: hugai-workspace-pvc
          - name: config
            configMap:
              name: hugai-config
    ```

    ### Horizontal Pod Autoscaler
    ```yaml
    # k8s/hugai-agent-hpa.yml
    apiVersion: autoscaling/v2
    kind: HorizontalPodAutoscaler
    metadata:
      name: hugai-agent-hpa
      namespace: hugai-system
    spec:
      scaleTargetRef:
        apiVersion: apps/v1
        kind: Deployment
        name: hugai-implementation-agents
      minReplicas: 2
      maxReplicas: 10
      metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 70
      - type: Resource
        resource:
          name: memory
          target:
            type: Utilization
            averageUtilization: 80
      behavior:
        scaleDown:
          stabilizationWindowSeconds: 300
          policies:
          - type: Percent
            value: 10
            periodSeconds: 60
        scaleUp:
          stabilizationWindowSeconds: 60
          policies:
          - type: Percent
            value: 50
            periodSeconds: 30
    ```

=== "Service Mesh"
    ### Istio Configuration
    
    ```yaml
    # k8s/hugai-virtualservice.yml
    apiVersion: networking.istio.io/v1beta1
    kind: VirtualService
    metadata:
      name: hugai-agent-vs
      namespace: hugai-system
    spec:
      hosts:
      - hugai-agents.local
      http:
      - match:
        - headers:
            agent-type:
              exact: implementation
        route:
        - destination:
            host: hugai-implementation-service
            port:
              number: 8080
          weight: 100
        fault:
          delay:
            percentage:
              value: 0.1
            fixedDelay: 5s
      - match:
        - headers:
            agent-type:
              exact: testing
        route:
        - destination:
            host: hugai-testing-service
            port:
              number: 8080
    
    ---
    apiVersion: networking.istio.io/v1beta1
    kind: DestinationRule
    metadata:
      name: hugai-agent-dr
      namespace: hugai-system
    spec:
      host: hugai-implementation-service
      trafficPolicy:
        loadBalancer:
          simple: LEAST_CONN
        connectionPool:
          tcp:
            maxConnections: 100
          http:
            http1MaxPendingRequests: 50
            maxRequestsPerConnection: 10
        circuitBreaker:
          consecutiveErrors: 3
          interval: 30s
          baseEjectionTime: 30s
    ```

=== "Storage & Persistence"
    ### Persistent Volume Configuration
    
    ```yaml
    # k8s/hugai-storage.yml
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: hugai-workspace-pvc
      namespace: hugai-system
    spec:
      accessModes:
        - ReadWriteMany
      storageClassName: hugai-shared-storage
      resources:
        requests:
          storage: 100Gi
    
    ---
    apiVersion: storage.k8s.io/v1
    kind: StorageClass
    metadata:
      name: hugai-shared-storage
    provisioner: kubernetes.io/aws-efs
    parameters:
      type: Regional
      replicationLevel: max-io
    allowVolumeExpansion: true
    volumeBindingMode: Immediate
    
    ---
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: hugai-config
      namespace: hugai-system
    data:
      hugai.yml: |
        orchestrator:
          max_concurrent_agents: 10
          task_timeout: 3600
          retry_limit: 3
        
        agents:
          implementation:
            image: hugai/implementation-agent:latest
            resources:
              cpu: 500m
              memory: 512Mi
          testing:
            image: hugai/testing-agent:latest
            resources:
              cpu: 250m
              memory: 256Mi
    ```

## Container Registry Management

=== "Image Building"
    ### Automated Build Pipeline
    
    ```yaml
    # .github/workflows/container-build.yml
    name: Container Build and Push
    
    on:
      push:
        branches: [ main, develop ]
        paths: [ 'src/**', 'Dockerfile*', 'package.json' ]
    
    jobs:
      build:
        runs-on: ubuntu-latest
        strategy:
          matrix:
            agent-type: [implementation, testing, security, documentation]
        
        steps:
        - uses: actions/checkout@v4
        
        - name: Set up Docker Buildx
          uses: docker/setup-buildx-action@v3
        
        - name: Login to Container Registry
          uses: docker/login-action@v3
          with:
            registry: ghcr.io
            username: ${{ github.actor }}
            password: ${{ secrets.GITHUB_TOKEN }}
        
        - name: Extract metadata
          id: meta
          uses: docker/metadata-action@v5
          with:
            images: ghcr.io/${{ github.repository }}/hugai-${{ matrix.agent-type }}
            tags: |
              type=ref,event=branch
              type=ref,event=pr
              type=sha,prefix={{branch}}-
              type=raw,value=latest,enable={{is_default_branch}}
        
        - name: Build and push
          uses: docker/build-push-action@v5
          with:
            context: .
            file: ./Dockerfile.${{ matrix.agent-type }}
            platforms: linux/amd64,linux/arm64
            push: true
            tags: ${{ steps.meta.outputs.tags }}
            labels: ${{ steps.meta.outputs.labels }}
            cache-from: type=gha
            cache-to: type=gha,mode=max
    ```

=== "Image Security"
    ### Vulnerability Scanning
    
    ```dockerfile
    # Multi-stage security scanning
    FROM hugai/base:latest AS scanner
    
    # Install security scanning tools
    RUN apk add --no-cache trivy grype
    
    # Copy application for scanning
    COPY . /app
    WORKDIR /app
    
    # Run security scans
    RUN trivy fs --exit-code 1 --severity HIGH,CRITICAL .
    RUN grype /app --fail-on high
    
    # Final stage - only if scans pass
    FROM hugai/base:latest AS production
    COPY --from=scanner /app /app
    WORKDIR /app
    CMD ["npm", "start"]
    ```

## Performance Optimization

=== "Resource Management"
    ### Container Resource Tuning
    
    ```yaml
    # k8s/hugai-resource-tuning.yml
    apiVersion: v1
    kind: LimitRange
    metadata:
      name: hugai-limits
      namespace: hugai-system
    spec:
      limits:
      - default:
          cpu: 500m
          memory: 512Mi
        defaultRequest:
          cpu: 250m
          memory: 256Mi
        type: Container
      - max:
          cpu: 2
          memory: 2Gi
        min:
          cpu: 100m
          memory: 128Mi
        type: Container
    
    ---
    apiVersion: v1
    kind: ResourceQuota
    metadata:
      name: hugai-quota
      namespace: hugai-system
    spec:
      hard:
        requests.cpu: "4"
        requests.memory: 8Gi
        limits.cpu: "8"
        limits.memory: 16Gi
        persistentvolumeclaims: "10"
        services: "5"
    ```

=== "Image Optimization"
    ### Distroless Images
    
    ```dockerfile
    # Dockerfile.distroless
    FROM node:18-alpine AS builder
    WORKDIR /app
    COPY package*.json ./
    RUN npm ci --only=production
    
    FROM gcr.io/distroless/nodejs18-debian11
    WORKDIR /app
    COPY --from=builder /app/node_modules ./node_modules
    COPY dist ./dist
    COPY package.json ./
    
    USER nonroot:nonroot
    CMD ["dist/index.js"]
    ```

## Best Practices

!!! tip "Container Optimization"
    - **Layer Caching**: Order Dockerfile instructions from least to most frequently changing
    - **Multi-stage Builds**: Separate build dependencies from runtime dependencies
    - **Base Image Selection**: Use minimal, security-focused base images like Alpine or Distroless

!!! warning "Security Considerations"
    - **Non-root Users**: Always run containers as non-root users
    - **Image Scanning**: Implement automated vulnerability scanning in CI/CD
    - **Secret Management**: Use Kubernetes secrets or external secret management systems

!!! success "Performance Tips"
    - **Resource Limits**: Set appropriate CPU and memory limits to prevent resource contention
    - **Health Checks**: Implement proper liveness and readiness probes
    - **Horizontal Scaling**: Use HPA for automatic scaling based on metrics