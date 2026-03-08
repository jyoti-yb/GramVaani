# Azure Container Apps Deployment Guide

## Prerequisites
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login
```

## Deploy Backend

### 1. Deploy Container App
```bash
cd backend
./deploy-azure.sh
```

### 2. Add Environment Secrets
```bash
./add-secrets.sh
```

### 3. Update Frontend
Update `frontend/src` API URLs from `http://localhost:8000` to your Azure URL:
```
https://gramvaani-backend.{region}.azurecontainerapps.io
```

## Manual Deployment (Alternative)

```bash
# Build locally and push
docker build -t gramvaani-backend .
az acr login --name gramvaaniregistry
docker tag gramvaani-backend gramvaaniregistry.azurecr.io/gramvaani-backend:latest
docker push gramvaaniregistry.azurecr.io/gramvaani-backend:latest

# Update container app
az containerapp update \
  --name gramvaani-backend \
  --resource-group gramvaani-rg \
  --image gramvaaniregistry.azurecr.io/gramvaani-backend:latest
```

## Monitor & Logs
```bash
# View logs
az containerapp logs show \
  --name gramvaani-backend \
  --resource-group gramvaani-rg \
  --follow

# Check status
az containerapp show \
  --name gramvaani-backend \
  --resource-group gramvaani-rg
```

## Cost Optimization
- Free tier: 180,000 vCPU-seconds/month
- Auto-scale: 1-3 replicas
- Estimated: $10-30/month

## Cleanup
```bash
az group delete --name gramvaani-rg --yes
```
