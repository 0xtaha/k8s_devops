"""
Pytest fixtures for Kubernetes E2E tests.
This module contains shared fixtures used across all test modules.
"""

import os
import time

import pytest
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Global variables (set by test_k8s_e2e.py main)
NAMESPACE = "test-auto"
POD_NAME = "nginx-healthcheck"
POD_YAML_PATH = "nginx-healthcheck.yaml"
TIMEOUT = 300
CLUSTER_CONFIG = {}


@pytest.fixture(scope="module")
def k8s_clients():
    """
    Initialize Kubernetes clients.

    Returns:
        tuple: (CoreV1Api, AppsV1Api) clients
    """
    # Get cluster configuration from global variable
    cluster_config = globals().get("CLUSTER_CONFIG", {})

    try:
        if cluster_config:
            # Load config based on cluster configuration
            kubeconfig_path = cluster_config.get("kubeconfig", "")
            context_name = cluster_config.get("context", "")

            if not kubeconfig_path and not context_name:
                # Use in-cluster config (for CI/CD environments)
                print("Using in-cluster Kubernetes configuration")
                config.load_incluster_config()
            else:
                # Load from kubeconfig file
                kubeconfig_path = (
                    os.path.expanduser(kubeconfig_path) if kubeconfig_path else None
                )
                print(
                    f"Loading kubeconfig from: {kubeconfig_path or 'default location'}"
                )
                if context_name:
                    print(f"Using context: {context_name}")
                    config.load_kube_config(
                        config_file=kubeconfig_path, context=context_name
                    )
                else:
                    config.load_kube_config(config_file=kubeconfig_path)
        else:
            # No cluster config provided, use default behavior
            try:
                config.load_incluster_config()
                print("Using in-cluster Kubernetes configuration")
            except config.ConfigException:
                config.load_kube_config()
                print("Using default kubeconfig")

    except Exception as e:
        print(f"Error loading Kubernetes configuration: {e}")
        raise

    core_v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    return core_v1, apps_v1


@pytest.fixture(scope="module")
def setup_namespace(k8s_clients):
    """
    Create the test namespace if it doesn't exist.

    Args:
        k8s_clients: Kubernetes client tuple

    Yields:
        str: Namespace name
    """
    core_v1, _ = k8s_clients
    namespace = globals().get("NAMESPACE", "test-auto")

    # Check if namespace exists
    try:
        core_v1.read_namespace(name=namespace)
        print(f"Namespace '{namespace}' already exists")
    except ApiException as e:
        if e.status == 404:
            # Create namespace
            ns = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace))
            core_v1.create_namespace(body=ns)
            print(f"Namespace '{namespace}' created")

    yield namespace

    # Cleanup is handled in the test_cleanup function


@pytest.fixture(scope="module")
def deploy_pod(k8s_clients, setup_namespace):
    """
    Deploy the test pod from YAML file.

    Args:
        k8s_clients: Kubernetes client tuple
        setup_namespace: The namespace to deploy to

    Yields:
        str: Pod name
    """
    import yaml

    core_v1, _ = k8s_clients
    namespace = globals().get("NAMESPACE", "test-auto")
    pod_name = globals().get("POD_NAME", "nginx-healthcheck")
    pod_yaml_path = globals().get("POD_YAML_PATH", "nginx-healthcheck.yaml")

    # Load pod definition from YAML
    with open(pod_yaml_path, "r") as f:
        pod_manifest = yaml.safe_load(f)

    # Check if pod already exists and delete it
    try:
        core_v1.delete_namespaced_pod(
            name=pod_name, namespace=namespace, body=client.V1DeleteOptions()
        )
        print(f"Existing pod '{pod_name}' deleted")
        time.sleep(10)  # Wait for deletion
    except ApiException as e:
        if e.status != 404:
            raise

    # Create the pod
    core_v1.create_namespaced_pod(namespace=namespace, body=pod_manifest)
    print(f"Pod '{pod_name}' created")

    # Wait for pod to be ready
    timeout = globals().get("TIMEOUT", 300)
    wait_for_pod_ready(core_v1, pod_name, namespace, timeout=timeout)

    yield pod_name


def wait_for_pod_ready(core_v1, pod_name, namespace, timeout=300):
    """
    Wait for a pod to be in Ready state.

    Args:
        core_v1: CoreV1Api client
        pod_name: Name of the pod
        namespace: Namespace of the pod
        timeout: Maximum time to wait in seconds

    Returns:
        bool: True if pod is ready, False otherwise
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            pod = core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)

            if pod.status.phase == "Running":
                # Check if all containers are ready
                if pod.status.conditions:
                    for condition in pod.status.conditions:
                        if condition.type == "Ready" and condition.status == "True":
                            print(f"Pod '{pod_name}' is ready")
                            return True

            time.sleep(2)
        except ApiException as e:
            if e.status == 404:
                print(f"Waiting for pod '{pod_name}' to be created...")
                time.sleep(2)
            else:
                raise

    raise TimeoutError(
        f"Pod '{pod_name}' did not become ready within {timeout} seconds"
    )
