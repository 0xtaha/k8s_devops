# Kubernetes E2E Tests

End-to-end testing suite for Kubernetes cluster verification and pod health checks.

## Overview

This test suite performs comprehensive end-to-end tests on a Kubernetes cluster to verify:

1. **Cluster Accessibility** - Verifies API server is accessible and nodes are ready
2. **Pod Status** - Validates pod deployment, existence, and running state
3. **Health Checks** - Tests Liveness and Readiness Probe configuration
4. **Automatic Recovery** - Simulates failures and verifies automatic pod restart
5. **Cleanup** - Removes test resources after completion

## Project Structure

```
k8s-tests-project/
├── conftest.py              # Pytest fixtures (shared across all tests)
├── test_k8s_e2e.py          # Main test runner script
├── configs.yml              # Cluster connection configurations
├── nginx-healthcheck.yaml   # Sample pod manifest
├── tests/                   # Test modules
│   ├── __init__.py
│   ├── test_cluster.py      # Cluster status tests
│   ├── test_pod.py          # Pod status tests
│   ├── test_health.py       # Health check tests
│   ├── test_liveness.py     # Liveness probe failure tests
│   └── test_cleanup.py      # Resource cleanup tests
└── README.md
```

## Prerequisites

### Required Software

- Python 3.7 or higher
- kubectl configured with cluster access
- Kubernetes cluster (local or remote)

### Python Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Required packages:
- `pytest` - Testing framework
- `kubernetes` - Kubernetes Python client
- `PyYAML` - YAML file handling

## Configuration

The test suite supports cluster connection configuration through a YAML file, while test parameters (namespace, pod name) are passed as command-line arguments.

### Configuration File (configs.yml)

Create a `configs.yml` file to manage different Kubernetes cluster connections:

```yaml
# Local Minikube cluster
minikube:
  kubeconfig: "~/.kube/config"
  context: "minikube"
  api_server: ""  # Auto-detected from kubeconfig
  verify_ssl: false  # Minikube uses self-signed certificates
  timeout: 300

# Local development cluster (kind/docker-desktop)
local:
  kubeconfig: "~/.kube/config"
  context: "docker-desktop"  # or "kind-kind" for kind
  api_server: ""  # Auto-detected from kubeconfig
  verify_ssl: false  # Local clusters typically use self-signed certs
  timeout: 300

# Development cluster
development:
  kubeconfig: "~/.kube/config"
  context: "dev-cluster"
  api_server: "https://dev-k8s.example.com:6443"
  verify_ssl: true
  timeout: 300

# Staging cluster
staging:
  kubeconfig: "~/.kube/config"
  context: "staging-cluster"
  api_server: "https://staging-k8s.example.com:6443"
  verify_ssl: true
  timeout: 600

# Production cluster
production:
  kubeconfig: "~/.kube/config"
  context: "prod-cluster"
  api_server: "https://prod-k8s.example.com:6443"
  verify_ssl: true
  timeout: 900

# CI/CD cluster (in-cluster config)
ci:
  kubeconfig: ""  # Empty means use in-cluster config
  context: ""
  api_server: ""
  verify_ssl: true
  timeout: 450

# Custom cluster with certificates
custom:
  kubeconfig: "/path/to/custom/kubeconfig"
  context: "custom-context"
  api_server: "https://custom-k8s.example.com:6443"
  verify_ssl: true
  certificate_authority: "/path/to/ca.crt"  # Optional
  client_certificate: "/path/to/client.crt"  # Optional
  client_key: "/path/to/client.key"  # Optional
  timeout: 300
```

### Configuration Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `kubeconfig` | Path to kubeconfig file (empty for in-cluster) | Yes |
| `context` | Kubernetes context name | Yes |
| `api_server` | Kubernetes API server URL | No |
| `verify_ssl` | Verify SSL certificates | No |
| `timeout` | Default timeout for operations (seconds) | No |
| `certificate_authority` | Path to CA certificate | No |
| `client_certificate` | Path to client certificate | No |
| `client_key` | Path to client key | No |

## Quick Start

### 1. Basic Usage (Default Kubeconfig)

Run tests using your default kubeconfig:

```bash
python test_k8s_e2e.py --namespace test-auto --pod-name nginx-healthcheck
```

This uses:
- Default kubeconfig from `~/.kube/config`
- Current context
- Namespace and pod name from arguments

