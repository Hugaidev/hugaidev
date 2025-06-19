---
title: CI/CD Pipelines
description: Continuous integration and deployment workflows with automated quality gates for AI-assisted development.
---

# CI/CD Pipelines

Automated build, test, and deployment pipelines enforce quality gates at every stage of the AI-assisted development lifecycle, ensuring code quality and maintaining human oversight over critical decisions.

!!! info "Core Purpose"
    CI/CD pipelines provide automated validation and deployment workflows that integrate AI agent outputs with human checkpoints, maintaining code quality and deployment safety.

## Pipeline Architecture

=== "GitHub Actions"
    ### Complete AI-Assisted Workflow
    
    ```yaml
    # .github/workflows/hugai-pipeline.yml
    name: HUG AI Development Pipeline
    
    on:
      pull_request:
        branches: [ main, develop ]
      push:
        branches: [ main ]
    
    env:
      NODE_VERSION: '18'
      HUGAI_CLI_VERSION: 'latest'
    
    jobs:
      # Stage 1: Initial Validation
      validate:
        runs-on: ubuntu-latest
        outputs:
          human-review-required: ${{ steps.ai-analysis.outputs.human-review }}
          risk-level: ${{ steps.ai-analysis.outputs.risk-level }}
        steps:
          - uses: actions/checkout@v4
            with:
              fetch-depth: 0
          
          - name: Setup Node.js
            uses: actions/setup-node@v4
            with:
              node-version: ${{ env.NODE_VERSION }}
              cache: 'npm'
          
          - name: Install HUG AI CLI
            run: npm install -g @hugai/cli@${{ env.HUGAI_CLI_VERSION }}
          
          - name: AI Code Analysis
            id: ai-analysis
            run: |
              hugai analyze --pr ${{ github.event.number }} \
                --output-format json > analysis.json
              
              echo "human-review=$(jq -r '.humanReviewRequired' analysis.json)" >> $GITHUB_OUTPUT
              echo "risk-level=$(jq -r '.riskLevel' analysis.json)" >> $GITHUB_OUTPUT
          
          - name: Upload Analysis Results
            uses: actions/upload-artifact@v4
            with:
              name: ai-analysis
              path: analysis.json
    
      # Stage 2: Automated Testing
      test:
        needs: validate
        runs-on: ubuntu-latest
        strategy:
          matrix:
            test-type: [unit, integration, e2e]
        steps:
          - uses: actions/checkout@v4
          
          - name: Setup Test Environment
            uses: ./.github/actions/setup-test-env
            with:
              test-type: ${{ matrix.test-type }}
          
          - name: Run Tests
            run: |
              case "${{ matrix.test-type }}" in
                "unit")
                  npm run test:unit -- --coverage
                  ;;
                "integration")
                  npm run test:integration
                  ;;
                "e2e")
                  npm run test:e2e
                  ;;
              esac
          
          - name: Upload Test Results
            uses: actions/upload-artifact@v4
            if: always()
            with:
              name: test-results-${{ matrix.test-type }}
              path: |
                coverage/
                test-results/
    
      # Stage 3: Security & Quality Gates
      security:
        needs: validate
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          
          - name: Dependency Security Scan
            uses: securecodewarrior/github-action-add-sarif@v1
            with:
              sarif-file: security-scan.sarif
          
          - name: Code Quality Analysis
            uses: sonarcloud/sonarcloud-github-action@master
            env:
              GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
              SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          
          - name: AI Security Review
            run: |
              hugai security-review \
                --changes $(git diff --name-only origin/main) \
                --severity high
    
      # Stage 4: Human Review Gate (Conditional)
      human-review:
        needs: [validate, test, security]
        if: needs.validate.outputs.human-review-required == 'true'
        runs-on: ubuntu-latest
        environment: human-approval
        steps:
          - name: Request Human Review
            uses: actions/github-script@v7
            with:
              script: |
                const { data: review } = await github.rest.pulls.requestReviewers({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  pull_number: context.issue.number,
                  reviewers: ['${{ vars.SENIOR_DEVELOPER }}']
                });
                
                await github.rest.issues.createComment({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: context.issue.number,
                  body: `🤖 AI Analysis completed. Human review required due to:
                  - Risk Level: ${{ needs.validate.outputs.risk-level }}
                  - Changes affect critical system components
                  
                  @${{ vars.SENIOR_DEVELOPER }} please review and approve.`
                });
    
      # Stage 5: Deployment (Main branch only)
      deploy:
        needs: [test, security]
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        runs-on: ubuntu-latest
        environment: production
        steps:
          - uses: actions/checkout@v4
          
          - name: Build Application
            run: |
              npm ci
              npm run build
          
          - name: Deploy to Staging
            run: hugai deploy --environment staging --validate
          
          - name: Run Smoke Tests
            run: npm run test:smoke -- --env staging
          
          - name: Deploy to Production
            run: hugai deploy --environment production --canary 10%
          
          - name: Monitor Deployment
            run: hugai monitor --deployment-id ${{ github.sha }} --duration 300
    ```

