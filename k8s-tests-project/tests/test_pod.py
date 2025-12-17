"""
Pod Status Tests

Tests for pod status and deployment.
"""

import pytest
from kubernetes.client.rest import ApiException


# Get global variables from conftest
def get_namespace():
    import conftest

    return conftest.NAMESPACE


def get_pod_name():
    import conftest

    return conftest.POD_NAME


class TestPodStatus:
    """Test pod status and deployment."""

    def test_namespace_exists(self, k8s_clients, setup_namespace):
        """Test if the test namespace exists."""
        core_v1, _ = k8s_clients
        namespace = get_namespace()

        try:
            ns = core_v1.read_namespace(name=namespace)
            assert ns.metadata.name == namespace
            print(f"Namespace '{namespace}' exists")
        except ApiException as e:
            pytest.fail(f"Namespace '{namespace}' does not exist: {e}")

    def test_pod_exists(self, k8s_clients, deploy_pod):
        """Test if the nginx pod exists in the namespace."""
        core_v1, _ = k8s_clients
        namespace = get_namespace()
        pod_name = get_pod_name()

        pods = core_v1.list_namespaced_pod(namespace=namespace)
        pod_names = [pod.metadata.name for pod in pods.items]

        assert pod_name in pod_names, (
            f"Pod '{pod_name}' not found in namespace '{namespace}'"
        )
        print(f"Pod '{pod_name}' exists in namespace '{namespace}'")

    def test_pod_running(self, k8s_clients, deploy_pod):
        """Test if the nginx pod is in Running state."""
        core_v1, _ = k8s_clients
        namespace = get_namespace()
        pod_name = get_pod_name()

        pod = core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)

        assert pod.status.phase == "Running", (
            f"Pod is in {pod.status.phase} state, expected Running"
        )
        print(f"Pod '{pod_name}' is in Running state")