### 2. Connect to Specific Cluster

#### Use Minikube Cluster

```bash
python test_k8s_e2e.py --cluster minikube --namespace test-ns --pod-name nginx-test
```

#### Use Local Cluster (Kind/Docker Desktop)

```bash
python test_k8s_e2e.py --cluster local --namespace test-ns --pod-name nginx-test
```

#### Use Development Cluster

```bash
python test_k8s_e2e.py --cluster development --namespace dev-test --pod-name nginx-dev
```

#### Use Staging Cluster

```bash
python test_k8s_e2e.py --cluster staging --namespace staging-test --pod-name nginx-staging
```

#### Use Production Cluster

```bash
python test_k8s_e2e.py --cluster production --namespace prod-test --pod-name nginx-prod
```

### 3. Advanced Usage

#### Use Custom Config File

```bash
python test_k8s_e2e.py --config my-clusters.yml --cluster dev --namespace test --pod-name nginx
```

#### Override Cluster Timeout

```bash
# Use production cluster config but override timeout
python test_k8s_e2e.py --cluster production --namespace prod-test --pod-name nginx-prod --timeout 1200
```

#### Custom Pod YAML File

```bash
python test_k8s_e2e.py --cluster local --namespace test --pod-name custom-pod --pod-yaml custom-pod.yaml
```

#### In-Cluster Testing (CI/CD)

```bash
# Uses in-cluster config when running inside a Kubernetes pod
python test_k8s_e2e.py --cluster ci --namespace ci-test --pod-name test-pod
```

### 4. Running Specific Tests

#### Run Specific Test Classes

```bash
# Only run cluster status tests
python test_k8s_e2e.py --namespace test --pod-name nginx -k TestClusterStatus

# Only run health check tests on staging cluster
python test_k8s_e2e.py --cluster staging --namespace test --pod-name nginx -k TestHealthChecks

# Run pod status tests on production
python test_k8s_e2e.py --cluster production --namespace prod-test --pod-name nginx -k TestPodStatus
```

#### Increase Verbosity

```bash
# More verbose output
python test_k8s_e2e.py -vv

# Show print statements
python test_k8s_e2e.py -s
```

#### Stop on First Failure

```bash
python test_k8s_e2e.py -x
```

#### Custom Namespace with Specific Tests

```bash
python test_k8s_e2e.py --namespace production-test -k TestPodStatus -v
```

## Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--config` | string | `configs.yml` | Path to cluster configuration YAML file |
| `--cluster` | string | None | Cluster name from config file (minikube, local, development, staging, production, ci, custom) |
| `--namespace` | string | `test-auto` | Kubernetes namespace for tests |
| `--pod-name` | string | `nginx-healthcheck` | Name of the test pod |
| `--pod-yaml` | string | `nginx-healthcheck.yaml` | Path to pod YAML manifest |
| `--timeout` | integer | from cluster config or `300` | Timeout for pod operations in seconds (overrides cluster config) |

### Getting Help

```bash
python test_k8s_e2e.py --help
```

## Test Suite Structure

The test suite is organized into separate modules for better maintainability:

### tests/test_cluster.py - TestClusterStatus

Verifies cluster accessibility and health:
- `test_api_accessible` - Kubernetes API server is reachable
- `test_nodes_ready` - All cluster nodes are in Ready state

### tests/test_pod.py - TestPodStatus

Validates pod deployment and state:
- `test_namespace_exists` - Test namespace exists
- `test_pod_exists` - Test pod is deployed
- `test_pod_running` - Pod is in Running state

### tests/test_health.py - TestHealthChecks

Verifies health probe configuration:
- `test_pod_has_probes` - Liveness and Readiness Probes are configured
- `test_readiness_probe_passes` - Readiness Probe returns success
- `test_liveness_probe_working` - Liveness Probe is functional

### tests/test_liveness.py - TestLivenessProbeFailure

Tests automatic recovery mechanisms:
- `test_simulate_liveness_failure` - Simulates failure and verifies restart

### tests/test_cleanup.py - TestCleanup

Removes test resources:
- `test_delete_pod` - Deletes test pod and verifies cleanup

### conftest.py - Shared Fixtures

Contains pytest fixtures shared across all test modules:
- `k8s_clients` - Initializes Kubernetes API clients with cluster config
- `setup_namespace` - Creates/verifies test namespace
- `deploy_pod` - Deploys test pod from YAML
- `wait_for_pod_ready` - Helper function to wait for pod readiness

