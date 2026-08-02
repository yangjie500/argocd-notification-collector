{{/*
Expand the name of the chart.
*/}}
{{- define "event-collector.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "event-collector.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "event-collector.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels.
*/}}
{{- define "event-collector.labels" -}}
helm.sh/chart: {{ include "event-collector.chart" . }}
{{ include "event-collector.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels.
*/}}
{{- define "event-collector.selectorLabels" -}}
app.kubernetes.io/name: {{ include "event-collector.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Service account name.
*/}}
{{- define "event-collector.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "event-collector.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Webhook token secret name.
*/}}
{{- define "event-collector.webhookSecretName" -}}
{{- if .Values.webhookToken.existingSecret }}
{{- .Values.webhookToken.existingSecret }}
{{- else }}
{{- include "event-collector.fullname" . }}
{{- end }}
{{- end }}

{{/*
OTLP authorization header secret name.
*/}}
{{- define "event-collector.otelAuthorizationSecretName" -}}
{{- if .Values.observability.authorizationHeader.existingSecret }}
{{- .Values.observability.authorizationHeader.existingSecret }}
{{- else }}
{{- printf "%s-otel" (include "event-collector.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
