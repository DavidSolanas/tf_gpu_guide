#!/usr/bin/env bash
set -e

# Variables de ejemplo
IMAGE_NAME="tf-gpu-img"
IMAGE_TAG="v1.0"
FULL_IMAGE_NAME=""
REGION="eu-west-1"
#GCP
PROJECT_ID=""
#Azure
ACR_NAME=""
#AWS
AWS_ACCOUNT_ID=""

# Detectar proveedor
PROVIDER=$1
if [ -z "$PROVIDER" ]; then
  echo "Usar: bash build_and_push.sh [aws|azure|gcp]"
  exit 1
fi

# Build Docker
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

# Tag & push según proveedor
# AWS
if [ "$PROVIDER" = "aws" ]; then
  AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
  FULL_IMAGE_NAME="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${IMAGE_NAME}:${IMAGE_TAG}"
  aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
  docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE_NAME}
  docker push ${FULL_IMAGE_NAME}
fi

# Azure
if [ "$PROVIDER" = "azure" ]; then
  FULL_IMAGE_NAME="${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}"
  az acr login --name ${ACR_NAME}
  docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE_NAME}
  docker push ${FULL_IMAGE_NAME}
fi

# GCP
if [ "$PROVIDER" = "gcp" ]; then
  FULL_IMAGE_NAME="europe-docker.pkg.dev/${PROJECT_ID}/${IMAGE_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"
  gcloud auth configure-docker europe-docker.pkg.dev
  docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE_NAME}
  docker push ${FULL_IMAGE_NAME}
fi
