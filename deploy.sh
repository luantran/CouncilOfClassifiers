#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="${GCLOUD_PROJECT_ID}"
SERVICE_NAME="council-of-classifiers"
REGION="${GCLOUD_REGION:-us-central1}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
HF_TOKEN="${HF_TOKEN}"  # Add this line

echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Council of Classifiers - Cloud Run Deployment${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    exit 1
fi

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: GCLOUD_PROJECT_ID environment variable is not set${NC}"
    exit 1
fi

if [ -z "$HF_TOKEN" ]; then
    echo -e "${YELLOW}Warning: HF_TOKEN not set. May hit rate limits.${NC}"
    echo "Get token from: https://huggingface.co/settings/tokens"
    ENV_VARS="FLASK_ENV=production,MODEL_CACHE_DIR=/app/server/hf_models"
else
    ENV_VARS="FLASK_ENV=production,MODEL_CACHE_DIR=/app/server/hf_models,HF_TOKEN=${HF_TOKEN}"
fi

echo -e "${GREEN}✓ Configuration${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Service Name: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  Image: $IMAGE_NAME"
echo "  HF Token: ${HF_TOKEN:+Set (hidden)}${HF_TOKEN:-Not set (may hit rate limits)}"
echo ""

gcloud config set project $PROJECT_ID

echo -e "${YELLOW}→ Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com

echo -e "${YELLOW}→ Building Docker image...${NC}"
gcloud builds submit --tag $IMAGE_NAME --timeout=30m

echo -e "${YELLOW}→ Deploying to Cloud Run...${NC}"
echo "$ENV_VARS"
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 1200s \
    --cpu-boost \
    --max-instances 5 \
    --min-instances 0 \
    --port 8080 \
    --set-env-vars "$ENV_VARS"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Deployment successful!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
echo -e "Your service is now available at:"
echo -e "${BLUE}$SERVICE_URL${NC}"
echo ""
echo -e "Health check: ${BLUE}$SERVICE_URL/api/health${NC}"
echo ""
echo -e "${YELLOW}Note: First request may take 1-2 minutes due to model loading${NC}"