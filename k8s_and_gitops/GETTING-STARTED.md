# Getting Started with RKE2 and GitOps

Welcome! This guide will help you get started quickly with deploying a Kubernetes cluster using RKE2 and implementing GitOps with ArgoCD.

## What You'll Deploy

By following this guide, you'll have:
- A fully functional RKE2 Kubernetes cluster (single node)
- ArgoCD for GitOps continuous deployment
- Google's Online Boutique microservices demo application (11 microservices)
- NGINX Ingress Controller for external access
- Self-healing and auto-sync capabilities

## Prerequisites Check

Before starting, ensure you have:
- [ ] A Linux VM (Ubuntu 20.04/22.04 or Rocky Linux 8/9)
- [ ] At least 8 GB RAM and 4 CPU cores
- [ ] 50 GB of free disk space
- [ ] Root or sudo access
- [ ] Internet connectivity

## Choose Your Path

### Option 1: Automated Installation (Recommended for Quick Setup)

Use the automated installation script:

```bash
cd k8s_and_gitops
sudo bash install.sh
```

This will automatically:
1. Install RKE2
2. Configure kubectl
3. Install NGINX Ingress
4. Install ArgoCD
5. Deploy Online Boutique
6. Configure Ingress
7. Set up DNS entries

**Time**: ~20-30 minutes (mostly waiting for components to start)

### Option 2: Manual Step-by-Step Installation (Recommended for Learning)

Follow the detailed guides in order:

1. **[01-RKE2-INSTALLATION.md](./01-RKE2-INSTALLATION.md)** - Set up Kubernetes cluster
2. **[02-ARGOCD-INSTALLATION.md](./02-ARGOCD-INSTALLATION.md)** - Install ArgoCD
3. **[03-DEPLOY-APPLICATION.md](./03-DEPLOY-APPLICATION.md)** - Deploy the application
4. **[04-EXPOSE-APPLICATION.md](./04-EXPOSE-APPLICATION.md)** - Expose via Ingress
5. **[05-RECONCILIATION-TESTING.md](./05-RECONCILIATION-TESTING.md)** - Test GitOps features

**Time**: ~60-90 minutes (with reading and understanding)

### Option 3: Using Manifests Only

If you already have a Kubernetes cluster:

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Deploy application using the provided manifests
kubectl apply -f manifests/argocd-application.yaml

# Create Ingress
kubectl apply -f manifests/online-boutique-ingress.yaml
```

## What Happens During Installation?

### Phase 1: Cluster Setup
- RKE2 downloads and installs Kubernetes components
- Control plane starts (API server, scheduler, controller manager)
- Networking (CNI) is configured
- CoreDNS is deployed for service discovery

### Phase 2: Ingress Setup
- NGINX Ingress Controller is deployed
- NodePort services are created for external access
- Admission webhooks are configured

### Phase 3: ArgoCD Installation
- ArgoCD namespace is created
- ArgoCD components are deployed (server, controller, repo-server, redis, dex)
- Initial admin credentials are generated
- ArgoCD becomes ready to manage applications

### Phase 4: Application Deployment
- ArgoCD Application resource is created
- ArgoCD clones the microservices-demo Git repository
- 11 microservices are deployed
- Services and deployments are created
- Pods start running

### Phase 5: Access Configuration
- Ingress rules are created
- DNS entries are added to /etc/hosts
- Application becomes accessible via browser

## After Installation

### 1. Verify Everything is Running

```bash
# Set up environment (if not using automated script)
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
export PATH=$PATH:/var/lib/rancher/rke2/bin

# Check cluster
kubectl get nodes

# Check ArgoCD
kubectl get pods -n argocd

# Check application
kubectl get pods -n online-boutique

# Check ingress
kubectl get ingress -n online-boutique
```

### 2. Access the Application

Find your NodePort:
```bash
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

Open in browser:
```
http://shop.local:<HTTP_NODEPORT>
```

### 3. Access ArgoCD

Get the admin password:
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
echo
```

Port-forward to access UI:
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open in browser: `https://localhost:8080`
- Username: `admin`
- Password: (from command above)

### 4. Test GitOps Reconciliation

Try scaling a deployment manually:
```bash
kubectl scale deployment frontend -n online-boutique --replicas=5
```

Watch ArgoCD automatically revert it back:
```bash
kubectl get deployment frontend -n online-boutique -w
```

Within 3-5 minutes, ArgoCD will detect the drift and correct it back to 1 replica.

