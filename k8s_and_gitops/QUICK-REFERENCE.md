# Quick Reference Guide

This is a condensed reference for common commands and operations. For detailed explanations, refer to the main guides.

## RKE2 Commands

### Service Management
```bash
# Start RKE2
sudo systemctl start rke2-server.service

# Stop RKE2
sudo systemctl stop rke2-server.service

# Restart RKE2
sudo systemctl restart rke2-server.service

# Check status
sudo systemctl status rke2-server.service

# View logs
sudo journalctl -u rke2-server -f
```

### Environment Setup
```bash
# Set KUBECONFIG
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml

# Add to PATH
export PATH=$PATH:/var/lib/rancher/rke2/bin

# Make permanent
echo 'export KUBECONFIG=/etc/rancher/rke2/rke2.yaml' >> ~/.bashrc
echo 'export PATH=$PATH:/var/lib/rancher/rke2/bin' >> ~/.bashrc
source ~/.bashrc
```

## Kubernetes Commands

### Cluster Info
```bash
# Get cluster info
kubectl cluster-info

# Get nodes
kubectl get nodes

# Get all resources in all namespaces
kubectl get all -A

# Get pods with wide output
kubectl get pods -o wide -A
```

### Namespace Operations
```bash
# Create namespace
kubectl create namespace <namespace-name>

# List namespaces
kubectl get namespaces

# Delete namespace
kubectl delete namespace <namespace-name>
```

### Pod Operations
```bash
# Get pods in namespace
kubectl get pods -n <namespace>

# Describe pod
kubectl describe pod <pod-name> -n <namespace>

# View logs
kubectl logs <pod-name> -n <namespace>

# Follow logs
kubectl logs -f <pod-name> -n <namespace>

# Execute command in pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# Delete pod
kubectl delete pod <pod-name> -n <namespace>
```

### Deployment Operations
```bash
# Get deployments
kubectl get deployments -n <namespace>

# Scale deployment
kubectl scale deployment <name> -n <namespace> --replicas=<count>

# Restart deployment
kubectl rollout restart deployment <name> -n <namespace>

# Check rollout status
kubectl rollout status deployment <name> -n <namespace>
```

### Service Operations
```bash
# Get services
kubectl get svc -n <namespace>

# Describe service
kubectl describe svc <service-name> -n <namespace>

# Port forward
kubectl port-forward svc/<service-name> -n <namespace> <local-port>:<service-port>
```

### Ingress Operations
```bash
# Get ingress
kubectl get ingress -n <namespace>

# Describe ingress
kubectl describe ingress <ingress-name> -n <namespace>

# Delete ingress
kubectl delete ingress <ingress-name> -n <namespace>
```

## ArgoCD Commands

### Login
```bash
# Port-forward method
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Login via CLI
argocd login localhost:8080 --insecure

# Login with IP
argocd login <VM-IP>:<NODEPORT> --insecure
```

### Password Management
```bash
# Get initial password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
echo

# Change password
argocd account update-password
```

### Application Management
```bash
# List applications
argocd app list

# Get application details
argocd app get <app-name>

# Create application
argocd app create <app-name> \
  --repo <git-url> \
  --path <path> \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace <namespace>

# Delete application
argocd app delete <app-name>

# Sync application
argocd app sync <app-name>

# Refresh application
argocd app get <app-name> --refresh

# Hard refresh
argocd app get <app-name> --hard-refresh

# View sync history
argocd app history <app-name>

# Rollback application
argocd app rollback <app-name> <revision-id>
```

### Sync Policy
```bash
# Enable auto-sync
argocd app set <app-name> --sync-policy automated

# Enable auto-prune
argocd app set <app-name> --auto-prune

# Enable self-heal
argocd app set <app-name> --self-heal

# Disable auto-sync
argocd app set <app-name> --sync-policy none
```

### Repository Management
```bash
# List repositories
argocd repo list

# Add repository
argocd repo add <git-url>

# Remove repository
argocd repo rm <git-url>
```

### Project Management
```bash
# List projects
argocd proj list

# Create project
argocd proj create <project-name>

# Delete project
argocd proj delete <project-name>
```

## Online Boutique Specific

### Check Application Status
```bash
# Get all pods
kubectl get pods -n online-boutique

# Watch pods
kubectl get pods -n online-boutique -w

# Get services
kubectl get svc -n online-boutique

# Get ingress
kubectl get ingress -n online-boutique
```

### View Logs
```bash
# Frontend logs
kubectl logs -n online-boutique deployment/frontend

# All services
kubectl logs -n online-boutique -l app=<service-name>
```

