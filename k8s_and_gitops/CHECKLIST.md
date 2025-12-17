# Deployment Checklist

Use this checklist to track your deployment progress and ensure all components are properly configured.

## Pre-Installation

- [ ] VM meets minimum requirements (4 CPU, 8GB RAM, 50GB disk)
- [ ] Linux OS installed (Ubuntu 20.04/22.04 or Rocky Linux 8/9)
- [ ] Root or sudo access available
- [ ] Internet connectivity verified
- [ ] Firewall rules reviewed (ports 6443, 9345, 10250, 30000-32767)

## Phase 1: RKE2 Installation

- [ ] System updated (`apt update && apt upgrade` or `yum update`)
- [ ] Swap disabled (`swapoff -a`)
- [ ] RKE2 downloaded and installed (`curl -sfL https://get.rke2.io | sudo sh -`)
- [ ] RKE2 config file created (`/etc/rancher/rke2/config.yaml`)
- [ ] RKE2 service enabled (`systemctl enable rke2-server`)
- [ ] RKE2 service started (`systemctl start rke2-server`)
- [ ] RKE2 service is running (`systemctl status rke2-server`)
- [ ] KUBECONFIG environment variable set
- [ ] kubectl PATH configured
- [ ] Cluster node is Ready (`kubectl get nodes`)
- [ ] All system pods are Running (`kubectl get pods -A`)
- [ ] Control plane taints removed (for single node)

## Phase 2: Ingress Controller

- [ ] NGINX Ingress manifest applied
- [ ] Ingress namespace created (`ingress-nginx`)
- [ ] Ingress controller pods are Running (`kubectl get pods -n ingress-nginx`)
- [ ] Ingress controller service created
- [ ] NodePort assigned to ingress service
- [ ] Ingress controller validated (`kubectl get svc -n ingress-nginx`)

## Phase 3: ArgoCD Installation

- [ ] ArgoCD namespace created (`kubectl create namespace argocd`)
- [ ] ArgoCD manifests applied
- [ ] All ArgoCD pods are Running (`kubectl get pods -n argocd`)
  - [ ] argocd-server
  - [ ] argocd-application-controller
  - [ ] argocd-repo-server
  - [ ] argocd-redis
  - [ ] argocd-dex-server
- [ ] Initial admin password retrieved
- [ ] ArgoCD UI accessible (port-forward or Ingress)
- [ ] Logged into ArgoCD UI successfully
- [ ] ArgoCD CLI installed (optional)
- [ ] Logged into ArgoCD CLI (optional)
- [ ] Admin password changed (recommended)

## Phase 4: Application Deployment

- [ ] ArgoCD Application resource created
- [ ] Application appears in ArgoCD UI
- [ ] Application sync policy configured (automated, prune, selfHeal)
- [ ] Application synced successfully
- [ ] online-boutique namespace created
- [ ] All microservice pods are Running (`kubectl get pods -n online-boutique`)
  - [ ] frontend
  - [ ] cartservice
  - [ ] productcatalogservice
  - [ ] currencyservice
  - [ ] paymentservice
  - [ ] shippingservice
  - [ ] emailservice
  - [ ] checkoutservice
  - [ ] recommendationservice
  - [ ] adservice
  - [ ] redis-cart
  - [ ] loadgenerator (optional)
- [ ] All services created (`kubectl get svc -n online-boutique`)
- [ ] Application health is "Healthy" in ArgoCD
- [ ] Application sync status is "Synced" in ArgoCD

## Phase 5: Application Exposure

- [ ] Ingress resource created for Online Boutique
- [ ] Ingress appears in namespace (`kubectl get ingress -n online-boutique`)
- [ ] shop.local added to /etc/hosts
- [ ] DNS resolution works (`ping shop.local`)
- [ ] Application accessible in browser
- [ ] Can browse products
- [ ] Can add items to cart
- [ ] Frontend loads without errors

## Phase 6: GitOps Validation

- [ ] Manual scaling detected and reverted by ArgoCD
- [ ] Deleted resources recreated automatically
- [ ] Unauthorized labels removed
- [ ] Sync history shows automatic operations
- [ ] Self-heal working correctly
- [ ] Prune working correctly
- [ ] Application always returns to "Synced" state

## Optional Components

- [ ] ArgoCD Ingress created
- [ ] argocd.local added to /etc/hosts
- [ ] ArgoCD accessible via Ingress
- [ ] MetalLB installed (if using LoadBalancer)
- [ ] cert-manager installed (if using TLS)
- [ ] TLS certificates configured
- [ ] HTTPS access working
- [ ] ArgoCD project created
- [ ] Additional applications deployed

