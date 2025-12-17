"""
Cluster Status Tests

Tests for cluster accessibility and node status.
"""

import pytest


class TestClusterStatus:
    """Test cluster accessibility and node status."""

    def test_api_accessible(self, k8s_clients):
        """Test if the Kubernetes API is accessible."""
        core_v1, _ = k8s_clients

        try:
            version = core_v1.get_api_resources()
            print(f"Kubernetes API is accessible")
            assert version is not None
        except Exception as e:
            pytest.fail(f"Failed to access Kubernetes API: {e}")

    def test_nodes_ready(self, k8s_clients):
        """Test if cluster nodes are in Ready state."""
        core_v1, _ = k8s_clients

        nodes = core_v1.list_node()
        assert len(nodes.items) > 0, "No nodes found in the cluster"

        ready_nodes = []
        not_ready_nodes = []

        for node in nodes.items:
            node_ready = False
            if node.status.conditions:
                for condition in node.status.conditions:
                    if condition.type == "Ready":
                        if condition.status == "True":
                            ready_nodes.append(node.metadata.name)
                            node_ready = True
                        else:
                            not_ready_nodes.append(node.metadata.name)
                        break

        print(f"Ready nodes: {ready_nodes}")
        if not_ready_nodes:
            print(f"Not ready nodes: {not_ready_nodes}")

        assert len(ready_nodes) > 0, "No nodes in Ready state"