### Access Application
```bash
# Get NodePort
kubectl get svc ingress-nginx-controller -n ingress-nginx

# Access URL
# http://shop.local:<NODEPORT>
```

## Troubleshooting Commands

### Check Cluster Health
```bash
# Node status
kubectl get nodes
kubectl describe node <node-name>

# Component status
kubectl get componentstatuses

# Events
kubectl get events -A --sort-by='.lastTimestamp'
```

### Resource Usage
```bash
# Node resources
kubectl top nodes

# Pod resources
kubectl top pods -A

# Specific namespace
kubectl top pods -n <namespace>
```

### Debug Pods
```bash
# Describe pod
kubectl describe pod <pod-name> -n <namespace>

# Get logs
kubectl logs <pod-name> -n <namespace>

# Previous logs
kubectl logs <pod-name> -n <namespace> --previous

# Multiple containers
kubectl logs <pod-name> -c <container-name> -n <namespace>
```

### Network Debugging
```bash
# Test DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default

# Test connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl <service-name>.<namespace>.svc.cluster.local
```

### ArgoCD Debugging
```bash
# ArgoCD server logs
kubectl logs -n argocd deployment/argocd-server

# ArgoCD controller logs
kubectl logs -n argocd deployment/argocd-application-controller

# ArgoCD repo server logs
kubectl logs -n argocd deployment/argocd-repo-server
```

## Configuration Files

### RKE2 Config
```
/etc/rancher/rke2/config.yaml
```

### Kubeconfig
```
/etc/rancher/rke2/rke2.yaml
```

### ArgoCD Admin Password
```bash
kubectl -n argocd get secret argocd-initial-admin-secret
```

## Useful Aliases

Add to `~/.bashrc`:

```bash
# kubectl aliases
alias k='kubectl'
alias kg='kubectl get'
alias kd='kubectl describe'
alias kdel='kubectl delete'
alias kl='kubectl logs'
alias kex='kubectl exec -it'

# Namespace specific
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgi='kubectl get ingress'

# ArgoCD aliases
alias argocd-login='kubectl port-forward svc/argocd-server -n argocd 8080:443 &'
alias argocd-apps='argocd app list'
```

## Quick Deployment

### Deploy Everything
```bash
# 1. Install RKE2
curl -sfL https://get.rke2.io | sudo sh -
sudo systemctl enable --now rke2-server.service

# 2. Configure kubectl
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
export PATH=$PATH:/var/lib/rancher/rke2/bin

# 3. Install NGINX Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.5/deploy/static/provider/baremetal/deploy.yaml

# 4. Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 5. Deploy Online Boutique
kubectl apply -f manifests/argocd-application.yaml

# 6. Create Ingress
kubectl apply -f manifests/online-boutique-ingress.yaml

# 7. Add to hosts
echo "$(hostname -I | awk '{print $1}') shop.local argocd.local" | sudo tee -a /etc/hosts
```

## Important URLs

- ArgoCD UI: `https://argocd.local:<NODEPORT>` or `https://localhost:8080` (port-forward)
- Online Boutique: `http://shop.local:<NODEPORT>`
- Kubernetes Dashboard (if installed): `http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/`

## Common Issues

### Pods in Pending State
```bash
kubectl describe pod <pod-name> -n <namespace>
# Check: Insufficient resources, node taints, PVC issues
```

### ImagePullBackOff
```bash
kubectl describe pod <pod-name> -n <namespace>
# Check: Image name, registry credentials, network connectivity
```

### CrashLoopBackOff
```bash
kubectl logs <pod-name> -n <namespace>
# Check: Application errors, configuration issues
```

### Ingress Not Working
```bash
kubectl get ingress -n <namespace>
kubectl describe ingress <ingress-name> -n <namespace>
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

### ArgoCD Not Syncing
```bash
argocd app get <app-name> --hard-refresh
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller
```

## Emergency Commands

### Restart Everything
```bash
sudo systemctl restart rke2-server.service
kubectl rollout restart deployment -n argocd
kubectl rollout restart deployment -n online-boutique
```

### Complete Cleanup
```bash
argocd app delete online-boutique
kubectl delete namespace online-boutique
kubectl delete namespace argocd
sudo /usr/local/bin/rke2-uninstall.sh
```

## Documentation Links

- [RKE2 Docs](https://docs.rke2.io/)
- [ArgoCD Docs](https://argo-cd.readthedocs.io/)
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [NGINX Ingress Docs](https://kubernetes.github.io/ingress-nginx/)