## Pod YAML Requirements

The pod YAML file must include:

1. **Liveness Probe** - HTTP GET probe for container health
2. **Readiness Probe** - HTTP GET probe for service readiness

Example `nginx-healthcheck.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-healthcheck
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 10
      periodSeconds: 5
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
```

## Troubleshooting

### Connection Issues

If tests fail with connection errors:

```bash
# Verify kubectl access
kubectl cluster-info

# Check current context
kubectl config current-context

# Test namespace access
kubectl get namespaces
```

### Permission Issues

Ensure your kubeconfig has permissions to:
- Create/delete namespaces
- Create/delete pods
- Execute commands in pods
- Read node status

### Timeout Errors

If pods take longer to start, increase timeout:

```bash
python test_k8s_e2e.py --timeout 600
```

### Pod YAML Not Found

Ensure the YAML file exists in the current directory or provide full path:

```bash
python test_k8s_e2e.py --pod-yaml /path/to/pod.yaml
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: K8s E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Set up kubectl
        uses: azure/setup-kubectl@v1
      
      - name: Run K8s E2E Tests
        run: |
          # Use CI cluster from configs.yml
          python test_k8s_e2e.py --cluster ci --namespace ci-test --pod-name nginx-ci
```

### GitLab CI Example

```yaml
k8s-e2e-tests:
  image: python:3.9
  before_script:
    - pip install -r requirements.txt
    - kubectl version
  script:
    # Use CI cluster with in-cluster config
    - python test_k8s_e2e.py --cluster ci --namespace ci-test --pod-name nginx-test
  only:
    - main
    - develop

# Multi-environment testing
k8s-e2e-staging:
  image: python:3.9
  before_script:
    - pip install -r requirements.txt
    - kubectl version
  script:
    - python test_k8s_e2e.py --cluster staging --namespace staging-test --pod-name nginx-staging
  only:
    - develop

k8s-e2e-production:
  image: python:3.9
  before_script:
    - pip install -r requirements.txt
    - kubectl version
  script:
    - python test_k8s_e2e.py --cluster production --namespace prod-test --pod-name nginx-prod
  only:
    - main
  when: manual
```

## Output Example

### Using Cluster Config

```
======================================================================
Kubernetes E2E Test Configuration
======================================================================
Cluster Config: cluster: staging (from configs.yml)
Kubeconfig:     ~/.kube/config
Context:        staging-cluster
Namespace:      staging-test
Pod Name:       nginx-staging
Pod YAML:       nginx-healthcheck.yaml
Timeout:        600s
======================================================================

Loading kubeconfig from: /home/user/.kube/config
Using context: staging-cluster

========================= test session starts ==========================
collected 11 items

test_k8s_e2e.py::TestClusterStatus::test_api_accessible PASSED
test_k8s_e2e.py::TestClusterStatus::test_nodes_ready PASSED
test_k8s_e2e.py::TestPodStatus::test_namespace_exists PASSED
test_k8s_e2e.py::TestPodStatus::test_pod_exists PASSED
test_k8s_e2e.py::TestPodStatus::test_pod_running PASSED
test_k8s_e2e.py::TestHealthChecks::test_pod_has_probes PASSED
test_k8s_e2e.py::TestHealthChecks::test_readiness_probe_passes PASSED
test_k8s_e2e.py::TestHealthChecks::test_liveness_probe_working PASSED
test_k8s_e2e.py::TestLivenessProbeFailure::test_simulate_liveness_failure PASSED
test_k8s_e2e.py::TestCleanup::test_delete_pod PASSED

========================== 11 passed in 45.23s ==========================
```

### Using Default Kubeconfig

```
======================================================================
Kubernetes E2E Test Configuration
======================================================================
Cluster Config: default kubeconfig
Namespace:      test-auto
Pod Name:       nginx-healthcheck
Pod YAML:       nginx-healthcheck.yaml
Timeout:        300s
======================================================================

Using default kubeconfig

========================= test session starts ==========================
[test output continues...]
```

## Contributing

When adding new tests:

1. Follow the existing test class structure
2. Use descriptive test method names
3. Add appropriate assertions with clear messages
4. Update this README with new features

## License

Orange DevOps Task - Kubernetes Testing Exercise
