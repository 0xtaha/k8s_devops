# Kubernetes Cluster Deployment with GitOps (RKE2 + ArgoCD)

This repository contains comprehensive guides for deploying a Kubernetes cluster using RKE2 and implementing GitOps practices with ArgoCD to deploy the Google Cloud Online Boutique microservices application.

## Project Overview

This project demonstrates:
1. Setting up a production-ready Kubernetes cluster using RKE2
2. Installing and configuring ArgoCD for GitOps workflows
3. Deploying a complex microservices application (Online Boutique)
4. Exposing applications using Ingress
5. Testing GitOps reconciliation and self-healing capabilities

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     RKE2 Kubernetes Cluster                 │
│                         (Single Node)                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   ArgoCD (GitOps)                     │  │
│  │                                                       │  │
│  │  - Application Controller                            │  │
│  │  - Repo Server                                       │  │
│  │  - Server UI/API                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Online Boutique Microservices                │  │
│  │                                                       │  │
│  │  - Frontend          - Cart Service                  │  │
│  │  - Product Catalog   - Checkout Service              │  │
│  │  - Recommendation    - Payment Service               │  │
│  │  - Currency Service  - Shipping Service              │  │
│  │  - Email Service     - Ad Service                    │  │
│  │  - Redis Cache       - Load Generator                │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              NGINX Ingress Controller                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    External Access via
                  shop.local (Browser)
```

## Prerequisites

### Hardware Requirements
- **Minimum Specifications**:
  - CPU: 4 cores
  - RAM: 8 GB
  - Disk: 50 GB
  - Network: Internet connectivity

- **Recommended Specifications**:
  - CPU: 8 cores
  - RAM: 16 GB
  - Disk: 100 GB

### Software Requirements
- Linux OS (Ubuntu 20.04/22.04, Rocky Linux 8/9, or similar)
- Root or sudo access
- curl, wget installed

## Quick Start

Follow these guides in order:

### 1. RKE2 Cluster Installation
**File**: [01-RKE2-INSTALLATION.md](./01-RKE2-INSTALLATION.md)

Install and configure a single-node RKE2 Kubernetes cluster with:
- RKE2 server setup
- kubectl configuration
- NGINX Ingress Controller
- Control plane taint removal for single-node operation

**Time**: ~15-20 minutes

### 2. ArgoCD Installation
**File**: [02-ARGOCD-INSTALLATION.md](./02-ARGOCD-INSTALLATION.md)

Deploy ArgoCD for GitOps workflows:
- ArgoCD installation
- UI and CLI access configuration
- Initial admin setup
- Repository connections

**Time**: ~10-15 minutes

### 3. Application Deployment
**File**: [03-DEPLOY-APPLICATION.md](./03-DEPLOY-APPLICATION.md)

Deploy Online Boutique using GitOps:
- Create ArgoCD Application
- Configure auto-sync and self-heal
- Monitor deployment status
- Verify all microservices

**Time**: ~10-15 minutes

### 4. Application Exposure
**File**: [04-EXPOSE-APPLICATION.md](./04-EXPOSE-APPLICATION.md)

Expose the application via Ingress:
- Create Ingress resource
- Configure DNS (local)
- Access via web browser
- Optional: TLS/HTTPS setup

**Time**: ~10 minutes

### 5. Reconciliation Testing
**File**: [05-RECONCILIATION-TESTING.md](./05-RECONCILIATION-TESTING.md)

Test GitOps capabilities:
- Manual drift detection
- Self-healing verification
- Resource pruning
- Sync policy validation

**Time**: ~15-20 minutes

## Step-by-Step Instructions

### Step 1: Clone or Navigate to This Directory

```bash
cd k8s_and_gitops
```

### Step 2: Install RKE2

```bash
# Follow 01-RKE2-INSTALLATION.md
# Key commands:
curl -sfL https://get.rke2.io | sudo sh -
sudo systemctl enable --now rke2-server.service
```

### Step 3: Verify Cluster

```bash
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
kubectl get nodes
kubectl get pods -A
```

### Step 4: Install ArgoCD

```bash
# Follow 02-ARGOCD-INSTALLATION.md
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Step 5: Deploy Application

```bash
# Follow 03-DEPLOY-APPLICATION.md
# Create ArgoCD Application with GitOps
kubectl apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: online-boutique
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/GoogleCloudPlatform/microservices-demo.git
    targetRevision: HEAD
    path: release
  destination:
    server: https://kubernetes.default.svc
    namespace: online-boutique
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
EOF
```

### Step 6: Create Ingress

```bash
# Follow 04-EXPOSE-APPLICATION.md
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: online-boutique-ingress
  namespace: online-boutique
spec:
  ingressClassName: nginx
  rules:
  - host: shop.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
EOF
```

### Step 7: Access Application

```bash
# Add to /etc/hosts
echo "$(hostname -I | awk '{print $1}') shop.local" | sudo tee -a /etc/hosts

# Get NodePort
kubectl get svc ingress-nginx-controller -n ingress-nginx

# Access in browser:
# http://shop.local:<NODEPORT>
```