## Verification Tests

- [ ] Cluster info displays correctly (`kubectl cluster-info`)
- [ ] Can view logs of application pods
- [ ] Can exec into pods
- [ ] Services resolve via DNS
- [ ] Port forwarding works
- [ ] Ingress routes traffic correctly
- [ ] ArgoCD detects out-of-sync state
- [ ] ArgoCD syncs automatically
- [ ] Application performs expected functions

## Documentation Review

- [ ] Read 01-RKE2-INSTALLATION.md
- [ ] Read 02-ARGOCD-INSTALLATION.md
- [ ] Read 03-DEPLOY-APPLICATION.md
- [ ] Read 04-EXPOSE-APPLICATION.md
- [ ] Read 05-RECONCILIATION-TESTING.md
- [ ] Reviewed QUICK-REFERENCE.md
- [ ] Reviewed GETTING-STARTED.md

## Security Considerations

- [ ] Changed ArgoCD admin password
- [ ] Removed or secured initial admin secret
- [ ] Reviewed RBAC policies
- [ ] Network policies considered (if needed)
- [ ] Ingress TLS configured (if production)
- [ ] Secrets management strategy defined
- [ ] Access logs reviewed
- [ ] Audit logging enabled (if needed)

## Performance Checks

- [ ] Node resources not exhausted (`kubectl top nodes`)
- [ ] Pod resources within limits (`kubectl top pods -A`)
- [ ] No pods in CrashLoopBackOff
- [ ] No pods in Pending state
- [ ] No pods with high restart counts
- [ ] Application response time acceptable
- [ ] Ingress latency acceptable

## Troubleshooting Completed

- [ ] Reviewed logs for errors
- [ ] No persistent error messages
- [ ] All components healthy
- [ ] No resource constraints
- [ ] No network issues
- [ ] Documentation matches actual setup

## Final Validation

- [ ] Can access Online Boutique at http://shop.local:NODEPORT
- [ ] Can access ArgoCD UI
- [ ] Application fully functional
- [ ] GitOps reconciliation working
- [ ] All required pods running
- [ ] No critical errors in logs
- [ ] Ready for demonstration/use

## Post-Deployment Tasks

- [ ] Document any customizations made
- [ ] Note NodePort numbers used
- [ ] Save ArgoCD admin credentials securely
- [ ] Create backup of configuration files
- [ ] Test disaster recovery procedure (optional)
- [ ] Set up monitoring (optional)
- [ ] Configure alerts (optional)
- [ ] Plan upgrade strategy

## Knowledge Validation

- [ ] Understand RKE2 architecture
- [ ] Understand ArgoCD GitOps workflow
- [ ] Know how to check application status
- [ ] Know how to troubleshoot pod issues
- [ ] Know how to view logs
- [ ] Know how to sync applications
- [ ] Know how to rollback changes
- [ ] Understand self-healing mechanism
- [ ] Can explain the deployment to others

## Success Criteria

All items below must be true:

- [ ] RKE2 cluster is running and healthy
- [ ] ArgoCD is installed and accessible
- [ ] Online Boutique application is deployed
- [ ] Application is accessible via browser
- [ ] GitOps reconciliation is functioning
- [ ] Self-healing is working
- [ ] No critical errors present
- [ ] Documentation is complete

---

## Completion Status

**Date Started**: _______________

**Date Completed**: _______________

**Deployed By**: _______________

**Cluster IP**: _______________

**HTTP NodePort**: _______________

**HTTPS NodePort**: _______________

**ArgoCD Password**: _______________ (store securely)

**Notes/Issues**:
```
[Add any notes or issues encountered during deployment]
```

**Customizations**:
```
[Document any changes from the standard installation]
```

---

## Quick Status Check Command

Run this command anytime to check overall status:

```bash
echo "=== RKE2 Status ===" && \
sudo systemctl status rke2-server --no-pager && \
echo -e "\n=== Cluster Nodes ===" && \
kubectl get nodes && \
echo -e "\n=== ArgoCD Pods ===" && \
kubectl get pods -n argocd && \
echo -e "\n=== Online Boutique Pods ===" && \
kubectl get pods -n online-boutique && \
echo -e "\n=== Application Status ===" && \
kubectl get application -n argocd && \
echo -e "\n=== Ingress ===" && \
kubectl get ingress -n online-boutique
```

---

**Status**: [ ] Not Started  [ ] In Progress  [ ] Completed  [ ] Verified
