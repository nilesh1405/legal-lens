#!/usr/bin/env bash
set -euo pipefail

# Usage: ./infra/cloudrun-deploy.sh <gcp-project-id> <service-name>
PROJECT_ID=${1:-}
SERVICE_NAME=${2:-legal-lens-api}
REGION=${REGION:-us-central1}

if [[ -z "$PROJECT_ID" ]]; then
  echo "Provide GCP project id" && exit 1
fi

gcloud config set project "$PROJECT_ID"

gcloud builds submit ../backend --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080

echo "Deployed $SERVICE_NAME to Cloud Run in $REGION"


