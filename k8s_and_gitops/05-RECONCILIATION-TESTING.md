# GitOps Reconciliation and Self-Healing Testing

This guide demonstrates how ArgoCD ensures reconciliation between the declared state in Git and the actual state in the cluster, including automatic correction of drift.

## Prerequisites

- Online Boutique deployed with ArgoCD sync policy enabled
- ArgoCD configured with auto-sync and self-heal

## Understanding GitOps Reconciliation

ArgoCD continuously monitors:
1. **Git Repository**: The source of truth for desired state
2. **Kubernetes Cluster**: The actual running state
3. **Differences**: Any drift between desired and actual state

With `selfHeal` enabled, ArgoCD automatically corrects drift by reverting to the Git state.

## Test 1: Manual Scaling Drift Detection

### Step 1: Check current state
```bash
kubectl get deployment frontend -n online-boutique
```

Note the current replica count (usually 1).

### Step 2: Manually scale the deployment
```bash
kubectl scale deployment frontend -n online-boutique --replicas=5
```

### Step 3: Verify the manual change
```bash
kubectl get deployment frontend -n online-boutique
```

You should see 5 replicas.

### Step 4: Watch ArgoCD detect and fix the drift

Monitor the deployment:
```bash
kubectl get deployment frontend -n online-boutique -w
```

Within 3-5 minutes (default sync interval), ArgoCD will detect the drift and revert the replica count back to 1.

### Step 5: Check ArgoCD UI

Open ArgoCD UI and observe:
- The application may briefly show as "OutOfSync"
- ArgoCD automatically syncs and returns it to "Synced" state
- The sync operation is logged in the application history

### Step 6: View sync history
```bash
argocd app history online-boutique
```

You should see an automatic sync operation.

## Test 2: Label Modification Detection

### Step 1: Add a custom label to a service
```bash
kubectl label service frontend -n online-boutique custom-label=test-value
```

### Step 2: Verify the label
```bash
kubectl get service frontend -n online-boutique --show-labels
```

### Step 3: Watch ArgoCD remove the unauthorized label

Wait for the next sync cycle (or force refresh):
```bash
argocd app get online-boutique --refresh
```

### Step 4: Verify label is removed
```bash
kubectl get service frontend -n online-boutique --show-labels
```

The custom label should be removed by ArgoCD.

## Test 3: Resource Deletion Detection

### Step 1: Check existing deployments
```bash
kubectl get deployments -n online-boutique
```

### Step 2: Delete a deployment
```bash
kubectl delete deployment recommendationservice -n online-boutique
```

### Step 3: Verify deletion
```bash
kubectl get deployment recommendationservice -n online-boutique
```

Should show "NotFound".

### Step 4: Watch ArgoCD recreate the deployment

Monitor deployments:
```bash
kubectl get deployments -n online-boutique -w
```

Within minutes, ArgoCD will detect the missing resource and recreate it.

### Step 5: Verify recreation
```bash
kubectl get deployment recommendationservice -n online-boutique
kubectl get pods -n online-boutique -l app=recommendationservice
```

The deployment and its pods should be running again.

## Test 4: Configuration Change Detection

### Step 1: Modify a ConfigMap (if exists)

First, check if there are any ConfigMaps:
```bash
kubectl get configmaps -n online-boutique
```

### Step 2: Create an unauthorized ConfigMap
```bash
kubectl create configmap test-config -n online-boutique --from-literal=key=value
```

### Step 3: Watch for ArgoCD to detect and remove it

Since this ConfigMap is not in Git, ArgoCD will remove it:
```bash
kubectl get configmap test-config -n online-boutique -w
```

With `prune: true`, ArgoCD will delete resources not defined in Git.

### Step 4: Verify removal
```bash
kubectl get configmap test-config -n online-boutique
```

Should show "NotFound" after sync.

## Test 5: Application Status Monitoring

### View current application status
```bash
argocd app get online-boutique
```

Look for:
- Sync Status: Should be "Synced"
- Health Status: Should be "Healthy"
- Last Sync: Recent timestamp

### Monitor application in real-time
```bash
watch argocd app get online-boutique
```

### View detailed resource status
```bash
kubectl get application online-boutique -n argocd -o yaml
```

## Test 6: Sync Policy Verification

### Check current sync policy
```bash
kubectl get application online-boutique -n argocd -o jsonpath='{.spec.syncPolicy}' | jq
```

Expected output:
```json
{
  "automated": {
    "prune": true,
    "selfHeal": true
  }
}
```

### Verify auto-sync behavior

