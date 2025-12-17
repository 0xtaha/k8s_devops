"""
Liveness Probe Failure Tests

Tests for automatic pod restart on Liveness Probe failure.
"""

import time

from kubernetes.stream import stream


# Get global variables from conftest
def get_namespace():
    import conftest

    return conftest.NAMESPACE


def get_pod_name():
    import conftest

    return conftest.POD_NAME


def get_timeout():
    import conftest

    return conftest.TIMEOUT


class TestLivenessProbeFailure:
    """Test automatic pod restart on Liveness Probe failure."""

    def test_simulate_liveness_failure(self, k8s_clients, deploy_pod):
        """
        Simulate a Liveness Probe failure and verify automatic restart.

        We'll do this by:
        1. Getting the current restart count
        2. Breaking the nginx service inside the container
        3. Waiting for Kubernetes to detect the failure
        4. Verifying the restart count increased
        """
        core_v1, _ = k8s_clients
        namespace = get_namespace()
        pod_name = get_pod_name()

        # Get initial restart count
        pod = core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        initial_restart_count = pod.status.container_statuses[0].restart_count
        print(f"Initial restart count: {initial_restart_count}")

        # Execute command to stop nginx inside the container
        try:
            exec_command = ["/bin/sh", "-c", "nginx -s stop"]
            resp = stream(
                core_v1.connect_get_namespaced_pod_exec,
                pod_name,
                namespace,
                command=exec_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
            )
            print(f"Stopped nginx service to trigger Liveness Probe failure")
            print(f"Command output: {resp}")
        except Exception as e:
            print(f"Error stopping nginx: {e}")

        # Wait for Kubernetes to detect the failure and restart the pod
        print("Waiting for Kubernetes to detect Liveness Probe failure...")
        time.sleep(30)  # Wait for probe to fail (initial delay + period)

        # Check if restart count increased
        max_wait = 60
        start_time = time.time()
        restart_detected = False

        while time.time() - start_time < max_wait:
            pod = core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            current_restart_count = pod.status.container_statuses[0].restart_count

            if current_restart_count > initial_restart_count:
                restart_detected = True
                print(f"Pod restarted! New restart count: {current_restart_count}")
                break

            time.sleep(5)

        assert restart_detected, "Pod did not restart after Liveness Probe failure"

        # Wait for pod to be ready again after restart
        from conftest import wait_for_pod_ready

        timeout = get_timeout()
        wait_for_pod_ready(core_v1, pod_name, namespace, timeout=timeout)
        print("Pod is ready again after restart")
