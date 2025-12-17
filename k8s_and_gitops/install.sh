#!/bin/bash

# RKE2 + ArgoCD + Online Boutique Installation Script
# This script automates the deployment process
# Run with: sudo bash install.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root or with sudo"
        exit 1
    fi
}

wait_for_pods() {
    local namespace=$1
    print_info "Waiting for pods in namespace $namespace to be ready..."
    kubectl wait --for=condition=Ready pods --all -n "$namespace" --timeout=300s || true
}

# Main installation steps
main() {
    print_info "Starting RKE2 + ArgoCD + Online Boutique installation"

    # Step 1: System preparation
    print_info "Step 1/8: Preparing system..."

    # Disable swap
    swapoff -a
    sed -i '/ swap / s/^/#/' /etc/fstab

    print_info "System prepared successfully"

    # Step 2: Install RKE2
    print_info "Step 2/8: Installing RKE2..."

    if [ -f /usr/local/bin/rke2 ]; then
        print_warning "RKE2 appears to be already installed, skipping..."
    else
        curl -sfL https://get.rke2.io | sh -

        # Create config directory
        mkdir -p /etc/rancher/rke2

        # Create configuration
        cat > /etc/rancher/rke2/config.yaml <<EOF
write-kubeconfig-mode: "0644"
tls-san:
  - "$(hostname -I | awk '{print $1}')"
  - "127.0.0.1"
EOF

        # Enable and start RKE2
        systemctl enable rke2-server.service
        systemctl start rke2-server.service

        print_info "RKE2 installed and started"
    fi

    # Step 3: Configure kubectl
    print_info "Step 3/8: Configuring kubectl..."

    export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
    export PATH=$PATH:/var/lib/rancher/rke2/bin

    # Wait for RKE2 to be ready
    print_info "Waiting for RKE2 to be ready..."
    sleep 30

    # Verify cluster is running
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if kubectl get nodes &>/dev/null; then
            print_info "Cluster is ready"
            break
        fi
        attempt=$((attempt + 1))
        sleep 10
    done

    # Remove control plane taints for single node
    kubectl taint nodes --all node-role.kubernetes.io/control-plane- || true
    kubectl taint nodes --all node-role.kubernetes.io/master- || true

    print_info "kubectl configured successfully"

    # Step 4: Install NGINX Ingress Controller
    print_info "Step 4/8: Installing NGINX Ingress Controller..."

    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.5/deploy/static/provider/baremetal/deploy.yaml

    print_info "Waiting for Ingress Controller to be ready..."
    sleep 20
    wait_for_pods "ingress-nginx"

    print_info "NGINX Ingress Controller installed"

    # Step 5: Install ArgoCD
    print_info "Step 5/8: Installing ArgoCD..."

    kubectl create namespace argocd || true
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

    print_info "Waiting for ArgoCD to be ready..."
    sleep 30
    wait_for_pods "argocd"

    print_info "ArgoCD installed successfully"

    # Step 6: Deploy Online Boutique
    print_info "Step 6/8: Deploying Online Boutique application..."

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

    print_info "Online Boutique application created"
    print_info "Waiting for application to sync (this may take a few minutes)..."
    sleep 60

    # Step 7: Create Ingress
    print_info "Step 7/8: Creating Ingress for Online Boutique..."

    # Wait for namespace to be created
    sleep 10

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

    print_info "Ingress created successfully"

    # Step 8: Configure DNS
    print_info "Step 8/8: Configuring local DNS..."

    VM_IP=$(hostname -I | awk '{print $1}')

    # Add to /etc/hosts if not already present
    if ! grep -q "shop.local" /etc/hosts; then
        echo "$VM_IP shop.local" >> /etc/hosts
        print_info "Added shop.local to /etc/hosts"
    fi

    if ! grep -q "argocd.local" /etc/hosts; then
        echo "$VM_IP argocd.local" >> /etc/hosts
        print_info "Added argocd.local to /etc/hosts"
    fi

    # Get NodePort
    sleep 5
    HTTP_NODEPORT=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.spec.ports[?(@.port==80)].nodePort}')
    HTTPS_NODEPORT=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.spec.ports[?(@.port==443)].nodePort}')

    # Get ArgoCD initial password
    print_info "Waiting for ArgoCD initial password secret..."
    sleep 10
    ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" 2>/dev/null | base64 -d || echo "Not available yet")

    # Print summary
    echo ""
    echo "=========================================="
    print_info "Installation completed successfully!"
    echo "=========================================="
    echo ""
    print_info "Access Details:"
    echo ""
    echo "  Online Boutique Application:"
    echo "    URL: http://shop.local:$HTTP_NODEPORT"
    echo "    URL: http://$VM_IP:$HTTP_NODEPORT"
    echo ""
    echo "  ArgoCD UI:"
    echo "    URL: https://argocd.local:$HTTPS_NODEPORT (via Ingress - needs setup)"
    echo "    Port-forward: kubectl port-forward svc/argocd-server -n argocd 8080:443"
    echo "    Then access: https://localhost:8080"
    echo "    Username: admin"
    echo "    Password: $ARGOCD_PASSWORD"
    echo ""
    print_info "Useful commands:"
    echo ""
    echo "  Check cluster status:"
    echo "    export KUBECONFIG=/etc/rancher/rke2/rke2.yaml"
    echo "    export PATH=\$PATH:/var/lib/rancher/rke2/bin"
    echo "    kubectl get nodes"
    echo ""
    echo "  Check Online Boutique pods:"
    echo "    kubectl get pods -n online-boutique"
    echo ""
    echo "  Check ArgoCD application:"
    echo "    kubectl get application online-boutique -n argocd"
    echo ""
    echo "  Install ArgoCD CLI:"
    echo "    curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64"
    echo "    sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd"
    echo ""
    print_warning "Note: It may take a few minutes for all pods to be fully ready."
    print_warning "Monitor with: kubectl get pods -n online-boutique -w"
    echo ""
}

# Run main function
check_root
main
