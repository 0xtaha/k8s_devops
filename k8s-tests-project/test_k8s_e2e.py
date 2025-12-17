#!/usr/bin/env python3
"""
Kubernetes E2E Tests - Main Runner
Orange DevOps Task - Kubernetes Testing Exercise

This script performs end-to-end tests on a Kubernetes cluster to verify:
1. Cluster accessibility and node status
2. Pod status verification
3. Health checks (Liveness and Readiness Probes)
4. Automatic pod restart on Liveness Probe failure
5. Cleanup after tests
"""

import argparse
import os
import sys

import pytest
import yaml

# Default Configuration
DEFAULT_NAMESPACE = "test-auto"
DEFAULT_POD_NAME = "nginx-healthcheck"
DEFAULT_POD_YAML_PATH = "nginx-healthcheck.yaml"
DEFAULT_TIMEOUT = 300  # 5 minutes timeout for pod operations
DEFAULT_CONFIG_FILE = "configs.yml"


def load_config_from_file(config_file, cluster="local"):
    """
    Load cluster configuration from YAML file.

    Args:
        config_file: Path to the configuration YAML file
        cluster: Cluster name (local, development, staging, production, ci, custom)

    Returns:
        dict: Configuration dictionary or None if file doesn't exist
    """
    if not os.path.exists(config_file):
        return None

    try:
        with open(config_file, "r") as f:
            all_configs = yaml.safe_load(f)

        if cluster not in all_configs:
            print(f"Warning: Cluster '{cluster}' not found in {config_file}")
            print(f"Available clusters: {', '.join(all_configs.keys())}")
            return None

        return all_configs[cluster]
    except Exception as e:
        print(f"Error loading config file {config_file}: {e}")
        return None


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Kubernetes E2E Tests - Orange DevOps Task",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default kubeconfig
  python test_k8s_e2e.py --namespace test-auto --pod-name nginx-test

  # Connect to local cluster (minikube/kind)
  python test_k8s_e2e.py --cluster local --namespace test-ns --pod-name my-pod

  # Connect to development cluster
  python test_k8s_e2e.py --cluster development --namespace dev-test --pod-name nginx-dev

  # Connect to production cluster with custom timeout
  python test_k8s_e2e.py --cluster production --namespace prod-test --pod-name nginx-prod --timeout 1200

  # Use custom config file
  python test_k8s_e2e.py --config my-clusters.yml --cluster staging --namespace test --pod-name nginx

  # Pass additional pytest arguments
  python test_k8s_e2e.py --cluster ci --namespace ci-test --pod-name test -k TestClusterStatus
        """,
    )

    parser.add_argument(
        "--config",
        type=str,
        default=DEFAULT_CONFIG_FILE,
        help=f"Path to cluster configuration YAML file (default: {DEFAULT_CONFIG_FILE})",
    )

    parser.add_argument(
        "--cluster",
        type=str,
        default=None,
        help="Cluster name from config file (minikube, local, development, staging, production, ci, custom)",
    )

    parser.add_argument(
        "--namespace",
        type=str,
        default=DEFAULT_NAMESPACE,
        help=f"Kubernetes namespace for tests (default: {DEFAULT_NAMESPACE})",
    )

    parser.add_argument(
        "--pod-name",
        type=str,
        default=DEFAULT_POD_NAME,
        help=f"Name of the test pod (default: {DEFAULT_POD_NAME})",
    )

    parser.add_argument(
        "--pod-yaml",
        type=str,
        default=DEFAULT_POD_YAML_PATH,
        help=f"Path to the pod YAML manifest (default: {DEFAULT_POD_YAML_PATH})",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Timeout for pod operations in seconds (overrides cluster config)",
    )

    # Parse known args to allow passing remaining args to pytest
    args, pytest_args = parser.parse_known_args()

    return args, pytest_args


if __name__ == "__main__":
    # Parse command line arguments
    args, pytest_args = parse_arguments()

    # Load cluster configuration from file if specified
    cluster_config = None
    if args.cluster:
        cluster_config = load_config_from_file(args.config, args.cluster)
        if cluster_config:
            config_source = f"cluster: {args.cluster} (from {args.config})"
        else:
            print(f"Warning: Could not load cluster config, using default kubeconfig")
            config_source = "default kubeconfig"
    else:
        config_source = "default kubeconfig"

    # Set test parameters - update conftest module
    import conftest

    conftest.NAMESPACE = args.namespace
    conftest.POD_NAME = args.pod_name
    conftest.POD_YAML_PATH = args.pod_yaml

    # Set timeout from cluster config or command line arg
    if args.timeout is not None:
        conftest.TIMEOUT = args.timeout
    elif cluster_config and "timeout" in cluster_config:
        conftest.TIMEOUT = cluster_config["timeout"]
    else:
        conftest.TIMEOUT = DEFAULT_TIMEOUT

    # Set cluster config
    if cluster_config:
        conftest.CLUSTER_CONFIG = cluster_config

    # Print configuration
    print("=" * 70)
    print("Kubernetes E2E Test Configuration")
    print("=" * 70)
    print(f"Cluster Config: {config_source}")
    if cluster_config:
        kubeconfig = cluster_config.get("kubeconfig", "in-cluster")
        context = cluster_config.get("context", "default")
        print(f"Kubeconfig:     {kubeconfig}")
        print(f"Context:        {context}")
    print(f"Namespace:      {conftest.NAMESPACE}")
    print(f"Pod Name:       {conftest.POD_NAME}")
    print(f"Pod YAML:       {conftest.POD_YAML_PATH}")
    print(f"Timeout:        {conftest.TIMEOUT}s")
    print("=" * 70)
    print()

    # Run pytest with tests directory and any additional pytest arguments
    pytest_cmd = ["tests/", "-v", "-s"] + pytest_args
    sys.exit(pytest.main(pytest_cmd))
