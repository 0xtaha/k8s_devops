# RKE2 Cluster Installation Guide

This guide walks you through setting up a single-node RKE2 Kubernetes cluster.

## Prerequisites

- A Linux VM (Ubuntu 20.04/22.04 or Rocky Linux 8/9 recommended)
- Minimum Recommended Specifications:
  - CPU: 4 cores
  - RAM: 8 GB
  - Disk: 50 GB
  - Root or sudo access

## Step 1: Prepare the System

### Update the system
```bash
# For Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# For RHEL/Rocky/CentOS
sudo yum update -y
```

### Disable swap (required for Kubernetes)
```bash
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab
```

### Configure firewall (if enabled)
```bash
# For Ubuntu with ufw
sudo ufw allow 6443/tcp  # Kubernetes API
sudo ufw allow 9345/tcp  # RKE2 supervisor API
sudo ufw allow 10250/tcp # Kubelet
sudo ufw allow 2379:2380/tcp # etcd
sudo ufw allow 30000:32767/tcp # NodePort Services

# For RHEL/Rocky with firewalld
sudo firewall-cmd --permanent --add-port=6443/tcp
sudo firewall-cmd --permanent --add-port=9345/tcp
sudo firewall-cmd --permanent --add-port=10250/tcp
sudo firewall-cmd --permanent --add-port=2379-2380/tcp
sudo firewall-cmd --permanent --add-port=30000-32767/tcp
sudo firewall-cmd --reload
```

## Step 2: Install RKE2

### Download and install RKE2
```bash
curl -sfL https://get.rke2.io | sudo sh -
```

### Create RKE2 configuration directory
```bash
sudo mkdir -p /etc/rancher/rke2
```

### Create RKE2 configuration file
```bash
sudo tee /etc/rancher/rke2/config.yaml <<EOF
# RKE2 Server Configuration
write-kubeconfig-mode: "0644"
tls-san:
  - "$(hostname -I | awk '{print $1}')"
  - "127.0.0.1"

# Disable components we don't need for single node
# cluster-cidr: "10.42.0.0/16"
# service-cidr: "10.43.0.0/16"

# Enable embedded etcd
# server: https://127.0.0.1:9345
EOF
```

## Step 3: Start RKE2 Service

### Enable and start RKE2 server
```bash
sudo systemctl enable rke2-server.service
sudo systemctl start rke2-server.service
```

### Check service status
```bash
sudo systemctl status rke2-server.service
```

### Monitor logs (optional, wait until fully started)
```bash
sudo journalctl -u rke2-server -f
```

Wait for the service to fully start. This may take 2-5 minutes.

## Step 4: Configure kubectl

### Add RKE2 binaries to PATH
```bash
echo 'export PATH=$PATH:/var/lib/rancher/rke2/bin' >> ~/.bashrc
echo 'export KUBECONFIG=/etc/rancher/rke2/rke2.yaml' >> ~/.bashrc
source ~/.bashrc
```

### For persistent configuration, add to profile
```bash
sudo tee /etc/profile.d/rke2.sh <<EOF
export PATH=\$PATH:/var/lib/rancher/rke2/bin
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
EOF

source /etc/profile.d/rke2.sh
```

### Create symlink for kubectl (alternative approach)
```bash
sudo ln -s /var/lib/rancher/rke2/bin/kubectl /usr/local/bin/kubectl
```

### Set proper permissions for kubeconfig
```bash
sudo chmod 644 /etc/rancher/rke2/rke2.yaml
```

## Step 5: Verify Installation

### Check cluster status
```bash
kubectl get nodes
```

Expected output:
```
NAME       STATUS   ROLES                       AGE   VERSION
your-vm    Ready    control-plane,etcd,master   1m    v1.28.x+rke2r1
```

### Check all pods are running
```bash
kubectl get pods -A
```

### Check cluster info
```bash
kubectl cluster-info
```

## Step 6: Install NGINX Ingress Controller

For exposing applications, we'll install the NGINX Ingress Controller.

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.5/deploy/static/provider/baremetal/deploy.yaml
```

### Verify Ingress Controller is running
```bash
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx
```

### Patch the Ingress service to use NodePort or LoadBalancer
For a single-node setup, NodePort is typically used:

```bash
kubectl patch svc ingress-nginx-controller -n ingress-nginx -p '{"spec":{"type":"NodePort"}}'
```

Get the NodePort assigned:
```bash
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

## Step 7: Allow Workloads on Control Plane (Single Node)

By default, RKE2 taints the control plane node. For a single-node cluster, remove the taint:

```bash
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
kubectl taint nodes --all node-role.kubernetes.io/master-
```

## Troubleshooting

### Check RKE2 logs
```bash
sudo journalctl -u rke2-server -xe
```

### Restart RKE2 service
```bash
sudo systemctl restart rke2-server
```

### Check network configuration
```bash
kubectl get pods -n kube-system
```

### Uninstall RKE2 (if needed)
```bash
sudo /usr/local/bin/rke2-uninstall.sh
```

## Next Steps

Once your RKE2 cluster is running, proceed to:
- [02-ARGOCD-INSTALLATION.md](./02-ARGOCD-INSTALLATION.md) - Install and configure ArgoCD
