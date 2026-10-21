# Store deployment runbook — local k3d

This runbook is for a disposable local assignment demo. A successful Helm render or unit test does not prove checkout, persistence or production deployment.

## Prerequisites

Install and start Docker Desktop, kubectl, Helm 3, k3d, Python 3.12 and Node.js 22. Run commands from the repository root.

```powershell
docker version
kubectl version --client
helm version
k3d version
```

## Validate chart first

```powershell
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
```

Inspect Secret references, PVCs, Ingress and NetworkPolicies in rendered output. Do not proceed if lint/render fails.

## Deploy locally

Use only disposable local values:

```powershell
./scripts/dev.sh
kubectl get pods -o wide
kubectl get jobs
kubectl get pvc
kubectl get ingress
kubectl logs job/wp-setup
```

If PowerShell cannot run the shell script, use Git Bash or WSL. Wait until expected pods are Ready, the setup Job is complete, and claims are Bound. Inspect logs/events before retrying failures.

Add these entries to the Windows hosts file as administrator if needed:

```text
127.0.0.1 store.urumi.local dashboard.urumi.local
```

Open `http://store.urumi.local` and `http://dashboard.urumi.local`.

## Verify store behavior

1. Confirm a published demo product is visible.
2. Add it to cart and complete checkout with Cash on Delivery using test-only details.
3. Verify order number, line items, total, payment method and status in wp-admin.
4. Run `python scripts/smoke_test_woocommerce.py` with disposable least-privilege REST credentials injected into the local shell.
5. Verify the WooCommerce tools through the gateway, not by bypassing it.

## Verify persistence

Record a product/order ID, then restart WordPress and MySQL pods without deleting PVCs:

```powershell
kubectl delete pod -l app=wordpress
kubectl delete pod -l app=mysql
kubectl get pods -w
```

After the pods are Ready, verify the recorded data still exists. Never delete PVCs as part of this acceptance test.

## Troubleshooting

- **Setup Job Pending:** inspect events, scheduling and PVC bindings.
- **Setup Job failing:** inspect its logs, WordPress initialization and MySQL readiness.
- **Wrong host/scheme redirect:** compare ingress host, WordPress canonical URL and forwarded-proto settings.
- **Woo REST 401/403:** verify the key's permissions and secret injection without printing the values.
- **Service connection errors:** check internal DNS and service names; do not expose databases/upstream MCPs publicly as a workaround.
- **Data missing after restart:** inspect PVC bindings and mounts; mark persistence failed until corrected.

## Completion evidence

Save Helm lint/template output, pod/Job/PVC/Ingress output, setup Job logs, a test checkout/order verification, REST smoke-test output without secrets, and post-restart persistence proof. Local k3d success is separate from production-like k3s/VPS acceptance.