=== "GitLab CI"
    ### GitLab Pipeline Configuration
    
    ```yaml
    # .gitlab-ci.yml
    stages:
      - validate
      - test
      - security
      - human-gate
      - deploy
      - monitor
    
    variables:
      HUGAI_CLI_VERSION: "latest"
      DOCKER_DRIVER: overlay2
      DOCKER_TLS_CERTDIR: "/certs"
    
    before_script:
      - npm install -g @hugai/cli@$HUGAI_CLI_VERSION
    
    # AI Validation Stage
    ai-validate:
      stage: validate
      image: node:18-alpine
      script:
        - hugai analyze --branch $CI_COMMIT_REF_NAME
        - hugai generate-test-plan --output test-plan.json
      artifacts:
        reports:
          junit: test-plan.json
        paths:
          - ai-analysis/
        expire_in: 1 hour
      only:
        - merge_requests
        - main
    
    # Parallel Testing
    .test-template: &test-template
      stage: test
      image: node:18
      before_script:
        - npm ci
      artifacts:
        reports:
          junit: test-results.xml
          coverage_report:
            coverage_format: cobertura
            path: coverage/cobertura-coverage.xml
        paths:
          - coverage/
        expire_in: 1 week
    
    test:unit:
      <<: *test-template
      script:
        - npm run test:unit -- --reporter junit --outputFile test-results.xml
      coverage: '/Statements\s*:\s*([^%]+)/'
    
    test:integration:
      <<: *test-template
      services:
        - postgres:13
        - redis:6-alpine
      variables:
        POSTGRES_DB: hugai_test
        POSTGRES_USER: hugai
        POSTGRES_PASSWORD: test_password
      script:
        - npm run test:integration -- --reporter junit --outputFile test-results.xml
    
    # Security Scanning
    security:sast:
      stage: security
      include:
        - template: Security/SAST.gitlab-ci.yml
    
    security:dependency:
      stage: security
      image: node:18-alpine
      script:
        - npm audit --audit-level high
        - hugai security-scan --dependency-check
      allow_failure: false
    
    # Human Review Gate
    human-review:
      stage: human-gate
      image: alpine:latest
      script:
        - echo "Human review required for critical changes"
      when: manual
      only:
        variables:
          - $HUMAN_REVIEW_REQUIRED == "true"
      environment:
        name: human-approval
        action: start
    
    # Deployment
    deploy:staging:
      stage: deploy
      image: node:18-alpine
      script:
        - hugai deploy --environment staging
        - hugai verify --environment staging
      environment:
        name: staging
        url: https://staging.hugai.dev
      only:
        - main
    
    deploy:production:
      stage: deploy
      image: node:18-alpine
      script:
        - hugai deploy --environment production --strategy blue-green
      environment:
        name: production
        url: https://hugai.dev
      when: manual
      only:
        - main
    
    # Post-deployment Monitoring
    monitor:
      stage: monitor
      image: node:18-alpine
      script:
        - hugai monitor --environment production --duration 600
      when: on_success
      only:
        - main
    ```

