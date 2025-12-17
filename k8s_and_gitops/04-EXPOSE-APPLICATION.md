# Expose Online Boutique Application Using Ingress

This guide shows how to expose the Online Boutique application using NGINX Ingress Controller so it can be accessed via a web browser.

## Prerequisites

- Online Boutique application deployed (see [03-DEPLOY-APPLICATION.md](./03-DEPLOY-APPLICATION.md))
- NGINX Ingress Controller installed (covered in [01-RKE2-INSTALLATION.md](./01-RKE2-INSTALLATION.md))

## Step 1: Verify Frontend Service

The Online Boutique application exposes a frontend service. Let's check it:

```bash
kubectl get svc frontend -n online-boutique
```

The service should be of type `ClusterIP` by default.

## Step 2: Create Ingress Resource

### Option 1: Simple Ingress with NodePort Access

Create an Ingress resource for the frontend:

```bash
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: online-boutique-ingress
  namespace: online-boutique
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
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

### Option 2: Ingress with Multiple Paths (if needed)

If you want to expose other services:

```bash
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: online-boutique-ingress
  namespace: online-boutique
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
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

## Step 3: Configure Local DNS

### Add entry to /etc/hosts

Find your VM IP address:
```bash
hostname -I | awk '{print $1}'
```

Add the entry to /etc/hosts:
```bash
echo "$(hostname -I | awk '{print $1}') shop.local" | sudo tee -a /etc/hosts
```

## Step 4: Get Ingress Access Details

### Check Ingress status
```bash
kubectl get ingress -n online-boutique
```

### Get the NodePort of NGINX Ingress Controller
```bash
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

Look for the NodePort mapped to port 80 (HTTP). It will be in the 30000-32767 range.

Example output:
```
NAME                       TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx-controller   NodePort   10.43.xxx.xxx   <none>        80:30080/TCP,443:30443/TCP   10m
```

In this example, port 80 is mapped to NodePort 30080.

## Step 5: Access the Application

### Using NodePort
Open your browser and navigate to:
```
http://shop.local:30080
```

Replace `30080` with your actual NodePort number from the previous step.

### Verify application is accessible
You should see the Online Boutique homepage with various products.

## Step 6: Configure LoadBalancer (Optional for Cloud/MetalLB)

If you have MetalLB or are running in a cloud environment, you can use LoadBalancer type:

### Install MetalLB (for bare-metal/VM setup)

```bash
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb-native.yaml
```

Wait for MetalLB pods to be ready:
```bash
kubectl wait --namespace metallb-system \
  --for=condition=ready pod \
  --selector=app=metallb \
  --timeout=90s
```

### Configure MetalLB IP Address Pool

```bash
kubectl apply -f - <<EOF
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: first-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.240-192.168.1.250
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: example
  namespace: metallb-system
spec:
  ipAddressPools:
  - first-pool
EOF
```

Note: Adjust the IP range to match your network. Use IPs that are available on your network but outside your DHCP range.

### Change Ingress Controller to LoadBalancer
```bash
kubectl patch svc ingress-nginx-controller -n ingress-nginx -p '{"spec":{"type":"LoadBalancer"}}'
```

### Get the LoadBalancer IP
```bash
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

### Update /etc/hosts with LoadBalancer IP
```bash
echo "<LOADBALANCER-IP> shop.local" | sudo tee -a /etc/hosts
```

### Access via LoadBalancer
```
http://shop.local
```

## Step 7: Enable HTTPS (Optional)

### Install cert-manager for automatic TLS certificates

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml
```

### Create a self-signed certificate issuer

```bash
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-issuer
spec:
  selfSigned: {}
EOF
```

### Update Ingress to use TLS

```bash
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: online-boutique-ingress
  namespace: online-boutique
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: selfsigned-issuer
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - shop.local
    secretName: shop-tls
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

### Access via HTTPS
```
https://shop.local:30443
```

Note: You'll need to accept the self-signed certificate warning in your browser.

## Step 8: Verify Ingress Configuration

### Check Ingress details
```bash
kubectl describe ingress online-boutique-ingress -n online-boutique
```

### Check Ingress Controller logs
```bash
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

### Test from command line
```bash
curl -H "Host: shop.local" http://<VM-IP>:<NODEPORT>
```

## Troubleshooting

### If you can't access the application

1. Check Ingress is created:
```bash
kubectl get ingress -n online-boutique
```

2. Check frontend service is running:
```bash
kubectl get svc frontend -n online-boutique
kubectl get pods -n online-boutique -l app=frontend
```

3. Check Ingress Controller logs:
```bash
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

4. Verify /etc/hosts entry:
```bash
cat /etc/hosts | grep shop.local
```

5. Test direct service access:
```bash
kubectl port-forward -n online-boutique svc/frontend 8080:80
```
Then access http://localhost:8080

6. Check if frontend pod is healthy:
```bash
kubectl describe pod -n online-boutique -l app=frontend
```

### If Ingress shows no address

Check Ingress Controller service:
```bash
kubectl get svc -n ingress-nginx
```

### DNS resolution issues

Test DNS resolution:
```bash
nslookup shop.local
ping shop.local
```

### Backend service not found

Verify the service name and port:
```bash
kubectl get svc -n online-boutique
kubectl get endpoints frontend -n online-boutique
```

## Testing the Application

Once accessible, you should be able to:
1. Browse products
2. Add items to cart
3. Proceed through checkout
4. See the complete microservices architecture in action

## Next Steps

Proceed to test GitOps reconciliation:
- [05-RECONCILIATION-TESTING.md](./05-RECONCILIATION-TESTING.md) - Verify ArgoCD reconciliation and self-healing
