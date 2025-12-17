"""
Cleanup Tests

Tests for cleanup of test resources.
"""

import time

import pytest
from kubernetes import client
from kubernetes.client.rest import ApiException


# Get global variables from conftest
def get_namespace():
    import conftest

    return conftest.NAMESPACE


def get_pod_name():
    import conftest

    return conftest.POD_NAME


class TestCleanup:
    """Cleanup test resources."""

    def test_delete_pod(self, k8s_clients):
        """Delete the test pod after all tests."""
        core_v1, _ = k8s_clients
        namespace = get_namespace()
        pod_name = get_pod_name()

        try:
            core_v1.delete_namespaced_pod(
                name=pod_name, namespace=namespace, body=client.V1DeleteOptions()
            )
            print(f"Pod '{pod_name}' deleted successfully")

            # Wait for pod to be deleted
            time.sleep(10)

            # Verify deletion
            try:
                core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
                pytest.fail(f"Pod '{pod_name}' still exists after deletion")
            except ApiException as e:
                if e.status == 404:
                    print(f"Pod '{pod_name}' deletion confirmed")
                else:
                    raise
        except ApiException as e:
            if e.status == 404:
                print(f"Pod '{pod_name}' does not exist")
            else:
                pytest.fail(f"Failed to delete pod: {e}")