### Step 8: Test GitOps

```bash
# Follow 05-RECONCILIATION-TESTING.md
# Test self-healing
kubectl scale deployment frontend -n online-boutique --replicas=5

# Watch ArgoCD revert the change
kubectl get deployment frontend -n online-boutique -w
```

## Key Features

### GitOps Benefits
- **Declarative Configuration**: All infrastructure as code
- **Version Control**: Complete audit trail in Git
- **Automated Sync**: Continuous reconciliation
- **Self-Healing**: Automatic drift correction
- **Easy Rollback**: Git-based version control

### RKE2 Benefits
- **Security Focused**: CIS hardened by default
- **Production Ready**: Enterprise-grade Kubernetes
- **Easy Management**: Simple installation and upgrades
- **Lightweight**: Efficient resource usage

### Online Boutique Application
- **11 Microservices**: Real-world complexity
- **Multiple Languages**: Go, Python, Node.js, Java, C#
- **gRPC Communication**: Modern service mesh
- **Observability**: Metrics and tracing ready

## Accessing Components

### Kubernetes Cluster
```bash
kubectl cluster-info
kubectl get nodes
```

### ArgoCD UI
```bash
# Port-forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Access: https://localhost:8080
# Username: admin
# Password: 
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Online Boutique Application
```
http://shop.local:<NODEPORT>
```

## Monitoring and Management

### Check Application Status
```bash
# ArgoCD CLI
argocd app get online-boutique

# Kubectl
kubectl get application online-boutique -n argocd
kubectl get pods -n online-boutique
```

### View Logs
```bash
# Application logs
kubectl logs -n online-boutique deployment/frontend

# ArgoCD logs
kubectl logs -n argocd deployment/argocd-server
```

### Sync Operations
```bash
# Manual sync
argocd app sync online-boutique

# View history
argocd app history online-boutique
```

## Troubleshooting

### Common Issues

#### Pods Not Starting
```bash
kubectl describe pod <pod-name> -n online-boutique
kubectl logs <pod-name> -n online-boutique
```

#### Ingress Not Working
```bash
kubectl get ingress -n online-boutique
kubectl describe ingress online-boutique-ingress -n online-boutique
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

#### ArgoCD Not Syncing
```bash
argocd app get online-boutique --refresh
kubectl logs -n argocd deployment/argocd-application-controller
```

#### RKE2 Service Issues
```bash
sudo systemctl status rke2-server
sudo journalctl -u rke2-server -xe
```

### Getting Help

Check the detailed troubleshooting sections in each guide:
- [01-RKE2-INSTALLATION.md](./01-RKE2-INSTALLATION.md#troubleshooting)
- [02-ARGOCD-INSTALLATION.md](./02-ARGOCD-INSTALLATION.md#troubleshooting)
- [04-EXPOSE-APPLICATION.md](./04-EXPOSE-APPLICATION.md#troubleshooting)
- [05-RECONCILIATION-TESTING.md](./05-RECONCILIATION-TESTING.md#troubleshooting)

## Cleanup

### Remove Application
```bash
argocd app delete online-boutique
kubectl delete namespace online-boutique
```

### Remove ArgoCD
```bash
kubectl delete namespace argocd
```

### Remove RKE2
```bash
sudo /usr/local/bin/rke2-uninstall.sh
```

## Additional Resources

### Documentation
- [RKE2 Documentation](https://docs.rke2.io/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Online Boutique Repository](https://github.com/GoogleCloudPlatform/microservices-demo)

### Related Tools
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [Helm](https://helm.sh/)
- [cert-manager](https://cert-manager.io/)
- [MetalLB](https://metallb.universe.tf/)

## Project Structure

```
k8s_and_gitops/
├── README.md                          # This file
├── 01-RKE2-INSTALLATION.md           # RKE2 cluster setup
├── 02-ARGOCD-INSTALLATION.md         # ArgoCD deployment
├── 03-DEPLOY-APPLICATION.md          # Application deployment
├── 04-EXPOSE-APPLICATION.md          # Ingress configuration
└── 05-RECONCILIATION-TESTING.md      # GitOps testing
```

## Learning Objectives

After completing this guide, you will understand:
1. How to deploy a production-ready Kubernetes cluster with RKE2
2. GitOps principles and ArgoCD workflows
3. Microservices deployment and management
4. Ingress configuration and application exposure
5. Self-healing and reconciliation in GitOps
6. Kubernetes troubleshooting and debugging

## Contributing

This guide is part of the Orange DevOps Task project. For improvements or issues:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is provided as-is for educational and demonstration purposes.

## Support

For questions or issues:
1. Review the troubleshooting sections in each guide
2. Check the official documentation links
3. Review Kubernetes and ArgoCD logs
4. Consult the community forums

## Acknowledgments

- RKE2 by Rancher/SUSE
- ArgoCD by Argoproj
- Online Boutique by Google Cloud Platform
- Kubernetes community

---

**Next Steps**: Start with [01-RKE2-INSTALLATION.md](./01-RKE2-INSTALLATION.md) to begin your deployment journey.