## Quick Reference

For common commands and operations, see **[QUICK-REFERENCE.md](./QUICK-REFERENCE.md)**

## Project Structure

```
k8s_and_gitops/
├── README.md                          # Project overview
├── GETTING-STARTED.md                 # This file
├── QUICK-REFERENCE.md                 # Command reference
├── install.sh                         # Automated installation script
│
├── 01-RKE2-INSTALLATION.md           # RKE2 setup guide
├── 02-ARGOCD-INSTALLATION.md         # ArgoCD installation
├── 03-DEPLOY-APPLICATION.md          # Application deployment
├── 04-EXPOSE-APPLICATION.md          # Ingress configuration
├── 05-RECONCILIATION-TESTING.md      # GitOps testing
│
└── manifests/
    ├── argocd-application.yaml       # ArgoCD App definition
    ├── argocd-ingress.yaml           # ArgoCD UI Ingress
    └── online-boutique-ingress.yaml  # Application Ingress
```

## Common First-Time Issues

### Issue: Pods stuck in Pending
**Solution**: Check if control plane taints are removed
```bash
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
kubectl taint nodes --all node-role.kubernetes.io/master-
```

### Issue: Can't access application in browser
**Solution**: Verify /etc/hosts entry and NodePort
```bash
cat /etc/hosts | grep shop.local
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

### Issue: ArgoCD shows OutOfSync
**Solution**: This is normal initially. Wait for auto-sync or manually sync
```bash
# Check status
kubectl get application online-boutique -n argocd

# Manual sync if needed
argocd app sync online-boutique
```

### Issue: Ingress shows no ADDRESS
**Solution**: This is expected with NodePort. Access via NodeIP:NodePort
```bash
# Get your node IP
hostname -I | awk '{print $1}'

# Get NodePort
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

## Learning Path

### Beginner
1. Follow the automated installation
2. Access and explore the Online Boutique application
3. View the application in ArgoCD UI
4. Try scaling a deployment and watch it revert

### Intermediate
1. Follow the manual step-by-step guides
2. Understand each component's role
3. Experiment with different sync policies
4. Deploy additional applications with ArgoCD

### Advanced
1. Customize RKE2 configuration
2. Implement custom Helm charts with ArgoCD
3. Set up multi-branch deployments (dev/staging/prod)
4. Configure ArgoCD with webhooks for instant sync
5. Implement ApplicationSets for multi-cluster deployments

## Next Steps

After completing the basic setup:

1. **Explore the Application**: Browse the Online Boutique, add items to cart, complete checkout
2. **Learn ArgoCD**: Explore the UI, view resource tree, check sync status
3. **Test Self-Healing**: Make manual changes and watch ArgoCD revert them
4. **Customize**: Modify the manifests and redeploy
5. **Scale Up**: Consider adding worker nodes to your cluster
6. **Add Monitoring**: Install Prometheus and Grafana
7. **Implement CI/CD**: Connect your own Git repositories

## Support and Documentation

- **Guides**: All numbered guides (01-05) in this directory
- **Quick Reference**: [QUICK-REFERENCE.md](./QUICK-REFERENCE.md)
- **Main README**: [README.md](./README.md)
- **RKE2 Docs**: https://docs.rke2.io/
- **ArgoCD Docs**: https://argo-cd.readthedocs.io/
- **Kubernetes Docs**: https://kubernetes.io/docs/

## Tips for Success

1. **Be Patient**: Initial deployment can take 10-15 minutes
2. **Watch Logs**: Use `kubectl logs` to understand what's happening
3. **Use -w Flag**: Watch resources in real-time with `kubectl get pods -w`
4. **Check Events**: Use `kubectl get events` to see cluster activity
5. **Read Error Messages**: Kubernetes error messages are usually helpful
6. **Start Simple**: Get the basics working before customizing

## Cleanup

When you're done experimenting:

```bash
# Remove application
kubectl delete namespace online-boutique

# Remove ArgoCD
kubectl delete namespace argocd

# Completely remove RKE2
sudo /usr/local/bin/rke2-uninstall.sh
```

## Ready to Start?

Choose your installation method above and begin! Remember:
- **Automated**: Fast setup, good for demos and quick testing
- **Manual**: Better understanding, recommended for learning
- **Manifests Only**: If you already have Kubernetes

Good luck, and enjoy exploring Kubernetes and GitOps! 🚀
