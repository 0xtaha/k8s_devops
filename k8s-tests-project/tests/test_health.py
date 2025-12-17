"""
Health Check Tests

Tests for pod health checks (Liveness and Readiness Probes).
"""

import pytest


# Get global variables from conftest
def get_namespace():
    import conftest

    return conftest.NAMESPACE


def get_pod_name():
    import conftest

    return conftest.POD_NAME


class TestHealthChecks:
    """Test pod health checks (Liveness and Readiness Probes)."""

    def test_pod_has_probes(self, k8s_clients, deploy_pod):
        """Test if the pod has Liveness and Readiness Probes configured."""
        core_v1, _ = k8s_clients
        namespace = get_namespace()
        pod_name = get_pod_name()

        pod = core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)

        # Get the first container
        assert len(pod.spec.containers) > 0, "No containers found in pod"
        container = pod.spec.containers[0]

        # Check for Liveness Probe
        assert container.liveness_probe is not None, "Liveness Probe not configured"
        print(f"Liveness Probe configured: {container.liveness_probe.http_get.path}")

        # Check for Readiness Probe
        assert container.readiness_probe is not None, "Readiness Probe not configured"
        print(f"Readiness Probe configured: {container.readiness_probe.http_get.path}")

    def test_readiness_probe_passes(self, k8s_clients, deploy_pod):
        """Test if the Readiness Probe passes (Pod is Ready)."""
        core_v1, _ = k8s_clients
        namespace = get_namespace()
        pod_name = get_pod_name()

        pod = core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)

        # Check pod conditions
        ready = False
        if pod.status.conditions:
            for condition in pod.status.conditions:
                if condition.type == "Ready" and condition.status == "True":
                    ready = True
                    break

        assert ready, "Readiness Probe is not passing"
        print(f"Readiness Probe is passing - Pod is Ready")

    def test_liveness_probe_working(self, k8s_clients, deploy_pod):
        """Test if the Liveness Probe is working."""
        core_v1, _ = k8s_clients
        namespace = get_namespace()
        pod_name = get_pod_name()

        pod = core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)

        # Check container status
        assert len(pod.status.container_statuses) > 0, "No container statuses found"
        container_status = pod.status.container_statuses[0]

        # If restart count is 0, the liveness probe hasn't triggered a restart
        # This is expected for a healthy pod
        print(f"Container restart count: {container_status.restart_count}")
        print(f"Container ready: {container_status.ready}")

        assert container_status.ready, "Container is not ready"
