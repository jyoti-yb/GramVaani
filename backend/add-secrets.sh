#!/bin/bash

# Configuration
RESOURCE_GROUP="gramvaani-rg"
CONTAINER_APP_NAME="gramvaani-backend"

echo "🔐 Adding secrets to Azure Container App"
echo "Enter your environment variables:"

read -p "MONGO_URL: " MONGO_URL
read -p "AZURE_OPENAI_ENDPOINT: " AZURE_OPENAI_ENDPOINT
read -sp "AZURE_OPENAI_API_KEY: " AZURE_OPENAI_API_KEY
echo ""
read -p "AZURE_OPENAI_DEPLOYMENT: " AZURE_OPENAI_DEPLOYMENT
read -sp "AZURE_SPEECH_KEY: " AZURE_SPEECH_KEY
echo ""
read -p "AZURE_SPEECH_REGION: " AZURE_SPEECH_REGION
read -sp "OPENWEATHER_API_KEY: " OPENWEATHER_API_KEY
echo ""
read -sp "SECRET_KEY: " SECRET_KEY
echo ""
read -sp "AWS_ACCESS_KEY_ID: " AWS_ACCESS_KEY_ID
echo ""
read -sp "AWS_SECRET_ACCESS_KEY: " AWS_SECRET_ACCESS_KEY
echo ""

# Add secrets
az containerapp secret set \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --secrets \
    mongo-url="$MONGO_URL" \
    azure-openai-endpoint="$AZURE_OPENAI_ENDPOINT" \
    azure-openai-key="$AZURE_OPENAI_API_KEY" \
    azure-openai-deployment="$AZURE_OPENAI_DEPLOYMENT" \
    azure-speech-key="$AZURE_SPEECH_KEY" \
    azure-speech-region="$AZURE_SPEECH_REGION" \
    openweather-key="$OPENWEATHER_API_KEY" \
    secret-key="$SECRET_KEY" \
    aws-access-key="$AWS_ACCESS_KEY_ID" \
    aws-secret-key="$AWS_SECRET_ACCESS_KEY"

echo "✅ Secrets added successfully!"