=== "Azure DevOps"
    ### Azure Pipelines YAML
    
    ```yaml
    # azure-pipelines.yml
    trigger:
      branches:
        include:
          - main
          - develop
      paths:
        include:
          - src/*
          - tests/*
          - package.json
    
    pr:
      branches:
        include:
          - main
          - develop
    
    variables:
      buildConfiguration: 'Release'
      hugaiCliVersion: 'latest'
    
    stages:
    - stage: Validate
      displayName: 'AI Validation & Analysis'
      jobs:
      - job: AIAnalysis
        displayName: 'AI Code Analysis'
        pool:
          vmImage: 'ubuntu-latest'
        steps:
        - task: NodeTool@0
          inputs:
            versionSpec: '18.x'
        
        - script: |
            npm install -g @hugai/cli@$(hugaiCliVersion)
            hugai analyze --pr $(System.PullRequest.PullRequestId)
          displayName: 'Run AI Analysis'
        
        - task: PublishTestResults@2
          inputs:
            testResultsFormat: 'JUnit'
            testResultsFiles: 'ai-analysis-results.xml'
    
    - stage: Test
      displayName: 'Automated Testing'
      dependsOn: Validate
      jobs:
      - job: UnitTests
        displayName: 'Unit Tests'
        pool:
          vmImage: 'ubuntu-latest'
        steps:
        - task: NodeTool@0
          inputs:
            versionSpec: '18.x'
        
        - script: |
            npm ci
            npm run test:unit -- --reporter junit --outputFile unit-test-results.xml
          displayName: 'Run Unit Tests'
        
        - task: PublishTestResults@2
          inputs:
            testResultsFormat: 'JUnit'
            testResultsFiles: 'unit-test-results.xml'
        
        - task: PublishCodeCoverageResults@1
          inputs:
            codeCoverageTool: 'Cobertura'
            summaryFileLocation: 'coverage/cobertura-coverage.xml'
    
    - stage: Security
      displayName: 'Security & Quality Gates'
      dependsOn: Test
      jobs:
      - job: SecurityScan
        displayName: 'Security Analysis'
        pool:
          vmImage: 'ubuntu-latest'
        steps:
        - task: NodeTool@0
          inputs:
            versionSpec: '18.x'
        
        - script: |
            npm ci
            npm audit --audit-level high
            hugai security-review --changes $(Build.SourceVersion)
          displayName: 'Security Scanning'
    
    - stage: Deploy
      displayName: 'Deployment'
      dependsOn: Security
      condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
      jobs:
      - deployment: DeployToStaging
        displayName: 'Deploy to Staging'
        environment: 'hugai-staging'
        strategy:
          runOnce:
            deploy:
              steps:
              - script: |
                  hugai deploy --environment staging
                  hugai verify --environment staging
                displayName: 'Deploy and Verify Staging'
      
      - deployment: DeployToProduction
        displayName: 'Deploy to Production'
        dependsOn: DeployToStaging
        environment: 'hugai-production'
        strategy:
          runOnce:
            deploy:
              steps:
              - script: |
                  hugai deploy --environment production --strategy canary
                displayName: 'Canary Deploy to Production'
    ```

=== "Jenkins Pipeline"
    ### Jenkinsfile Configuration
    
    ```groovy
    // Jenkinsfile
    pipeline {
        agent any
        
        environment {
            HUGAI_CLI_VERSION = 'latest'
            NODE_VERSION = '18'
        }
        
        options {
            buildDiscarder(logRotator(numToKeepStr: '10'))
            timeout(time: 1, unit: 'HOURS')
            retry(3)
        }
        
        stages {
            stage('Setup') {
                steps {
                    script {
                        env.BRANCH_NAME = env.BRANCH_NAME ?: 'main'
                        env.BUILD_USER = wrap([$class: 'BuildUser']) {
                            return env.BUILD_USER ?: 'automated'
                        }
                    }
                    
                    nodejs(nodeJSInstallationName: "Node ${NODE_VERSION}") {
                        sh "npm install -g @hugai/cli@${HUGAI_CLI_VERSION}"
                    }
                }
            }
            
            stage('AI Validation') {
                steps {
                    nodejs(nodeJSInstallationName: "Node ${NODE_VERSION}") {
                        script {
                            def analysisResult = sh(
                                script: "hugai analyze --branch ${env.BRANCH_NAME} --format json",
                                returnStdout: true
                            ).trim()
                            
                            def analysis = readJSON text: analysisResult
                            env.HUMAN_REVIEW_REQUIRED = analysis.humanReviewRequired
                            env.RISK_LEVEL = analysis.riskLevel
                            
                            if (analysis.riskLevel == 'HIGH') {
                                currentBuild.result = 'UNSTABLE'
                                echo "High risk changes detected - human review required"
                            }
                        }
                    }
                }
                
                post {
                    always {
                        archiveArtifacts artifacts: 'ai-analysis.json', fingerprint: true
                    }
                }
            }
            
            stage('Testing') {
                parallel {
                    stage('Unit Tests') {
                        steps {
                            nodejs(nodeJSInstallationName: "Node ${NODE_VERSION}") {
                                sh 'npm ci'
                                sh 'npm run test:unit -- --reporter junit --outputFile unit-test-results.xml'
                            }
                        }
                        post {
                            always {
                                junit 'unit-test-results.xml'
                                publishHTML([
                                    allowMissing: false,
                                    alwaysLinkToLastBuild: true,
                                    keepAll: true,
                                    reportDir: 'coverage',
                                    reportFiles: 'index.html',
                                    reportName: 'Coverage Report'
                                ])
                            }
                        }
                    }
                    
                    stage('Integration Tests') {
                        steps {
                            nodejs(nodeJSInstallationName: "Node ${NODE_VERSION}") {
                                sh 'npm run test:integration'
                            }
                        }
                    }
                    
                    stage('Security Scan') {
                        steps {
                            nodejs(nodeJSInstallationName: "Node ${NODE_VERSION}") {
                                sh 'npm audit --audit-level high'
                                sh 'hugai security-review'
                            }
                        }
                    }
                }
            }
            
            stage('Human Review Gate') {
                when {
                    environment name: 'HUMAN_REVIEW_REQUIRED', value: 'true'
                }
                steps {
                    script {
                        def approval = input message: 'Human review required. Approve deployment?',
                                           parameters: [
                                               choice(name: 'APPROVAL', 
                                                     choices: ['Approve', 'Reject'], 
                                                     description: 'Review the changes and decide')
                                           ]
                        
                        if (approval != 'Approve') {
                            error("Deployment rejected by human reviewer")
                        }
                    }
                }
            }
            
            stage('Deploy') {
                when {
                    branch 'main'
                }
                stages {
                    stage('Deploy to Staging') {
                        steps {
                            nodejs(nodeJSInstallationName: "Node ${NODE_VERSION}") {
                                sh 'hugai deploy --environment staging'
                                sh 'hugai verify --environment staging'
                            }
                        }
                    }
                    
                    stage('Deploy to Production') {
                        steps {
                            input message: 'Deploy to production?', ok: 'Deploy'
                            nodejs(nodeJSInstallationName: "Node ${NODE_VERSION}") {
                                sh 'hugai deploy --environment production --strategy blue-green'
                            }
                        }
                        
                        post {
                            success {
                                slackSend channel: '#deployments',
                                         color: 'good',
                                         message: "✅ Production deployment successful: ${env.BUILD_URL}"
                            }
                            failure {
                                slackSend channel: '#deployments',
                                         color: 'danger',
                                         message: "❌ Production deployment failed: ${env.BUILD_URL}"
                            }
                        }
                    }
                }
            }
        }
        
        post {
            always {
                cleanWs()
            }
            failure {
                emailext subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                         body: "Build failed. Check console output at ${env.BUILD_URL}",
                         to: "${env.CHANGE_AUTHOR_EMAIL}"
            }
        }
    }
    ```

