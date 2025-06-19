---
title: Security Scanning
description: Comprehensive security testing tools for vulnerability detection and compliance enforcement.
---

# Security Scanning

Comprehensive security scanning tools detect vulnerabilities, enforce security policies, and ensure compliance throughout the AI-assisted development lifecycle.

!!! info "Core Purpose"
    Multi-layered security scanning provides early detection of vulnerabilities, compliance validation, and automated security policy enforcement.

## Vulnerability Detection

=== "SAST (Static Analysis)"
    ### Source Code Security Analysis
    
    ```yaml
    # .github/workflows/security-scan.yml
    name: Security Scan
    on: [push, pull_request]
    
    jobs:
      sast:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - name: Run Semgrep
            uses: returntocorp/semgrep-action@v1
            with:
              config: >-
                p/security-audit
                p/secrets
                p/owasp-top-ten
          - name: CodeQL Analysis
            uses: github/codeql-action/analyze@v2
            with:
              languages: javascript,typescript
    ```

=== "DAST (Dynamic Analysis)"
    ### Runtime Security Testing
    
    ```typescript
    interface DASTConfig {
      target: string;
      authentication: AuthConfig;
      scanProfile: ScanProfile;
      exclusions: string[];
    }
    
    class DynamicSecurityScanner {
      async runDASTScan(config: DASTConfig): Promise<DASTResults> {
        const scanner = new ZAPScanner();
        
        await scanner.startProxy();
        await scanner.openUrl(config.target);
        
        if (config.authentication) {
          await scanner.authenticate(config.authentication);
        }
        
        const spiderResults = await scanner.spider(config.target);
        const activeScanResults = await scanner.activeScan(config.target);
        
        return {
          vulnerabilities: [...spiderResults.vulnerabilities, ...activeScanResults.vulnerabilities],
          coverage: spiderResults.coverage,
          scanDuration: activeScanResults.duration
        };
      }
    }
    ```

## Dependency Scanning

=== "NPM Audit"
    ### JavaScript/Node.js Dependencies
    
    ```json
    {
      "scripts": {
        "audit": "npm audit --audit-level=moderate",
        "audit:fix": "npm audit fix",
        "audit:report": "npm audit --json > audit-report.json"
      },
      "auditConfig": {
        "report-format": "json",
        "exclude": ["devDependencies"]
      }
    }
    ```

## Compliance Scanning

=== "Infrastructure Security"
    ### Cloud Security Compliance
    
    ```yaml
    # checkov configuration
    framework:
      - terraform
      - kubernetes
      - dockerfile
    
    skip-check:
      - CKV_K8S_43  # Image should use digest
      - CKV_DOCKER_2  # HEALTHCHECK instruction
    
    soft-fail: true
    output: json
    ```

## Best Practices

!!! tip "Security Integration"
    - **Shift Left**: Integrate security scanning early in development
    - **Continuous Monitoring**: Run scans on every code change
    - **Risk-Based**: Prioritize fixes based on vulnerability severity

!!! warning "Common Issues"
    - **False Positives**: Tune scanners to reduce noise
    - **Performance**: Balance scan thoroughness with speed
    - **Coverage**: Ensure all code paths are scanned

!!! success "Best Results"
    - **Multiple Tools**: Use different scanners for comprehensive coverage
    - **Regular Updates**: Keep vulnerability databases current
    - **Automated Remediation**: Fix low-risk issues automatically