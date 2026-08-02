# event-collector Helm Chart

Install with safe defaults:

```bash
helm upgrade --install event-collector charts/event-collector \
  --namespace event-collector \
  --create-namespace
```

Production example using existing webhook and OTEL authorization secrets:

```bash
kubectl create secret generic event-collector-webhook \
  --namespace event-collector \
  --from-literal=argocd-webhook-token='change-me'

kubectl create secret generic event-collector-otel \
  --namespace event-collector \
  --from-literal=authorization-header='Api-Token change-me'

helm upgrade --install event-collector charts/event-collector \
  --namespace event-collector \
  --create-namespace \
  -f charts/event-collector/values-production.yaml
```

The service endpoint for Argo CD notifications is:

```text
http://event-collector.event-collector.svc.cluster.local/api/v1/argocd/notifications
```

On OpenShift, `values-production.yaml` enables a Route. Leave `route.host`
empty for an auto-assigned host, or set it explicitly:

```bash
helm upgrade --install event-collector charts/event-collector \
  --namespace event-collector \
  --create-namespace \
  -f charts/event-collector/values-production.yaml \
  --set route.host=event-collector.apps.example.com
```