## Quality Gates Configuration

=== "Code Quality"
    ### SonarQube Integration
    
    ```properties
    # sonar-project.properties
    sonar.projectKey=hugai-development
    sonar.projectName=HUG AI Development
    sonar.projectVersion=1.0
    
    # Source and test paths
    sonar.sources=src
    sonar.tests=tests
    sonar.test.exclusions=**/*.spec.ts,**/*.test.ts
    
    # Coverage reports
    sonar.javascript.lcov.reportPaths=coverage/lcov.info
    sonar.typescript.lcov.reportPaths=coverage/lcov.info
    
    # Quality gates
    sonar.qualitygate.wait=true
    sonar.coverage.minimum=80
    sonar.duplicated_lines_density.maximum=3
    
    # AI-specific rules
    sonar.issue.ignore.multicriteria=e1,e2
    sonar.issue.ignore.multicriteria.e1.ruleKey=typescript:S100
    sonar.issue.ignore.multicriteria.e1.resourceKey=**/*agent*.ts
    sonar.issue.ignore.multicriteria.e2.ruleKey=typescript:S3776
    sonar.issue.ignore.multicriteria.e2.resourceKey=**/generated/*.ts
    ```

=== "Performance Gates"
    ### Lighthouse CI Integration
    
    ```json
    {
      "ci": {
        "collect": {
          "url": ["http://localhost:3000"],
          "startServerCommand": "npm start",
          "startServerReadyPattern": "ready on"
        },
        "assert": {
          "assertions": {
            "categories:performance": ["error", {"minScore": 0.8}],
            "categories:accessibility": ["error", {"minScore": 0.9}],
            "categories:best-practices": ["error", {"minScore": 0.9}],
            "categories:seo": ["error", {"minScore": 0.8}]
          }
        },
        "upload": {
          "target": "lhci",
          "serverBaseUrl": "https://lighthouse.hugai.dev"
        }
      }
    }
    ```

## Best Practices

!!! tip "Pipeline Optimization"
    - **Parallel Execution**: Run independent stages in parallel to reduce build time
    - **Caching**: Implement dependency caching for faster builds
    - **Incremental Testing**: Only run tests for changed components when possible

!!! warning "Security Considerations"
    - **Secret Management**: Use secure secret management for API keys and credentials
    - **Dependency Scanning**: Regularly scan dependencies for vulnerabilities
    - **Access Controls**: Implement proper RBAC for pipeline access and approvals

!!! success "Performance Tips"
    - **Build Optimization**: Use multi-stage Docker builds and layer caching
    - **Test Parallelization**: Distribute tests across multiple runners
    - **Artifact Management**: Efficiently handle build artifacts and test results