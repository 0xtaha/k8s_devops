# Deploy Online Boutique Application with GitOps

This guide covers deploying the Google Cloud Online Boutique microservices demo application using ArgoCD in GitOps mode.

## Prerequisites

- Running RKE2 Kubernetes cluster
- ArgoCD installed and accessible
- kubectl configured

## Understanding the Online Boutique Application

The Online Boutique is a cloud-native microservices demo application consisting of 11 microservices:
- Frontend
- Cart Service
- Product Catalog Service
- Currency Service
- Payment Service
- Shipping Service
- Email Service
- Checkout Service
- Recommendation Service
- Ad Service
- Load Generator

## Step 1: Create Namespace for the Application

```bash
kubectl create namespace online-boutique
```

## Step 2: Deploy Application Using ArgoCD

### Method 1: Using ArgoCD UI

1. Open ArgoCD UI in your browser
2. Click on "+ NEW APP" button
3. Fill in the application details:
   - Application Name: `online-boutique`
   - Project: `default` (or `online-boutique` if you created the project)
   - Sync Policy: `Automatic`
   - Enable "PRUNE RESOURCES" (for automatic cleanup)
   - Enable "SELF HEAL" (for automatic reconciliation)
   - Repository URL: `https://github.com/GoogleCloudPlatform/microservices-demo.git`
   - Revision: `HEAD` or `main`
   - Path: `release`
   - Cluster URL: `https://kubernetes.default.svc`
   - Namespace: `online-boutique`
4. Click "CREATE"

### Method 2: Using ArgoCD CLI

```bash
argocd app create online-boutique \
  --repo https://github.com/GoogleCloudPlatform/microservices-demo.git \
  --path release \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace online-boutique \
  --sync-policy automated \
  --auto-prune \
  --self-heal
```

### Method 3: Using Kubernetes Manifest (Declarative GitOps)

Create an ArgoCD Application manifest:

```bash
kubectl apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: online-boutique
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
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
      allowEmpty: false
    syncOptions:
    - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
EOF
```

## Step 3: Monitor Deployment

### Watch the sync status
```bash
argocd app get online-boutique --refresh
```

### Watch pods being created
```bash
kubectl get pods -n online-boutique -w
```

### Check application status
```bash
argocd app list
```

### View sync details in UI
Open ArgoCD UI and click on the `online-boutique` application to see the resource tree and sync status.

## Step 4: Verify All Services are Running

### Check all pods are running
```bash
kubectl get pods -n online-boutique
```

All pods should show `Running` status:
```
NAME                                     READY   STATUS    RESTARTS   AGE
adservice-xxx                            1/1     Running   0          2m
cartservice-xxx                          1/1     Running   0          2m
checkoutservice-xxx                      1/1     Running   0          2m
currencyservice-xxx                      1/1     Running   0          2m
emailservice-xxx                         1/1     Running   0          2m
frontend-xxx                             1/1     Running   0          2m
loadgenerator-xxx                        1/1     Running   0          2m
paymentservice-xxx                       1/1     Running   0          2m
productcatalogservice-xxx                1/1     Running   0          2m
recommendationservice-xxx                1/1     Running   0          2m
redis-cart-xxx                           1/1     Running   0          2m
shippingservice-xxx                      1/1     Running   0          2m
```

### Check services
```bash
kubectl get svc -n online-boutique
```

### Check application logs
```bash
kubectl logs -n online-boutique deployment/frontend
```

## Step 5: Configure Sync Policy Details

### View current sync policy
```bash
argocd app get online-boutique -o yaml | grep -A 10 syncPolicy
```

### Update sync options (if needed)
```bash
argocd app set online-boutique \
  --sync-option CreateNamespace=true \
  --sync-option PruneLast=true
```

## Understanding GitOps Reconciliation

With the sync policy configured as:
- **automated**: ArgoCD continuously monitors the Git repository
- **prune**: Resources removed from Git are automatically deleted from the cluster
- **selfHeal**: If someone manually changes resources in the cluster, ArgoCD reverts them back to the Git state

## Monitoring and Management

### View application health
```bash
argocd app get online-boutique
```

### Manually sync (if needed)
```bash
argocd app sync online-boutique
```

### View sync history
```bash
argocd app history online-boutique
```

### View application logs from ArgoCD
```bash
argocd app logs online-boutique
```

### Get application manifest diff
```bash
argocd app diff online-boutique
```

## Troubleshooting

### If application is not syncing
```bash
argocd app get online-boutique
kubectl describe application online-boutique -n argocd
```

### If pods are not starting
```bash
kubectl describe pod <pod-name> -n online-boutique
kubectl logs <pod-name> -n online-boutique
```

### Check resource quotas and limits
```bash
kubectl describe nodes
kubectl top nodes
kubectl top pods -n online-boutique
```

### Force refresh and sync
```bash
argocd app get online-boutique --hard-refresh
argocd app sync online-boutique --force
```

### Delete and recreate application
```bash
argocd app delete online-boutique
# Then recreate using one of the methods above
```

## Next Steps

Proceed to expose the application:
- [04-EXPOSE-APPLICATION.md](./04-EXPOSE-APPLICATION.md) - Configure Ingress to access the application
