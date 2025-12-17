# ArgoCD Installation and Configuration Guide

This guide covers installing ArgoCD on your RKE2 cluster and configuring it for GitOps deployments.

## Prerequisites

- Running RKE2 Kubernetes cluster (see [01-RKE2-INSTALLATION.md](./01-RKE2-INSTALLATION.md))
- kubectl configured and working
- Ingress controller installed

## Step 1: Create ArgoCD Namespace

```bash
kubectl create namespace argocd
```

## Step 2: Install ArgoCD

### Install ArgoCD using the official manifests
```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Wait for all ArgoCD pods to be ready
```bash
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=300s
```

### Verify installation
```bash
kubectl get pods -n argocd
```

Expected output (all pods should be Running):
```
NAME                                  READY   STATUS    RESTARTS   AGE
argocd-application-controller-0       1/1     Running   0          2m
argocd-dex-server-xxx                 1/1     Running   0          2m
argocd-redis-xxx                      1/1     Running   0          2m
argocd-repo-server-xxx                1/1     Running   0          2m
argocd-server-xxx                     1/1     Running   0          2m
```

## Step 3: Access ArgoCD UI

### Option 1: Using Port Forwarding (Quick Access)

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Access at: https://localhost:8080

### Option 2: Using Ingress (Recommended for Production)

Create an Ingress resource:

```bash
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-server-ingress
  namespace: argocd
  annotations:
    nginx.ingress.kubernetes.io/ssl-passthrough: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
spec:
  ingressClassName: nginx
  rules:
  - host: argocd.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: argocd-server
            port:
              name: https
EOF
```

Add to /etc/hosts:
```bash
echo "$(hostname -I | awk '{print $1}') argocd.local" | sudo tee -a /etc/hosts
```

Access at: https://argocd.local:NODEPORT (get NodePort from ingress-nginx service)

### Option 3: Using NodePort

```bash
kubectl patch svc argocd-server -n argocd -p '{"spec":{"type":"NodePort"}}'
```

Get the NodePort:
```bash
kubectl get svc argocd-server -n argocd
```

Access at: https://<VM-IP>:<NODEPORT>

## Step 4: Get Initial Admin Password

### Retrieve the initial admin password
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
echo
```

### Login credentials
- Username: `admin`
- Password: (output from the command above)

## Step 5: Install ArgoCD CLI (Optional but Recommended)

### Download and install ArgoCD CLI
```bash
# For Linux
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64
```

### Login to ArgoCD from CLI
```bash
# Using port-forward
argocd login localhost:8080 --insecure

# Or using NodePort/Ingress
argocd login <VM-IP>:<NODEPORT> --insecure
```

Enter username `admin` and the password retrieved earlier.

### Change admin password (recommended)
```bash
argocd account update-password
```

## Step 6: Configure ArgoCD for GitOps

### Create a Git repository connection (if using private repo)

For public repositories like the Online Boutique demo, this step is optional.

```bash
argocd repo add https://github.com/GoogleCloudPlatform/microservices-demo.git --type git --name microservices-demo
```

### Verify repository connection
```bash
argocd repo list
```

## Step 7: Configure ArgoCD Settings

### Enable auto-sync and self-healing (optional global settings)

Edit the ArgoCD ConfigMap to set default sync policies:

```bash
kubectl patch configmap argocd-cm -n argocd --type merge -p '{"data":{"application.instanceLabelKey":"argocd.argoproj.io/instance"}}'
```

## Step 8: Create Application Project (Optional)

Create a project for better organization:

```bash
kubectl apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: online-boutique
  namespace: argocd
spec:
  description: Online Boutique Microservices Demo
  sourceRepos:
  - 'https://github.com/GoogleCloudPlatform/microservices-demo.git'
  destinations:
  - namespace: '*'
    server: https://kubernetes.default.svc
  clusterResourceWhitelist:
  - group: '*'
    kind: '*'
EOF
```

## Verification

### Check ArgoCD is healthy
```bash
kubectl get all -n argocd
```

### Access the UI
Open your browser and navigate to the ArgoCD UI using one of the methods above.

### Verify CLI connection
```bash
argocd version
argocd cluster list
```

## Troubleshooting

### If ArgoCD pods are not starting
```bash
kubectl describe pod -n argocd <pod-name>
kubectl logs -n argocd <pod-name>
```

### Reset admin password
```bash
kubectl -n argocd delete secret argocd-initial-admin-secret
kubectl -n argocd scale deployment argocd-server --replicas=0
kubectl -n argocd scale deployment argocd-server --replicas=1
# Wait for pod to restart, then retrieve new password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Check ArgoCD server logs
```bash
kubectl logs -n argocd deployment/argocd-server -f
```

## Next Steps

Proceed to deploy the Online Boutique application:
- [03-DEPLOY-APPLICATION.md](./03-DEPLOY-APPLICATION.md) - Deploy Online Boutique with GitOps
