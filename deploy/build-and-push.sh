#!/bin/bash
set -e

# Configuration
AWS_REGION="${AWS_REGION:-eu-west-1}"
ECR_REGISTRY="${ECR_REGISTRY:-YOUR_ACCOUNT_ID.dkr.ecr.${AWS_REGION}.amazonaws.com}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

echo "🏗️  Building and pushing images..."

# Manager Service
echo "  → Building manager..."
docker build -t churn-manager:$IMAGE_TAG -f services/manager/Dockerfile .
docker tag churn-manager:$IMAGE_TAG $ECR_REGISTRY/churn-manager:$IMAGE_TAG
docker push $ECR_REGISTRY/churn-manager:$IMAGE_TAG

# Transcript Service
echo "  → Building transcript..."
docker build -t churn-transcript:$IMAGE_TAG -f services/transcript/Dockerfile .
docker tag churn-transcript:$IMAGE_TAG $ECR_REGISTRY/churn-transcript:$IMAGE_TAG
docker push $ECR_REGISTRY/churn-transcript:$IMAGE_TAG

# Churn Analyzer Service
echo "  → Building churn..."
docker build -t churn-analyzer:$IMAGE_TAG -f services/churn/Dockerfile .
docker tag churn-analyzer:$IMAGE_TAG $ECR_REGISTRY/churn-analyzer:$IMAGE_TAG
docker push $ECR_REGISTRY/churn-analyzer:$IMAGE_TAG

# Frontend Service
echo "  → Building frontend..."
docker build -t churn-frontend:$IMAGE_TAG -f services/frontend/Dockerfile .
docker tag churn-frontend:$IMAGE_TAG $ECR_REGISTRY/churn-frontend:$IMAGE_TAG
docker push $ECR_REGISTRY/churn-frontend:$IMAGE_TAG

echo "✅ All images pushed to ECR!"
echo ""
echo "Images:"
echo "  - $ECR_REGISTRY/churn-manager:$IMAGE_TAG"
echo "  - $ECR_REGISTRY/churn-transcript:$IMAGE_TAG"
echo "  - $ECR_REGISTRY/churn-analyzer:$IMAGE_TAG"
echo "  - $ECR_REGISTRY/churn-frontend:$IMAGE_TAG"

