# Orange DevOps Task - Python Programming Exercises

This repository contains solutions for the Orange DevOps Python programming exercises.
---

## Exercise 1: Car Fleet Management System

A RESTful API backend built with Flask to manage a car rental fleet using Object-Oriented Programming (OOP).

### Features

- **RESTful API** with Flask
- Add cars to the fleet via API
- Rent cars to clients via API
- Return cars after rental via API
- Get available cars via API
- Get all cars with status via API
- View detailed car information via API
- Fleet statistics endpoint
- CORS support for frontend integration
- Comprehensive error handling

### Classes

#### `Car` Class
- **Attributes**: `brand`, `model`, `year`, `registration`, `availability`
- **Methods**:
  - `display_details()`: Displays car information
  - `is_available()`: Returns availability status

#### `Agency` Class
- **Attributes**: `name`, `cars` (list of Car objects)
- **Methods**:
  - `add_car(car)`: Adds a car to the fleet
  - `rent_car(registration)`: Marks a car as rented
  - `return_car(registration)`: Returns a car and makes it available
  - `display_available_cars()`: Shows only available cars
  - `display_all_cars()`: Shows all cars with their status

### Code Structure

The application is organized into separate modules for better maintainability:

- **`car_fleet/car.py`**: Contains the `Car` class definition
- **`car_fleet/agency.py`**: Contains the `Agency` class definition
- **`car_fleet/__init__.py`**: Package initialization that exports classes
- **`app.py`**: Flask REST API backend
- **`main.py`**: CLI version (legacy - for reference)


## Exercise 2: Kubernetes E2E Tests (OPTIONAL)

Automated end-to-end tests for a Kubernetes cluster using Python, Pytest, and the Kubernetes Python client.

### Prerequisites

- RKE2 Kubernetes cluster (or any Kubernetes cluster)
- `kubectl` configured with cluster access
- Python 3.8+
- Cluster access permissions to create/delete resources

### Features

The test suite verifies:

1. **Cluster Status**
   - Kubernetes API accessibility
   - Node health (Ready state)

2. **Pod Deployment**
   - Namespace creation
   - Pod deployment and status

3. **Health Checks**
   - Liveness Probe configuration
   - Readiness Probe configuration
   - Probe functionality

4. **Failure Simulation**
   - Liveness Probe failure simulation
   - Automatic pod restart verification

5. **Cleanup**
   - Pod deletion after tests

### Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pytest kubernetes PyYAML
```

2. Configure kubectl access to your cluster:
```bash
# Verify cluster access
kubectl cluster-info
kubectl get nodes
```

### Running the Tests

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate
```

2. Navigate to the k8s-tests directory:
```bash
cd k8s-tests
```

3. Run all tests:
```bash
pytest test_k8s_e2e.py -v -s
```

4. Deactivate when done:
```bash
deactivate
```

3. Run specific test classes:
```bash
# Test cluster status only
pytest test_k8s_e2e.py::TestClusterStatus -v -s

# Test pod status only
pytest test_k8s_e2e.py::TestPodStatus -v -s

# Test health checks only
pytest test_k8s_e2e.py::TestHealthChecks -v -s

# Test liveness probe failure
pytest test_k8s_e2e.py::TestLivenessProbeFailure -v -s
```

4. Run with detailed output:
```bash
pytest test_k8s_e2e.py -v -s --tb=short
```

### Test Execution Flow

```
1. Initialize Kubernetes clients
2. Create test-auto namespace (if not exists)
3. Deploy nginx-healthcheck pod
4. Test cluster status
   ├── API accessibility
   └── Node readiness
5. Test pod status
   ├── Namespace exists
   ├── Pod exists
   └── Pod running
6. Test health checks
   ├── Probes configured
   ├── Readiness probe passes
   └── Liveness probe working
7. Simulate liveness failure
   ├── Stop nginx service
   ├── Wait for probe failure
   └── Verify automatic restart
8. Cleanup
   └── Delete pod
```

### Pod Configuration

The test uses an nginx pod with health checks:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-healthcheck
  namespace: test-auto
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
    - containerPort: 80
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10
```

### Manual Pod Deployment (Optional)

You can also deploy the pod manually:

```bash
# Create namespace
kubectl create namespace test-auto

# Deploy pod
kubectl apply -f nginx-healthcheck.yaml

# Check pod status
kubectl get pods -n test-auto

