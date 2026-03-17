#!/bin/bash

RESOURCE_GROUP="gramvaani-rg"
CONTAINER_APP_NAME="gramvaani-backend"

if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

source .env

echo "🔐 Adding secrets to Container App..."

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

echo ""
echo "🔄 Updating environment variables..."

az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    MONGO_URL=secretref:mongo-url \
    AZURE_OPENAI_ENDPOINT=secretref:azure-openai-endpoint \
    AZURE_OPENAI_API_KEY=secretref:azure-openai-key \
    AZURE_OPENAI_DEPLOYMENT=secretref:azure-openai-deployment \
    AZURE_SPEECH_KEY=secretref:azure-speech-key \
    AZURE_SPEECH_REGION=secretref:azure-speech-region \
    OPENWEATHER_API_KEY=secretref:openweather-key \
    SECRET_KEY=secretref:secret-key \
    AWS_ACCESS_KEY_ID=secretref:aws-access-key \
    AWS_SECRET_ACCESS_KEY=secretref:aws-secret-key \
    AWS_DEFAULT_REGION=ap-south-1 \
    WHATSAPP_ACCESS_TOKEN="$WHATSAPP_ACCESS_TOKEN" \
    WHATSAPP_PHONE_NUMBER_ID="$WHATSAPP_PHONE_NUMBER_ID" \
    WHATSAPP_VERIFY_TOKEN="$WHATSAPP_VERIFY_TOKEN"

echo "✅ Secrets configured!"
echo "🌐 Backend URL: https://gramvaani-backend.whiteglacier-e8ae20da.centralindia.azurecontainerapps.io"