Make a change:
```bash
kubectl annotate service frontend -n online-boutique test-annotation=test-value
```

Check application status:
```bash
argocd app get online-boutique
```

Watch for automatic sync within the sync window.

## Test 7: Force Manual Drift

### Create multiple drifted resources at once

```bash
# Scale multiple deployments
kubectl scale deployment frontend -n online-boutique --replicas=3
kubectl scale deployment cartservice -n online-boutique --replicas=2
kubectl scale deployment productcatalogservice -n online-boutique --replicas=2

# Add labels
kubectl label deployment checkoutservice -n online-boutique test=drift
kubectl label service emailservice -n online-boutique custom=label
```

### Monitor ArgoCD correction

```bash
# Watch ArgoCD status
watch argocd app get online-boutique

# Watch deployments
kubectl get deployments -n online-boutique -w
```

All changes should be reverted within the sync interval.

## Test 8: Sync Timing Analysis

### Check sync frequency
```bash
argocd app get online-boutique -o json | jq '.status.operationState'
```

### View sync statistics
```bash
argocd app history online-boutique
```

### Trigger manual sync
```bash
argocd app sync online-boutique
```

### Force hard refresh
```bash
argocd app get online-boutique --hard-refresh
```

## Monitoring and Observability

### View ArgoCD controller logs
```bash
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller --tail=100 -f
```

Look for reconciliation events.

### View ArgoCD server logs
```bash
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-server --tail=100 -f
```

### Check application events
```bash
kubectl get events -n online-boutique --sort-by='.lastTimestamp'
```

### Monitor ArgoCD metrics (if Prometheus is installed)
```bash
kubectl port-forward -n argocd svc/argocd-metrics 8082:8082
```

Access metrics at: http://localhost:8082/metrics

## Understanding Sync Behavior

### Sync Windows
ArgoCD checks for drift every 3 minutes by default. You can configure this:

```bash
kubectl patch configmap argocd-cm -n argocd --type merge -p '{"data":{"timeout.reconciliation":"60s"}}'
```

### Sync Options

View current sync options:
```bash
argocd app get online-boutique -o yaml | grep -A 20 syncPolicy
```

Key options:
- **automated.prune**: Remove resources not in Git
- **automated.selfHeal**: Revert manual changes
- **syncOptions.CreateNamespace**: Auto-create namespace
- **retry.limit**: Number of sync retry attempts

## Verification Checklist

Ensure the following behaviors are working:

- [ ] Manual scaling is automatically reverted
- [ ] Deleted resources are automatically recreated
- [ ] Unauthorized resources are removed (prune)
- [ ] Label changes are reverted
- [ ] ConfigMap changes are reverted
- [ ] Application status shows "Synced" and "Healthy"
- [ ] Sync history shows automatic sync operations
- [ ] ArgoCD UI reflects real-time cluster state

## Troubleshooting

### If self-healing is not working

1. Check sync policy:
```bash
argocd app get online-boutique -o yaml | grep -A 10 syncPolicy
```

2. Verify ArgoCD controller is running:
```bash
kubectl get pods -n argocd -l app.kubernetes.io/name=argocd-application-controller
```

3. Check controller logs for errors:
```bash
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller --tail=50
```

4. Force refresh:
```bash
argocd app get online-boutique --hard-refresh
argocd app sync online-boutique --force
```

### If prune is not removing resources

Ensure prune is enabled:
```bash
argocd app set online-boutique --auto-prune
```

### If sync is taking too long

Reduce reconciliation timeout:
```bash
kubectl edit configmap argocd-cm -n argocd
# Add or modify: timeout.reconciliation: "60s"
```

Restart ArgoCD application controller:
```bash
kubectl rollout restart deployment argocd-application-controller -n argocd
```

## Best Practices

1. **Always use Git as the source of truth**: Never make manual changes expecting them to persist
2. **Monitor sync history**: Regularly check for unexpected drift
3. **Use resource hooks**: For controlled deployment order and lifecycle management
4. **Implement health checks**: Ensure proper application health assessment
5. **Set resource limits**: Prevent runaway reconciliation loops
6. **Use app projects**: Organize applications and set RBAC policies

## Conclusion

GitOps with ArgoCD ensures:
- **Declarative Configuration**: All changes through Git
- **Automated Sync**: Continuous reconciliation
- **Self-Healing**: Automatic drift correction
- **Auditability**: Complete change history in Git
- **Rollback Capability**: Easy reversion to previous states

## Next Steps

Review the complete deployment:
- [README.md](./README.md) - Complete guide overview and summary