# View pod details
kubectl describe pod nginx-healthcheck -n test-auto

# Check pod logs
kubectl logs nginx-healthcheck -n test-auto

# Delete pod
kubectl delete pod nginx-healthcheck -n test-auto
```

### Test Output Example

```bash
$ pytest test_k8s_e2e.py -v -s

============================= test session starts ==============================
collected 10 items

test_k8s_e2e.py::TestClusterStatus::test_api_accessible
Kubernetes API is accessible
PASSED

test_k8s_e2e.py::TestClusterStatus::test_nodes_ready
Ready nodes: ['node-1']
PASSED

test_k8s_e2e.py::TestPodStatus::test_namespace_exists
Namespace 'test-auto' exists
PASSED

test_k8s_e2e.py::TestPodStatus::test_pod_exists
Pod 'nginx-healthcheck' exists in namespace 'test-auto'
PASSED

test_k8s_e2e.py::TestPodStatus::test_pod_running
Pod 'nginx-healthcheck' is in Running state
PASSED

test_k8s_e2e.py::TestHealthChecks::test_pod_has_probes
Liveness Probe configured: /
Readiness Probe configured: /
PASSED

test_k8s_e2e.py::TestHealthChecks::test_readiness_probe_passes
Readiness Probe is passing - Pod is Ready
PASSED

test_k8s_e2e.py::TestHealthChecks::test_liveness_probe_working
Container restart count: 0
Container ready: True
PASSED

test_k8s_e2e.py::TestLivenessProbeFailure::test_simulate_liveness_failure
Initial restart count: 0
Stopped nginx service to trigger Liveness Probe failure
Waiting for Kubernetes to detect Liveness Probe failure...
Pod restarted! New restart count: 1
Pod is ready again after restart
PASSED

test_k8s_e2e.py::TestCleanup::test_delete_pod
Pod 'nginx-healthcheck' deleted successfully
Pod 'nginx-healthcheck' deletion confirmed
PASSED

============================== 10 passed in 125.43s ===============================
```

### ✓ Verified Test Results

The test suite has been successfully verified on **Minikube v1.34.0**:
- ✅ **All 10 tests passed** (100% success rate)
- ⏱️ **Test duration**: ~81 seconds
- 🐍 **Environment**: Python 3.14.2, pytest 9.0.2
- 📋 See `TEST_RESULTS.md` for detailed test report

### Troubleshooting

#### Issue: kubectl not configured
```
kubernetes.config.config_exception.ConfigException: Invalid kube-config file
```
**Solution**: Configure kubectl with your cluster credentials

#### Issue: Permission denied
```
ApiException: (403) Forbidden
```
**Solution**: Ensure your user has appropriate RBAC permissions

#### Issue: Namespace already exists
The tests handle existing namespaces automatically. No action needed.

#### Issue: Pod stuck in Pending state
```
TimeoutError: Pod 'nginx-healthcheck' did not become ready within 300 seconds
```
**Solution**:
- Check node resources: `kubectl describe node`
- Check pod events: `kubectl describe pod nginx-healthcheck -n test-auto`
- Verify image pull: `kubectl get events -n test-auto`

#### Issue: Tests timeout
**Solution**: Increase timeout values in the test configuration:
```python
TIMEOUT = 600  # Increase to 10 minutes
```

### Configuration

Edit these variables in `test_k8s_e2e.py` to customize:

```python
NAMESPACE = "test-auto"           # Test namespace
POD_NAME = "nginx-healthcheck"    # Pod name
POD_YAML_PATH = "nginx-healthcheck.yaml"  # Pod YAML path
TIMEOUT = 300                     # Timeout in seconds
```

---

## Dependencies

### Car Fleet Management API
- Python 3.8+
- Flask >= 3.0.0
- flask-cors >= 4.0.0

### Kubernetes E2E Tests
- Python 3.8+
- pytest >= 7.4.0
- kubernetes >= 28.1.0
- PyYAML >= 6.0.1

Install all dependencies:
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Development

### Running Tests Locally

For the Kubernetes tests, you can use:
- Minikube
- Kind (Kubernetes in Docker)
- k3s/RKE2
- Any Kubernetes cluster with API access

### Code Style

The code follows:
- PEP 8 style guide
- Google-style docstrings
- Object-oriented design principles

---

## License

This project is for educational purposes as part of the Orange DevOps assessment.

---

## Author

Developed for Orange DevOps TasK
