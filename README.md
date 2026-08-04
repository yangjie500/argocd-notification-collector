[![CI](https://github.com/yangjie500/event-collector/actions/workflows/ci.yml/badge.svg)](https://github.com/yangjie500/event-collector/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/yangjie500/event-collector/branch/main/graph/badge.svg)](https://codecov.io/gh/yangjie500/event-collector)
[![PyPI](https://img.shields.io/pypi/v/event-collector.svg)](https://pypi.org/project/event-collector)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# event-collector

Backend service for receiving Argo CD deployment notification webhooks and
exporting structured OpenTelemetry logs.

## Run Locally

```bash
uv run event-collector serve --host 0.0.0.0 --port 8000 --reload
```

Health endpoints:

```text
/health/live
/health/ready
```

Argo CD notification endpoint:

```text
/api/v1/argocd/notifications
```

## Container Image

Build the runtime image:

```bash
podman build --target runtime -t event-collector:local .
```

Run it:

```bash
podman run --rm -p 8000:8000 event-collector:local
```

## Deploy With Helm

The Helm chart is in:

```text
charts/event-collector
```

Install with default values:

```bash
helm upgrade --install event-collector charts/event-collector \
  --namespace event-collector \
  --create-namespace
```

## Deploy On OpenShift

`values-production.yaml` is configured for OpenShift Route usage.

Review and update these values before deploying:

```yaml
image:
  repository: ghcr.io/yangjie500/argocd-notification-collector
  tag: latest

observability:
  otlpLogsEndpoint: yyy
  authorizationHeader:
    value: "Api-Token xxx"

route:
  host: "event-collector.apps.lab.yang.gov.sg"
```

Deploy:

```bash
helm upgrade --install event-collector charts/event-collector \
  --namespace event-collector \
  --create-namespace \
  -f charts/event-collector/values-production.yaml
```

After deployment, the public Route URL will be:

```text
https://event-collector.apps.lab.yang.gov.sg
```

The Argo CD webhook URL will be:

```text
https://event-collector.apps.lab.yang.gov.sg/api/v1/argocd/notifications
```

If `route.host` is empty, OpenShift can auto-assign a host. Check it with:

```bash
oc get route event-collector -n event-collector
```

## Secrets

The production values currently let Helm create the OTEL authorization Secret
from:

```yaml
observability:
  authorizationHeader:
    value: "Api-Token xxx"
```

This renders a Kubernetes Secret and injects it into the pod as:

```text
APP_OBSERVABILITY_OTLP_AUTHORIZATION_HEADER
```

For GitOps or shared repositories, prefer using an existing Secret instead of
committing the real token:

```bash
oc create secret generic event-collector-otel \
  --namespace event-collector \
  --from-literal=authorization-header='Api-Token <real-token>'
```

Then configure:

```yaml
observability:
  authorizationHeader:
    existingSecret: event-collector-otel
    existingSecretKey: authorization-header
    value: ""
```

The Argo CD webhook token is disabled in `values-production.yaml`:

```yaml
webhookToken:
  existingSecret: ""
  value: ""
```

If you enable it later, the app expects Argo CD to send:

```text
X-Event-Collector-Token: <token>
```

## Argo CD Notifications

An example Argo CD `NotificationsConfiguration` manifest is available at:

```text
deploy/argocd/notifications-configuration.yaml
```

Apply it after updating the webhook URL if needed:

```bash
oc apply -f deploy/argocd/notifications-configuration.yaml
```

## Validate

Run the full local check suite:

```bash
uv run tox -p
```

Render the production Helm chart:

```bash
helm template event-collector charts/event-collector \
  --namespace event-collector \
  -f charts/event-collector/values-production.yaml
```

codex resume 019fa4c0-52fd-7d40-95a3-6cacf0ff49b3
